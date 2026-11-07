import { useState, type FormEvent, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { authAPI } from '../services/api';
import INDIAN_LOCATIONS from '../data/indianLocations';
import { Mail, CheckCircle2, ShieldCheck, ArrowRight, RefreshCw, Lock, User, MapPin, Eye, EyeOff, Check, X } from 'lucide-react';

const STATES = Object.keys(INDIAN_LOCATIONS).sort();
const EMAIL_REGEX = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
const NAME_REGEX = /^[a-zA-Z\s]{3,50}$/;

export default function RegisterPage() {
  const { registerWithEmail } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    location_state: '',
    location_district: '',
    village: '',
    language: 'en',
  });

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [otpCode, setOtpCode] = useState('');
  const [otpSent, setOtpSent] = useState(false);
  const [timer, setTimer] = useState(0);

  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const [otpLoading, setOtpLoading] = useState(false);

  // Timer countdown for resending OTP
  useEffect(() => {
    let interval: any = null;
    if (timer > 0) {
      interval = setInterval(() => setTimer(t => t - 1), 1000);
    }
    return () => clearInterval(interval);
  }, [timer]);

  const update = (key: string, val: string) => setForm(f => ({ ...f, [key]: val }));

  const handleStateChange = (state: string) => {
    setForm(f => ({ ...f, location_state: state, location_district: '' }));
  };

  const districts = form.location_state ? (INDIAN_LOCATIONS[form.location_state] || []) : [];

  // Password rule checks
  const passwordRules = [
    { label: 'Minimum 8 characters', met: form.password.length >= 8 },
    { label: 'At least 1 uppercase letter (A-Z)', met: /[A-Z]/.test(form.password) },
    { label: 'At least 1 lowercase letter (a-z)', met: /[a-z]/.test(form.password) },
    { label: 'At least 1 number (0-9)', met: /[0-9]/.test(form.password) },
    { label: 'At least 1 special character (@, #, $, !)', met: /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>/?`~]/.test(form.password) },
  ];

  const isPasswordStrong = passwordRules.every(r => r.met);
  const isNameValid = NAME_REGEX.test(form.name.trim());
  const isEmailValid = EMAIL_REGEX.test(form.email.trim());

  // Step 1: Send OTP to Email
  const handleSendOTP = async () => {
    setError('');
    setSuccess('');

    // Strict Name Validation
    if (!form.name.trim()) {
      setError('Please enter your full name.');
      return;
    }
    if (form.name.trim().length < 3) {
      setError('Name must be at least 3 characters long.');
      return;
    }
    if (!isNameValid) {
      setError('Name can only contain alphabetic letters and spaces (no numbers or symbols).');
      return;
    }

    // Strict Email Validation
    if (!form.email.trim()) {
      setError('Please enter your email address.');
      return;
    }
    if (!isEmailValid) {
      setError('Please enter a valid email format (e.g. farmer@gmail.com).');
      return;
    }

    // Strict Password Validation
    if (!isPasswordStrong) {
      setError('Please ensure your password meets all 5 security requirements below.');
      return;
    }

    if (form.password !== form.confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    if (!form.location_state || !form.location_district) {
      setError('Please select your state and district.');
      return;
    }

    setOtpLoading(true);
    try {
      const res = await authAPI.sendEmailOTP({ email: form.email.trim().toLowerCase(), purpose: 'Registration' });
      setOtpSent(true);
      setTimer(60); // 60s cooldown for resend
      setSuccess(res.data.message || `Verification code sent to ${form.email}! Please check your inbox or spam.`);
    } catch (err: any) {
      console.error('Send OTP error:', err);
      setError(err.response?.data?.detail || 'Failed to send verification code. Please check your email.');
    } finally {
      setOtpLoading(false);
    }
  };

  // Step 2: Verify OTP and Register
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!otpSent) {
      handleSendOTP();
      return;
    }

    if (!otpCode.trim() || otpCode.trim().length !== 6) {
      setError('Please enter the 6-digit verification code sent to your email.');
      return;
    }

    setLoading(true);
    try {
      await registerWithEmail({
        name: form.name.trim(),
        email: form.email.trim().toLowerCase(),
        password: form.password,
        otp: otpCode.trim(),
        location_state: form.location_state,
        location_district: form.location_district,
        village: form.village.trim(),
        language: form.language,
      });

      setSuccess('Account created successfully! Welcome to Kisaan Mitra 🌾');
      setTimeout(() => navigate('/'), 1200);
    } catch (err: any) {
      console.error('Registration error:', err);
      setError(err.response?.data?.detail || 'Verification failed. Please check the code.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card" style={{ maxWidth: 520, padding: 32 }}>
        <div className="brand" style={{ textAlign: 'center', marginBottom: 24 }}>
          <div className="emoji" style={{ fontSize: '2.5rem' }}>🌾</div>
          <h1 style={{ fontSize: '1.6rem', marginTop: 4 }}>Farmer Registration</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
            Enter your details and verify your email to create a secure account.
          </p>
        </div>

        {error && <div className="alert-box error" style={{ marginBottom: 16 }}>{error}</div>}
        {success && <div className="alert-box success" style={{ marginBottom: 16 }}>{success}</div>}

        <form onSubmit={handleSubmit}>
          {/* Full Name */}
          <div className="form-group" style={{ marginBottom: 16 }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.875rem', fontWeight: 600 }}>
              <User size={15} /> Full Name (Only letters & spaces)
            </label>
            <input
              className="form-input"
              placeholder="e.g. Ramesh Chandra Mahapatra"
              value={form.name}
              onChange={e => update('name', e.target.value)}
              required
              disabled={loading}
              style={{
                borderColor: form.name ? (isNameValid ? '#22c55e' : '#ef4444') : undefined
              }}
            />
            {form.name && !isNameValid && (
              <span style={{ fontSize: '0.75rem', color: '#ef4444', marginTop: 4, display: 'block' }}>
                Letters only, 3 to 50 characters (no digits or symbols).
              </span>
            )}
          </div>

          {/* Email Address */}
          <div className="form-group" style={{ marginBottom: 16 }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.875rem', fontWeight: 600 }}>
              <Mail size={15} /> Email Address (Gmail / Valid Email)
            </label>
            <div style={{ display: 'flex', gap: 8 }}>
              <input
                className="form-input"
                type="email"
                placeholder="e.g. ramesh.farmer@gmail.com"
                value={form.email}
                onChange={e => update('email', e.target.value)}
                required
                disabled={otpSent || loading}
                style={{
                  flex: 1,
                  borderColor: form.email ? (isEmailValid ? '#22c55e' : '#ef4444') : undefined
                }}
              />
              {!otpSent ? (
                <button
                  type="button"
                  onClick={handleSendOTP}
                  disabled={otpLoading || !form.email || !form.name}
                  className="btn btn-secondary"
                  style={{ whiteSpace: 'nowrap', padding: '0 16px', fontWeight: 600 }}
                >
                  {otpLoading ? <RefreshCw className="animate-spin" size={16} /> : 'Send OTP'}
                </button>
              ) : (
                <button
                  type="button"
                  onClick={handleSendOTP}
                  disabled={timer > 0 || otpLoading}
                  className="btn btn-secondary"
                  style={{ whiteSpace: 'nowrap', padding: '0 14px', fontSize: '0.8rem' }}
                >
                  {timer > 0 ? `Resend (${timer}s)` : 'Resend'}
                </button>
              )}
            </div>
          </div>

          {/* OTP Input (Shown once OTP is sent) */}
          {otpSent && (
            <div className="form-group" style={{ marginBottom: 20, background: 'rgba(34, 197, 94, 0.08)', padding: 16, borderRadius: 8, border: '1px solid #22c55e' }}>
              <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#16a34a', fontWeight: 700, fontSize: '0.9rem' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <ShieldCheck size={18} /> Enter 6-Digit Email Code
                </span>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Check Inbox / Spam</span>
              </label>
              <input
                className="form-input"
                type="text"
                maxLength={6}
                placeholder="123456"
                value={otpCode}
                onChange={e => setOtpCode(e.target.value.replace(/\D/g, ''))}
                autoFocus
                style={{
                  fontSize: '1.4rem',
                  letterSpacing: '8px',
                  textAlign: 'center',
                  fontWeight: 700,
                  marginTop: 8,
                  borderColor: '#22c55e'
                }}
                required
              />
            </div>
          )}

          {/* Password & Confirm */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 8 }}>
            <div className="form-group">
              <label style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.875rem', fontWeight: 600 }}>
                <Lock size={15} /> Password
              </label>
              <div style={{ position: 'relative' }}>
                <input
                  className="form-input"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Strong password"
                  value={form.password}
                  onChange={e => update('password', e.target.value)}
                  required
                  disabled={loading}
                  style={{ paddingRight: 36 }}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  tabIndex={-1}
                  style={{
                    position: 'absolute',
                    right: 8,
                    top: '50%',
                    transform: 'translateY(-50%)',
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    color: 'var(--text-secondary)',
                    padding: 4
                  }}
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <div className="form-group">
              <label style={{ fontSize: '0.875rem', fontWeight: 600 }}>Confirm Password</label>
              <div style={{ position: 'relative' }}>
                <input
                  className="form-input"
                  type={showConfirmPassword ? 'text' : 'password'}
                  placeholder="Re-enter password"
                  value={form.confirmPassword}
                  onChange={e => update('confirmPassword', e.target.value)}
                  required
                  disabled={loading}
                  style={{ paddingRight: 36 }}
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  tabIndex={-1}
                  style={{
                    position: 'absolute',
                    right: 8,
                    top: '50%',
                    transform: 'translateY(-50%)',
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    color: 'var(--text-secondary)',
                    padding: 4
                  }}
                >
                  {showConfirmPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>
          </div>

          {/* Password Strength Checklist */}
          {form.password && (
            <div style={{
              background: 'var(--bg-secondary)',
              padding: '10px 14px',
              borderRadius: 6,
              fontSize: '0.75rem',
              marginBottom: 16,
              border: '1px solid var(--border-color)'
            }}>
              <div style={{ fontWeight: 600, marginBottom: 4, color: isPasswordStrong ? '#16a34a' : 'var(--text-color)' }}>
                Password Security Checklist:
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 4 }}>
                {passwordRules.map((rule, idx) => (
                  <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: 4, color: rule.met ? '#16a34a' : '#9ca3af' }}>
                    {rule.met ? <Check size={13} /> : <X size={13} />}
                    <span>{rule.label}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* State & District */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 16 }}>
            <div className="form-group">
              <label style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.875rem', fontWeight: 600 }}>
                <MapPin size={15} /> State
              </label>
              <select
                className="form-input"
                value={form.location_state}
                onChange={e => handleStateChange(e.target.value)}
                required
                disabled={loading}
              >
                <option value="">Select State</option>
                {STATES.map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>

            <div className="form-group">
              <label style={{ fontSize: '0.875rem', fontWeight: 600 }}>District</label>
              <select
                className="form-input"
                value={form.location_district}
                onChange={e => update('location_district', e.target.value)}
                required
                disabled={!form.location_state || loading}
              >
                <option value="">Select District</option>
                {districts.map(d => <option key={d} value={d}>{d}</option>)}
              </select>
            </div>
          </div>

          {/* Village & Language */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 20 }}>
            <div className="form-group">
              <label style={{ fontSize: '0.875rem', fontWeight: 600 }}>Village (Optional)</label>
              <input
                className="form-input"
                placeholder="e.g. Pipili"
                value={form.village}
                onChange={e => update('village', e.target.value)}
                disabled={loading}
              />
            </div>
            <div className="form-group">
              <label style={{ fontSize: '0.875rem', fontWeight: 600 }}>Preferred Language</label>
              <select
                className="form-input"
                value={form.language}
                onChange={e => update('language', e.target.value)}
                disabled={loading}
              >
                <option value="en">English</option>
                <option value="hi">हिंदी (Hindi)</option>
                <option value="or">ଓଡ଼ିଆ (Odia)</option>
                <option value="kn">ಕನ್ನಡ (Kannada)</option>
              </select>
            </div>
          </div>

          {/* Submit Button */}
          {otpSent ? (
            <button
              type="submit"
              disabled={loading || otpCode.length !== 6}
              className="btn btn-primary"
              style={{ width: '100%', padding: '12px 0', fontSize: '1rem', fontWeight: 700, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}
            >
              {loading ? (
                <span>Creating Account...</span>
              ) : (
                <>
                  <CheckCircle2 size={18} /> Verify Code & Complete Registration
                </>
              )}
            </button>
          ) : (
            <button
              type="button"
              onClick={handleSendOTP}
              disabled={otpLoading || !isNameValid || !isEmailValid || !isPasswordStrong}
              className="btn btn-primary"
              style={{ width: '100%', padding: '12px 0', fontSize: '1rem', fontWeight: 700, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}
            >
              {otpLoading ? (
                <span>Sending Code...</span>
              ) : (
                <>
                  Send Email Verification Code <ArrowRight size={18} />
                </>
              )}
            </button>
          )}
        </form>

        <div style={{ textAlign: 'center', marginTop: 24, fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
          Already have an account?{' '}
          <Link to="/login" style={{ color: 'var(--primary-color)', fontWeight: 600, textDecoration: 'none' }}>
            Login here
          </Link>
        </div>
      </div>
    </div>
  );
}
