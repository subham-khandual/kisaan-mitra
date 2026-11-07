/**
 * CropSelectionScreen — Farmer selects which crops & mandis to watch.
 * ✅ UPDATED:
 *   - User can type any custom crop not in the preset list
 *   - Markets are filtered based on user's state/district
 *   - User can also type a custom market/mandi name
 */

import React, { useState, useMemo } from 'react';
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity,
  TextInput, Alert, ActivityIndicator, Switch,
} from 'react-native';
import { userAPI, CropPreference } from '../services/api';
import { useAuth } from '../services/AuthContext';
import { COLORS, SPACING, RADIUS, SHADOWS, getCropMeta } from '../utils/theme';

// ── Preset crops (user can also type their own) ───────────────────────────────
const PRESET_CROPS = [
  'Tomato', 'Onion', 'Potato', 'Rice', 'Paddy', 'Maize',
  'Wheat', 'Groundnut', 'Soyabean', 'Brinjal', 'Cabbage',
  'Cauliflower', 'Chilli', 'Turmeric', 'Ginger', 'Garlic',
  'Banana', 'Mango', 'Sugarcane', 'Cotton', 'Jowar',
];

// ── Markets by state ──────────────────────────────────────────────────────────
const MARKETS_BY_STATE: Record<string, string[]> = {
  Karnataka: [
    'Bengaluru', 'Mysuru', 'Hubballi', 'Davangere', 'Raichur',
    'Bidar', 'Hassan', 'Tumakuru', 'Shimoga', 'Dharwad',
    'Mangaluru', 'Belagavi', 'Kalaburagi', 'Vijayapura', 'Udupi',
  ],
  Maharashtra: [
    'Mumbai', 'Pune', 'Nashik', 'Nagpur', 'Aurangabad',
    'Solapur', 'Kolhapur', 'Amravati', 'Nanded', 'Sangli',
  ],
  'Andhra Pradesh': [
    'Visakhapatnam', 'Vijayawada', 'Guntur', 'Tirupati', 'Kurnool',
    'Kakinada', 'Nellore', 'Rajahmundry', 'Kadapa', 'Anantapur',
  ],
  'Telangana': [
    'Hyderabad', 'Warangal', 'Nizamabad', 'Karimnagar', 'Khammam',
    'Mahbubnagar', 'Nalgonda', 'Adilabad', 'Medak', 'Rangareddy',
  ],
  'Tamil Nadu': [
    'Chennai', 'Coimbatore', 'Madurai', 'Trichy', 'Salem',
    'Tirunelveli', 'Erode', 'Vellore', 'Dindigul', 'Tirupur',
  ],
  'Uttar Pradesh': [
    'Lucknow', 'Kanpur', 'Agra', 'Varanasi', 'Meerut',
    'Allahabad', 'Ghaziabad', 'Bareilly', 'Moradabad', 'Mathura',
  ],
  Punjab: [
    'Amritsar', 'Ludhiana', 'Jalandhar', 'Patiala', 'Bathinda',
    'Mohali', 'Hoshiarpur', 'Gurdaspur', 'Firozpur', 'Fazilka',
  ],
  Haryana: [
    'Gurugram', 'Faridabad', 'Rohtak', 'Hisar', 'Karnal',
    'Ambala', 'Panipat', 'Sonipat', 'Yamunanagar', 'Rewari',
  ],
  Gujarat: [
    'Ahmedabad', 'Surat', 'Vadodara', 'Rajkot', 'Bhavnagar',
    'Jamnagar', 'Junagadh', 'Gandhinagar', 'Anand', 'Mehsana',
  ],
  'Madhya Pradesh': [
    'Bhopal', 'Indore', 'Gwalior', 'Jabalpur', 'Ujjain',
    'Sagar', 'Ratlam', 'Rewa', 'Dewas', 'Satna',
  ],
  Rajasthan: [
    'Jaipur', 'Jodhpur', 'Kota', 'Ajmer', 'Udaipur',
    'Bikaner', 'Alwar', 'Bharatpur', 'Sikar', 'Pali',
  ],
};

// Fallback markets if state not found
const DEFAULT_MARKETS = [
  'Local Mandi', 'District Mandi', 'State Mandi',
];

function getMarketsForState(state: string): string[] {
  if (!state) return DEFAULT_MARKETS;
  // Try exact match first
  if (MARKETS_BY_STATE[state]) return MARKETS_BY_STATE[state];
  // Try case-insensitive match
  const key = Object.keys(MARKETS_BY_STATE).find(
    k => k.toLowerCase() === state.toLowerCase()
  );
  return key ? MARKETS_BY_STATE[key] : DEFAULT_MARKETS;
}

export default function CropSelectionScreen({ navigation }: any) {
  const { user, refreshUser } = useAuth();
  const [crops, setCrops] = useState<CropPreference[]>(user?.crops ?? []);
  const [saving, setSaving] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);

  // Add form state
  const [cropSearch, setCropSearch] = useState('');
  const [newCrop, setNewCrop] = useState('');
  const [newMarket, setNewMarket] = useState('');
  const [customMarket, setCustomMarket] = useState('');
  const [useCustomMarket, setUseCustomMarket] = useState(false);

  const userState = user?.location_state ?? 'Karnataka';
  const userDistrict = user?.location_district ?? '';

  // Markets for user's state
  const stateMarkets = useMemo(() => getMarketsForState(userState), [userState]);

  // Filter preset crops by search query
  const filteredCrops = useMemo(() => {
    if (!cropSearch.trim()) return PRESET_CROPS;
    return PRESET_CROPS.filter(c =>
      c.toLowerCase().includes(cropSearch.toLowerCase())
    );
  }, [cropSearch]);

  // If typed text doesn't match any preset, show "Add custom" option
  const showCustomCropOption =
    cropSearch.trim().length > 1 &&
    !PRESET_CROPS.some(c => c.toLowerCase() === cropSearch.toLowerCase());

  const selectCrop = (crop: string) => {
    setNewCrop(crop);
    setCropSearch(crop);
  };

  const addCrop = () => {
    const finalCrop = newCrop.trim() || cropSearch.trim();
    const finalMarket = useCustomMarket
      ? customMarket.trim()
      : newMarket.trim();

    if (!finalCrop) {
      Alert.alert('Missing Info', 'Please select or type a crop name.');
      return;
    }
    if (!finalMarket) {
      Alert.alert('Missing Info', 'Please select or type a market/mandi name.');
      return;
    }

    const exists = crops.find(
      c =>
        c.commodity.toLowerCase() === finalCrop.toLowerCase() &&
        c.market.toLowerCase() === finalMarket.toLowerCase()
    );
    if (exists) {
      Alert.alert('Already added', `${finalCrop} at ${finalMarket} is already in your list.`);
      return;
    }

    setCrops(prev => [
      ...prev,
      {
        commodity: finalCrop,
        state: userState,
        district: userDistrict,
        market: finalMarket,
        alert_enabled: true,
      },
    ]);

    // Reset form
    setCropSearch('');
    setNewCrop('');
    setNewMarket('');
    setCustomMarket('');
    setUseCustomMarket(false);
    setShowAddForm(false);
  };

  const removeCrop = (idx: number) => {
    Alert.alert(
      'Remove Crop',
      `Remove ${crops[idx].commodity} from your watchlist?`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Remove',
          style: 'destructive',
          onPress: () => setCrops(c => c.filter((_, i) => i !== idx)),
        },
      ]
    );
  };

  const toggleAlert = (idx: number) => {
    setCrops(prev =>
      prev.map((c, i) => (i === idx ? { ...c, alert_enabled: !c.alert_enabled } : c))
    );
  };

  const savePreferences = async () => {
    setSaving(true);
    try {
      await userAPI.updatePreferences({ crops });
      await refreshUser();
      Alert.alert('Saved! 🌱', 'Your crop preferences have been updated.');
      navigation.goBack();
    } catch (err) {
      Alert.alert('Error', 'Could not save preferences. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.scrollContent}
      keyboardShouldPersistTaps="handled"
    >
      <Text style={styles.pageTitle}>🌾 My Crops</Text>
      <Text style={styles.pageSubtitle}>
        Select crops and mandis to get live price alerts
      </Text>

      {/* ── Existing crops ── */}
      {crops.map((crop, idx) => {
        const meta = getCropMeta(crop.commodity);
        return (
          <View key={idx} style={styles.cropCard}>
            <View style={[styles.cropIcon, { backgroundColor: meta.bg }]}>
              <Text style={styles.cropEmoji}>{meta.emoji}</Text>
            </View>
            <View style={styles.cropInfo}>
              <Text style={styles.cropName}>{crop.commodity}</Text>
              <Text style={styles.mandiName}>📍 {crop.market}, {crop.state}</Text>
            </View>
            <View style={styles.cropActions}>
              <Switch
                value={crop.alert_enabled}
                onValueChange={() => toggleAlert(idx)}
                trackColor={{ false: COLORS.border, true: COLORS.primaryMid }}
                thumbColor={crop.alert_enabled ? COLORS.primary : COLORS.textHint}
                style={{ transform: [{ scaleX: 0.85 }, { scaleY: 0.85 }] }}
              />
              <TouchableOpacity onPress={() => removeCrop(idx)} style={styles.removeBtn}>
                <Text style={styles.removeBtnText}>✕</Text>
              </TouchableOpacity>
            </View>
          </View>
        );
      })}

      {/* ── Add crop form ── */}
      {showAddForm ? (
        <View style={styles.addForm}>
          <Text style={styles.addFormTitle}>Add a Crop</Text>

          {/* ── Crop search/type ── */}
          <Text style={styles.label}>Search or Type Crop Name</Text>
          <View style={styles.searchWrapper}>
            <Text style={styles.searchIcon}>🔍</Text>
            <TextInput
              style={styles.searchInput}
              placeholder="e.g. Tomato, Bajra, Jowar..."
              placeholderTextColor={COLORS.textHint}
              value={cropSearch}
              onChangeText={text => {
                setCropSearch(text);
                setNewCrop(''); // clear selection when typing
              }}
              autoCapitalize="words"
            />
            {cropSearch.length > 0 && (
              <TouchableOpacity
                onPress={() => { setCropSearch(''); setNewCrop(''); }}
                style={styles.clearBtn}
              >
                <Text style={styles.clearBtnText}>✕</Text>
              </TouchableOpacity>
            )}
          </View>

          {/* Selected crop indicator */}
          {newCrop ? (
            <View style={styles.selectedBadge}>
              <Text style={styles.selectedBadgeText}>
                {getCropMeta(newCrop).emoji} {newCrop} selected ✓
              </Text>
            </View>
          ) : null}

          {/* Custom crop add option */}
          {showCustomCropOption && (
            <TouchableOpacity
              style={styles.customAddRow}
              onPress={() => selectCrop(cropSearch.trim())}
            >
              <Text style={styles.customAddIcon}>➕</Text>
              <Text style={styles.customAddText}>
                Add "<Text style={styles.customAddHighlight}>{cropSearch.trim()}</Text>" as a new crop
              </Text>
            </TouchableOpacity>
          )}

          {/* Filtered preset chips */}
          {filteredCrops.length > 0 && (
            <ScrollView
              horizontal
              showsHorizontalScrollIndicator={false}
              style={styles.chipRow}
            >
              {filteredCrops.map(crop => (
                <TouchableOpacity
                  key={crop}
                  style={[styles.chip, newCrop === crop && styles.chipActive]}
                  onPress={() => selectCrop(crop)}
                >
                  <Text style={styles.chipEmoji}>{getCropMeta(crop).emoji}</Text>
                  <Text style={[styles.chipText, newCrop === crop && styles.chipTextActive]}>
                    {crop}
                  </Text>
                </TouchableOpacity>
              ))}
            </ScrollView>
          )}

          {/* ── Market / Mandi ── */}
          <Text style={[styles.label, { marginTop: 4 }]}>
            Select Market (Mandi) — {userState}
          </Text>

          {/* Toggle: preset vs custom */}
          <View style={styles.marketToggleRow}>
            <TouchableOpacity
              style={[styles.toggleBtn, !useCustomMarket && styles.toggleBtnActive]}
              onPress={() => setUseCustomMarket(false)}
            >
              <Text style={[styles.toggleBtnText, !useCustomMarket && styles.toggleBtnTextActive]}>
                📍 Choose from list
              </Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.toggleBtn, useCustomMarket && styles.toggleBtnActive]}
              onPress={() => setUseCustomMarket(true)}
            >
              <Text style={[styles.toggleBtnText, useCustomMarket && styles.toggleBtnTextActive]}>
                ✏️ Type mandi name
              </Text>
            </TouchableOpacity>
          </View>

          {useCustomMarket ? (
            <TextInput
              style={styles.customMarketInput}
              placeholder="e.g. Yelahanka Mandi, Kolar APMC..."
              placeholderTextColor={COLORS.textHint}
              value={customMarket}
              onChangeText={setCustomMarket}
              autoCapitalize="words"
            />
          ) : (
            <ScrollView
              horizontal
              showsHorizontalScrollIndicator={false}
              style={styles.chipRow}
            >
              {stateMarkets.map(m => (
                <TouchableOpacity
                  key={m}
                  style={[styles.marketChip, newMarket === m && styles.chipActive]}
                  onPress={() => setNewMarket(m)}
                >
                  <Text
                    style={[
                      styles.chipText,
                      newMarket === m && styles.chipTextActive,
                    ]}
                  >
                    📍 {m}
                  </Text>
                </TouchableOpacity>
              ))}
            </ScrollView>
          )}

          {/* Selected market indicator */}
          {((!useCustomMarket && newMarket) || (useCustomMarket && customMarket.trim())) ? (
            <View style={[styles.selectedBadge, { backgroundColor: '#E3F2FD' }]}>
              <Text style={[styles.selectedBadgeText, { color: '#1565C0' }]}>
                📍 {useCustomMarket ? customMarket.trim() : newMarket} selected ✓
              </Text>
            </View>
          ) : null}

          <View style={styles.addFormBtns}>
            <TouchableOpacity
              style={styles.cancelBtn}
              onPress={() => {
                setShowAddForm(false);
                setCropSearch('');
                setNewCrop('');
                setNewMarket('');
                setCustomMarket('');
                setUseCustomMarket(false);
              }}
            >
              <Text style={styles.cancelBtnText}>Cancel</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.confirmBtn} onPress={addCrop}>
              <Text style={styles.confirmBtnText}>Add Crop ✓</Text>
            </TouchableOpacity>
          </View>
        </View>
      ) : (
        <TouchableOpacity
          style={styles.addCropBtn}
          onPress={() => setShowAddForm(true)}
        >
          <Text style={styles.addCropBtnText}>+ Add Crop</Text>
        </TouchableOpacity>
      )}

      {/* Save button */}
      <TouchableOpacity
        style={[styles.saveBtn, saving && styles.btnDisabled]}
        onPress={savePreferences}
        disabled={saving}
      >
        {saving ? (
          <ActivityIndicator color={COLORS.white} />
        ) : (
          <Text style={styles.saveBtnText}>Save Preferences 💾</Text>
        )}
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.background },
  scrollContent: { padding: SPACING.md, paddingBottom: 60 },
  pageTitle: { fontSize: 24, fontWeight: '800', color: COLORS.textPrimary, marginBottom: 4 },
  pageSubtitle: { fontSize: 14, color: COLORS.textSecondary, marginBottom: SPACING.lg, lineHeight: 20 },

  cropCard: {
    backgroundColor: COLORS.surface, borderRadius: RADIUS.lg,
    padding: SPACING.md, marginBottom: 10,
    flexDirection: 'row', alignItems: 'center',
    ...SHADOWS.card,
  },
  cropIcon: { width: 48, height: 48, borderRadius: RADIUS.md, alignItems: 'center', justifyContent: 'center', marginRight: 12 },
  cropEmoji: { fontSize: 26 },
  cropInfo: { flex: 1 },
  cropName: { fontSize: 16, fontWeight: '700', color: COLORS.textPrimary },
  mandiName: { fontSize: 12, color: COLORS.textSecondary, marginTop: 2 },
  cropActions: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  removeBtn: { width: 28, height: 28, borderRadius: 14, backgroundColor: COLORS.dangerLight, alignItems: 'center', justifyContent: 'center' },
  removeBtnText: { color: COLORS.danger, fontSize: 12, fontWeight: '700' },

  addCropBtn: {
    borderWidth: 2, borderStyle: 'dashed', borderColor: COLORS.primary,
    borderRadius: RADIUS.lg, padding: SPACING.md,
    alignItems: 'center', marginBottom: SPACING.md,
  },
  addCropBtnText: { color: COLORS.primary, fontWeight: '700', fontSize: 16 },

  addForm: {
    backgroundColor: COLORS.surface, borderRadius: RADIUS.xl,
    padding: SPACING.md, marginBottom: SPACING.md, ...SHADOWS.card,
  },
  addFormTitle: { fontSize: 17, fontWeight: '700', color: COLORS.textPrimary, marginBottom: 12 },
  label: { fontSize: 12, fontWeight: '600', color: COLORS.textSecondary, marginBottom: 8, textTransform: 'uppercase', letterSpacing: 0.5 },

  // Search input
  searchWrapper: {
    flexDirection: 'row', alignItems: 'center',
    borderWidth: 1.5, borderColor: COLORS.border,
    borderRadius: RADIUS.md, paddingHorizontal: 12,
    backgroundColor: COLORS.background, marginBottom: 10,
    height: 46,
  },
  searchIcon: { fontSize: 16, marginRight: 8 },
  searchInput: { flex: 1, fontSize: 15, color: COLORS.textPrimary },
  clearBtn: { padding: 4 },
  clearBtnText: { color: COLORS.textHint, fontSize: 13 },

  // Selected badge
  selectedBadge: {
    backgroundColor: COLORS.primaryLight,
    borderRadius: RADIUS.pill, paddingHorizontal: 12, paddingVertical: 6,
    alignSelf: 'flex-start', marginBottom: 10,
  },
  selectedBadgeText: { color: COLORS.primary, fontSize: 13, fontWeight: '700' },

  // Custom crop add row
  customAddRow: {
    flexDirection: 'row', alignItems: 'center', gap: 8,
    padding: 12, borderRadius: RADIUS.md,
    backgroundColor: '#FFF8E1', marginBottom: 10,
    borderWidth: 1, borderColor: '#FFD54F',
  },
  customAddIcon: { fontSize: 16 },
  customAddText: { flex: 1, fontSize: 14, color: COLORS.textPrimary },
  customAddHighlight: { color: COLORS.primary, fontWeight: '700' },

  chipRow: { marginBottom: 12 },
  chip: {
    flexDirection: 'row', alignItems: 'center', gap: 4,
    paddingHorizontal: 12, paddingVertical: 8, marginRight: 8,
    borderRadius: RADIUS.pill, borderWidth: 1.5, borderColor: COLORS.border,
    backgroundColor: COLORS.background,
  },
  chipActive: { borderColor: COLORS.primary, backgroundColor: COLORS.primaryLight },
  chipEmoji: { fontSize: 16 },
  chipText: { fontSize: 13, color: COLORS.textSecondary },
  chipTextActive: { color: COLORS.primary, fontWeight: '700' },
  marketChip: {
    paddingHorizontal: 12, paddingVertical: 8, marginRight: 8,
    borderRadius: RADIUS.pill, borderWidth: 1.5, borderColor: COLORS.border,
    backgroundColor: COLORS.background,
  },

  // Market toggle
  marketToggleRow: { flexDirection: 'row', gap: 8, marginBottom: 12 },
  toggleBtn: {
    flex: 1, paddingVertical: 8, paddingHorizontal: 10,
    borderRadius: RADIUS.md, borderWidth: 1.5, borderColor: COLORS.border,
    alignItems: 'center', backgroundColor: COLORS.background,
  },
  toggleBtnActive: { borderColor: COLORS.primary, backgroundColor: COLORS.primaryLight },
  toggleBtnText: { fontSize: 12, fontWeight: '600', color: COLORS.textSecondary },
  toggleBtnTextActive: { color: COLORS.primary },

  // Custom market input
  customMarketInput: {
    borderWidth: 1.5, borderColor: COLORS.border,
    borderRadius: RADIUS.md, paddingHorizontal: 14,
    height: 46, fontSize: 15, color: COLORS.textPrimary,
    backgroundColor: COLORS.background, marginBottom: 12,
  },

  addFormBtns: { flexDirection: 'row', gap: 10, marginTop: 4 },
  cancelBtn: { flex: 1, borderWidth: 1.5, borderColor: COLORS.border, borderRadius: RADIUS.md, padding: 12, alignItems: 'center' },
  cancelBtnText: { color: COLORS.textSecondary, fontWeight: '600' },
  confirmBtn: { flex: 2, backgroundColor: COLORS.primary, borderRadius: RADIUS.md, padding: 12, alignItems: 'center' },
  confirmBtnText: { color: COLORS.white, fontWeight: '700' },

  saveBtn: {
    backgroundColor: COLORS.primary, borderRadius: RADIUS.lg,
    padding: SPACING.md, alignItems: 'center',
    marginTop: SPACING.md, ...SHADOWS.card,
  },
  btnDisabled: { opacity: 0.6 },
  saveBtnText: { color: COLORS.white, fontSize: 16, fontWeight: '700' },
});