import { useEffect, useState } from 'react';
import { notificationsAPI, type NotificationRecord } from '../services/api';

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<NotificationRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await notificationsAPI.getNotifications(50);
        setNotifications(res.data);
      } catch { /* ignore */ }
      setLoading(false);
    };
    load();
  }, []);

  const getIcon = (type: string) => {
    switch (type) {
      case 'critical': return '🚨';
      case 'big_jump': return '📈';
      case 'inactive': return '💤';
      default: return '🔔';
    }
  };

  const formatDate = (d: string) => {
    try { return new Date(d).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' }); }
    catch { return d; }
  };

  return (
    <>
      <div className="page-header">
        <h1>🔔 Price Alerts</h1>
        <p>Your notification history</p>
      </div>
      <div className="page-body">
        <div className="card">
          <div className="card-body">
            {loading ? (
              <div className="loading-center"><div className="spinner" /><span>Loading alerts...</span></div>
            ) : notifications.length === 0 ? (
              <div className="empty-state">
                <div className="emoji">🔕</div>
                <h3>No alerts yet</h3>
                <p>You'll receive alerts when your watched crop prices change significantly</p>
              </div>
            ) : (
              notifications.map(n => (
                <div className="notification-item" key={n.id}>
                  <div className={`notif-icon ${n.alert_type}`}>{getIcon(n.alert_type)}</div>
                  <div className="notif-body">
                    <h4>
                      {n.commodity} — {n.market}
                      <span className={`badge ${n.alert_type}`} style={{ marginLeft: 8 }}>{n.alert_type.replace('_', ' ')}</span>
                    </h4>
                    <p>{n.message_en}</p>
                    <div style={{ display: 'flex', gap: 16, marginTop: 8, flexWrap: 'wrap' }}>
                      <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                        ₹{n.old_price.toLocaleString()} → ₹{n.new_price.toLocaleString()}
                      </span>
                      <span className={`badge ${n.change_pct > 0 ? 'up' : 'down'}`}>
                        {n.change_pct > 0 ? '↑' : '↓'} {Math.abs(n.change_pct).toFixed(1)}%
                      </span>
                    </div>
                    <div className="notif-meta">
                      <span>{formatDate(n.created_at)}</span>
                      {n.firebase_sent && <span>✅ Push sent</span>}
                      {n.sms_sent && <span>📱 SMS sent</span>}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </>
  );
}
