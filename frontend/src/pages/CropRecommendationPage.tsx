import { useState, type FormEvent } from 'react';
import { cropAPI, reportsAPI, type MLCropRecommendationResult } from '../services/api';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
import { Thermometer, Droplets, CloudRain, Activity, Award, Download } from 'lucide-react';

export default function CropRecommendationPage() {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // ── Machine Learning Form State ──
  const [mlForm, setMlForm] = useState({
    N: '80',
    P: '45',
    K: '40',
    ph: '6.5',
    temperature: '27',
    humidity: '72',
    rainfall: '120',
  });
  const [mlResult, setMlResult] = useState<MLCropRecommendationResult | null>(null);

  const updateMl = (k: string, v: string) => setMlForm(f => ({ ...f, [k]: v }));

  const handleMlSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    setMlResult(null);
    try {
      const data = {
        N: parseFloat(mlForm.N),
        P: parseFloat(mlForm.P),
        K: parseFloat(mlForm.K),
        ph: parseFloat(mlForm.ph),
        temperature: parseFloat(mlForm.temperature),
        humidity: parseFloat(mlForm.humidity),
        rainfall: parseFloat(mlForm.rainfall),
      };
      const res = await cropAPI.getMLRecommendations(data);
      setMlResult(res.data);

      // Save to history if logged in
      if (user) {
        const token = localStorage.getItem('token');
        if (token) {
          await axios.post(`${API_BASE}/history`, {
            activity_type: 'crop_recommendation',
            title: 'Crop Recommendation',
            description: `Predicted crop suitability with NPK: ${data.N}/${data.P}/${data.K}`,
            data: {
              recommended_crop: res.data.recommended_crop,
              confidence: res.data.confidence,
              npk: `${data.N}/${data.P}/${data.K}`
            }
          }, {
            headers: { Authorization: `Bearer ${token}` }
          }).catch(console.error);
        }
      }

    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to analyze soil chemistry. Verify that parameters are numeric.');
    } finally {
      setLoading(false);
    }
  };

  const downloadReport = async () => {
    if (!mlResult) return;
    try {
      const res = await reportsAPI.generateReport({
        report_type: 'soil',
        data: {
          ...mlResult.soil_health,
          N: mlForm.N,
          P: mlForm.P,
          K: mlForm.K,
          ph: mlForm.ph
        }
      });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'soil_health.pdf');
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
        <h1>🌱 Precision AI Crop Advisor</h1>
        <p>Harness scientific Machine Learning to determine optimal crop sowing patterns</p>
      </div>

      <div className="page-body">
        <div className="grid-2">
          {/* Left Panel: Form */}
          <div className="card">
            <div className="card-header">
              <h2>🔬 Soil Chemistry &amp; Climate Parameters</h2>
            </div>

            <div className="card-body">
              {error && <div className="alert-box error" style={{ marginBottom: 16 }}>{error}</div>}

              <form onSubmit={handleMlSubmit}>
                {/* Soil macronutrients */}
                <h3 style={{ fontSize: '0.9rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 1, margin: '8px 0 16px 0' }}>
                  🧬 Soil Chemistry Indices (NPK)
                </h3>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12, marginBottom: 16 }}>
                  <div className="form-group">
                    <label>Nitrogen (N) *</label>
                    <input type="number" className="form-input" placeholder="0-140 mg/kg" value={mlForm.N} onChange={e => updateMl('N', e.target.value)} required min="0" />
                  </div>
                  <div className="form-group">
                    <label>Phosphorus (P) *</label>
                    <input type="number" className="form-input" placeholder="0-140 mg/kg" value={mlForm.P} onChange={e => updateMl('P', e.target.value)} required min="0" />
                  </div>
                  <div className="form-group">
                    <label>Potassium (K) *</label>
                    <input type="number" className="form-input" placeholder="0-205 mg/kg" value={mlForm.K} onChange={e => updateMl('K', e.target.value)} required min="0" />
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 12, marginBottom: 16 }}>
                  <div className="form-group">
                    <label>Soil pH Level (0-14) *</label>
                    <input type="number" step="0.1" className="form-input" placeholder="e.g. 6.5" value={mlForm.ph} onChange={e => updateMl('ph', e.target.value)} required min="0" max="14" />
                  </div>
                </div>

                {/* Microclimate values */}
                <h3 style={{ fontSize: '0.9rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 1, margin: '24px 0 16px 0' }}>
                  ☀️ Climate Micro-parameters
                </h3>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12, marginBottom: 20 }}>
                  <div className="form-group">
                    <label style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                      <Thermometer size={14} /> Temp (°C)
                    </label>
                    <input type="number" step="0.1" className="form-input" value={mlForm.temperature} onChange={e => updateMl('temperature', e.target.value)} required />
                  </div>
                  <div className="form-group">
                    <label style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                      <Droplets size={14} /> Humidity (%)
                    </label>
                    <input type="number" step="0.1" className="form-input" value={mlForm.humidity} onChange={e => updateMl('humidity', e.target.value)} required />
                  </div>
                  <div className="form-group">
                    <label style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                      <CloudRain size={14} /> Rainfall (mm)
                    </label>
                    <input type="number" step="0.1" className="form-input" value={mlForm.rainfall} onChange={e => updateMl('rainfall', e.target.value)} required />
                  </div>
                </div>

                <button type="submit" className="btn btn-primary btn-full btn-lg" disabled={loading}>
                  <Activity size={18} />
                  {loading ? 'Analyzing Soil Metrics...' : 'Execute Scientific ML Advisory'}
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
                    <h3 style={{ fontSize: '1.1rem', marginBottom: 4 }}>AI is Sifting Models...</h3>
                    <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Executing multi-layered algorithms and fertilizer matrices</p>
                  </div>
                </div>
              </div>
            )}

            {/* Render ML Results */}
            {mlResult && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                {/* Champion Recommended Crop */}
                <div className="card" style={{ borderLeft: '5px solid var(--primary)', background: 'linear-gradient(135deg, var(--bg-card), var(--bg-secondary))' }}>
                  <div className="card-body" style={{ padding: 20 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                      <span className="badge up" style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                        <Award size={14} /> Champion Recommendation
                      </span>
                      <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Confidence: <strong>{mlResult.confidence}%</strong></span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                      <span style={{ fontSize: '3rem' }}>🌾</span>
                      <div>
                        <h2 style={{ fontSize: '1.8rem', margin: 0, fontWeight: 800, textTransform: 'capitalize', color: 'var(--primary)' }}>
                          {mlResult.recommended_crop}
                        </h2>
                        <p style={{ margin: '4px 0 0 0', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                          Perfect compatibility matched by the tuned Random Forest ensemble.
                        </p>
                      </div>
                    </div>
                    <button onClick={downloadReport} className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: '0.8rem', marginTop: 12 }}>
                      <Download size={14} /> Download PDF
                    </button>
                  </div>
                </div>

                {/* Grid details: Soil health & Yield */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                  <div className="card">
                    <div className="card-body" style={{ padding: 16 }}>
                      <h3 style={{ fontSize: '0.9rem', color: 'var(--text-muted)', margin: '0 0 12px 0', textTransform: 'uppercase', letterSpacing: 0.5 }}>
                        🧪 Soil Health Index
                      </h3>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
                        <span style={{ fontSize: '1.8rem', fontWeight: 800, color: mlResult.soil_health.score >= 80 ? 'var(--primary)' : '#eab308' }}>
                          {mlResult.soil_health.score}/100
                        </span>
                        <span className={`badge ${mlResult.soil_health.score >= 80 ? 'up' : 'down'}`}>
                          {mlResult.soil_health.rating}
                        </span>
                      </div>
                      <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0 }}>
                        {mlResult.soil_health.details}
                      </p>
                    </div>
                  </div>

                  <div className="card">
                    <div className="card-body" style={{ padding: 16 }}>
                      <h3 style={{ fontSize: '0.9rem', color: 'var(--text-muted)', margin: '0 0 12px 0', textTransform: 'uppercase', letterSpacing: 0.5 }}>
                        📈 Metric Yield Forecast
                      </h3>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
                        <span style={{ fontSize: '1.5rem', fontWeight: 800 }}>
                          {mlResult.yield_forecasting.expected_yield_tonnes_hectare} t/ha
                        </span>
                        <span className="badge up">
                          {mlResult.yield_forecasting.yield_rating}
                        </span>
                      </div>
                      <ul style={{ margin: 0, paddingLeft: 16, fontSize: '0.775rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                        {mlResult.yield_forecasting.yield_factors.map((f, idx) => (
                          <li key={idx} style={{ marginBottom: 2 }}>{f}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>

                {/* Fertilizer Matrix Prescription */}
                <div className="card">
                  <div className="card-header" style={{ padding: '12px 16px', background: 'var(--bg-secondary)' }}>
                    <h3 style={{ fontSize: '0.9rem', margin: 0, textTransform: 'uppercase', letterSpacing: 0.5 }}>
                      🩹 Soil Deficit &amp; Fertilizer Prescription
                    </h3>
                  </div>
                  <div className="card-body" style={{ padding: 16 }}>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12, marginBottom: 16, textAlign: 'center' }}>
                      <div style={{ background: 'var(--bg-secondary)', padding: '8px 4px', borderRadius: 8 }}>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>N-Deficit</span>
                        <p style={{ margin: '4px 0 0 0', fontWeight: 700, color: mlResult.fertilizer_prescription.N_deficit > 0 ? '#ef4444' : 'var(--primary)' }}>
                          {mlResult.fertilizer_prescription.N_deficit} mg/kg
                        </p>
                      </div>
                      <div style={{ background: 'var(--bg-secondary)', padding: '8px 4px', borderRadius: 8 }}>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>P-Deficit</span>
                        <p style={{ margin: '4px 0 0 0', fontWeight: 700, color: mlResult.fertilizer_prescription.P_deficit > 0 ? '#ef4444' : 'var(--primary)' }}>
                          {mlResult.fertilizer_prescription.P_deficit} mg/kg
                        </p>
                      </div>
                      <div style={{ background: 'var(--bg-secondary)', padding: '8px 4px', borderRadius: 8 }}>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>K-Deficit</span>
                        <p style={{ margin: '4px 0 0 0', fontWeight: 700, color: mlResult.fertilizer_prescription.K_deficit > 0 ? '#ef4444' : 'var(--primary)' }}>
                          {mlResult.fertilizer_prescription.K_deficit} mg/kg
                        </p>
                      </div>
                    </div>

                    <h4 style={{ fontSize: '0.8rem', margin: '0 0 8px 0', color: 'var(--text-muted)' }}>Recommended Chemical Application:</h4>
                    {mlResult.fertilizer_prescription.chemical_remediation.length > 0 ? (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: 16 }}>
                        {mlResult.fertilizer_prescription.chemical_remediation.map((chem, idx) => (
                          <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 12px', background: 'var(--bg-secondary)', borderRadius: 8 }}>
                            <div>
                              <strong style={{ fontSize: '0.85rem', color: 'var(--text-color)' }}>{chem.fertilizer}</strong>
                              <p style={{ margin: 0, fontSize: '0.725rem', color: 'var(--text-muted)' }}>Stage: {chem.application_stage}</p>
                            </div>
                            <span style={{ fontWeight: 700, fontSize: '0.875rem', color: 'var(--primary)' }}>
                              {chem.amount_kg_hectare} kg/ha
                            </span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p style={{ fontSize: '0.8rem', color: 'var(--primary)', fontWeight: 600, margin: '0 0 16px 0' }}>
                        🎉 Excellent soil nutrient content! No chemical fertilizer is required.
                      </p>
                    )}

                    <h4 style={{ fontSize: '0.8rem', margin: '0 0 8px 0', color: 'var(--text-muted)' }}>Organic Remediation &amp; Care Actions:</h4>
                    <ul style={{ margin: 0, paddingLeft: 16, fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                      {mlResult.fertilizer_prescription.organic_remediation.map((org, idx) => (
                        <li key={idx} style={{ marginBottom: 4 }}>{org}</li>
                      ))}
                      {mlResult.soil_health.remediation.map((rem, idx) => (
                        <li key={idx} style={{ marginBottom: 4 }}>{rem}</li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* Alternative Crops */}
                {mlResult.alternatives?.length > 1 && (
                  <div className="card">
                    <div className="card-header" style={{ padding: '12px 16px', background: 'var(--bg-secondary)' }}>
                      <h3 style={{ fontSize: '0.85rem', margin: 0, textTransform: 'uppercase', letterSpacing: 0.5 }}>
                        🌽 High-Probability Alternative Crops
                      </h3>
                    </div>
                    <div className="card-body" style={{ padding: 12, display: 'flex', gap: 12, flexWrap: 'wrap' }}>
                      {mlResult.alternatives.slice(1, 4).map((alt, idx) => (
                        <div key={idx} style={{ flex: 1, minWidth: 100, background: 'var(--bg-secondary)', padding: '10px 14px', borderRadius: 8, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span style={{ fontSize: '0.85rem', fontWeight: 700, textTransform: 'capitalize' }}>
                            {alt.crop}
                          </span>
                          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)' }}>
                            {alt.confidence}%
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Empty State */}
            {!loading && !mlResult && (
              <div className="card">
                <div className="card-body">
                  <div className="empty-state" style={{ padding: '40px 20px', textAlign: 'center' }}>
                    <div className="emoji" style={{ fontSize: '3rem', marginBottom: 12 }}>🤖</div>
                    <h3 style={{ fontSize: '1.2rem', marginBottom: 6 }}>Ready for Agricultural Diagnosis</h3>
                    <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', maxWidth: 360, margin: '0 auto', lineHeight: 1.5 }}>
                      Provide NPK, pH levels, and weather parameters to execute scientific crop yield and soil calculations.
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
