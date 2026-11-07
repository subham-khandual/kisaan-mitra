import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import { authAPI, userAPI, type User, type AuthResponse } from '../services/api';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (identifier: string, password: string, rememberMe?: boolean) => Promise<void>;
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
  }) => Promise<void>;
  register: (data: {
    name: string;
    phone: string;
    email?: string;
    password: string;
    location_state: string;
    location_district: string;
    village?: string;
    language?: string;
  }) => Promise<void>;
  loginWithFirebase: (data: {
    id_token: string;
    name?: string;
    email?: string;
    location_state?: string;
    location_district?: string;
    village?: string;
    language?: string;
  }, rememberMe?: boolean) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const savedToken = localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token');
    const savedUser = localStorage.getItem('user_data') || sessionStorage.getItem('user_data');
    if (savedToken && savedUser) {
      setToken(savedToken);
      setUser(JSON.parse(savedUser));
    }
    setIsLoading(false);
  }, []);

  const handleAuthResponse = (data: AuthResponse, rememberMe: boolean = true) => {
    setToken(data.access_token);
    setUser(data.user);
    const storage = rememberMe ? localStorage : sessionStorage;
    storage.setItem('auth_token', data.access_token);
    storage.setItem('user_data', JSON.stringify(data.user));
  };

  const login = async (identifier: string, password: string, rememberMe: boolean = true) => {
    const payload = identifier.includes('@')
      ? { email: identifier.trim().toLowerCase(), password }
      : { phone: identifier.trim(), password };
    const res = await authAPI.login(payload);
    handleAuthResponse(res.data, rememberMe);
  };

  const registerWithEmail = async (data: {
    name: string;
    email: string;
    password: string;
    otp: string;
    location_state: string;
    location_district: string;
    village?: string;
    language?: string;
    phone?: string;
  }) => {
    const res = await authAPI.registerWithEmail(data);
    handleAuthResponse(res.data, true);
  };

  const register = async (data: {
    name: string;
    phone: string;
    email?: string;
    password: string;
    location_state: string;
    location_district: string;
    village?: string;
    language?: string;
  }) => {
    const res = await authAPI.register({ ...data, language: data.language || 'en', crops: [] });
    handleAuthResponse(res.data, true);
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_data');
    sessionStorage.removeItem('auth_token');
    sessionStorage.removeItem('user_data');
  };

  const refreshUser = async () => {
    try {
      const res = await userAPI.getProfile();
      setUser(res.data);
      localStorage.setItem('user_data', JSON.stringify(res.data));
    } catch {
      // silently fail
    }
  };

  const loginWithFirebase = async (
    data: {
      id_token: string;
      name?: string;
      email?: string;
      location_state?: string;
      location_district?: string;
      village?: string;
      language?: string;
    },
    rememberMe: boolean = true
  ) => {
    const res = await authAPI.firebaseLogin(data);
    handleAuthResponse(res.data, rememberMe);
  };

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, register, registerWithEmail, loginWithFirebase, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be inside AuthProvider');
  return ctx;
}
