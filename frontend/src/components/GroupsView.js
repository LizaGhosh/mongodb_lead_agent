import React, { useState, useEffect } from 'react';
import { getGroups } from '../services/api';
import PersonCard from './PersonCard';

/**
 * Component for displaying meetings grouped by priority (P0, P1, P2)
 */
const GroupsView = ({ userId = 'default' }) => {
  const [groups, setGroups] = useState({ P0: [], P1: [], P2: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchGroups = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await getGroups(userId);
      setGroups(data);
    } catch (err) {
      setError('Error loading groups. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGroups();
  }, [userId]);

  if (loading) {
    return (
      <div style={styles.container}>
        <p>Loading...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={styles.container}>
        <p style={styles.error}>{error}</p>
        <button onClick={fetchGroups} style={styles.retryButton}>
          Retry
        </button>
      </div>
    );
  }

  const totalCount = groups.P0.length + groups.P1.length + groups.P2.length;

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h2 style={styles.title}>Priority Groups</h2>
        <button onClick={fetchGroups} style={styles.refreshButton}>
          Refresh
        </button>
      </div>

      {totalCount === 0 ? (
        <p style={styles.empty}>No meetings processed yet. Submit a meeting to get started.</p>
      ) : (
        <>
          {/* P0 Group */}
          <div style={styles.group}>
            <h3 style={styles.groupTitle}>
              P0 - Highest Priority ({groups.P0.length})
            </h3>
            {groups.P0.length === 0 ? (
              <p style={styles.emptyGroup}>No P0 meetings</p>
            ) : (
              groups.P0.map((person, index) => (
                <PersonCard key={index} person={person} />
              ))
            )}
          </div>

          {/* P1 Group */}
          <div style={styles.group}>
            <h3 style={styles.groupTitle}>
              P1 - Medium Priority ({groups.P1.length})
            </h3>
            {groups.P1.length === 0 ? (
              <p style={styles.emptyGroup}>No P1 meetings</p>
            ) : (
              groups.P1.map((person, index) => (
                <PersonCard key={index} person={person} />
              ))
            )}
          </div>

          {/* P2 Group */}
          <div style={styles.group}>
            <h3 style={styles.groupTitle}>
              P2 - Lower Priority ({groups.P2.length})
            </h3>
            {groups.P2.length === 0 ? (
              <p style={styles.emptyGroup}>No P2 meetings</p>
            ) : (
              groups.P2.map((person, index) => (
                <PersonCard key={index} person={person} />
              ))
            )}
          </div>
        </>
      )}
    </div>
  );
};

const styles = {
  container: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '20px',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '30px',
  },
  title: {
    fontSize: '28px',
    fontWeight: 'bold',
  },
  refreshButton: {
    padding: '8px 16px',
    backgroundColor: '#000',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '14px',
  },
  group: {
    marginBottom: '40px',
  },
  groupTitle: {
    fontSize: '20px',
    fontWeight: 'bold',
    marginBottom: '20px',
    paddingBottom: '10px',
    borderBottom: '2px solid #000',
  },
  empty: {
    textAlign: 'center',
    padding: '40px',
    fontSize: '16px',
    color: '#666',
  },
  emptyGroup: {
    padding: '20px',
    textAlign: 'center',
    color: '#666',
    fontStyle: 'italic',
  },
  error: {
    color: '#d32f2f',
    marginBottom: '10px',
  },
  retryButton: {
    padding: '8px 16px',
    backgroundColor: '#000',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
  },
};

export default GroupsView;
