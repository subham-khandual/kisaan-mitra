import { useState, type FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authAPI } from '../services/api';
import { Mail, Lock, ShieldCheck, Check, X, CheckCircle2, ArrowRight } from 'lucide-react';

const EMAIL_REGEX = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

const PASSWORD_RULES = [
  { label: 'Minimum 8 characters', test: (p: string) => p.length >= 8 },
  { label: 'At least 1 uppercase letter (A-Z)', test: (p: string) => /[A-Z]/.test(p) },
  { label: 'At least 1 lowercase letter (a-z)', test: (p: string) => /[a-z]/.test(p) },
  { label: 'At least 1 number (0-9)', test: (p: string) => /[0-9]/.test(p) },
  { label: 'At least 1 special character (@, #, $, !)', test: (p: string) => /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>/?`~]/.test(p) },
];

export default function ForgotPasswordPage() {
  const navigate = useNavigate();
  const [step, setStep] = useState<1 | 2>(1);
  const [email, setEmail] = useState('');
  const [otp, setOtp] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const isPasswordStrong = PASSWORD_RULES.every(r => r.test(newPassword));

  const handleRequestOTP = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    const trimmed = email.trim().toLowerCase();
    if (!trimmed) {
      setError('Please enter your registered email address');
      return;
    }

    if (!EMAIL_REGEX.test(trimmed)) {
      setError('Please enter a valid email address (e.g. farmer@gmail.com)');
      return;
    }

    setLoading(true);
    try {
      const res = await authAPI.emailForgotPassword({ email: trimmed });
      setSuccess(res.data.message || 'Verification code sent to your email! Please check inbox/spam.');
      setStep(2);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to request password reset code. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOTP = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!isPasswordStrong) {
      setError('Password must satisfy all security requirements below.');
      return;
    }

    if (newPassword !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (!otp.trim() || otp.trim().length !== 6) {
      setError('Please enter the 6-digit verification code.');
      return;
    }

    setLoading(true);
    try {
      const trimmed = email.trim().toLowerCase();
      await authAPI.emailVerifyOTP({ email: trimmed, otp: otp.trim(), new_password: newPassword });
      setSuccess('Password reset successfully! Redirecting to login...');
      setTimeout(() => navigate('/login'), 1500);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to verify code or reset password.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card" style={{ maxWidth: 460, padding: 32 }}>
        <div className="brand" style={{ textAlign: 'center', marginBottom: 24 }}>
          <div className="emoji" style={{ fontSize: '2.5rem' }}>🌾</div>
          <h1 style={{ fontSize: '1.6rem', marginTop: 4 }}>Reset Password</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
            {step === 1 ? 'Enter your registered email address to receive an OTP code.' : 'Enter the 6-digit code and choose a new password.'}
          </p>
        </div>

        {error && <div className="alert-box error" style={{ marginBottom: 16 }}>{error}</div>}
        {success && <div className="alert-box success" style={{ marginBottom: 16 }}>{success}</div>}

        {step === 1 ? (
          <form onSubmit={handleRequestOTP}>
            <div className="form-group" style={{ marginBottom: 20 }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.875rem', fontWeight: 600 }}>
                <Mail size={15} /> Registered Email Address
              </label>
              <input
                id="fp-email"
                className="form-input"
                type="email"
                placeholder="name@gmail.com"
                value={email}
                onChange={e => setEmail(e.target.value)}
                required
                autoFocus
              />
            </div>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading || !email.trim()}
              style={{ width: '100%', padding: '12px 0', fontSize: '1rem', fontWeight: 700, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}
            >
              {loading ? 'Sending Code...' : (
                <>
                  Send Reset Code <ArrowRight size={18} />
                </>
              )}
            </button>
          </form>
        ) : (
          <form onSubmit={handleVerifyOTP}>
            <div className="form-group" style={{ marginBottom: 16 }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.875rem', fontWeight: 600 }}>
                <ShieldCheck size={16} /> Enter 6-Digit Email Code
              </label>
              <input
                id="fp-otp"
                className="form-input"
                type="text"
                placeholder="123456"
                value={otp}
                onChange={e => setOtp(e.target.value.replace(/\D/g, ''))}
                maxLength={6}
                required
                autoFocus
                style={{
                  fontSize: '1.3rem',
                  letterSpacing: '6px',
                  textAlign: 'center',
                  fontWeight: 700,
                }}
              />
            </div>

            <div className="form-group" style={{ marginBottom: 16 }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.875rem', fontWeight: 600 }}>
                <Lock size={15} /> New Password
              </label>
              <input
                id="fp-new-password"
                className="form-input"
                type="password"
                placeholder="Enter new password"
                value={newPassword}
                onChange={e => setNewPassword(e.target.value)}
                required
              />
            </div>

            <div className="form-group" style={{ marginBottom: 16 }}>
              <label style={{ fontSize: '0.875rem', fontWeight: 600 }}>Confirm New Password</label>
              <input
                id="fp-confirm-password"
                className="form-input"
                type="password"
                placeholder="Re-enter new password"
                value={confirmPassword}
                onChange={e => setConfirmPassword(e.target.value)}
                required
              />
            </div>

            {/* Checklist */}
            {newPassword && (
              <div style={{
                background: 'var(--bg-secondary)',
                padding: '10px 14px',
                borderRadius: 6,
                fontSize: '0.75rem',
                marginBottom: 16,
                border: '1px solid var(--border-color)'
              }}>
                <div style={{ fontWeight: 600, marginBottom: 4, color: isPasswordStrong ? '#16a34a' : 'var(--text-color)' }}>
                  Password Requirements:
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 4 }}>
                  {PASSWORD_RULES.map((rule, idx) => (
                    <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: 4, color: rule.test(newPassword) ? '#16a34a' : '#9ca3af' }}>
                      {rule.test(newPassword) ? <Check size={13} /> : <X size={13} />}
                      <span>{rule.label}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading || !isPasswordStrong || otp.length !== 6}
              style={{ width: '100%', padding: '12px 0', fontSize: '1rem', fontWeight: 700, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}
            >
              {loading ? 'Resetting Password...' : (
                <>
                  <CheckCircle2 size={18} /> Reset Password & Login
                </>
              )}
            </button>
          </form>
        )}

        <div style={{ textAlign: 'center', marginTop: 24, fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
          Remember your password?{' '}
          <Link to="/login" style={{ color: 'var(--primary-color)', fontWeight: 600, textDecoration: 'none' }}>
            Back to login
          </Link>
        </div>
      </div>
    </div>
  );
}
