import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { pricesAPI, weatherAPI, notificationsAPI, type PriceRecord, type WeatherData, type NotificationRecord } from '../services/api';
import { TrendingUp, CloudSun, Sprout, Bell, BellRing } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function DashboardPage() {
  const { user } = useAuth();
  const [prices, setPrices] = useState<PriceRecord[]>([]);
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [trending, setTrending] = useState<any[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [recentAlerts, setRecentAlerts] = useState<NotificationRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [pRes, wRes, tRes, uRes, aRes] = await Promise.allSettled([
          pricesAPI.getPrices({ limit: 5 }),
          weatherAPI.getWeather({
            city: user?.location_district || 'Bengaluru',
            state: user?.location_state || 'Karnataka',
          }),
          pricesAPI.getTrending(user?.location_state),
          notificationsAPI.getUnreadCount(),
          notificationsAPI.getNotifications(3)
        ]);
        if (pRes.status === 'fulfilled') setPrices(pRes.value.data);
        if (wRes.status === 'fulfilled') setWeather(wRes.value.data.weather);
        if (tRes.status === 'fulfilled') setTrending(tRes.value.data || []);
        if (uRes.status === 'fulfilled') setUnreadCount(uRes.value.data.unread_count);
        if (aRes.status === 'fulfilled') setRecentAlerts(aRes.value.data);
      } catch { /* ignore */ }
      setLoading(false);
    };
    load();
  }, [user]);

  return (
    <>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1>Welcome back, {user?.name?.split(' ')[0] || 'Farmer'} 👋</h1>
          <p>{user?.location_district}, {user?.location_state}</p>
        </div>
        <Link to="/notifications" style={{ position: 'relative', color: 'var(--text-color)', padding: 12, background: 'var(--bg-secondary)', borderRadius: '50%' }}>
          <BellRing size={24} />
          {unreadCount > 0 && (
            <span style={{ position: 'absolute', top: 6, right: 6, background: '#ef4444', color: 'white', fontSize: '0.7rem', fontWeight: 'bold', width: 18, height: 18, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              {unreadCount}
            </span>
          )}
        </Link>
      </div>
      <div className="page-body">
        {/* Stats */}
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon green"><TrendingUp size={24} /></div>
            <div className="stat-info">
              <h3>{prices.length}</h3>
              <p>Tracked Prices</p>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon amber"><Sprout size={24} /></div>
            <div className="stat-info">
              <h3>{user?.crops?.length || 0}</h3>
              <p>Watched Crops</p>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon blue"><CloudSun size={24} /></div>
            <div className="stat-info">
              <h3>{weather ? `${Math.round(weather.temp)}°C` : '—'}</h3>
              <p>{weather?.description || 'Loading weather...'}</p>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon red"><Bell size={24} /></div>
            <div className="stat-info">
              <h3>{trending.length}</h3>
              <p>Trending Moves</p>
            </div>
          </div>
        </div>

        <div className="grid-2">
          {/* Recent Prices */}
          <div className="card">
            <div className="card-header">
              <h2>📊 Recent Prices</h2>
              <Link to="/prices" className="btn btn-secondary" style={{ fontSize: '0.8rem', padding: '6px 12px' }}>View All</Link>
            </div>
            <div className="card-body">
              {loading ? (
                <div className="loading-center"><div className="spinner" /><span>Loading...</span></div>
              ) : prices.length === 0 ? (
                <div className="empty-state">
                  <div className="emoji">📦</div>
                  <h3>No prices yet</h3>
                  <p>Add crops to your watchlist to see prices here</p>
                </div>
              ) : (
                <div className="table-wrapper">
                  <table>
                    <thead><tr><th>Crop</th><th>Market</th><th>Price (₹)</th><th>Trend</th></tr></thead>
                    <tbody>
                      {prices.map((p, i) => (
                        <tr key={i}>
                          <td style={{ fontWeight: 600 }}>{p.commodity}</td>
                          <td>{p.market}</td>
                          <td>₹{p.modal_price.toLocaleString()}</td>
                          <td>
                            {p.trend && (
                              <span className={`badge ${p.trend}`}>
                                {p.trend === 'up' ? '↑' : p.trend === 'down' ? '↓' : '→'}
                                {p.change_pct != null ? ` ${Math.abs(p.change_pct)}%` : ''}
                              </span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>

          {/* Weather + Trending */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            {weather && (
              <div className="weather-hero">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <div className="temp">{Math.round(weather.temp)}°C</div>
                    <div className="condition">{weather.description}</div>
                    <div style={{ fontSize: '0.85rem', opacity: 0.7, marginTop: 4 }}>{weather.city}</div>
                  </div>
                  <CloudSun size={48} style={{ opacity: 0.5 }} />
                </div>
                <div className="details">
                  <div className="detail-item">💧 Humidity: {weather.humidity}%</div>
                  <div className="detail-item">🌬️ Wind: {weather.wind_speed} m/s</div>
                  <div className="detail-item">☁️ Clouds: {weather.cloudiness}%</div>
                </div>
              </div>
            )}

            {trending.length > 0 && (
              <div className="card">
                <div className="card-header"><h2>🔥 Top Movers</h2></div>
                <div className="card-body" style={{ padding: 0 }}>
                  <div className="table-wrapper">
                    <table>
                      <thead><tr><th>Crop</th><th>Price</th><th>Change</th></tr></thead>
                      <tbody>
                        {trending.slice(0, 5).map((t, i) => (
                          <tr key={i}>
                            <td style={{ fontWeight: 600 }}>{t.commodity}</td>
                            <td>₹{t.modal_price?.toLocaleString()}</td>
                            <td>
                              <span className={`badge ${t.change_pct > 0 ? 'up' : 'down'}`}>
                                {t.change_pct > 0 ? '↑' : '↓'} {Math.abs(t.change_pct)}%
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}

            {recentAlerts.length > 0 && (
              <div className="card">
                <div className="card-header">
                  <h2>🔔 Recent Alerts</h2>
                  <Link to="/notifications" className="btn btn-secondary" style={{ fontSize: '0.8rem', padding: '6px 12px' }}>View All</Link>
                </div>
                <div className="card-body" style={{ padding: '8px 16px' }}>
                  {recentAlerts.map((a, i) => (
                    <div key={i} style={{ padding: '8px 0', borderBottom: i < recentAlerts.length - 1 ? '1px solid var(--border-color)' : 'none' }}>
                      <div style={{ fontWeight: 600, fontSize: '0.875rem' }}>{a.commodity} — {a.market}</div>
                      <div style={{ fontSize: '0.775rem', color: 'var(--text-secondary)' }}>{a.message_en}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
