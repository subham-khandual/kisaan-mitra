/**
 * CropRecommendationScreen — AI-powered crop recommendations.
 * Uses Groq AI + real-time weather + soil/water/season parameters.
 */

import React, { useState } from 'react';
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity,
  TextInput, ActivityIndicator, StatusBar, Alert,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useAuth } from '../services/AuthContext';
import { cropAPI } from '../services/api';
import { COLORS, SPACING, RADIUS, SHADOWS } from '../utils/theme';

// ── Constants ────────────────────────────────────────────────────────────────

const SOIL_TYPES = [
  { id: 'Black Soil',  emoji: '🟫', desc: 'Cotton belt — high moisture retention' },
  { id: 'Red Soil',    emoji: '🔴', desc: 'Peninsular India — low nutrients' },
  { id: 'Loamy Soil',  emoji: '🟤', desc: 'Best for most crops — balanced' },
  { id: 'Sandy Soil',  emoji: '🟡', desc: 'Quick drainage — drought crops' },
  { id: 'Clay Soil',   emoji: '⬛', desc: 'Heavy — holds water well' },
  { id: 'Silt Soil',   emoji: '🌫️', desc: 'River banks — very fertile' },
  { id: 'Alluvial Soil', emoji: '💧', desc: 'Indo-Gangetic plains — highly fertile' },
  { id: 'Laterite Soil', emoji: '🧱', desc: 'Hilly areas — acidic, iron-rich' },
];

const WATER_OPTIONS = [
  { id: 'Well Irrigated',   emoji: '💦', desc: 'Borewell / canal / drip available' },
  { id: 'Partially Irrigated', emoji: '🚿', desc: '1-2 irrigations possible' },
  { id: 'Rainfed Only',     emoji: '🌧️', desc: 'Depends entirely on rainfall' },
];

const FARMING_TYPES = [
  { id: 'Conventional',  emoji: '🌾' },
  { id: 'Organic',       emoji: '🌿' },
  { id: 'Mixed Farming', emoji: '🐄' },
];

const LAND_SIZES = ['< 1 acre', '1-2 acres', '2-5 acres', '5-10 acres', '> 10 acres'];

// ── Main Screen ──────────────────────────────────────────────────────────────

export default function CropRecommendationScreen() {
  const { user } = useAuth();

  const [soilType,    setSoilType]    = useState('');
  const [water,       setWater]       = useState('');
  const [prevCrop,    setPrevCrop]    = useState('');
  const [landSize,    setLandSize]    = useState('');
  const [farmingType, setFarmingType] = useState('Conventional');
  const [loading,     setLoading]     = useState(false);
  const [result,      setResult]      = useState<any>(null);
  const [step,        setStep]        = useState(1); // 1=form, 2=results

  const handleGetRecommendations = async () => {
    if (!soilType) { Alert.alert('Required', 'Please select your soil type.'); return; }
    if (!water)    { Alert.alert('Required', 'Please select water availability.'); return; }

    setLoading(true);
    try {
      const res = await cropAPI.getRecommendations({
        soil_type:          soilType,
        water_availability: water,
        previous_crop:      prevCrop,
        state:              user?.location_state    ?? 'Karnataka',
        district:           user?.location_district ?? 'Bengaluru',
        land_size:          landSize,
        farming_type:       farmingType,
      });
      setResult(res.data);
      setStep(2);
    } catch (err: any) {
      Alert.alert('Error', 'Could not get recommendations. Please try again.');
      console.log('Crop rec error:', err?.response?.data ?? err?.message);
    } finally {
      setLoading(false);
    }
  };

  if (step === 2 && result) {
    return (
      <ResultsScreen
        result={result}
        onBack={() => { setStep(1); setResult(null); }}
        user={user}
      />
    );
  }

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <StatusBar barStyle="light-content" />

      {/* ── Header ──────────────────────────────────────────────────── */}
      <LinearGradient colors={['#1B5E20', '#2D7A45']} style={styles.header}>
        <Text style={styles.headerEmoji}>🤖</Text>
        <Text style={styles.headerTitle}>AI Crop Advisor</Text>
        <Text style={styles.headerSubtitle}>
          Get personalized crop recommendations based on your soil, weather & location
        </Text>
        <View style={styles.locationBadge}>
          <Text style={styles.locationText}>
            📍 {user?.location_district}, {user?.location_state}
          </Text>
        </View>
      </LinearGradient>

      <View style={styles.form}>

        {/* ── Soil Type ─────────────────────────────────────────────── */}
        <SectionTitle emoji="🌱" title="Soil Type" subtitle="Select the type of soil in your field" />
        <View style={styles.optionGrid}>
          {SOIL_TYPES.map(s => (
            <TouchableOpacity
              key={s.id}
              style={[styles.soilCard, soilType === s.id && styles.soilCardActive]}
              onPress={() => setSoilType(s.id)}
            >
              <Text style={styles.soilEmoji}>{s.emoji}</Text>
              <Text style={[styles.soilName, soilType === s.id && styles.activeText]}>{s.id}</Text>
              <Text style={styles.soilDesc} numberOfLines={2}>{s.desc}</Text>
              {soilType === s.id && <Text style={styles.checkmark}>✓</Text>}
            </TouchableOpacity>
          ))}
        </View>

        {/* ── Water Availability ────────────────────────────────────── */}
        <SectionTitle emoji="💧" title="Water Availability" subtitle="How much irrigation is available?" />
        {WATER_OPTIONS.map(w => (
          <TouchableOpacity
            key={w.id}
            style={[styles.waterCard, water === w.id && styles.waterCardActive]}
            onPress={() => setWater(w.id)}
          >
            <Text style={styles.waterEmoji}>{w.emoji}</Text>
            <View style={styles.waterInfo}>
              <Text style={[styles.waterName, water === w.id && styles.activeText]}>{w.id}</Text>
              <Text style={styles.waterDesc}>{w.desc}</Text>
            </View>
            {water === w.id && <Text style={styles.checkmarkRight}>✓</Text>}
          </TouchableOpacity>
        ))}

        {/* ── Previous Crop ─────────────────────────────────────────── */}
        <SectionTitle emoji="🌾" title="Previous Crop" subtitle="What crop did you grow last season? (Optional)" />
        <TextInput
          style={styles.textInput}
          placeholder="e.g. Rice, Wheat, Maize, None..."
          value={prevCrop}
          onChangeText={setPrevCrop}
          placeholderTextColor={COLORS.textHint}
        />

        {/* ── Land Size ─────────────────────────────────────────────── */}
        <SectionTitle emoji="📐" title="Land Size" subtitle="How much land do you have? (Optional)" />
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.chipScroll}>
          {LAND_SIZES.map(size => (
            <TouchableOpacity
              key={size}
              style={[styles.chip, landSize === size && styles.chipActive]}
              onPress={() => setLandSize(size)}
            >
              <Text style={[styles.chipText, landSize === size && styles.chipTextActive]}>
                {size}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>

        {/* ── Farming Type ──────────────────────────────────────────── */}
        <SectionTitle emoji="🧑‍🌾" title="Farming Type" subtitle="Your farming approach" />
        <View style={styles.farmingRow}>
          {FARMING_TYPES.map(f => (
            <TouchableOpacity
              key={f.id}
              style={[styles.farmingChip, farmingType === f.id && styles.chipActive]}
              onPress={() => setFarmingType(f.id)}
            >
              <Text style={styles.farmingEmoji}>{f.emoji}</Text>
              <Text style={[styles.chipText, farmingType === f.id && styles.chipTextActive]}>
                {f.id}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* ── Get Recommendations Button ────────────────────────────── */}
        <TouchableOpacity
          style={[styles.submitBtn, loading && styles.submitBtnDisabled]}
          onPress={handleGetRecommendations}
          disabled={loading}
        >
          {loading ? (
            <View style={styles.loadingRow}>
              <ActivityIndicator color="#fff" size="small" />
              <Text style={styles.submitBtnText}>  Analyzing your farm conditions...</Text>
            </View>
          ) : (
            <Text style={styles.submitBtnText}>🤖 Get AI Recommendations</Text>
          )}
        </TouchableOpacity>

        <Text style={styles.poweredBy}>⚡ Powered by Groq AI + Real-time Weather</Text>

      </View>
      <View style={{ height: 40 }} />
    </ScrollView>
  );
}

// ── Results Screen ───────────────────────────────────────────────────────────

function ResultsScreen({ result, onBack, user }: any) {
  const recs   = result?.recommendations?.recommendations ?? [];
  const data   = result?.recommendations ?? {};
  const weather = result?.weather_used ?? {};
  const [expanded, setExpanded] = useState<number | null>(0);

  const confidenceColor = (score: number) => {
    if (score >= 85) return '#2D7A45';
    if (score >= 70) return '#F59E0B';
    return '#EF4444';
  };

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <LinearGradient colors={['#1B5E20', '#2D7A45']} style={styles.resultHeader}>
        <TouchableOpacity onPress={onBack} style={styles.backBtn}>
          <Text style={styles.backText}>← Back</Text>
        </TouchableOpacity>
        <Text style={styles.resultTitle}>🌾 Your Crop Recommendations</Text>
        <Text style={styles.resultLocation}>📍 {result?.location}</Text>
        <Text style={styles.resultSeason}>📅 {data?.season}</Text>
      </LinearGradient>

      {/* Weather Used */}
      <View style={styles.weatherBadgeRow}>
        <WeatherPill emoji="🌡️" label={`${weather.temp}°C`} />
        <WeatherPill emoji="💧" label={`${weather.humidity}%`} />
        <WeatherPill emoji="☁️" label={weather.condition} />
        <WeatherPill emoji="💨" label={`${weather.wind_speed}km/h`} />
      </View>

      {/* Analysis Summary */}
      <View style={styles.summaryCard}>
        <Text style={styles.summaryTitle}>🔍 Condition Analysis</Text>
        <Text style={styles.summaryText}>{data?.analysis_summary}</Text>
      </View>

      {/* Top 3 Crop Cards */}
      <Text style={styles.topCropsTitle}>✅ Top {recs.length} Recommended Crops</Text>

      {recs.map((crop: any, idx: number) => (
        <TouchableOpacity
          key={idx}
          style={styles.cropCard}
          onPress={() => setExpanded(expanded === idx ? null : idx)}
          activeOpacity={0.9}
        >
          {/* Card Header */}
          <View style={styles.cropCardHeader}>
            <View style={styles.rankBadge}>
              <Text style={styles.rankText}>#{crop.rank}</Text>
            </View>
            <Text style={styles.cropCardEmoji}>{crop.emoji}</Text>
            <View style={styles.cropCardInfo}>
              <Text style={styles.cropCardName}>{crop.crop}</Text>
              <Text style={styles.cropCardSow}>🌱 Sow: {crop.sowing_time}</Text>
            </View>
            <View style={[styles.confidenceBadge, { backgroundColor: confidenceColor(crop.confidence) }]}>
              <Text style={styles.confidenceText}>{crop.confidence}%</Text>
              <Text style={styles.confidenceLabel}>match</Text>
            </View>
          </View>

          {/* Confidence Bar */}
          <View style={styles.progressBg}>
            <View style={[styles.progressFill, {
              width: `${crop.confidence}%` as any,
              backgroundColor: confidenceColor(crop.confidence),
            }]} />
          </View>

          {/* Expanded Details */}
          {expanded === idx && (
            <View style={styles.cropDetails}>
              <DetailRow emoji="✅" label="Why Suitable" value={crop.why_suitable} />
              <DetailRow emoji="📅" label="Harvest Time" value={crop.harvest_time} />
              <DetailRow emoji="⚖️" label="Expected Yield" value={crop.expected_yield} />
              <DetailRow emoji="💧" label="Water Need" value={crop.water_need} />
              <DetailRow emoji="💰" label="Market Outlook" value={crop.market_outlook} />
              <DetailRow emoji="🌿" label="Key Care Tips" value={crop.key_care_tips} />
            </View>
          )}

          <Text style={styles.expandHint}>
            {expanded === idx ? '▲ Tap to collapse' : '▼ Tap for details'}
          </Text>
        </TouchableOpacity>
      ))}

      {/* Avoid Crops */}
      {data?.avoid_crops?.length > 0 && (
        <View style={styles.avoidCard}>
          <Text style={styles.avoidTitle}>⚠️ Avoid These Crops Now</Text>
          <View style={styles.avoidChips}>
            {data.avoid_crops.map((c: string, i: number) => (
              <View key={i} style={styles.avoidChip}>
                <Text style={styles.avoidChipText}>❌ {c}</Text>
              </View>
            ))}
          </View>
          <Text style={styles.avoidReason}>{data.avoid_reason}</Text>
        </View>
      )}

      <TouchableOpacity style={styles.newSearchBtn} onPress={onBack}>
        <Text style={styles.newSearchText}>🔄 Get New Recommendations</Text>
      </TouchableOpacity>

      <View style={{ height: 40 }} />
    </ScrollView>
  );
}

// ── Helper Components ────────────────────────────────────────────────────────

function SectionTitle({ emoji, title, subtitle }: any) {
  return (
    <View style={styles.sectionTitle}>
      <Text style={styles.sectionEmoji}>{emoji}</Text>
      <View>
        <Text style={styles.sectionTitleText}>{title}</Text>
        {subtitle && <Text style={styles.sectionSubtitle}>{subtitle}</Text>}
      </View>
    </View>
  );
}

function WeatherPill({ emoji, label }: any) {
  return (
    <View style={styles.weatherPill}>
      <Text style={styles.weatherPillEmoji}>{emoji}</Text>
      <Text style={styles.weatherPillText}>{label}</Text>
    </View>
  );
}

function DetailRow({ emoji, label, value }: any) {
  return (
    <View style={styles.detailRow}>
      <Text style={styles.detailEmoji}>{emoji}</Text>
      <View style={styles.detailContent}>
        <Text style={styles.detailLabel}>{label}</Text>
        <Text style={styles.detailValue}>{value}</Text>
      </View>
    </View>
  );
}

// ── Styles ───────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  container:    { flex: 1, backgroundColor: COLORS.background },

  header:       { paddingTop: 56, paddingBottom: 32, paddingHorizontal: SPACING.lg, alignItems: 'center' },
  headerEmoji:  { fontSize: 48, marginBottom: 8 },
  headerTitle:  { fontSize: 26, fontWeight: '800', color: '#fff', textAlign: 'center' },
  headerSubtitle: { fontSize: 14, color: 'rgba(255,255,255,0.8)', textAlign: 'center', marginTop: 8, lineHeight: 20 },
  locationBadge: {
    backgroundColor: 'rgba(255,255,255,0.15)',
    borderRadius: RADIUS.pill, paddingHorizontal: 16, paddingVertical: 6, marginTop: 14,
  },
  locationText: { color: 'rgba(255,255,255,0.9)', fontSize: 13, fontWeight: '600' },

  form:         { padding: SPACING.md },

  sectionTitle: { flexDirection: 'row', alignItems: 'center', gap: 10, marginTop: SPACING.lg, marginBottom: 12 },
  sectionEmoji: { fontSize: 24 },
  sectionTitleText: { fontSize: 16, fontWeight: '700', color: COLORS.textPrimary },
  sectionSubtitle:  { fontSize: 12, color: COLORS.textSecondary, marginTop: 2 },

  optionGrid:   { flexDirection: 'row', flexWrap: 'wrap', gap: 10 },
  soilCard: {
    width: '47%', backgroundColor: COLORS.surface,
    borderRadius: RADIUS.lg, padding: SPACING.sm,
    borderWidth: 2, borderColor: COLORS.border,
    alignItems: 'center', ...SHADOWS.card,
  },
  soilCardActive: { borderColor: COLORS.primary, backgroundColor: COLORS.primaryLight },
  soilEmoji:    { fontSize: 28, marginBottom: 4 },
  soilName:     { fontSize: 13, fontWeight: '700', color: COLORS.textPrimary, textAlign: 'center' },
  soilDesc:     { fontSize: 11, color: COLORS.textSecondary, textAlign: 'center', marginTop: 3 },
  activeText:   { color: COLORS.primary },
  checkmark:    { position: 'absolute', top: 6, right: 8, color: COLORS.primary, fontWeight: '800', fontSize: 14 },

  waterCard: {
    flexDirection: 'row', alignItems: 'center',
    backgroundColor: COLORS.surface, borderRadius: RADIUS.lg,
    padding: SPACING.md, marginBottom: 10,
    borderWidth: 2, borderColor: COLORS.border, ...SHADOWS.card,
  },
  waterCardActive: { borderColor: COLORS.primary, backgroundColor: COLORS.primaryLight },
  waterEmoji:   { fontSize: 32, marginRight: 12 },
  waterInfo:    { flex: 1 },
  waterName:    { fontSize: 15, fontWeight: '700', color: COLORS.textPrimary },
  waterDesc:    { fontSize: 12, color: COLORS.textSecondary, marginTop: 2 },
  checkmarkRight: { color: COLORS.primary, fontWeight: '800', fontSize: 18 },

  textInput: {
    backgroundColor: COLORS.surface, borderRadius: RADIUS.md,
    padding: 13, fontSize: 15, color: COLORS.textPrimary,
    borderWidth: 1.5, borderColor: COLORS.border,
  },

  chipScroll:   { marginBottom: 4 },
  chip: {
    paddingHorizontal: 16, paddingVertical: 9,
    borderRadius: RADIUS.pill, backgroundColor: COLORS.surface,
    borderWidth: 1.5, borderColor: COLORS.border, marginRight: 8,
  },
  chipActive:   { backgroundColor: COLORS.primary, borderColor: COLORS.primary },
  chipText:     { fontSize: 13, fontWeight: '600', color: COLORS.textSecondary },
  chipTextActive: { color: '#fff' },

  farmingRow:   { flexDirection: 'row', gap: 10 },
  farmingChip: {
    flex: 1, flexDirection: 'row', alignItems: 'center',
    justifyContent: 'center', gap: 6,
    paddingVertical: 10, borderRadius: RADIUS.md,
    backgroundColor: COLORS.surface,
    borderWidth: 1.5, borderColor: COLORS.border,
  },
  farmingEmoji: { fontSize: 18 },

  submitBtn: {
    backgroundColor: COLORS.primary, borderRadius: RADIUS.lg,
    padding: 16, alignItems: 'center', marginTop: SPACING.lg,
    ...SHADOWS.card,
  },
  submitBtnDisabled: { opacity: 0.7 },
  submitBtnText:     { color: '#fff', fontSize: 17, fontWeight: '800' },
  loadingRow:        { flexDirection: 'row', alignItems: 'center' },
  poweredBy: {
    textAlign: 'center', color: COLORS.textHint,
    fontSize: 12, marginTop: 10, fontStyle: 'italic',
  },

  // Results
  resultHeader: { paddingTop: 56, paddingBottom: 28, paddingHorizontal: SPACING.lg },
  backBtn:      { marginBottom: 12 },
  backText:     { color: 'rgba(255,255,255,0.8)', fontSize: 15 },
  resultTitle:  { fontSize: 22, fontWeight: '800', color: '#fff' },
  resultLocation: { color: 'rgba(255,255,255,0.8)', marginTop: 6, fontSize: 13 },
  resultSeason:   { color: 'rgba(255,255,255,0.7)', marginTop: 4, fontSize: 13 },

  weatherBadgeRow: {
    flexDirection: 'row', flexWrap: 'wrap', gap: 8,
    padding: SPACING.md,
  },
  weatherPill: {
    flexDirection: 'row', alignItems: 'center', gap: 4,
    backgroundColor: COLORS.surface, borderRadius: RADIUS.pill,
    paddingHorizontal: 12, paddingVertical: 6, ...SHADOWS.card,
  },
  weatherPillEmoji: { fontSize: 14 },
  weatherPillText:  { fontSize: 13, color: COLORS.textPrimary, fontWeight: '600' },

  summaryCard: {
    margin: SPACING.md, backgroundColor: COLORS.surface,
    borderRadius: RADIUS.lg, padding: SPACING.md,
    borderLeftWidth: 4, borderLeftColor: COLORS.primary, ...SHADOWS.card,
  },
  summaryTitle: { fontSize: 14, fontWeight: '700', color: COLORS.textPrimary, marginBottom: 6 },
  summaryText:  { fontSize: 14, color: COLORS.textSecondary, lineHeight: 20 },

  topCropsTitle: {
    fontSize: 17, fontWeight: '800', color: COLORS.textPrimary,
    paddingHorizontal: SPACING.md, marginBottom: 8,
  },

  cropCard: {
    backgroundColor: COLORS.surface, borderRadius: RADIUS.xl,
    marginHorizontal: SPACING.md, marginBottom: 14,
    padding: SPACING.md, ...SHADOWS.card,
    borderWidth: 1, borderColor: COLORS.border,
  },
  cropCardHeader:  { flexDirection: 'row', alignItems: 'center', gap: 10 },
  rankBadge: {
    width: 32, height: 32, borderRadius: 16,
    backgroundColor: COLORS.primary, alignItems: 'center', justifyContent: 'center',
  },
  rankText:        { color: '#fff', fontWeight: '800', fontSize: 14 },
  cropCardEmoji:   { fontSize: 36 },
  cropCardInfo:    { flex: 1 },
  cropCardName:    { fontSize: 18, fontWeight: '800', color: COLORS.textPrimary },
  cropCardSow:     { fontSize: 12, color: COLORS.textSecondary, marginTop: 2 },
  confidenceBadge: { borderRadius: RADIUS.md, padding: 8, alignItems: 'center', minWidth: 56 },
  confidenceText:  { color: '#fff', fontWeight: '800', fontSize: 18 },
  confidenceLabel: { color: 'rgba(255,255,255,0.8)', fontSize: 10 },

  progressBg: {
    height: 6, backgroundColor: COLORS.border,
    borderRadius: 3, marginTop: 12, overflow: 'hidden',
  },
  progressFill:    { height: 6, borderRadius: 3 },

  cropDetails:     { marginTop: 14, gap: 10 },
  detailRow:       { flexDirection: 'row', gap: 10 },
  detailEmoji:     { fontSize: 18, marginTop: 2 },
  detailContent:   { flex: 1 },
  detailLabel:     { fontSize: 12, color: COLORS.textHint, fontWeight: '700', textTransform: 'uppercase' },
  detailValue:     { fontSize: 14, color: COLORS.textSecondary, lineHeight: 20, marginTop: 2 },

  expandHint: {
    textAlign: 'center', color: COLORS.textHint,
    fontSize: 12, marginTop: 10,
  },

  avoidCard: {
    margin: SPACING.md, backgroundColor: '#FFF3E0',
    borderRadius: RADIUS.lg, padding: SPACING.md,
    borderLeftWidth: 4, borderLeftColor: '#FF6F00',
  },
  avoidTitle:    { fontSize: 15, fontWeight: '700', color: '#E65100', marginBottom: 10 },
  avoidChips:    { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginBottom: 10 },
  avoidChip:     { backgroundColor: '#FFCCBC', borderRadius: RADIUS.pill, paddingHorizontal: 12, paddingVertical: 5 },
  avoidChipText: { color: '#BF360C', fontWeight: '600', fontSize: 13 },
  avoidReason:   { fontSize: 13, color: '#E65100', lineHeight: 18 },

  newSearchBtn: {
    backgroundColor: COLORS.primary, borderRadius: RADIUS.lg,
    margin: SPACING.md, padding: 14, alignItems: 'center',
  },
  newSearchText: { color: '#fff', fontWeight: '700', fontSize: 15 },
});
