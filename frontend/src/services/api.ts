/**
 * Kisaan Mitra — Web API Service
 * Adapted from React Native to standard web React.
 */

import axios, { type AxiosInstance, type AxiosResponse } from 'axios';

// ── Change this to your backend URL ──────────────────────────────────────────
const BASE_URL = 'http://localhost:8000/api/v1';

const api: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user_data');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ═══════════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════════

export interface CropPreference {
  commodity: string;
  state: string;
  district: string;
  market: string;
  alert_enabled: boolean;
}

export interface User {
  id: string;
  name: string;
  phone?: string;
  email?: string;
  location_state: string;
  location_district: string;
  village?: string;
  language: string;
  crops: CropPreference[];
  last_active: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface PriceRecord {
  commodity: string;
  market: string;
  district: string;
  state: string;
  modal_price: number;
  min_price: number;
  max_price: number;
  arrival_date: string;
  change_pct: number | null;
  trend: 'up' | 'down' | 'stable' | null;
}

export interface NotificationRecord {
  id: string;
  alert_type: 'normal' | 'big_jump' | 'inactive' | 'critical';
  commodity: string;
  market: string;
  old_price: number;
  new_price: number;
  change_pct: number;
  message_en: string;
  firebase_sent: boolean;
  sms_sent: boolean;
  status: string;
  created_at: string;
}

export interface WeatherData {
  city: string;
  temp: number;
  feels_like: number;
  humidity: number;
  condition: string;
  description: string;
  icon: string;
  wind_speed: number;
  rain_1h: number;
  cloudiness: number;
}

export interface FarmingTipsData {
  summary: string;
  severity: 'good' | 'caution' | 'warning';
  tips: string[];
}

export interface WeatherResponse {
  weather: WeatherData;
  alert: { title: string; body: string; alert_type: string } | null;
  farming_tips: FarmingTipsData | null;
}

export interface CropRecommendationResult {
  season: string;
  analysis_summary: string;
  recommendations: {
    rank: number;
    crop: string;
    emoji: string;
    confidence: number;
    why_suitable: string;
    sowing_time: string;
    harvest_time: string;
    expected_yield: string;
    water_need: string;
    market_outlook: string;
    key_care_tips: string;
  }[];
  avoid_crops: string[];
  avoid_reason: string;
}

export interface MLCropRecommendationResult {
  success: boolean;
  recommended_crop: string;
  confidence: number;
  alternatives: {
    crop: string;
    confidence: number;
  }[];
  soil_health: {
    score: number;
    rating: string;
    details: string;
    remediation: string[];
  };
  fertilizer_prescription: {
    N_deficit: number;
    P_deficit: number;
    K_deficit: number;
    chemical_remediation: {
      fertilizer: string;
      amount_kg_hectare: number;
      application_stage: string;
    }[];
    organic_remediation: string[];
  };
  yield_forecasting: {
    expected_yield_tonnes_hectare: number;
    yield_rating: string;
    yield_factors: string[];
  };
  inputs_used: {
    N: number;
    P: number;
    K: number;
    temperature: number;
    humidity: number;
    ph: number;
    rainfall: number;
  };
}

export interface CropYieldPredictionResult {
  success: boolean;
  data?: {
    estimated_yield_tons_per_hectare: number;
  };
  error?: string;
}

export interface CropYieldMetadata {
  success: boolean;
  data: {
    Region: string[];
    Soil_Type: string[];
    Crop: string[];
    Weather_Condition: string[];
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// Auth
// ═══════════════════════════════════════════════════════════════════════════════

export const authAPI = {
  sendEmailOTP: (data: { email: string; purpose?: string }) =>
    api.post('/auth/send-email-otp', data),

  registerWithEmail: (data: {
    name: string;
    email: string;
    password: string;
    otp: string;
    location_state: string;
    location_district: string;
    village?: string;
    language?: string;
    phone?: string;
  }): Promise<AxiosResponse<AuthResponse>> => api.post('/auth/register-with-email', data),

  register: (data: {
    name: string;
    phone: string;
    email?: string;
    password: string;
    location_state: string;
    location_district: string;
    village?: string;
    language?: string;
    crops?: CropPreference[];
  }): Promise<AxiosResponse<AuthResponse>> => api.post('/register', data),

  login: (data: { email?: string; phone?: string; password: string }): Promise<AxiosResponse<AuthResponse>> =>
    api.post('/login', data),

  forgotPassword: (data: { phone: string }) => api.post('/forgot-password', data),

  verifyOTP: (data: { phone: string; otp: string; new_password: string }) => api.post('/verify-otp', data),

  emailForgotPassword: (data: { email: string }) => api.post('/auth/email/forgot-password', data),

  emailVerifyOTP: (data: { email: string; otp: string; new_password: string }) =>
    api.post('/auth/email/verify-otp', data),

  firebaseLogin: (data: {
    id_token: string;
    name?: string;
    email?: string;
    location_state?: string;
    location_district?: string;
    village?: string;
    language?: string;
  }): Promise<AxiosResponse<AuthResponse>> => api.post('/firebase-login', data),
};

// ═══════════════════════════════════════════════════════════════════════════════
// Prices
// ═══════════════════════════════════════════════════════════════════════════════

export const pricesAPI = {
  getPrices: (params: {
    commodity?: string;
    state?: string;
    district?: string;
    market?: string;
    limit?: number;
  }): Promise<AxiosResponse<PriceRecord[]>> => api.get('/prices', { params }),

  getHistory: (commodity: string, market: string, days = 7) =>
    api.get('/prices/history', { params: { commodity, market, days } }),

  getTrending: (state?: string) =>
    api.get('/prices/trending', { params: { state } }),

  manualRefresh: (commodity?: string, state?: string) =>
    api.post('/prices/refresh', null, { params: { commodity, state } }),
};

// ═══════════════════════════════════════════════════════════════════════════════
// Notifications
// ═══════════════════════════════════════════════════════════════════════════════

export const notificationsAPI = {
  getNotifications: (limit = 20, skip = 0): Promise<AxiosResponse<NotificationRecord[]>> =>
    api.get('/notifications', { params: { limit, skip } }),
  getUnreadCount: () => api.get('/notifications/unread-count'),
};

// ═══════════════════════════════════════════════════════════════════════════════
// Weather
// ═══════════════════════════════════════════════════════════════════════════════

export const weatherAPI = {
  getWeather: (params: {
    lat?: number;
    lon?: number;
    city?: string;
    state?: string;
    country?: string;
    crops?: string;
  }): Promise<AxiosResponse<WeatherResponse>> => api.get('/weather', { params }),
};

// ═══════════════════════════════════════════════════════════════════════════════
// AI Crop Recommendation
// ═══════════════════════════════════════════════════════════════════════════════

export const cropAPI = {
  getRecommendations: (data: {
    soil_type: string;
    water_availability: string;
    previous_crop?: string;
    land_size?: string;
    farming_type?: string;
  }) => api.post('/crop-recommendation', data),

  getMLRecommendations: (data: {
    N: number;
    P: number;
    K: number;
    temperature: number;
    humidity: number;
    ph: number;
    rainfall: number;
    state?: string;
    district?: string;
  }): Promise<AxiosResponse<MLCropRecommendationResult>> => api.post('/crop-recommendation/predict', data),
};

// ═══════════════════════════════════════════════════════════════════════════════
// Crop Yield Prediction
// ═══════════════════════════════════════════════════════════════════════════════

export const yieldAPI = {
  predictYield: (data: {
    region: string;
    soil_type: string;
    crop: string;
    rainfall_mm: number;
    temperature_celsius: number;
    fertilizer_used: boolean;
    irrigation_used: boolean;
    weather_condition: string;
    days_to_harvest: number;
  }): Promise<AxiosResponse<CropYieldPredictionResult>> => api.post('/crop-yield/predict', data),

  getMetadata: (): Promise<AxiosResponse<CropYieldMetadata>> => api.get('/crop-yield/metadata'),
};

// ═══════════════════════════════════════════════════════════════════════════════
// Disease Detection
// ═══════════════════════════════════════════════════════════════════════════════

export const diseaseAPI = {
  detectDisease: (formData: FormData) => api.post('/disease/detect', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
};

// ═══════════════════════════════════════════════════════════════════════════════
// Marketplace
// ═══════════════════════════════════════════════════════════════════════════════

export const marketplaceAPI = {
  getListings: (params?: { category?: string; state?: string; query?: string }) => 
    api.get('/marketplace', { params }),
    
  createListing: (data: any) => api.post('/marketplace', data),
};

// ═══════════════════════════════════════════════════════════════════════════════
// Reports (PDF)
// ═══════════════════════════════════════════════════════════════════════════════

export const reportsAPI = {
  generateReport: (data: { report_type: string; data: any }) => 
    api.post('/reports/generate', data, { responseType: 'blob' }),
};

// ═══════════════════════════════════════════════════════════════════════════════
// User
// ═══════════════════════════════════════════════════════════════════════════════

export const userAPI = {
  getProfile: (): Promise<AxiosResponse<User>> => api.get('/user/profile'),

  updatePreferences: (data: {
    crops?: CropPreference[];
    language?: string;
    location_state?: string;
    location_district?: string;
  }) => api.post('/user/preferences', data),
};

export default api;
