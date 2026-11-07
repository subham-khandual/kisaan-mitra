import { useState, useEffect, type FormEvent } from 'react';
import { yieldAPI, reportsAPI, type CropYieldPredictionResult, type CropYieldMetadata } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { Activity, BarChart, Calendar, Cloud, Droplets, MapPin, Sprout, Sun, Download } from 'lucide-react';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export default function CropYieldPage() {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [metadata, setMetadata] = useState<CropYieldMetadata['data'] | null>(null);
  
  const [form, setForm] = useState({
    region: '',
    soil_type: '',
    crop: '',
    rainfall_mm: '500',
    temperature_celsius: '25',
    fertilizer_used: false,
    irrigation_used: false,
    weather_condition: '',
    days_to_harvest: '120'
  });

  const [result, setResult] = useState<CropYieldPredictionResult['data'] | null>(null);

  useEffect(() => {
    const fetchMetadata = async () => {
      try {
        const res = await yieldAPI.getMetadata();
        if (res.data.success) {
          setMetadata(res.data.data);
          // Set defaults
          setForm(f => ({
            ...f,
            region: res.data.data.Region[0] || '',
            soil_type: res.data.data.Soil_Type[0] || '',
            crop: res.data.data.Crop[0] || '',
            weather_condition: res.data.data.Weather_Condition[0] || ''
          }));
        }
      } catch (err) {
        console.error("Failed to load metadata", err);
      }
    };
    fetchMetadata();
  }, []);

  const updateForm = (k: string, v: any) => setForm(f => ({ ...f, [k]: v }));

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    setResult(null);
    try {
      const data = {
        ...form,
        rainfall_mm: parseFloat(form.rainfall_mm),
        temperature_celsius: parseFloat(form.temperature_celsius),
        days_to_harvest: parseInt(form.days_to_harvest, 10)
      };
      const res = await yieldAPI.predictYield(data);
      if (res.data.success && res.data.data) {
        setResult(res.data.data);

        if (user) {
          const token = localStorage.getItem('token');
          if (token) {
            await axios.post(`${API_BASE}/history`, {
              activity_type: 'crop_yield_prediction',
              title: 'Yield Forecast',
              description: `Predicted yield for ${form.crop} in ${form.region}`,
              data: {
                estimated_yield: res.data.data.estimated_yield_tons_per_hectare,
                crop: form.crop
              }
            }, {
              headers: { Authorization: `Bearer ${token}` }
            }).catch(console.error);
          }
        }
      } else {
        setError(res.data.error || 'Failed to predict yield.');
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Error connecting to prediction server.');
    } finally {
      setLoading(false);
    }
  };

  const downloadReport = async () => {
    if (!result) return;
    try {
      const res = await reportsAPI.generateReport({
        report_type: 'yield',
        data: {
          ...result,
          crop: form.crop,
          region: form.region
        }
      });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'yield_forecast.pdf');
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error("Failed to download PDF", error);
    }
  };

  return (
    <>
      <div className="page-header">
        <h1>📊 AI Crop Yield Forecaster</h1>
        <p>Advanced predictive modeling to estimate crop yield in tonnes per hectare</p>
      </div>

      <div className="page-body">
        <div className="grid-2">
          {/* Left Panel: Form */}
          <div className="card">
            <div className="card-header">
              <h2>🚜 Agronomy & Climate Inputs</h2>
            </div>

            <div className="card-body">
              {error && <div className="alert-box error" style={{ marginBottom: 16 }}>{error}</div>}

              <form onSubmit={handleSubmit}>
                <h3 style={{ fontSize: '0.9rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 1, margin: '8px 0 16px 0' }}>
                  🌍 Location & Soil
                </h3>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 16 }}>
                  <div className="form-group">
                    <label style={{ display: 'flex', alignItems: 'center', gap: 4 }}><MapPin size={14} /> Region</label>
                    <select className="form-input" value={form.region} onChange={e => updateForm('region', e.target.value)} required>
                      {metadata?.Region.map(r => <option key={r} value={r}>{r}</option>)}
                    </select>
                  </div>
                  <div className="form-group">
                    <label style={{ display: 'flex', alignItems: 'center', gap: 4 }}><Sprout size={14} /> Soil Type</label>
                    <select className="form-input" value={form.soil_type} onChange={e => updateForm('soil_type', e.target.value)} required>
                      {metadata?.Soil_Type.map(r => <option key={r} value={r}>{r}</option>)}
                    </select>
                  </div>
                </div>

                <div className="form-group" style={{ marginBottom: 16 }}>
                  <label style={{ display: 'flex', alignItems: 'center', gap: 4 }}>🌾 Crop Cultivar</label>
                  <select className="form-input" value={form.crop} onChange={e => updateForm('crop', e.target.value)} required>
                    {metadata?.Crop.map(r => <option key={r} value={r}>{r}</option>)}
                  </select>
                </div>

                <h3 style={{ fontSize: '0.9rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 1, margin: '24px 0 16px 0' }}>
                  🌤️ Climate & Practices
                </h3>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 16 }}>
                  <div className="form-group">
                    <label style={{ display: 'flex', alignItems: 'center', gap: 4 }}><Droplets size={14} /> Rainfall (mm)</label>
                    <input type="number" step="0.1" className="form-input" value={form.rainfall_mm} onChange={e => updateForm('rainfall_mm', e.target.value)} required />
                  </div>
                  <div className="form-group">
                    <label style={{ display: 'flex', alignItems: 'center', gap: 4 }}><Sun size={14} /> Temp (°C)</label>
                    <input type="number" step="0.1" className="form-input" value={form.temperature_celsius} onChange={e => updateForm('temperature_celsius', e.target.value)} required />
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 16 }}>
                  <div className="form-group">
                    <label style={{ display: 'flex', alignItems: 'center', gap: 4 }}><Cloud size={14} /> Weather</label>
                    <select className="form-input" value={form.weather_condition} onChange={e => updateForm('weather_condition', e.target.value)} required>
                      {metadata?.Weather_Condition.map(r => <option key={r} value={r}>{r}</option>)}
                    </select>
                  </div>
                  <div className="form-group">
                    <label style={{ display: 'flex', alignItems: 'center', gap: 4 }}><Calendar size={14} /> Harvest Days</label>
                    <input type="number" className="form-input" value={form.days_to_harvest} onChange={e => updateForm('days_to_harvest', e.target.value)} required />
                  </div>
                </div>

                <div style={{ display: 'flex', gap: 20, marginBottom: 24 }}>
                  <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
                    <input type="checkbox" checked={form.fertilizer_used} onChange={e => updateForm('fertilizer_used', e.target.checked)} style={{ width: 18, height: 18 }} />
                    Fertilizer Applied
                  </label>
                  <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
                    <input type="checkbox" checked={form.irrigation_used} onChange={e => updateForm('irrigation_used', e.target.checked)} style={{ width: 18, height: 18 }} />
                    Irrigation Used
                  </label>
                </div>

                <button type="submit" className="btn btn-primary btn-full btn-lg" disabled={loading || !metadata}>
                  <Activity size={18} />
                  {loading ? 'Running Random Forest Model...' : 'Calculate Predicted Yield'}
                </button>
              </form>
            </div>
          </div>

          {/* Right Panel: Results */}
          <div>
            {loading && (
              <div className="card">
                <div className="card-body">
                  <div className="loading-center" style={{ padding: '40px 0', textAlign: 'center' }}>
                    <div className="spinner" style={{ margin: '0 auto 16px auto', border: '3px solid rgba(0,0,0,0.1)', borderTop: '3px solid var(--primary)', borderRadius: '50%', width: 40, height: 40, animation: 'spin 1s linear infinite' }} />
                    <h3 style={{ fontSize: '1.1rem', marginBottom: 4 }}>Forecasting Yield...</h3>
                    <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Analyzing multidimensional crop and climate data</p>
                  </div>
                </div>
              </div>
            )}

            {result && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                <div className="card" style={{ borderLeft: '5px solid var(--primary)', background: 'linear-gradient(135deg, var(--bg-card), var(--bg-secondary))' }}>
                  <div className="card-body" style={{ padding: 24 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                      <span className="badge up" style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                        <BarChart size={14} /> Yield Estimation
                      </span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
                      <span style={{ fontSize: '3.5rem' }}>🌾</span>
                      <div>
                        <h2 style={{ fontSize: '2.5rem', margin: 0, fontWeight: 800, color: 'var(--primary)', lineHeight: 1.2 }}>
                          {result.estimated_yield_tons_per_hectare.toFixed(2)} <span style={{ fontSize: '1.2rem', color: 'var(--text-muted)', fontWeight: 600 }}>t/ha</span>
                        </h2>
                        <p style={{ margin: '8px 0 0 0', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                          Estimated yield for {form.crop} based on current agronomic variables.
                        </p>
                      </div>
                    </div>
                    <button onClick={downloadReport} className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: '0.8rem', marginTop: 12 }}>
                      <Download size={14} /> Download PDF
                    </button>
                  </div>
                </div>

                <div className="card">
                  <div className="card-header" style={{ padding: '12px 16px', background: 'var(--bg-secondary)' }}>
                    <h3 style={{ fontSize: '0.9rem', margin: 0, textTransform: 'uppercase', letterSpacing: 0.5 }}>
                      💡 Optimization Tips
                    </h3>
                  </div>
                  <div className="card-body" style={{ padding: 16 }}>
                    <ul style={{ margin: 0, paddingLeft: 16, fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                      {!form.fertilizer_used && <li>Applying suitable fertilizer based on a soil test could significantly increase this yield.</li>}
                      {!form.irrigation_used && <li>Ensuring optimal irrigation scheduling could prevent water stress and improve yields.</li>}
                      {Number(form.days_to_harvest) < 90 && <li>Short duration crops require highly synchronized nutrient and water delivery.</li>}
                      <li>Monitor {form.weather_condition.toLowerCase()} conditions to prevent pest outbreaks.</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {!loading && !result && (
              <div className="card">
                <div className="card-body">
                  <div className="empty-state" style={{ padding: '40px 20px', textAlign: 'center' }}>
                    <div className="emoji" style={{ fontSize: '3rem', marginBottom: 12 }}>📈</div>
                    <h3 style={{ fontSize: '1.2rem', marginBottom: 6 }}>Ready for Yield Forecast</h3>
                    <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', maxWidth: 360, margin: '0 auto', lineHeight: 1.5 }}>
                      Provide crop details and climate expectations to simulate potential harvest outcomes using ML.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
