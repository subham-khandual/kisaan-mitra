/**
 * WeatherScreen — Real-time weather for farmer's location.
 * Works for ANY location worldwide.
 * Passes both district and state for accurate results.
 */

import React, { useEffect, useState, useCallback } from 'react';
import {
  View, Text, StyleSheet, ScrollView, RefreshControl,
  ActivityIndicator, TouchableOpacity, StatusBar,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useAuth } from '../services/AuthContext';
import { weatherAPI, WeatherData } from '../services/api';
import { COLORS, SPACING, RADIUS, SHADOWS } from '../utils/theme';

function getWeatherGradient(condition: string): [string, string] {
  const c = condition.toLowerCase();
  if (c.includes('thunderstorm')) return ['#37474F', '#546E7A'];
  if (c.includes('rain'))         return ['#1565C0', '#1E88E5'];
  if (c.includes('drizzle'))      return ['#1976D2', '#42A5F5'];
  if (c.includes('snow'))         return ['#546E7A', '#78909C'];
  if (c.includes('mist') || c.includes('fog')) return ['#607D8B', '#90A4AE'];
  if (c.includes('cloud'))        return ['#455A64', '#607D8B'];
  if (c.includes('clear'))        return ['#E65100', '#FF8F00'];
  return ['#2D7A45', '#1B5E20'];
}

function getWeatherEmoji(condition: string): string {
  const c = condition.toLowerCase();
  if (c.includes('thunderstorm')) return '⛈️';
  if (c.includes('heavy rain'))   return '🌧️';
  if (c.includes('rain'))         return '🌦️';
  if (c.includes('drizzle'))      return '🌦️';
  if (c.includes('snow'))         return '❄️';
  if (c.includes('mist') || c.includes('fog')) return '🌫️';
  if (c.includes('cloud'))        return '⛅';
  if (c.includes('clear'))        return '☀️';
  return '🌤️';
}

function getAlertColor(alertType: string): string {
  switch (alertType) {
    case 'thunderstorm': return '#B71C1C';
    case 'heavy_rain':   return '#1565C0';
    case 'rain':         return '#1976D2';
    case 'extreme_heat': return '#BF360C';
    case 'heat':         return '#E65100';
    case 'strong_wind':  return '#4527A0';
    case 'humidity':     return '#00695C';
    case 'cold':         return '#1A237E';
    default:             return COLORS.primary;
  }
}

export default function WeatherScreen() {
  const { user } = useAuth();
  const [weather, setWeather]     = useState<WeatherData | null>(null);
  const [alert, setAlert]         = useState<{ title: string; body: string; alert_type: string } | null>(null);
  const [loading, setLoading]     = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError]         = useState('');

  const loadWeather = useCallback(async () => {
    try {
      setError('');

      const district = user?.location_district ?? 'Bengaluru';
      const state    = user?.location_state    ?? 'Karnataka';

      console.log(`🌤️ Fetching weather for: ${district}, ${state}`);

      // Pass both city (district) and state for accurate results
      const res = await weatherAPI.getWeather({
        city:  district,
        state: state,
      });

      setWeather(res.data.weather);
      setAlert(res.data.alert ?? null);
    } catch (e: any) {
      console.log('Weather error:', e?.response?.data ?? e?.message);
      setError('Could not load weather. Check your connection.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [user]);

  useEffect(() => { loadWeather(); }, [loadWeather]);

  const onRefresh = () => { setRefreshing(true); loadWeather(); };

  if (loading) {
    return (
      <View style={styles.loader}>
        <ActivityIndicator size="large" color={COLORS.primary} />
        <Text style={styles.loaderText}>
          Fetching weather for {user?.location_district ?? 'your location'}...
        </Text>
      </View>
    );
  }

  const gradient = weather
    ? getWeatherGradient(weather.condition)
    : ['#2D7A45', '#1B5E20'] as [string, string];
  const emoji = weather ? getWeatherEmoji(weather.condition) : '🌤️';

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#fff" />
      }
      showsVerticalScrollIndicator={false}
    >
      <StatusBar barStyle="light-content" />

      {/* ── Hero Weather Card ─────────────────────────────────────────── */}
      <LinearGradient colors={gradient} style={styles.hero}>
        <Text style={styles.locationText}>
          📍 {weather?.city ?? user?.location_district}, {user?.location_state}
        </Text>
        <Text style={styles.weatherEmoji}>{emoji}</Text>
        <Text style={styles.tempText}>{weather?.temp ?? '--'}°C</Text>
        <Text style={styles.descText}>{weather?.description ?? 'Unable to load'}</Text>
        <Text style={styles.feelsLike}>Feels like {weather?.feels_like ?? '--'}°C</Text>
      </LinearGradient>

      {/* ── Weather Alert Banner ──────────────────────────────────────── */}
      {alert && (
        <View style={[styles.alertBanner, { backgroundColor: getAlertColor(alert.alert_type) }]}>
          <Text style={styles.alertTitle}>{alert.title}</Text>
          <Text style={styles.alertBody}>{alert.body}</Text>
        </View>
      )}

      {!alert && weather && (
        <View style={styles.goodWeatherBanner}>
          <Text style={styles.goodWeatherText}>
            ✅ Weather looks good for farming today in {weather.city}!
          </Text>
        </View>
      )}

      {/* ── Stats Grid ───────────────────────────────────────────────── */}
      {weather && (
        <View style={styles.statsGrid}>
          <StatCard emoji="💧" label="Humidity"    value={`${weather.humidity}%`} />
          <StatCard emoji="💨" label="Wind Speed"  value={`${weather.wind_speed} km/h`} />
          <StatCard emoji="☁️" label="Cloud Cover" value={`${weather.cloudiness}%`} />
          <StatCard emoji="🌧️" label="Rain (1h)"   value={`${weather.rain_1h} mm`} />
        </View>
      )}

      {/* ── Farming Tips ─────────────────────────────────────────────── */}
      {weather && <FarmingTips weather={weather} />}

      {/* ── Error State ──────────────────────────────────────────────── */}
      {error ? (
        <View style={styles.errorBox}>
          <Text style={styles.errorEmoji}>🌐</Text>
          <Text style={styles.errorText}>{error}</Text>
          <Text style={styles.errorSubtext}>
            Location: {user?.location_district}, {user?.location_state}
          </Text>
          <TouchableOpacity style={styles.retryBtn} onPress={loadWeather}>
            <Text style={styles.retryText}>🔄 Retry</Text>
          </TouchableOpacity>
        </View>
      ) : null}

      <View style={{ height: 40 }} />
    </ScrollView>
  );
}

function StatCard({ emoji, label, value }: { emoji: string; label: string; value: string }) {
  return (
    <View style={styles.statCard}>
      <Text style={styles.statEmoji}>{emoji}</Text>
      <Text style={styles.statValue}>{value}</Text>
      <Text style={styles.statLabel}>{label}</Text>
    </View>
  );
}

function FarmingTips({ weather }: { weather: WeatherData }) {
  const tips: string[] = [];
  const c = weather.condition.toLowerCase();

  if (c.includes('thunderstorm')) {
    tips.push('⚡ Stay indoors — do not go to the field during thunderstorm.');
    tips.push('🏠 Bring harvested produce and equipment indoors.');
    tips.push('🚫 Avoid operating any electrical farm equipment.');
  } else if (c.includes('rain') || c.includes('drizzle')) {
    tips.push('🚫 Avoid spraying pesticides or fertilizers today.');
    tips.push('🌊 Check field drainage to prevent waterlogging.');
    tips.push('🏠 Bring harvested produce indoors.');
  } else if (weather.temp >= 38) {
    tips.push('💦 Increase irrigation frequency today.');
    tips.push('⏰ Do field work early morning or after 5 PM.');
    tips.push('🌿 Check for wilting in sensitive crops.');
  } else if (weather.humidity >= 85) {
    tips.push('🔍 Inspect crops for signs of fungal disease.');
    tips.push('🌬️ Ensure good ventilation in greenhouse/storage.');
    tips.push('💊 Consider preventive fungicide if humidity persists.');
  } else if (weather.wind_speed >= 30) {
    tips.push('🏗️ Secure shade nets and farm structures.');
    tips.push('🌱 Support tall crops to prevent lodging.');
    tips.push('🚿 Avoid irrigation by sprinklers today.');
  } else if (weather.temp <= 10) {
    tips.push('🧊 Protect sensitive crops from cold stress.');
    tips.push('🌡️ Consider covering young seedlings overnight.');
    tips.push('💧 Reduce irrigation — plants absorb less water in cold.');
  } else {
    tips.push('✅ Good conditions for field work today.');
    tips.push('💧 Normal irrigation schedule is fine.');
    tips.push('🌾 Good time for harvesting if crops are ready.');
  }

  return (
    <View style={styles.tipsCard}>
      <Text style={styles.tipsTitle}>🌾 Farming Tips for Today</Text>
      {tips.map((tip, i) => (
        <Text key={i} style={styles.tipText}>{tip}</Text>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  container:  { flex: 1, backgroundColor: COLORS.background },
  loader: {
    flex: 1, alignItems: 'center', justifyContent: 'center',
    backgroundColor: COLORS.background, padding: SPACING.lg,
  },
  loaderText: { marginTop: 12, color: COLORS.textSecondary, fontSize: 15, textAlign: 'center' },

  hero: {
    paddingTop: 60, paddingBottom: 40,
    alignItems: 'center', paddingHorizontal: SPACING.lg,
  },
  locationText: { color: 'rgba(255,255,255,0.85)', fontSize: 15, marginBottom: 8, textAlign: 'center' },
  weatherEmoji: { fontSize: 80, marginVertical: 8 },
  tempText:     { fontSize: 72, fontWeight: '800', color: '#fff', lineHeight: 80 },
  descText:     { fontSize: 20, color: 'rgba(255,255,255,0.9)', marginTop: 8, fontWeight: '600' },
  feelsLike:    { fontSize: 14, color: 'rgba(255,255,255,0.7)', marginTop: 4 },

  alertBanner: {
    margin: SPACING.md, borderRadius: RADIUS.lg,
    padding: SPACING.md, ...SHADOWS.card,
  },
  alertTitle: { color: '#fff', fontSize: 16, fontWeight: '800', marginBottom: 6 },
  alertBody:  { color: 'rgba(255,255,255,0.92)', fontSize: 14, lineHeight: 20 },

  goodWeatherBanner: {
    margin: SPACING.md, borderRadius: RADIUS.lg,
    padding: SPACING.md, backgroundColor: COLORS.primaryLight,
    borderLeftWidth: 4, borderLeftColor: COLORS.primary,
  },
  goodWeatherText: { color: COLORS.primary, fontSize: 14, fontWeight: '600' },

  statsGrid: {
    flexDirection: 'row', flexWrap: 'wrap',
    paddingHorizontal: SPACING.md, gap: 10, marginBottom: SPACING.md,
  },
  statCard: {
    width: '47%', backgroundColor: COLORS.surface,
    borderRadius: RADIUS.lg, padding: SPACING.md,
    alignItems: 'center', ...SHADOWS.card,
  },
  statEmoji: { fontSize: 28, marginBottom: 6 },
  statValue: { fontSize: 22, fontWeight: '800', color: COLORS.textPrimary },
  statLabel: { fontSize: 12, color: COLORS.textSecondary, marginTop: 2 },

  tipsCard: {
    margin: SPACING.md, backgroundColor: COLORS.surface,
    borderRadius: RADIUS.lg, padding: SPACING.md, ...SHADOWS.card,
  },
  tipsTitle: { fontSize: 16, fontWeight: '700', color: COLORS.textPrimary, marginBottom: 12 },
  tipText:   { fontSize: 14, color: COLORS.textSecondary, lineHeight: 22, marginBottom: 6 },

  errorBox:    { margin: SPACING.md, alignItems: 'center', padding: SPACING.lg },
  errorEmoji:  { fontSize: 48, marginBottom: 12 },
  errorText:   { color: COLORS.danger, fontSize: 15, fontWeight: '600', marginBottom: 6 },
  errorSubtext:{ color: COLORS.textSecondary, fontSize: 13, marginBottom: 16 },
  retryBtn:    {
    backgroundColor: COLORS.primary, borderRadius: RADIUS.md,
    paddingHorizontal: 32, paddingVertical: 12,
  },
  retryText:   { color: '#fff', fontWeight: '700', fontSize: 15 },
});
