import { NavLink, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import {
  LayoutDashboard, TrendingUp, CloudSun, Bell,
  Sprout, User, LogOut, Menu, X, MessageCircle, FlaskConical, BarChart3, Stethoscope, Store
} from 'lucide-react';

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/prices', icon: TrendingUp, label: 'Mandi Prices' },
  { to: '/weather', icon: CloudSun, label: 'Weather' },
  { to: '/notifications', icon: Bell, label: 'Alerts' },
  { to: '/crop-ai', icon: Sprout, label: 'AI Crop Advisor' },
  { to: '/fertilizer', icon: FlaskConical, label: 'Fertilizer AI' },
  { to: '/crop-yield', icon: BarChart3, label: 'Crop Yield AI' },
  { to: '/disease-ai', icon: Stethoscope, label: 'Disease AI' },
  { to: '/marketplace', icon: Store, label: 'Marketplace' },
  { to: '/chat', icon: MessageCircle, label: 'KrushiMitra AI' },
  { to: '/profile', icon: User, label: 'Profile' },
];

export default function Layout({ children }: { children: React.ReactNode }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="app-layout">
      {/* Mobile Header */}
      <div className="mobile-header">
        <button className="hamburger" onClick={() => setSidebarOpen(true)}>
          <Menu size={24} />
        </button>
        <h1>🌾 Kisaan Mitra</h1>
      </div>

      {/* Overlay */}
      <div
        className={`overlay ${sidebarOpen ? 'active' : ''}`}
        onClick={() => setSidebarOpen(false)}
      />

      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-brand">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h1><span>🌾</span> Kisaan Mitra</h1>
            <button
              className="hamburger"
              onClick={() => setSidebarOpen(false)}
              style={{ display: sidebarOpen ? 'block' : 'none' }}
            >
              <X size={20} />
            </button>
          </div>
          <p>Smart Farmer Assistant</p>
        </div>

        <nav className="sidebar-nav">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
              onClick={() => setSidebarOpen(false)}
            >
              <Icon size={20} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          {user && (
            <div style={{ padding: '8px 16px', fontSize: '0.8rem', opacity: 0.6, marginBottom: 8 }}>
              👤 {user.name}
            </div>
          )}
          <button className="nav-link" onClick={handleLogout} style={{ color: 'rgba(255,255,255,0.6)' }}>
            <LogOut size={20} />
            Logout
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        {children}
      </main>
    </div>
  );
}
