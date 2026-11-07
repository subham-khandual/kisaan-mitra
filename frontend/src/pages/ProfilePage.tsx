import { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { MapPin, Phone, Globe, Calendar, Sprout, Activity } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export default function ProfilePage() {
  const { user } = useAuth();

  if (!user) return null;

  const initial = user.name?.charAt(0)?.toUpperCase() || '?';
  const joinDate = (() => {
    try { return new Date(user.created_at).toLocaleDateString('en-IN', { dateStyle: 'long' }); }
    catch { return user.created_at; }
  })();

  const [history, setHistory] = useState<any[]>([]);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const token = localStorage.getItem('token');
        if (token) {
          const { data } = await axios.get(`${API_BASE}/history`, {
            headers: { Authorization: `Bearer ${token}` }
          });
          setHistory(data);
        }
      } catch (err) {
        console.error("Failed to fetch history:", err);
      }
    };
    fetchHistory();
  }, []);

  return (
    <>
      <div className="page-header">
        <h1>👤 My Profile</h1>
        <p>Your account details and preferences</p>
      </div>
      <div className="page-body">
        <div className="card" style={{ marginBottom: 24 }}>
          <div className="card-body">
            <div className="profile-info">
              <div className="profile-avatar">{initial}</div>
              <div>
                <h2>{user.name}</h2>
                <p>Registered farmer • {user.location_state}</p>
              </div>
            </div>

            <div className="info-grid">
              <div className="info-item">
                <label><Phone size={12} style={{ marginRight: 4 }} />Phone</label>
                <p>{user.phone}</p>
              </div>
              <div className="info-item">
                <label><MapPin size={12} style={{ marginRight: 4 }} />Location</label>
                <p>{user.location_district}, {user.location_state}</p>
              </div>
              <div className="info-item">
                <label><Globe size={12} style={{ marginRight: 4 }} />Language</label>
                <p>{user.language === 'en' ? 'English' : user.language === 'hi' ? 'Hindi' : 'Kannada'}</p>
              </div>
              <div className="info-item">
                <label><Calendar size={12} style={{ marginRight: 4 }} />Joined</label>
                <p>{joinDate}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h2><Sprout size={18} style={{ marginRight: 8 }} />Watched Crops</h2>
            <span className="badge up">{user.crops?.length || 0} crops</span>
          </div>
          <div className="card-body">
            {(!user.crops || user.crops.length === 0) ? (
              <div className="empty-state">
                <div className="emoji">🌾</div>
                <h3>No crops added yet</h3>
                <p>Add crops to receive price alerts and recommendations</p>
              </div>
            ) : (
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr><th>Commodity</th><th>State</th><th>District</th><th>Market</th><th>Alerts</th></tr>
                  </thead>
                  <tbody>
                    {user.crops.map((crop, i) => (
                      <tr key={i}>
                        <td style={{ fontWeight: 600 }}>🌾 {crop.commodity}</td>
                        <td>{crop.state}</td>
                        <td>{crop.district}</td>
                        <td>{crop.market}</td>
                        <td>
                          <span className={`badge ${crop.alert_enabled ? 'up' : 'stable'}`}>
                            {crop.alert_enabled ? '✅ On' : '❌ Off'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
        <div className="card">
          <div className="card-header">
            <h2><Activity size={18} style={{ marginRight: 8 }} />Activity Timeline</h2>
          </div>
          <div className="card-body">
            {history.length === 0 ? (
              <div className="empty-state">
                <div className="emoji">🕰️</div>
                <h3>No activity yet</h3>
                <p>Your predictions and searches will appear here.</p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {history.map((record, i) => (
                  <div key={i} style={{ padding: '16px', borderRadius: '12px', background: 'var(--bg-secondary)', borderLeft: '4px solid var(--primary)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                      <strong style={{ fontSize: '1.1rem' }}>{record.title}</strong>
                      <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                        {new Date(record.created_at).toLocaleDateString('en-IN')}
                      </span>
                    </div>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>{record.description}</p>
                    
                    {/* Activity Specific Details */}
                    {record.activity_type === 'fertilizer_recommendation' && record.data.fertilizer && (
                      <div style={{ marginTop: '8px', padding: '8px', background: 'rgba(76, 175, 80, 0.1)', borderRadius: '8px', color: '#4CAF50', fontWeight: 'bold' }}>
                        🌾 Recommended: {record.data.fertilizer}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
