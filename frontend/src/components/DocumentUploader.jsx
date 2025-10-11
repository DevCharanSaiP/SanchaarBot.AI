import React, { useState, useEffect, useRef } from 'react';
import { apiCall } from '../api';

const DocumentUploader = ({ user, onError, onSuccess }) => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [view, setView] = useState('grid'); // 'grid' or 'list'
  const [filter, setFilter] = useState('all');
  const fileInputRef = useRef(null);

  useEffect(() => {
    loadDocuments();
  }, [user.id]);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      const response = await apiCall('/api/documents', 'GET', null, { user_id: user.id });
      
      if (response.documents) {
        setDocuments(response.documents);
      }
    } catch (error) {
      console.error('Error loading documents:', error);
      onError('Failed to load documents');
    } finally {
      setLoading(false);
    }
  };

  const uploadDocument = async (file, documentType = 'other') => {
    try {
      setUploading(true);
      
      // Convert file to base64
      const base64Content = await fileToBase64(file);
      
      const response = await apiCall('/api/documents', 'POST', {
        user_id: user.id,
        action: 'upload',
        filename: file.name,
        file_content: base64Content,
        content_type: file.type,
        document_type: documentType
      });

      if (response.document) {
        setDocuments(prev => [response.document, ...prev]);
        onSuccess(`Document "${file.name}" uploaded successfully!`);
      }
    } catch (error) {
      console.error('Error uploading document:', error);
      onError(`Failed to upload "${file.name}"`);
    } finally {
      setUploading(false);
    }
  };

  const deleteDocument = async (documentKey) => {
    if (!window.confirm('Are you sure you want to delete this document?')) {
      return;
    }

    try {
      await apiCall('/api/documents', 'POST', {
        user_id: user.id,
        action: 'delete',
        document_key: documentKey
      });

      setDocuments(documents.filter(doc => doc.s3_key !== documentKey));
      onSuccess('Document deleted successfully');
    } catch (error) {
      console.error('Error deleting document:', error);
      onError('Failed to delete document');
    }
  };

  const downloadDocument = async (documentKey, filename) => {
    try {
      const response = await apiCall('/api/documents/download', 'POST', {
        user_id: user.id,
        document_key: documentKey
      });

      if (response.download_url) {
        const link = document.createElement('a');
        link.href = response.download_url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
    } catch (error) {
      console.error('Error downloading document:', error);
      onError('Failed to download document');
    }
  };

  const scanDocument = async (documentKey) => {
    try {
      const response = await apiCall('/api/documents', 'POST', {
        user_id: user.id,
        action: 'scan',
        document_key: documentKey
      });

      if (response.extracted_text) {
        onSuccess(`Text extracted successfully! Word count: ${response.word_count}`);
        // You could show the extracted text in a modal or separate component
      }
    } catch (error) {
      console.error('Error scanning document:', error);
      onError('Failed to extract text from document');
    }
  };

  const organizeDocuments = async () => {
    try {
      setLoading(true);
      const response = await apiCall('/api/documents', 'POST', {
        user_id: user.id,
        action: 'organize'
      });

      if (response.organization_stats) {
        onSuccess('Documents organized successfully!');
        await loadDocuments(); // Reload documents
      }
    } catch (error) {
      console.error('Error organizing documents:', error);
      onError('Failed to organize documents');
    } finally {
      setLoading(false);
    }
  };

  const fileToBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        // Remove the data:image/jpeg;base64, prefix
        const base64 = reader.result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = error => reject(error);
    });
  };

  const handleFileSelect = (files) => {
    Array.from(files).forEach(file => {
      // Determine document type based on filename
      const documentType = classifyDocumentType(file.name);
      uploadDocument(file, documentType);
    });
  };

  const classifyDocumentType = (filename) => {
    const name = filename.toLowerCase();
    
    if (name.includes('passport') || name.includes('visa') || name.includes('id')) {
      return 'identification';
    } else if (name.includes('ticket') || name.includes('boarding') || name.includes('flight')) {
      return 'flight_document';
    } else if (name.includes('hotel') || name.includes('reservation') || name.includes('booking')) {
      return 'accommodation';
    } else if (name.includes('insurance') || name.includes('policy')) {
      return 'insurance';
    } else if (name.includes('itinerary') || name.includes('plan') || name.includes('schedule')) {
      return 'itinerary';
    }
    
    return 'other';
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileSelect(files);
    }
  };

  const formatFileSize = (bytes) => {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };

  const getDocumentIcon = (type) => {
    const icons = {
      'identification': '🆔',
      'flight_document': '✈️',
      'accommodation': '🏨',
      'insurance': '🛡️',
      'itinerary': '📅',
      'other': '📄'
    };
    return icons[type] || '📄';
  };

  const filteredDocuments = documents.filter(doc => {
    if (filter === 'all') return true;
    return doc.document_type === filter;
  });

  const documentTypes = [...new Set(documents.map(doc => doc.document_type))];

  if (loading && documents.length === 0) {
    return (
      <div className="documents-loading">
        <div className="loading-spinner"></div>
        <p>Loading documents...</p>
      </div>
    );
  }

  return (
    <div className="document-uploader">
      {/* Header */}
      <div className="documents-header">
        <div className="header-info">
          <h2>Travel Documents</h2>
          <span className="documents-count">
            {documents.length} document{documents.length !== 1 ? 's' : ''}
          </span>
        </div>
        
        <div className="header-actions">
          <div className="view-toggles">
            <button 
              className={`view-button ${view === 'grid' ? 'active' : ''}`}
              onClick={() => setView('grid')}
            >
              ⊞ Grid
            </button>
            <button 
              className={`view-button ${view === 'list' ? 'active' : ''}`}
              onClick={() => setView('list')}
            >
              ☰ List
            </button>
          </div>
          
          <select 
            value={filter} 
            onChange={(e) => setFilter(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Types</option>
            {documentTypes.map(type => (
              <option key={type} value={type}>
                {type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </option>
            ))}
          </select>
          
          <button 
            className="organize-button"
            onClick={organizeDocuments}
            disabled={loading || documents.length === 0}
          >
            🗂️ Organize
          </button>
        </div>
      </div>

      {/* Upload Area */}
      <div 
        className={`upload-area ${dragOver ? 'drag-over' : ''} ${uploading ? 'uploading' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={(e) => handleFileSelect(e.target.files)}
          multiple
          accept=".pdf,.doc,.docx,.jpg,.jpeg,.png,.gif,.txt"
          style={{ display: 'none' }}
        />
        
        <div className="upload-content">
          {uploading ? (
            <>
              <div className="upload-spinner"></div>
              <p>Uploading documents...</p>
            </>
          ) : (
            <>
              <div className="upload-icon">📁</div>
              <h3>Upload Travel Documents</h3>
              <p>Drag and drop files here, or click to browse</p>
              <div className="supported-formats">
                Supports: PDF, DOC, DOCX, JPG, PNG, TXT
              </div>
            </>
          )}
        </div>
      </div>

      {/* Documents Grid/List */}
      <div className={`documents-container ${view}`}>
        {filteredDocuments.length === 0 ? (
          <div className="no-documents">
            <div className="empty-state">
              <span className="empty-icon">📄</span>
              <h3>No Documents</h3>
              <p>
                {filter === 'all' 
                  ? "Upload your travel documents to get started."
                  : `No documents of type "${filter}".`
                }
              </p>
            </div>
          </div>
        ) : (
          <div className={`documents-${view}`}>
            {filteredDocuments.map(document => (
              <div key={document.s3_key} className="document-item">
                <div className="document-header">
                  <div className="document-icon">
                    {getDocumentIcon(document.document_type)}
                  </div>
                  <div className="document-info">
                    <h4 className="document-name" title={document.filename}>
                      {document.filename}
                    </h4>
                    <div className="document-meta">
                      <span className="document-type">
                        {document.document_type.replace(/_/g, ' ')}
                      </span>
                      <span className="document-size">
                        {formatFileSize(document.size)}
                      </span>
                      <span className="document-date">
                        {new Date(document.uploaded_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="document-actions">
                  <button
                    className="action-button download"
                    onClick={() => downloadDocument(document.s3_key, document.filename)}
                    title="Download"
                  >
                    ⬇️
                  </button>
                  
                  {document.content_type?.includes('pdf') && (
                    <button
                      className="action-button scan"
                      onClick={() => scanDocument(document.s3_key)}
                      title="Extract text"
                    >
                      🔍
                    </button>
                  )}
                  
                  <button
                    className="action-button delete"
                    onClick={() => deleteDocument(document.s3_key)}
                    title="Delete"
                  >
                    🗑️
                  </button>
                </div>

                <div className="document-status">
                  <span className={`status-badge ${document.status}`}>
                    {document.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Document Statistics */}
      {documents.length > 0 && (
        <div className="documents-stats">
          <div className="stats-row">
            <div className="stat-item">
              <span className="stat-value">
                {documents.reduce((total, doc) => total + doc.size, 0) / (1024 * 1024) < 1 
                  ? `${Math.round(documents.reduce((total, doc) => total + doc.size, 0) / 1024)} KB`
                  : `${Math.round(documents.reduce((total, doc) => total + doc.size, 0) / (1024 * 1024))} MB`
                }
              </span>
              <span className="stat-label">Total Size</span>
            </div>
            
            {documentTypes.map(type => (
              <div key={type} className="stat-item">
                <span className="stat-value">
                  {documents.filter(doc => doc.document_type === type).length}
                </span>
                <span className="stat-label">
                  {type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="quick-actions">
        <button 
          className="quick-action-button"
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
        >
          📎 Upload More
        </button>
        
        <button 
          className="quick-action-button"
          onClick={loadDocuments}
          disabled={loading}
        >
          🔄 Refresh
        </button>
        
        {documents.length > 0 && (
          <button 
            className="quick-action-button"
            onClick={() => {
              // Create backup functionality
              apiCall('/api/documents/backup', 'POST', { user_id: user.id })
                .then(() => onSuccess('Backup created successfully'))
                .catch(() => onError('Failed to create backup'));
            }}
          >
            💾 Backup All
          </button>
        )}
      </div>
    </div>
  );
};

export default DocumentUploader;