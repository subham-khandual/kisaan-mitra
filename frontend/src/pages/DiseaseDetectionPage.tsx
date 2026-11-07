import { useState, useRef } from 'react';
import { diseaseAPI, reportsAPI } from '../services/api';
import { Activity, Camera, UploadCloud, AlertTriangle, CheckCircle, Download } from 'lucide-react';

export default function DiseaseDetectionPage() {
  const [image, setImage] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<any>(null);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setImage(file);
      setPreview(URL.createObjectURL(file));
      setResult(null);
      setError('');
    }
  };

  const handleUpload = async () => {
    if (!image) return;
    
    setLoading(true);
    setError('');
    setResult(null);
    
    const formData = new FormData();
    formData.append('file', image);
    
    try {
      const res = await diseaseAPI.detectDisease(formData);
      if (res.data.success) {
        setResult(res.data.data);
      } else {
        setError("Failed to analyze image.");
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "Network error while reaching AI servers.");
    } finally {
      setLoading(false);
    }
  };

  const downloadReport = async () => {
    if (!result) return;
    try {
      const res = await reportsAPI.generateReport({
        report_type: 'disease',
        data: result
      });
      
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'disease_diagnosis.pdf');
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
        <h1>🔍 AI Plant Disease Detection</h1>
        <p>Upload a clear photo of an infected leaf to get an instant CNN diagnosis</p>
      </div>

      <div className="page-body">
        <div className="grid-2">
          {/* Left Panel: Image Upload */}
          <div className="card">
            <div className="card-header">
              <h2>📸 Image Scanner</h2>
            </div>
            <div className="card-body">
              {error && <div className="alert-box error" style={{ marginBottom: 16 }}>{error}</div>}
              
              <div 
                style={{
                  border: '2px dashed var(--border-color)',
                  borderRadius: 12,
                  padding: 40,
                  textAlign: 'center',
                  background: 'var(--bg-secondary)',
                  cursor: 'pointer',
                  position: 'relative',
                  overflow: 'hidden',
                  marginBottom: 20
                }}
                onClick={() => fileInputRef.current?.click()}
              >
                <input 
                  type="file" 
                  accept="image/*" 
                  ref={fileInputRef} 
                  onChange={handleImageChange} 
                  style={{ display: 'none' }} 
                />
                
                {preview ? (
                  <img src={preview} alt="Leaf preview" style={{ width: '100%', maxHeight: 300, objectFit: 'contain', borderRadius: 8 }} />
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12, opacity: 0.7 }}>
                    <Camera size={48} />
                    <h3 style={{ margin: 0 }}>Click to Upload Leaf Photo</h3>
                    <p style={{ margin: 0, fontSize: '0.85rem' }}>Supports JPG, PNG (Max 5MB)</p>
                  </div>
                )}
              </div>
              
              <button 
                className="btn btn-primary btn-full btn-lg" 
                onClick={handleUpload} 
                disabled={!image || loading}
              >
                {loading ? <Activity className="spin" size={18} /> : <UploadCloud size={18} />}
                {loading ? 'Running ResNet50 Inference...' : 'Analyze Image'}
              </button>
            </div>
          </div>

          {/* Right Panel: Results */}
          <div>
            {loading && (
              <div className="card">
                <div className="card-body" style={{ padding: '60px 20px', textAlign: 'center' }}>
                  <div className="spinner" style={{ margin: '0 auto 16px auto', width: 40, height: 40, border: '3px solid rgba(0,0,0,0.1)', borderTop: '3px solid var(--primary)', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
                  <h3 style={{ marginBottom: 8 }}>Extracting Image Features...</h3>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Matching with PlantVillage Neural Network layers</p>
                </div>
              </div>
            )}

            {result && !loading && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                <div className="card" style={{ borderLeft: `5px solid ${result.action_required ? '#ef4444' : '#10b981'}`, background: 'linear-gradient(135deg, var(--bg-card), var(--bg-secondary))' }}>
                  <div className="card-body" style={{ padding: 24 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 }}>
                      <div>
                        <span className={`badge ${result.action_required ? 'down' : 'up'}`} style={{ display: 'inline-flex', alignItems: 'center', gap: 6, marginBottom: 12 }}>
                          {result.action_required ? <AlertTriangle size={14} /> : <CheckCircle size={14} />}
                          {result.action_required ? 'Disease Detected' : 'Plant is Healthy'}
                        </span>
                        <h2 style={{ margin: 0, fontSize: '2rem', color: result.action_required ? '#ef4444' : '#10b981' }}>{result.disease}</h2>
                        <p style={{ margin: '4px 0 0 0', color: 'var(--text-muted)' }}>Detected on <strong>{result.crop}</strong> plant</p>
                      </div>
                      
                      <div style={{ textAlign: 'right' }}>
                        <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--primary)' }}>{result.confidence}%</div>
                        <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-muted)', letterSpacing: 1 }}>Match</div>
                      </div>
                    </div>
                    
                    <button onClick={downloadReport} className="btn btn-secondary" style={{ padding: '8px 16px', fontSize: '0.85rem' }}>
                      <Download size={14} /> Download PDF Report
                    </button>
                  </div>
                </div>

                {result.action_required && (
                  <div className="card">
                    <div className="card-header" style={{ background: 'rgba(239, 68, 68, 0.1)' }}>
                      <h3 style={{ margin: 0, color: '#ef4444', display: 'flex', alignItems: 'center', gap: 8 }}>
                        <AlertTriangle size={18} /> Treatment & Pesticide Suggestions
                      </h3>
                    </div>
                    <div className="card-body">
                      <p style={{ lineHeight: 1.6, color: 'var(--text-color)' }}>{result.treatment}</p>
                    </div>
                  </div>
                )}
              </div>
            )}

            {!result && !loading && (
              <div className="card">
                <div className="card-body" style={{ padding: '60px 20px', textAlign: 'center' }}>
                  <div style={{ fontSize: '3rem', marginBottom: 16 }}>🩺</div>
                  <h3>Awaiting Scan</h3>
                  <p style={{ color: 'var(--text-muted)', maxWidth: 300, margin: '0 auto' }}>Upload an image of your crop to instantly identify potential diseases and receive treatment guidance.</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
