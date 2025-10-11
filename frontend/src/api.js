// API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

// API client for communicating with the backend
export const apiCall = async (endpoint, method = 'GET', data = null, params = null) => {
  try {
    // Build URL with query parameters if provided
    let url = `${API_BASE_URL}${endpoint}`;
    
    if (params) {
      const searchParams = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        if (value !== null && value !== undefined) {
          searchParams.append(key, value);
        }
      });
      
      if (searchParams.toString()) {
        url += `?${searchParams.toString()}`;
      }
    }

    // Configure request options
    const options = {
      method,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    };

    // Add body for POST/PUT requests
    if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
      options.body = JSON.stringify(data);
    }

    // Add authentication headers if available
    const authToken = localStorage.getItem('auth_token');
    if (authToken) {
      options.headers.Authorization = `Bearer ${authToken}`;
    }

    // Make the request
    const response = await fetch(url, options);

    // Handle different response types
    const contentType = response.headers.get('content-type');
    let responseData;

    if (contentType?.includes('application/json')) {
      responseData = await response.json();
    } else if (contentType?.includes('text/')) {
      responseData = { text: await response.text() };
    } else {
      responseData = { blob: await response.blob() };
    }

    // Handle HTTP errors
    if (!response.ok) {
      const errorMessage = responseData?.error || 
                          responseData?.message || 
                          `HTTP ${response.status}: ${response.statusText}`;
      
      throw new APIError(errorMessage, response.status, responseData);
    }

    return responseData;

  } catch (error) {
    // Handle network errors and other exceptions
    if (error instanceof APIError) {
      throw error;
    }
    
    // Network or other errors
    console.error('API call failed:', error);
    throw new APIError(
      error.message || 'Network error occurred',
      0,
      null
    );
  }
};

// Custom error class for API errors
class APIError extends Error {
  constructor(message, status, data) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.data = data;
  }
}

// Utility functions for common API operations

export const chatAPI = {
  sendMessage: async (userId, message) => {
    return await apiCall('/api/chat', 'POST', {
      user_id: userId,
      message: message
    });
  }
};

export const itineraryAPI = {
  get: async (userId) => {
    return await apiCall('/api/itinerary', 'GET', null, { user_id: userId });
  },

  create: async (userId, itineraryData) => {
    return await apiCall('/api/itinerary', 'POST', {
      user_id: userId,
      action: 'create',
      itinerary_data: itineraryData
    });
  },

  update: async (userId, itineraryData) => {
    return await apiCall('/api/itinerary', 'POST', {
      user_id: userId,
      action: 'update',
      itinerary_data: itineraryData
    });
  },

  delete: async (userId) => {
    return await apiCall('/api/itinerary', 'POST', {
      user_id: userId,
      action: 'delete'
    });
  },

  generate: async (userId, preferences) => {
    return await apiCall('/api/itinerary', 'POST', {
      user_id: userId,
      action: 'generate',
      preferences: preferences
    });
  },

  export: async (userId) => {
    return await apiCall('/api/itinerary/export', 'POST', {
      user_id: userId
    });
  }
};

export const bookingAPI = {
  searchFlights: async (userId, searchParams) => {
    return await apiCall('/api/booking', 'POST', {
      user_id: userId,
      booking_type: 'flight',
      booking_details: searchParams
    });
  },

  searchHotels: async (userId, searchParams) => {
    return await apiCall('/api/booking', 'POST', {
      user_id: userId,
      booking_type: 'hotel',
      booking_details: searchParams
    });
  },

  confirmBooking: async (userId, bookingType, selection, paymentDetails = {}) => {
    return await apiCall('/api/booking/confirm', 'POST', {
      user_id: userId,
      booking_type: bookingType,
      selection: selection,
      payment_details: paymentDetails
    });
  },

  getUserBookings: async (userId) => {
    return await apiCall('/api/booking/history', 'GET', null, { user_id: userId });
  },

  cancelBooking: async (userId, bookingId) => {
    return await apiCall('/api/booking/cancel', 'POST', {
      user_id: userId,
      booking_id: bookingId
    });
  }
};

export const alertsAPI = {
  getAlerts: async (userId) => {
    return await apiCall('/api/alerts', 'GET', null, { user_id: userId });
  },

  dismissAlert: async (userId, alertId) => {
    return await apiCall('/api/alerts/dismiss', 'POST', {
      user_id: userId,
      alert_id: alertId
    });
  },

  createCustomAlert: async (userId, alertData) => {
    return await apiCall('/api/alerts/custom', 'POST', {
      user_id: userId,
      alert: alertData
    });
  }
};

export const documentAPI = {
  listDocuments: async (userId) => {
    return await apiCall('/api/documents', 'GET', null, { user_id: userId });
  },

  uploadDocument: async (userId, filename, fileContent, contentType, documentType = 'other') => {
    return await apiCall('/api/documents', 'POST', {
      user_id: userId,
      action: 'upload',
      filename: filename,
      file_content: fileContent,
      content_type: contentType,
      document_type: documentType
    });
  },

  downloadDocument: async (userId, documentKey) => {
    return await apiCall('/api/documents/download', 'POST', {
      user_id: userId,
      document_key: documentKey
    });
  },

  deleteDocument: async (userId, documentKey) => {
    return await apiCall('/api/documents', 'POST', {
      user_id: userId,
      action: 'delete',
      document_key: documentKey
    });
  },

  scanDocument: async (userId, documentKey) => {
    return await apiCall('/api/documents', 'POST', {
      user_id: userId,
      action: 'scan',
      document_key: documentKey
    });
  },

  organizeDocuments: async (userId) => {
    return await apiCall('/api/documents', 'POST', {
      user_id: userId,
      action: 'organize'
    });
  },

  createBackup: async (userId) => {
    return await apiCall('/api/documents/backup', 'POST', {
      user_id: userId
    });
  }
};

export const translationAPI = {
  translateText: async (text, targetLanguage, sourceLanguage = 'auto', service = 'aws') => {
    return await apiCall('/api/translate', 'POST', {
      text: text,
      target_language: targetLanguage,
      source_language: sourceLanguage,
      service: service
    });
  },

  getTravelPhrases: async (targetLanguage, category = 'general') => {
    return await apiCall('/api/translate/phrases', 'POST', {
      target_language: targetLanguage,
      category: category
    });
  },

  getSupportedLanguages: async () => {
    return await apiCall('/api/translate/languages', 'GET');
  },

  saveTranslation: async (userId, translationData) => {
    return await apiCall('/api/translate/save', 'POST', {
      user_id: userId,
      translation: translationData
    });
  },

  getSavedTranslations: async (userId) => {
    return await apiCall('/api/translate/saved', 'GET', null, { user_id: userId });
  }
};

// Health check endpoint
export const healthCheck = async () => {
  return await apiCall('/health', 'GET');
};

// Utility function to handle file uploads with progress
export const uploadFileWithProgress = async (endpoint, file, additionalData = {}, onProgress = null) => {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    const formData = new FormData();
    
    // Append file
    formData.append('file', file);
    
    // Append additional data
    Object.entries(additionalData).forEach(([key, value]) => {
      formData.append(key, value);
    });

    // Track upload progress
    if (onProgress) {
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          const percentComplete = (e.loaded / e.total) * 100;
          onProgress(percentComplete);
        }
      });
    }

    // Handle response
    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          const response = JSON.parse(xhr.responseText);
          resolve(response);
        } catch (e) {
          resolve({ success: true, text: xhr.responseText });
        }
      } else {
        reject(new APIError(
          `Upload failed: ${xhr.statusText}`,
          xhr.status,
          xhr.responseText
        ));
      }
    };

    xhr.onerror = () => {
      reject(new APIError('Upload failed: Network error', 0, null));
    };

    // Send request
    xhr.open('POST', `${API_BASE_URL}${endpoint}`);
    
    // Add auth header if available
    const authToken = localStorage.getItem('auth_token');
    if (authToken) {
      xhr.setRequestHeader('Authorization', `Bearer ${authToken}`);
    }
    
    xhr.send(formData);
  });
};

// Retry mechanism for failed requests
export const retryApiCall = async (apiCallFunction, maxRetries = 3, delay = 1000) => {
  let lastError;
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await apiCallFunction();
    } catch (error) {
      lastError = error;
      
      if (attempt === maxRetries) {
        throw error;
      }
      
      // Exponential backoff
      const waitTime = delay * Math.pow(2, attempt - 1);
      await new Promise(resolve => setTimeout(resolve, waitTime));
    }
  }
  
  throw lastError;
};

// Export the APIError class for use in components
export { APIError };