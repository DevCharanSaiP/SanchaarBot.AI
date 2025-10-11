import React, { useState, useEffect, useRef } from 'react';
import { apiCall } from '../api';

const ChatWindow = ({ user, onError, onSuccess, loading, setLoading }) => {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    // Load previous messages from localStorage
    const savedMessages = localStorage.getItem(`chat_history_${user.id}`);
    if (savedMessages) {
      setMessages(JSON.parse(savedMessages));
    } else {
      // Add welcome message
      setMessages([
        {
          id: 'welcome',
          type: 'bot',
          text: "Hello! I'm your Travel Companion AI. I can help you plan trips, book flights and hotels, check weather, translate text, and manage your travel documents. What would you like to do today?",
          timestamp: new Date().toISOString(),
          suggestions: [
            "Plan a trip to Paris",
            "Find flights to Tokyo",
            "Check weather in London",
            "Translate 'Where is the bathroom?' to Spanish",
            "Help me organize my travel documents"
          ]
        }
      ]);
    }
  }, [user.id]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Save messages to localStorage whenever messages change
    if (messages.length > 0) {
      localStorage.setItem(`chat_history_${user.id}`, JSON.stringify(messages));
    }
  }, [messages, user.id]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async (messageText = inputText) => {
    if (!messageText.trim()) return;

    const userMessage = {
      id: Date.now().toString(),
      type: 'user',
      text: messageText.trim(),
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsTyping(true);
    setLoading(true);

    try {
      const response = await apiCall('/api/chat', 'POST', {
        user_id: user.id,
        message: messageText.trim()
      });

      const botMessage = {
        id: Date.now().toString() + '_bot',
        type: 'bot',
        text: response.response?.text || 'I apologize, but I encountered an issue processing your request.',
        timestamp: new Date().toISOString(),
        data: response.response?.data,
        actionRequired: response.response?.action_required,
        messageType: response.response?.type
      };

      setMessages(prev => [...prev, botMessage]);

      // Handle specific response types
      if (response.response?.type === 'flight_booking') {
        // Could trigger flight search UI or other specific actions
      } else if (response.response?.type === 'hotel_booking') {
        // Could trigger hotel search UI
      }

    } catch (error) {
      console.error('Chat error:', error);
      
      const errorMessage = {
        id: Date.now().toString() + '_error',
        type: 'bot',
        text: 'I apologize, but I encountered an error. Please try again.',
        timestamp: new Date().toISOString(),
        isError: true
      };

      setMessages(prev => [...prev, errorMessage]);
      onError('Failed to send message. Please try again.');
    } finally {
      setIsTyping(false);
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setInputText(suggestion);
    handleSendMessage(suggestion);
  };

  const clearChat = () => {
    if (window.confirm('Are you sure you want to clear the chat history?')) {
      setMessages([
        {
          id: 'cleared',
          type: 'bot',
          text: "Chat history cleared. How can I help you today?",
          timestamp: new Date().toISOString()
        }
      ]);
      localStorage.removeItem(`chat_history_${user.id}`);
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const renderMessage = (message) => {
    const isUser = message.type === 'user';
    
    return (
      <div
        key={message.id}
        className={`message ${isUser ? 'user-message' : 'bot-message'} ${message.isError ? 'error-message' : ''}`}
      >
        <div className="message-avatar">
          {isUser ? (
            <div className="user-avatar">{user.name.charAt(0).toUpperCase()}</div>
          ) : (
            <div className="bot-avatar">🤖</div>
          )}
        </div>
        
        <div className="message-content">
          <div className="message-text">{message.text}</div>
          
          {message.suggestions && (
            <div className="message-suggestions">
              {message.suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  className="suggestion-button"
                  onClick={() => handleSuggestionClick(suggestion)}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          )}
          
          {message.data && (
            <div className="message-data">
              <pre>{JSON.stringify(message.data, null, 2)}</pre>
            </div>
          )}
          
          <div className="message-timestamp">
            {formatTimestamp(message.timestamp)}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="chat-window">
      <div className="chat-header">
        <div className="chat-title">
          <span className="chat-icon">💬</span>
          <h2>Chat with AI Assistant</h2>
        </div>
        <div className="chat-actions">
          <button className="clear-chat-button" onClick={clearChat}>
            Clear Chat
          </button>
        </div>
      </div>

      <div className="chat-messages">
        {messages.map(renderMessage)}
        
        {isTyping && (
          <div className="typing-indicator">
            <div className="message bot-message">
              <div className="message-avatar">
                <div className="bot-avatar">🤖</div>
              </div>
              <div className="message-content">
                <div className="typing-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input">
        <div className="input-container">
          <textarea
            ref={inputRef}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message... (Enter to send, Shift+Enter for new line)"
            className="message-input"
            rows="1"
            disabled={loading}
          />
          <button
            className={`send-button ${inputText.trim() ? 'active' : ''}`}
            onClick={() => handleSendMessage()}
            disabled={loading || !inputText.trim()}
          >
            {loading ? (
              <div className="button-spinner"></div>
            ) : (
              <span>📤</span>
            )}
          </button>
        </div>
        
        <div className="quick-actions">
          <button
            className="quick-action-button"
            onClick={() => handleSuggestionClick("What can you help me with?")}
          >
            💡 What can you do?
          </button>
          <button
            className="quick-action-button"
            onClick={() => handleSuggestionClick("Show me my current itinerary")}
          >
            📅 My Itinerary
          </button>
          <button
            className="quick-action-button"
            onClick={() => handleSuggestionClick("Check for travel alerts")}
          >
            🚨 Alerts
          </button>
          <button
            className="quick-action-button"
            onClick={() => handleSuggestionClick("Help me translate something")}
          >
            🌐 Translate
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatWindow;