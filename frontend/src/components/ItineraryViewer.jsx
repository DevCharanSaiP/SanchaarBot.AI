import React, { useState, useEffect } from 'react';
import { apiCall } from '../api';

const ItineraryViewer = ({ user, onError, onSuccess }) => {
  const [itinerary, setItinerary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editMode, setEditMode] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);

  useEffect(() => {
    loadItinerary();
  }, [user.id]);

  const loadItinerary = async () => {
    try {
      setLoading(true);
      const response = await apiCall('/api/itinerary', 'GET', null, { user_id: user.id });
      
      if (response.found) {
        setItinerary(response.itinerary);
        setShowCreateForm(false);
      } else {
        setItinerary(null);
        setShowCreateForm(true);
      }
    } catch (error) {
      console.error('Error loading itinerary:', error);
      onError('Failed to load itinerary');
    } finally {
      setLoading(false);
    }
  };

  const createItinerary = async (formData) => {
    try {
      setLoading(true);
      const response = await apiCall('/api/itinerary', 'POST', {
        user_id: user.id,
        action: 'create',
        itinerary_data: formData
      });

      if (response.itinerary) {
        setItinerary(response.itinerary);
        setShowCreateForm(false);
        onSuccess('Itinerary created successfully!');
      }
    } catch (error) {
      console.error('Error creating itinerary:', error);
      onError('Failed to create itinerary');
    } finally {
      setLoading(false);
    }
  };

  const generateItinerary = async (preferences) => {
    try {
      setLoading(true);
      const response = await apiCall('/api/itinerary', 'POST', {
        user_id: user.id,
        action: 'generate',
        preferences: preferences
      });

      if (response.itinerary) {
        setItinerary(response.itinerary);
        setShowCreateForm(false);
        onSuccess('AI-generated itinerary created!');
      }
    } catch (error) {
      console.error('Error generating itinerary:', error);
      onError('Failed to generate itinerary');
    } finally {
      setLoading(false);
    }
  };

  const deleteItinerary = async () => {
    if (!window.confirm('Are you sure you want to delete this itinerary?')) {
      return;
    }

    try {
      setLoading(true);
      await apiCall('/api/itinerary', 'POST', {
        user_id: user.id,
        action: 'delete'
      });

      setItinerary(null);
      setShowCreateForm(true);
      onSuccess('Itinerary deleted successfully');
    } catch (error) {
      console.error('Error deleting itinerary:', error);
      onError('Failed to delete itinerary');
    } finally {
      setLoading(false);
    }
  };

  const exportItinerary = async () => {
    try {
      const response = await apiCall('/api/itinerary/export', 'POST', {
        user_id: user.id
      });

      if (response.download_url) {
        window.open(response.download_url, '_blank');
        onSuccess('Itinerary exported successfully!');
      }
    } catch (error) {
      console.error('Error exporting itinerary:', error);
      onError('Failed to export itinerary');
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString([], {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatCurrency = (amount, currency = 'USD') => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="itinerary-loading">
        <div className="loading-spinner"></div>
        <p>Loading itinerary...</p>
      </div>
    );
  }

  if (showCreateForm) {
    return <CreateItineraryForm onSubmit={createItinerary} onGenerate={generateItinerary} />;
  }

  if (!itinerary) {
    return (
      <div className="no-itinerary">
        <div className="empty-state">
          <span className="empty-icon">📅</span>
          <h3>No Itinerary Found</h3>
          <p>Create your first travel itinerary to get started.</p>
          <button 
            className="create-button primary"
            onClick={() => setShowCreateForm(true)}
          >
            Create Itinerary
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="itinerary-viewer">
      {/* Header */}
      <div className="itinerary-header">
        <div className="header-info">
          <h2>{itinerary.title}</h2>
          <div className="trip-details">
            <span className="destination">📍 {itinerary.destination}</span>
            <span className="dates">
              🗓️ {formatDate(itinerary.start_date)} - {formatDate(itinerary.end_date)}
            </span>
            <span className="duration">⏱️ {itinerary.duration_days} days</span>
            <span className="travelers">👥 {itinerary.travelers} traveler{itinerary.travelers !== 1 ? 's' : ''}</span>
          </div>
          {itinerary.description && (
            <p className="trip-description">{itinerary.description}</p>
          )}
        </div>
        
        <div className="header-actions">
          <button className="action-button" onClick={() => setEditMode(true)}>
            ✏️ Edit
          </button>
          <button className="action-button" onClick={exportItinerary}>
            📥 Export
          </button>
          <button className="action-button danger" onClick={deleteItinerary}>
            🗑️ Delete
          </button>
        </div>
      </div>

      {/* Budget Summary */}
      {itinerary.budget && (
        <div className="budget-summary">
          <h3>Budget Overview</h3>
          <div className="budget-total">
            Total Estimated: {formatCurrency(itinerary.budget.total_estimated, itinerary.budget.currency)}
          </div>
          {itinerary.budget.breakdown && (
            <div className="budget-breakdown">
              {Object.entries(itinerary.budget.breakdown).map(([category, amount]) => (
                <div key={category} className="budget-item">
                  <span className="category">{category}</span>
                  <span className="amount">{formatCurrency(amount, itinerary.budget.currency)}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Daily Itinerary */}
      <div className="daily-itinerary">
        <h3>Daily Schedule</h3>
        {itinerary.days?.map((day, index) => (
          <div key={day.day || index} className="day-card">
            <div className="day-header">
              <h4>{day.title || `Day ${day.day}`}</h4>
              <span className="day-date">{formatDate(day.date)}</span>
            </div>

            <div className="day-activities">
              {day.activities?.map((activity, actIndex) => (
                <div key={actIndex} className="activity-item">
                  <div className="activity-time">{activity.time}</div>
                  <div className="activity-content">
                    <h5>{activity.title}</h5>
                    <p>{activity.description}</p>
                    {activity.location && (
                      <div className="activity-location">📍 {activity.location}</div>
                    )}
                    <div className="activity-details">
                      <span className="duration">⏱️ {activity.duration}</span>
                      {activity.estimated_cost > 0 && (
                        <span className="cost">
                          💰 {formatCurrency(activity.estimated_cost)}
                        </span>
                      )}
                      <span className="type">🏷️ {activity.type}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {day.transportation && (
              <div className="day-transportation">
                <strong>Transportation:</strong> {day.transportation.type}
                {day.transportation.estimated_cost > 0 && (
                  <span> - {formatCurrency(day.transportation.estimated_cost)}</span>
                )}
              </div>
            )}

            <div className="day-summary">
              <div className="day-total">
                Daily Total: {formatCurrency(day.total_estimated_cost)}
              </div>
              {day.notes && (
                <div className="day-notes">
                  <strong>Notes:</strong> {day.notes}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Metadata */}
      <div className="itinerary-metadata">
        <div className="metadata-item">
          <strong>Created:</strong> {formatDate(itinerary.created_at)}
        </div>
        <div className="metadata-item">
          <strong>Last Updated:</strong> {formatDate(itinerary.updated_at)}
        </div>
        {itinerary.generated_by_ai && (
          <div className="metadata-item">
            <span className="ai-badge">🤖 AI Generated</span>
          </div>
        )}
        <div className="metadata-item">
          <strong>Status:</strong> 
          <span className={`status-badge ${itinerary.status}`}>
            {itinerary.status}
          </span>
        </div>
      </div>
    </div>
  );
};

// Create Itinerary Form Component
const CreateItineraryForm = ({ onSubmit, onGenerate }) => {
  const [formData, setFormData] = useState({
    destination: '',
    start_date: '',
    end_date: '',
    title: '',
    description: '',
    travelers: 1,
    budget: '',
    interests: [],
    travel_style: 'balanced'
  });

  const [showAIForm, setShowAIForm] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (showAIForm) {
      const preferences = {
        destination: formData.destination,
        duration: calculateDuration(formData.start_date, formData.end_date),
        start_date: formData.start_date,
        budget: formData.budget || 'medium',
        interests: formData.interests,
        travel_style: formData.travel_style,
        travelers: formData.travelers
      };
      onGenerate(preferences);
    } else {
      onSubmit(formData);
    }
  };

  const calculateDuration = (start, end) => {
    if (!start || !end) return 3;
    const startDate = new Date(start);
    const endDate = new Date(end);
    return Math.max(1, Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24)) + 1);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Auto-generate title if destination changes
    if (name === 'destination' && value) {
      setFormData(prev => ({ 
        ...prev, 
        title: prev.title || `Trip to ${value}` 
      }));
    }
  };

  const handleInterestsChange = (interest) => {
    setFormData(prev => ({
      ...prev,
      interests: prev.interests.includes(interest)
        ? prev.interests.filter(i => i !== interest)
        : [...prev.interests, interest]
    }));
  };

  const interestOptions = [
    'sightseeing', 'culture', 'food', 'adventure', 'relaxation',
    'history', 'art', 'nature', 'nightlife', 'shopping', 'photography'
  ];

  return (
    <div className="create-itinerary-form">
      <div className="form-header">
        <h2>Create New Itinerary</h2>
        <div className="form-tabs">
          <button 
            className={`tab-button ${!showAIForm ? 'active' : ''}`}
            onClick={() => setShowAIForm(false)}
          >
            Manual Creation
          </button>
          <button 
            className={`tab-button ${showAIForm ? 'active' : ''}`}
            onClick={() => setShowAIForm(true)}
          >
            🤖 AI Generate
          </button>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="itinerary-form">
        <div className="form-row">
          <div className="form-group">
            <label>Destination *</label>
            <input
              type="text"
              name="destination"
              value={formData.destination}
              onChange={handleInputChange}
              placeholder="e.g., Paris, France"
              required
            />
          </div>
          <div className="form-group">
            <label>Trip Title</label>
            <input
              type="text"
              name="title"
              value={formData.title}
              onChange={handleInputChange}
              placeholder="e.g., Spring Break in Paris"
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Start Date *</label>
            <input
              type="date"
              name="start_date"
              value={formData.start_date}
              onChange={handleInputChange}
              required
            />
          </div>
          <div className="form-group">
            <label>End Date *</label>
            <input
              type="date"
              name="end_date"
              value={formData.end_date}
              onChange={handleInputChange}
              min={formData.start_date}
              required
            />
          </div>
          <div className="form-group">
            <label>Travelers</label>
            <select
              name="travelers"
              value={formData.travelers}
              onChange={handleInputChange}
            >
              {[1, 2, 3, 4, 5, 6].map(num => (
                <option key={num} value={num}>{num}</option>
              ))}
            </select>
          </div>
        </div>

        {showAIForm && (
          <>
            <div className="form-group">
              <label>Budget Level</label>
              <select
                name="budget"
                value={formData.budget}
                onChange={handleInputChange}
              >
                <option value="low">Budget-Friendly</option>
                <option value="medium">Mid-Range</option>
                <option value="high">Luxury</option>
              </select>
            </div>

            <div className="form-group">
              <label>Travel Style</label>
              <select
                name="travel_style"
                value={formData.travel_style}
                onChange={handleInputChange}
              >
                <option value="relaxed">Relaxed</option>
                <option value="balanced">Balanced</option>
                <option value="packed">Action-Packed</option>
              </select>
            </div>

            <div className="form-group">
              <label>Interests</label>
              <div className="interests-grid">
                {interestOptions.map(interest => (
                  <label key={interest} className="interest-checkbox">
                    <input
                      type="checkbox"
                      checked={formData.interests.includes(interest)}
                      onChange={() => handleInterestsChange(interest)}
                    />
                    <span>{interest}</span>
                  </label>
                ))}
              </div>
            </div>
          </>
        )}

        <div className="form-group">
          <label>Description</label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleInputChange}
            placeholder="Brief description of your trip..."
            rows="3"
          />
        </div>

        <div className="form-actions">
          <button type="submit" className="submit-button primary">
            {showAIForm ? '🤖 Generate with AI' : 'Create Itinerary'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default ItineraryViewer;