import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { weatherAPI, type WeatherData, type FarmingTipsData } from '../services/api';
import { Thermometer, Droplets, Wind, Cloud, CheckCircle } from 'lucide-react';
import INDIAN_LOCATIONS from '../data/indianLocations';

export default function WeatherPage() {
  const { user } = useAuth();
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [tips, setTips] = useState<FarmingTipsData | null>(null);
  const [alert, setAlert] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [state, setState] = useState(user?.location_state || 'Maharashtra');
  const [city, setCity] = useState(user?.location_district || 'Pune');

  const handleStateChange = (selectedState: string) => {
    setState(selectedState);
    const districts = INDIAN_LOCATIONS[selectedState] || [];
    setCity(districts[0] || '');
  };

  const fetchWeather = async () => {
    setLoading(true);
    try {
      const crops = user?.crops?.map(c => c.commodity).join(',') || '';
      const res = await weatherAPI.getWeather({ city: city || 'Pune', state: state || 'Maharashtra', crops });
      setWeather(res.data.weather);
      setTips(res.data.farming_tips);
      setAlert(res.data.alert);
    } catch { /* ignore */ }
    setLoading(false);
  };

  useEffect(() => { fetchWeather(); }, [city, state]);

  return (
    <>
      <div className="page-header">
        <h1>🌤️ Weather & Farming Tips</h1>
        <p>Real-time weather with AI-powered farming advice</p>
      </div>
      <div className="page-body">
        <div className="filters-bar" style={{ marginBottom: 24, gap: 16, display: 'flex', flexWrap: 'wrap', alignItems: 'flex-end' }}>
          <div style={{ display: 'flex', flexDirection: 'column', minWidth: 200, flex: 1 }}>
            <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>Select State</label>
            <select 
              className="form-input" 
              value={state} 
              onChange={e => handleStateChange(e.target.value)}
              style={{ width: '100%', height: '42px', cursor: 'pointer', padding: '0 12px', border: '1px solid var(--border-color)', borderRadius: '6px' }}
            >
              {Object.keys(INDIAN_LOCATIONS).map(st => (
                <option key={st} value={st}>{st}</option>
              ))}
            </select>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', minWidth: 200, flex: 1 }}>
            <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>Select District</label>
            <select 
              className="form-input" 
              value={city} 
              onChange={e => setCity(e.target.value)}
              style={{ width: '100%', height: '42px', cursor: 'pointer', padding: '0 12px', border: '1px solid var(--border-color)', borderRadius: '6px' }}
            >
              {(INDIAN_LOCATIONS[state] || []).map(dt => (
                <option key={dt} value={dt}>{dt}</option>
              ))}
            </select>
          </div>
          <button className="btn btn-primary" onClick={fetchWeather} style={{ height: '42px', minWidth: 150 }}>Check Weather</button>
        </div>

        {loading ? (
          <div className="loading-center"><div className="spinner" /><span>Fetching weather...</span></div>
        ) : weather ? (
          <div className="grid-2">
            <div>
              <div className="weather-hero">
                <div className="temp">{Math.round(weather.temp)}°C</div>
                <div className="condition">{weather.description}</div>
                <div style={{ fontSize: '0.85rem', opacity: 0.7, marginTop: 4 }}>
                  {weather.city} • Feels like {Math.round(weather.feels_like)}°C
                </div>
                <div className="details">
                  <div className="detail-item"><Droplets size={16} /> {weather.humidity}%</div>
                  <div className="detail-item"><Wind size={16} /> {weather.wind_speed} m/s</div>
                  <div className="detail-item"><Cloud size={16} /> {weather.cloudiness}%</div>
                  <div className="detail-item"><Thermometer size={16} /> {Math.round(weather.feels_like)}°C</div>
                </div>
              </div>

              {alert && (
                <div className="card" style={{ borderLeft: '4px solid var(--amber-500)', marginTop: 16 }}>
                  <div className="card-body">
                    <h3 style={{ fontSize: '1rem', marginBottom: 8 }}>⚠️ {alert.title}</h3>
                    <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>{alert.body}</p>
                  </div>
                </div>
              )}
            </div>

            {tips && (
              <div className={`card tips-card ${tips.severity}`}>
                <div className="card-header">
                  <h2>🌱 Farming Tips</h2>
                  <span className={`badge ${tips.severity === 'good' ? 'up' : tips.severity === 'caution' ? 'big_jump' : 'critical'}`}>
                    {tips.severity.toUpperCase()}
                  </span>
                </div>
                <div className="card-body">
                  <p style={{ fontSize: '0.9rem', fontWeight: 500, marginBottom: 16, color: 'var(--text-primary)' }}>
                    {tips.summary}
                  </p>
                  {tips.tips.map((tip, i) => (
                    <div className="tip-item" key={i}>
                      <CheckCircle size={16} style={{ color: 'var(--green-500)', marginTop: 2, flexShrink: 0 }} />
                      <span>{tip}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="empty-state">
            <div className="emoji">🌧️</div>
            <h3>Could not load weather</h3>
            <p>Check your OpenWeather API key in the backend</p>
          </div>
        )}
      </div>
    </>
  );
}
