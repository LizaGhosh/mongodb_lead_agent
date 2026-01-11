import React from 'react';

/**
 * Component for displaying a person's information
 */
const PersonCard = ({ person }) => {
  return (
    <div style={styles.card}>
      <div style={styles.header}>
        <h3 style={styles.name}>{person.name || 'Unknown'}</h3>
        <div style={styles.meta}>
          {person.company && (
            <span style={styles.company}>{person.company}</span>
          )}
          {person.designation && (
            <span style={styles.designation}>{person.designation}</span>
          )}
        </div>
      </div>
      
      {person.summary && (
        <div style={styles.summary}>
          <strong>Summary:</strong> {person.summary}
        </div>
      )}
      
      {person.meeting_date && (
        <div style={styles.date}>
          <strong>Meeting Date:</strong> {new Date(person.meeting_date).toLocaleDateString()}
          {person.meeting_timestamp && (
            <span style={styles.timestamp}>
              {' '}at {new Date(person.meeting_timestamp).toLocaleTimeString()}
            </span>
          )}
        </div>
      )}
    </div>
  );
};

const styles = {
  card: {
    border: '1px solid #000',
    borderRadius: '4px',
    padding: '20px',
    marginBottom: '15px',
    backgroundColor: '#fff',
  },
  header: {
    marginBottom: '15px',
  },
  name: {
    fontSize: '18px',
    fontWeight: 'bold',
    marginBottom: '8px',
  },
  meta: {
    display: 'flex',
    gap: '15px',
    fontSize: '14px',
  },
  company: {
    fontWeight: '500',
  },
  designation: {
    color: '#666',
  },
  summary: {
    marginTop: '15px',
    padding: '15px',
    backgroundColor: '#f5f5f5',
    border: '1px solid #ddd',
    borderRadius: '4px',
    fontSize: '14px',
    lineHeight: '1.6',
  },
  date: {
    marginTop: '10px',
    fontSize: '12px',
    color: '#666',
  },
  timestamp: {
    fontSize: '11px',
    color: '#999',
  },
};

export default PersonCard;
