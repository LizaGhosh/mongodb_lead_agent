import React, { useState } from 'react';
import { clearAllData } from '../services/api';

/**
 * Component for clearing all data with confirmation
 */
const ClearDataButton = ({ onDataCleared }) => {
  const [showConfirm, setShowConfirm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleClear = async () => {
    setLoading(true);
    setMessage('');

    try {
      const result = await clearAllData();
      setMessage(`Data cleared successfully! Deleted: ${result.deleted_counts.meetings_deleted} meetings, ${result.deleted_counts.people_deleted} people.`);
      setShowConfirm(false);
      
      // Notify parent component
      if (onDataCleared) {
        onDataCleared();
      }
    } catch (error) {
      setMessage('Error clearing data. Please try again.');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      {!showConfirm ? (
        <button
          onClick={() => setShowConfirm(true)}
          style={styles.clearButton}
        >
          🗑️ Clear All Data
        </button>
      ) : (
        <div style={styles.confirmContainer}>
          <p style={styles.confirmText}>
            Are you sure you want to delete all meetings and people data? This action cannot be undone.
          </p>
          <div style={styles.buttonGroup}>
            <button
              onClick={handleClear}
              disabled={loading}
              style={loading ? { ...styles.confirmButton, ...styles.buttonDisabled } : styles.confirmButton}
            >
              {loading ? 'Clearing...' : 'Yes, Clear All'}
            </button>
            <button
              onClick={() => {
                setShowConfirm(false);
                setMessage('');
              }}
              disabled={loading}
              style={styles.cancelButton}
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {message && (
        <div style={styles.message}>
          {message}
        </div>
      )}
    </div>
  );
};

const styles = {
  container: {
    marginBottom: '20px',
  },
  clearButton: {
    padding: '10px 20px',
    backgroundColor: '#d32f2f',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    fontSize: '14px',
    fontWeight: '500',
    cursor: 'pointer',
  },
  confirmContainer: {
    padding: '15px',
    border: '2px solid #d32f2f',
    borderRadius: '4px',
    backgroundColor: '#fff3f3',
  },
  confirmText: {
    marginBottom: '15px',
    fontSize: '14px',
    color: '#000',
    fontWeight: '500',
  },
  buttonGroup: {
    display: 'flex',
    gap: '10px',
  },
  confirmButton: {
    padding: '8px 16px',
    backgroundColor: '#d32f2f',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    fontSize: '14px',
    cursor: 'pointer',
  },
  cancelButton: {
    padding: '8px 16px',
    backgroundColor: '#666',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    fontSize: '14px',
    cursor: 'pointer',
  },
  buttonDisabled: {
    backgroundColor: '#999',
    cursor: 'not-allowed',
  },
  message: {
    marginTop: '10px',
    padding: '10px',
    backgroundColor: '#f5f5f5',
    border: '1px solid #000',
    borderRadius: '4px',
    fontSize: '14px',
  },
};

export default ClearDataButton;
