import { useEffect, useState, type FormEvent } from 'react';
import { pricesAPI, type PriceRecord } from '../services/api';
import { Search, RefreshCw } from 'lucide-react';


export default function PricesPage() {
  const [prices, setPrices] = useState<PriceRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [commodity, setCommodity] = useState('');
  const [state, setState] = useState('');

  const fetchPrices = async (crop = commodity, st = state) => {
    setLoading(true);
    try {
      const params: any = { limit: 100 };
      if (crop) params.commodity = crop;
      if (st)   params.state     = st;
      const res = await pricesAPI.getPrices(params);
      setPrices(res.data);
    } catch { /* ignore */ }
    setLoading(false);
  };

  useEffect(() => { fetchPrices(); }, []);

  const handleStateChange = (val: string) => {
    setState(val);
  };

  const handleSearch = (e: FormEvent) => {
    e.preventDefault();
    fetchPrices();
  };

  const handleReset = () => {
    setCommodity('');
    setState('');
    fetchPrices('', '');
  };

  return (
    <>
      <div className="page-header">
        <h1>📊 Mandi Prices</h1>
        <p>Real-time crop prices from Government of India</p>
      </div>

      <div className="page-body">
        <form onSubmit={handleSearch} className="filters-bar">

          {/* Crop text input */}
          <input
            className="form-input"
            placeholder="🔍 Crop name (e.g. Tomato)"
            value={commodity}
            onChange={e => setCommodity(e.target.value)}
          />

          {/* State text input */}
          <input
            className="form-input"
            placeholder="📍 State"
            value={state}
            onChange={e => handleStateChange(e.target.value)}
          />


          <button type="submit" className="btn btn-primary">
            <Search size={16} /> Search
          </button>
          <button type="button" className="btn btn-secondary" onClick={handleReset}>
            <RefreshCw size={16} /> Reset
          </button>
        </form>

        <div className="card">
          <div className="card-body" style={{ padding: 0 }}>
            {loading ? (
              <div className="loading-center"><div className="spinner" /><span>Fetching prices...</span></div>
            ) : prices.length === 0 ? (
              <div className="empty-state">
                <div className="emoji">📦</div>
                <h3>No prices found</h3>
                <p>Try a different filter combination or reset to view all records</p>
              </div>
            ) : (
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Commodity</th>
                      <th>Market</th>
                      <th>District</th>
                      <th>State</th>
                      <th>Min (₹)</th>
                      <th>Modal (₹)</th>
                      <th>Max (₹)</th>
                      <th>Date</th>
                      <th>Trend</th>
                    </tr>
                  </thead>
                  <tbody>
                    {prices.map((p, i) => (
                      <tr key={i}>
                        <td style={{ fontWeight: 600 }}>{p.commodity}</td>
                        <td>{p.market}</td>
                        <td>{p.district}</td>
                        <td>{p.state}</td>
                        <td>₹{p.min_price.toLocaleString()}</td>
                        <td style={{ fontWeight: 600, color: 'var(--green-700)' }}>₹{p.modal_price.toLocaleString()}</td>
                        <td>₹{p.max_price.toLocaleString()}</td>
                        <td style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{p.arrival_date}</td>
                        <td>
                          {p.trend ? (
                            <span className={`badge ${p.trend}`}>
                              {p.trend === 'up' ? '↑' : p.trend === 'down' ? '↓' : '→'}
                              {p.change_pct != null ? ` ${Math.abs(p.change_pct)}%` : ''}
                            </span>
                          ) : <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>—</span>}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
