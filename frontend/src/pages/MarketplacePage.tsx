import { useState, useEffect } from 'react';
import { marketplaceAPI } from '../services/api';
import { Search, MapPin, Tag, Phone, Plus } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function MarketplacePage() {
  const { user } = useAuth();
  const [listings, setListings] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  
  // Form State
  const [form, setForm] = useState({
    title: '',
    description: '',
    category: 'crop',
    price: '',
    unit: 'kg',
    location_state: user?.location_state || '',
    location_district: user?.location_district || '',
    contact_whatsapp: user?.phone || '',
  });

  const loadListings = async () => {
    setLoading(true);
    try {
      const res = await marketplaceAPI.getListings({ query, category });
      setListings(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadListings();
  }, [category]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadListings();
  };

  const handleAddSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await marketplaceAPI.createListing({
        ...form,
        price: parseFloat(form.price)
      });
      setShowAddForm(false);
      setForm({ ...form, title: '', description: '', price: '' });
      loadListings();
    } catch (err) {
      console.error("Failed to add listing", err);
    }
  };

  return (
    <>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1>🛒 Farmer Marketplace</h1>
          <p>Buy seeds & fertilizers directly, or sell your harvest globally</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowAddForm(!showAddForm)}>
          <Plus size={18} /> {showAddForm ? 'Cancel' : 'Add Listing'}
        </button>
      </div>

      <div className="page-body">
        {showAddForm && (
          <div className="card" style={{ marginBottom: 24, borderLeft: '5px solid var(--primary)' }}>
            <div className="card-header">
              <h2>Post a New Listing</h2>
            </div>
            <div className="card-body">
              <form onSubmit={handleAddSubmit} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                <div className="form-group">
                  <label>Title</label>
                  <input type="text" className="form-input" required value={form.title} onChange={e => setForm({...form, title: e.target.value})} placeholder="e.g. Organic Basmati Rice 100kg" />
                </div>
                <div className="form-group">
                  <label>Category</label>
                  <select className="form-input" value={form.category} onChange={e => setForm({...form, category: e.target.value})}>
                    <option value="crop">Harvest/Crop</option>
                    <option value="seed">Seeds</option>
                    <option value="fertilizer">Fertilizers</option>
                    <option value="equipment">Farming Equipment</option>
                  </select>
                </div>
                <div className="form-group" style={{ gridColumn: '1 / -1' }}>
                  <label>Description</label>
                  <textarea className="form-input" required value={form.description} onChange={e => setForm({...form, description: e.target.value})} rows={3} placeholder="Quality, age, variety details..." />
                </div>
                <div style={{ display: 'flex', gap: 12 }}>
                  <div className="form-group" style={{ flex: 2 }}>
                    <label>Price (₹)</label>
                    <input type="number" className="form-input" required value={form.price} onChange={e => setForm({...form, price: e.target.value})} />
                  </div>
                  <div className="form-group" style={{ flex: 1 }}>
                    <label>Unit</label>
                    <select className="form-input" value={form.unit} onChange={e => setForm({...form, unit: e.target.value})}>
                      <option value="kg">per kg</option>
                      <option value="quintal">per quintal</option>
                      <option value="packet">per packet</option>
                      <option value="piece">per piece</option>
                    </select>
                  </div>
                </div>
                <div className="form-group">
                  <label>WhatsApp Number</label>
                  <input type="text" className="form-input" required value={form.contact_whatsapp} onChange={e => setForm({...form, contact_whatsapp: e.target.value})} />
                </div>
                <div className="form-group" style={{ gridColumn: '1 / -1' }}>
                  <button type="submit" className="btn btn-primary">Post Listing to Global Market</button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Search & Filter Bar */}
        <div style={{ display: 'flex', gap: 12, marginBottom: 24 }}>
          <form onSubmit={handleSearch} style={{ display: 'flex', flex: 1, gap: 12 }}>
            <div className="form-group" style={{ flex: 1, margin: 0, position: 'relative' }}>
              <Search size={18} style={{ position: 'absolute', left: 14, top: 14, color: 'var(--text-muted)' }} />
              <input 
                type="text" 
                className="form-input" 
                placeholder="Search for rice, urea, tractors..." 
                style={{ paddingLeft: 42 }}
                value={query}
                onChange={e => setQuery(e.target.value)}
              />
            </div>
            <button type="submit" className="btn btn-secondary">Search</button>
          </form>
          <select className="form-input" style={{ width: 180 }} value={category} onChange={e => setCategory(e.target.value)}>
            <option value="">All Categories</option>
            <option value="crop">Crops</option>
            <option value="seed">Seeds</option>
            <option value="fertilizer">Fertilizers</option>
            <option value="equipment">Equipment</option>
          </select>
        </div>

        {loading ? (
          <div className="loading-center" style={{ padding: '40px 0' }}><div className="spinner" /></div>
        ) : listings.length === 0 ? (
          <div className="card"><div className="card-body" style={{ textAlign: 'center', padding: '60px 20px' }}>
            <div style={{ fontSize: '3rem', marginBottom: 16 }}>🛒</div>
            <h3>No listings found</h3>
            <p style={{ color: 'var(--text-muted)' }}>Try a different search term or category.</p>
          </div></div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 20 }}>
            {listings.map((item) => (
              <div key={item.id} className="card" style={{ display: 'flex', flexDirection: 'column' }}>
                <div className="card-body" style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
                    <span className="badge" style={{ background: 'var(--bg-secondary)', color: 'var(--text-color)', textTransform: 'uppercase', fontSize: '0.7rem' }}>
                      <Tag size={10} style={{ marginRight: 4 }} /> {item.category}
                    </span>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      {new Date(item.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  
                  <h3 style={{ margin: '0 0 8px 0', fontSize: '1.2rem', lineHeight: 1.3 }}>{item.title}</h3>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: 1.5, flex: 1, margin: '0 0 16px 0' }}>
                    {item.description.length > 80 ? item.description.substring(0, 80) + '...' : item.description}
                  </p>
                  
                  <div style={{ background: 'var(--bg-background)', padding: '12px', borderRadius: 8, marginBottom: 16 }}>
                    <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--primary)', marginBottom: 4 }}>
                      ₹{item.price} <span style={{ fontSize: '0.85rem', fontWeight: 500, color: 'var(--text-muted)' }}>/ {item.unit}</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      <MapPin size={12} /> {item.location_district}, {item.location_state}
                    </div>
                  </div>
                  
                  <a 
                    href={`https://wa.me/91${item.contact_whatsapp}?text=Hi%20${item.seller_name},%20I'm%20interested%20in%20your%20listing:%20${item.title}`}
                    target="_blank"
                    rel="noreferrer"
                    className="btn btn-primary" 
                    style={{ background: '#25D366', color: '#fff', border: 'none', width: '100%', display: 'flex', justifyContent: 'center' }}
                  >
                    <Phone size={16} /> Contact via WhatsApp
                  </a>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  );
}
