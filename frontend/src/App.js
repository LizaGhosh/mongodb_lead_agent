import React, { useState, useEffect } from 'react';
import MeetingInput from './components/MeetingInput';
import GroupsView from './components/GroupsView';
import ClearDataButton from './components/ClearDataButton';
import OnboardingForm from './components/OnboardingForm';
import { checkOnboarding, resetOnboarding } from './services/api';

/**
 * Main App Component
 */
function App() {
  const [refreshKey, setRefreshKey] = useState(0);
  const [onboardingComplete, setOnboardingComplete] = useState(false);
  const [loading, setLoading] = useState(true);
  const [userPreferences, setUserPreferences] = useState(null);

  // Check onboarding status on mount
  useEffect(() => {
    const checkStatus = async () => {
      try {
        const result = await checkOnboarding('default');
        setOnboardingComplete(result.completed);
        if (result.preferences) {
          setUserPreferences(result.preferences);
        }
      } catch (error) {
        console.error('Error checking onboarding:', error);
        setOnboardingComplete(false);
      } finally {
        setLoading(false);
      }
    };
    checkStatus();
  }, []);

  const handleMeetingSubmitted = () => {
    // Trigger refresh of groups view
    setRefreshKey(prev => prev + 1);
  };

  const handleDataCleared = () => {
    // Trigger refresh of groups view after data is cleared
    setRefreshKey(prev => prev + 1);
  };

  const handleOnboardingComplete = (prefs) => {
    setOnboardingComplete(true);
    setUserPreferences(prefs);
  };

  const handleResetOnboarding = async () => {
    if (window.confirm('Reset onboarding? You will need to fill out the form again.')) {
      try {
        await resetOnboarding('default');
        setOnboardingComplete(false);
        setUserPreferences(null);
      } catch (error) {
        console.error('Error resetting onboarding:', error);
        alert('Failed to reset onboarding. Please try again.');
      }
    }
  };

  if (loading) {
    return (
      <div style={styles.app}>
        <div style={styles.loading}>Loading...</div>
      </div>
    );
  }

  // Show onboarding if not completed
  if (!onboardingComplete) {
    return (
      <div style={styles.app}>
        <header style={styles.header}>
          <h1 style={styles.logo}>Networking Assistant</h1>
          <p style={styles.subtitle}>Multi-Agent System for Networking Management</p>
        </header>
        <main style={styles.main}>
          <OnboardingForm onComplete={handleOnboardingComplete} />
        </main>
      </div>
    );
  }

  // Show main app if onboarding is complete
  return (
    <div style={styles.app}>
      <header style={styles.header}>
        <div style={styles.headerContent}>
          <div style={styles.headerText}>
            <h1 style={styles.logo}>Networking Assistant</h1>
            <p style={styles.subtitle}>Multi-Agent System for Networking Management</p>
            {userPreferences?.event_details && (
              <p style={styles.eventInfo}>
                Event: {userPreferences.event_details.event_name || 'Networking Event'} | 
                {userPreferences.event_details.event_date && ` Date: ${new Date(userPreferences.event_details.event_date).toLocaleDateString()}`} | 
                {userPreferences.event_details.event_location && ` Location: ${userPreferences.event_details.event_location}`}
              </p>
            )}
          </div>
          <button
            onClick={handleResetOnboarding}
            style={styles.resetButton}
            title="Reset onboarding to see the form again"
          >
            Reset Onboarding
          </button>
        </div>
      </header>

      <main style={styles.main}>
        <div style={styles.controlsContainer}>
          <MeetingInput onMeetingSubmitted={handleMeetingSubmitted} />
          <ClearDataButton onDataCleared={handleDataCleared} />
        </div>
        <GroupsView key={refreshKey} userId="default" />
      </main>

      <footer style={styles.footer}>
        <p>Powered by MongoDB Atlas & Multi-Agent System</p>
      </footer>
    </div>
  );
}

const styles = {
  app: {
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    backgroundColor: '#ffffff',
  },
  header: {
    backgroundColor: '#000',
    color: '#fff',
    padding: '30px 20px',
  },
  headerContent: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    maxWidth: '1200px',
    margin: '0 auto',
  },
  headerText: {
    textAlign: 'center',
    flex: 1,
  },
  resetButton: {
    padding: '8px 16px',
    backgroundColor: '#666',
    color: '#fff',
    border: '1px solid #999',
    borderRadius: '4px',
    fontSize: '12px',
    cursor: 'pointer',
    whiteSpace: 'nowrap',
  },
  logo: {
    fontSize: '32px',
    fontWeight: 'bold',
    marginBottom: '10px',
  },
  subtitle: {
    fontSize: '16px',
    opacity: 0.9,
  },
  main: {
    flex: 1,
    padding: '40px 20px',
  },
  controlsContainer: {
    maxWidth: '1200px',
    margin: '0 auto 30px',
  },
  footer: {
    backgroundColor: '#f5f5f5',
    padding: '20px',
    textAlign: 'center',
    borderTop: '1px solid #ddd',
    fontSize: '14px',
    color: '#666',
  },
  loading: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '100vh',
    fontSize: '18px',
  },
  eventInfo: {
    fontSize: '14px',
    opacity: 0.8,
    marginTop: '10px',
  },
};

export default App;
