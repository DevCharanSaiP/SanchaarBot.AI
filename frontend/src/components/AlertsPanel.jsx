import React, { useState, useEffect } from 'react';
import { apiCall } from '../api';

const AlertsPanel = ({ user, notifications, onDismiss, onError }) => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    loadAlerts();
  }, [user.id]);

  const loadAlerts = async () => {
    try {
      setLoading(true);
      const response = await apiCall('/api/alerts', 'GET', null, { user_id: user.id });
      
      if (response.alerts) {
        setAlerts(response.alerts);
      }
    } catch (error) {
      console.error('Error loading alerts:', error);
      onError('Failed to load alerts');
    } finally {
      setLoading(false);
    }
  };

  const dismissAlert = async (alertId) => {
    try {
      await apiCall('/api/alerts/dismiss', 'POST', {
        user_id: user.id,
        alert_id: alertId
      });

      setAlerts(alerts.filter(alert => alert.id !== alertId));
      onDismiss(alertId);
    } catch (error) {
      console.error('Error dismissing alert:', error);
      onError('Failed to dismiss alert');
    }
  };

  const getAlertIcon = (type) => {
    const icons = {
      'flight_checkin_reminder': '✈️',
      'departure_reminder': '🛫',
      'gate_change': '🚪',
      'severe_weather': '⛈️',
      'weather_advisory': '🌦️',
      'travel_advisory': '⚠️',
      'document_expiry': '📄',
      'custom': '📌',
      'security': '🔒'
    };
    return icons[type] || '🔔';
  };

  const getAlertColor = (priority) => {
    switch (priority) {
      case 5: return 'critical';
      case 4: return 'high';
      case 3: return 'medium';
      case 2: return 'low';
      default: return 'info';
    }
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 3600000) { // Less than 1 hour
      return `${Math.floor(diff / 60000)} minutes ago`;
    } else if (diff < 86400000) { // Less than 24 hours
      return `${Math.floor(diff / 3600000)} hours ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  const filteredAlerts = alerts.filter(alert => {
    if (filter === 'all') return true;
    if (filter === 'action_required') return alert.action_required;
    if (filter === 'high_priority') return alert.priority >= 4;
    return alert.type === filter;
  });

  const alertTypes = [...new Set(alerts.map(alert => alert.type))];

  if (loading) {
    return (
      <div className="alerts-loading">
        <div className="loading-spinner"></div>
        <p>Loading alerts...</p>
      </div>
    );
  }

  return (
    <div className="alerts-panel">
      <div className="alerts-header">
        <div className="header-info">
          <h2>Travel Alerts</h2>
          <span className="alerts-count">
            {alerts.length} alert{alerts.length !== 1 ? 's' : ''}
          </span>
        </div>
        
        <div className="alerts-filters">
          <select 
            value={filter} 
            onChange={(e) => setFilter(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Alerts</option>
            <option value="action_required">Action Required</option>
            <option value="high_priority">High Priority</option>
            {alertTypes.map(type => (
              <option key={type} value={type}>
                {type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </option>
            ))}
          </select>
          
          <button 
            className="refresh-button"
            onClick={loadAlerts}
            disabled={loading}
          >
            🔄 Refresh
          </button>
        </div>
      </div>

      <div className="alerts-content">
        {filteredAlerts.length === 0 ? (
          <div className="no-alerts">
            <div className="empty-state">
              <span className="empty-icon">✅</span>
              <h3>No Alerts</h3>
              <p>
                {filter === 'all' 
                  ? "You're all set! No alerts at this time."
                  : `No alerts matching "${filter}" filter.`
                }
              </p>
            </div>
          </div>
        ) : (
          <div className="alerts-list">
            {filteredAlerts.map(alert => (
              <div 
                key={alert.id || alert.created_at}
                className={`alert-item ${getAlertColor(alert.priority)} ${alert.action_required ? 'action-required' : ''}`}
              >
                <div className="alert-header">
                  <div className="alert-icon">
                    {getAlertIcon(alert.type)}
                  </div>
                  
                  <div className="alert-info">
                    <h4 className="alert-title">{alert.title}</h4>
                    <div className="alert-meta">
                      <span className="alert-type">
                        {alert.type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </span>
                      <span className="alert-time">
                        {formatTimestamp(alert.created_at)}
                      </span>
                      {alert.location && (
                        <span className="alert-location">
                          📍 {alert.location}
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="alert-actions">
                    {alert.action_required && (
                      <span className="action-badge">Action Required</span>
                    )}
                    <button
                      className="dismiss-button"
                      onClick={() => dismissAlert(alert.id)}
                      title="Dismiss alert"
                    >
                      ×
                    </button>
                  </div>
                </div>

                <div className="alert-body">
                  <p className="alert-message">{alert.message}</p>
                  
                  {alert.booking_id && (
                    <div className="alert-booking">
                      <strong>Booking:</strong> {alert.booking_id}
                    </div>
                  )}
                  
                  {alert.date && (
                    <div className="alert-date">
                      <strong>Date:</strong> {new Date(alert.date).toLocaleDateString()}
                    </div>
                  )}
                  
                  {alert.url && (
                    <div className="alert-link">
                      <a 
                        href={alert.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="external-link"
                      >
                        View Details →
                      </a>
                    </div>
                  )}
                </div>

                <div className="alert-footer">
                  <div className="priority-indicator">
                    Priority: 
                    <span className={`priority-level ${getAlertColor(alert.priority)}`}>
                      {['Very Low', 'Low', 'Medium', 'High', 'Critical'][alert.priority - 1] || 'Unknown'}
                    </span>
                  </div>
                  
                  {alert.source && (
                    <div className="alert-source">
                      Source: {alert.source}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Alert Statistics */}
      <div className="alerts-stats">
        <div className="stats-row">
          <div className="stat-item">
            <span className="stat-value">{alerts.filter(a => a.action_required).length}</span>
            <span className="stat-label">Action Required</span>
          </div>
          <div className="stat-item">
            <span className="stat-value">{alerts.filter(a => a.priority >= 4).length}</span>
            <span className="stat-label">High Priority</span>
          </div>
          <div className="stat-item">
            <span className="stat-value">
              {alerts.filter(a => {
                const alertTime = new Date(a.created_at);
                const dayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);
                return alertTime >= dayAgo;
              }).length}
            </span>
            <span className="stat-label">Last 24h</span>
          </div>
        </div>
      </div>

      {/* Create Custom Alert */}
      <div className="create-alert-section">
        <button 
          className="create-alert-button"
          onClick={() => setShowCreateForm(true)}
        >
          + Create Custom Alert
        </button>
      </div>
    </div>
  );
};

// Custom Alert Creation Form
const CreateAlertForm = ({ user, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    title: '',
    message: '',
    priority: 2,
    trigger_date: '',
    action_required: false
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  return (
    <div className="create-alert-form">
      <h3>Create Custom Alert</h3>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Alert Title *</label>
          <input
            type="text"
            name="title"
            value={formData.title}
            onChange={handleInputChange}
            placeholder="e.g., Passport Renewal Reminder"
            required
          />
        </div>

        <div className="form-group">
          <label>Message *</label>
          <textarea
            name="message"
            value={formData.message}
            onChange={handleInputChange}
            placeholder="Enter alert message..."
            rows="3"
            required
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Priority</label>
            <select
              name="priority"
              value={formData.priority}
              onChange={handleInputChange}
            >
              <option value={1}>Very Low</option>
              <option value={2}>Low</option>
              <option value={3}>Medium</option>
              <option value={4}>High</option>
              <option value={5}>Critical</option>
            </select>
          </div>
          
          <div className="form-group">
            <label>Trigger Date</label>
            <input
              type="datetime-local"
              name="trigger_date"
              value={formData.trigger_date}
              onChange={handleInputChange}
            />
          </div>
        </div>

        <div className="form-group">
          <label className="checkbox-label">
            <input
              type="checkbox"
              name="action_required"
              checked={formData.action_required}
              onChange={handleInputChange}
            />
            <span>Action Required</span>
          </label>
        </div>

        <div className="form-actions">
          <button type="button" onClick={onCancel} className="cancel-button">
            Cancel
          </button>
          <button type="submit" className="submit-button primary">
            Create Alert
          </button>
        </div>
      </form>
    </div>
  );
};

export default AlertsPanel;