import React, { useState, useEffect } from 'react';
import './styles.css';
import ChatWindow from './components/ChatWindow';
import ItineraryViewer from './components/ItineraryViewer';
import AlertsPanel from './components/AlertsPanel';
import DocumentUploader from './components/DocumentUploader';
import { apiCall } from './api';

function App() {
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('chat');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [notifications, setNotifications] = useState([]);

  // Initialize user session
  useEffect(() => {
    initializeUser();
    checkForAlerts();
  }, []);

  const initializeUser = () => {
    // Get or create user ID from localStorage
    let userId = localStorage.getItem('travel_companion_user_id');
    if (!userId) {
      userId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('travel_companion_user_id', userId);
    }
    
    setUser({ 
      id: userId, 
      name: 'Traveler',
      preferences: JSON.parse(localStorage.getItem('user_preferences') || '{}')
    });
  };

  const checkForAlerts = async () => {
    try {
      const userId = localStorage.getItem('travel_companion_user_id');
      if (userId) {
        const response = await apiCall('/api/alerts', 'GET', null, { user_id: userId });
        if (response.alerts && response.alerts.length > 0) {
          setNotifications(response.alerts.filter(alert => alert.action_required));
        }
      }
    } catch (error) {
      console.error('Error checking alerts:', error);
    }
  };

  const handleError = (errorMessage) => {
    setError(errorMessage);
    setTimeout(() => setError(null), 5000); // Clear error after 5 seconds
  };

  const handleSuccess = (message) => {
    // You could add a success notification system here
    console.log('Success:', message);
  };

  const dismissNotification = (notificationId) => {
    setNotifications(notifications.filter(n => n.id !== notificationId));
  };

  const tabs = [
    { id: 'chat', label: 'Chat', icon: '💬' },
    { id: 'itinerary', label: 'Itinerary', icon: '📅' },
    { id: 'alerts', label: 'Alerts', icon: '🚨', badge: notifications.length },
    { id: 'documents', label: 'Documents', icon: '📄' }
  ];

  if (!user) {
    return (
      <div className="app-loading">
        <div className="loading-spinner"></div>
        <p>Initializing Travel Companion...</p>
      </div>
    );
  }

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <div className="logo">
            <span className="logo-icon">✈️</span>
            <h1>Travel Companion AI</h1>
          </div>
          <div className="user-info">
            <span className="user-greeting">Hello, {user.name}!</span>
            <div className="user-avatar">
              {user.name.charAt(0).toUpperCase()}
            </div>
          </div>
        </div>
      </header>

      {/* Notifications Bar */}
      {notifications.length > 0 && (
        <div className="notifications-bar">
          <div className="notification-content">
            <span className="notification-icon">🔔</span>
            <span className="notification-text">
              You have {notifications.length} important alert{notifications.length !== 1 ? 's' : ''}
            </span>
            <button 
              className="notification-dismiss"
              onClick={() => setActiveTab('alerts')}
            >
              View All
            </button>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="app-main">
        {/* Navigation Tabs */}
        <nav className="tab-navigation">
          {tabs.map(tab => (
            <button
              key={tab.id}
              className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <span className="tab-icon">{tab.icon}</span>
              <span className="tab-label">{tab.label}</span>
              {tab.badge > 0 && (
                <span className="tab-badge">{tab.badge}</span>
              )}
            </button>
          ))}
        </nav>

        {/* Tab Content */}
        <div className="tab-content">
          {activeTab === 'chat' && (
            <ChatWindow
              user={user}
              onError={handleError}
              onSuccess={handleSuccess}
              loading={loading}
              setLoading={setLoading}
            />
          )}

          {activeTab === 'itinerary' && (
            <ItineraryViewer
              user={user}
              onError={handleError}
              onSuccess={handleSuccess}
            />
          )}

          {activeTab === 'alerts' && (
            <AlertsPanel
              user={user}
              notifications={notifications}
              onDismiss={dismissNotification}
              onError={handleError}
            />
          )}

          {activeTab === 'documents' && (
            <DocumentUploader
              user={user}
              onError={handleError}
              onSuccess={handleSuccess}
            />
          )}
        </div>
      </main>

      {/* Error Display */}
      {error && (
        <div className="error-toast">
          <div className="error-content">
            <span className="error-icon">⚠️</span>
            <span className="error-message">{error}</span>
            <button 
              className="error-dismiss"
              onClick={() => setError(null)}
            >
              ×
            </button>
          </div>
        </div>
      )}

      {/* Loading Overlay */}
      {loading && (
        <div className="loading-overlay">
          <div className="loading-spinner"></div>
          <p>Processing your request...</p>
        </div>
      )}

      {/* Footer */}
      <footer className="app-footer">
        <div className="footer-content">
          <p>&copy; 2025 Travel Companion AI. Your intelligent travel assistant.</p>
          <div className="footer-links">
            <button className="footer-link">Privacy Policy</button>
            <button className="footer-link">Terms of Service</button>
            <button className="footer-link">Help</button>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;