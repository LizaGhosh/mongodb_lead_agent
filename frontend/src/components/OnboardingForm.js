import React, { useState } from 'react';
import { submitOnboarding } from '../services/api';

/**
 * Onboarding form for collecting user preferences and event details
 */
const OnboardingForm = ({ onComplete }) => {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  
  // Form data
  const [formData, setFormData] = useState({
    use_case: '',
    intent: '',
    event_date: '',
    event_location: '',
    event_name: '',
    goals: '',
    industries: [],
    company_sizes: [],
    job_titles: '',
    comments: ''
  });

  const useCases = [
    { value: 'sales', label: 'Sales / Lead Generation' },
    { value: 'job_hunting', label: 'Job Hunting' },
    { value: 'networking', label: 'General Networking' },
    { value: 'partnership', label: 'Partnerships' },
    { value: 'advertising', label: 'Advertising / Marketing' }
  ];

  const industries = [
    'Technology', 'Healthcare', 'Finance', 'Retail', 'Manufacturing',
    'Education', 'Real Estate', 'Consulting', 'Media', 'Energy'
  ];

  const companySizes = [
    'Startup (1-50)', 'Small (51-200)', 'Mid-size (201-1000)', 'Enterprise (1000+)'
  ];

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleIndustryToggle = (industry) => {
    setFormData(prev => ({
      ...prev,
      industries: prev.industries.includes(industry)
        ? prev.industries.filter(i => i !== industry)
        : [...prev.industries, industry]
    }));
  };

  const handleCompanySizeToggle = (size) => {
    setFormData(prev => ({
      ...prev,
      company_sizes: prev.company_sizes.includes(size)
        ? prev.company_sizes.filter(s => s !== size)
        : [...prev.company_sizes, size]
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (step < 3) {
      setStep(step + 1);
      return;
    }

    // Final step - submit
    if (!formData.use_case || !formData.intent || !formData.event_date) {
      setMessage('Please fill in all required fields');
      return;
    }

    setLoading(true);
    setMessage('');

    try {
      console.log('[OnboardingForm] Submitting form data:', formData);
      await submitOnboarding(formData);
      setMessage('Preferences saved successfully!');
      
      // Notify parent
      if (onComplete) {
        setTimeout(() => {
          onComplete(formData);
        }, 1000);
      }
    } catch (error) {
      console.error('[OnboardingForm] Submission error:', error);
      console.error('[OnboardingForm] Error details:', {
        message: error.message,
        status: error.status,
        isNetworkError: error.isNetworkError,
        response: error.response?.data
      });
      
      // Show more specific error message
      let errorMessage = 'Error saving preferences. Please try again.';
      if (error.isNetworkError) {
        errorMessage = 'Network error: Unable to reach server. Please check your connection.';
      } else if (error.status) {
        errorMessage = `Error (${error.status}): ${error.message || 'Please try again.'}`;
      } else if (error.message) {
        errorMessage = `Error: ${error.message}`;
      }
      
      setMessage(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const renderStep1 = () => (
    <div>
      <h3 style={styles.stepTitle}>Step 1: Use Case & Intent</h3>
      
      <div style={styles.inputGroup}>
        <label style={styles.label}>What's your primary goal? *</label>
        <select
          value={formData.use_case}
          onChange={(e) => handleInputChange('use_case', e.target.value)}
          style={styles.select}
          required
        >
          <option value="">Select use case</option>
          {useCases.map(uc => (
            <option key={uc.value} value={uc.value}>{uc.label}</option>
          ))}
        </select>
      </div>

      <div style={styles.inputGroup}>
        <label style={styles.label}>What's your intent for this event? *</label>
        <textarea
          value={formData.intent}
          onChange={(e) => handleInputChange('intent', e.target.value)}
          placeholder="e.g., Find potential clients in fintech, Connect with hiring managers..."
          style={styles.textarea}
          rows={3}
          required
        />
      </div>

      <div style={styles.inputGroup}>
        <label style={styles.label}>What do you want to achieve? *</label>
        <textarea
          value={formData.goals}
          onChange={(e) => handleInputChange('goals', e.target.value)}
          placeholder="e.g., Generate 10 qualified leads, Find 3 job opportunities, Build 5 strategic partnerships..."
          style={styles.textarea}
          rows={3}
          required
        />
      </div>
    </div>
  );

  const renderStep2 = () => (
    <div>
      <h3 style={styles.stepTitle}>Step 2: Event Details</h3>
      
      <div style={styles.inputGroup}>
        <label style={styles.label}>Event Name</label>
        <input
          type="text"
          value={formData.event_name}
          onChange={(e) => handleInputChange('event_name', e.target.value)}
          placeholder="e.g., Tech Conference 2024"
          style={styles.input}
        />
      </div>

      <div style={styles.inputGroup}>
        <label style={styles.label}>Event Date *</label>
        <input
          type="date"
          value={formData.event_date}
          onChange={(e) => handleInputChange('event_date', e.target.value)}
          style={styles.input}
          required
        />
      </div>

      <div style={styles.inputGroup}>
        <label style={styles.label}>Event Location *</label>
        <input
          type="text"
          value={formData.event_location}
          onChange={(e) => handleInputChange('event_location', e.target.value)}
          placeholder="e.g., San Francisco Convention Center"
          style={styles.input}
          required
        />
      </div>
    </div>
  );

  const renderStep3 = () => (
    <div>
      <h3 style={styles.stepTitle}>Step 3: Preferences & Details</h3>
      
      <div style={styles.inputGroup}>
        <label style={styles.label}>Industries of Interest</label>
        <div style={styles.checkboxGroup}>
          {industries.map(industry => (
            <label key={industry} style={styles.checkboxLabel}>
              <input
                type="checkbox"
                checked={formData.industries.includes(industry)}
                onChange={() => handleIndustryToggle(industry)}
                style={styles.checkbox}
              />
              {industry}
            </label>
          ))}
        </div>
      </div>

      <div style={styles.inputGroup}>
        <label style={styles.label}>Company Sizes</label>
        <div style={styles.checkboxGroup}>
          {companySizes.map(size => (
            <label key={size} style={styles.checkboxLabel}>
              <input
                type="checkbox"
                checked={formData.company_sizes.includes(size)}
                onChange={() => handleCompanySizeToggle(size)}
                style={styles.checkbox}
              />
              {size}
            </label>
          ))}
        </div>
      </div>

      <div style={styles.inputGroup}>
        <label style={styles.label}>Job Titles of Interest</label>
        <input
          type="text"
          value={formData.job_titles}
          onChange={(e) => handleInputChange('job_titles', e.target.value)}
          placeholder="e.g., CTO, VP Engineering, Head of Product (comma-separated)"
          style={styles.input}
        />
      </div>

      <div style={styles.inputGroup}>
        <label style={styles.label}>Additional Comments</label>
        <textarea
          value={formData.comments}
          onChange={(e) => handleInputChange('comments', e.target.value)}
          placeholder="Tell us more about what you're looking for. For example: specific industries, types of people, what makes a contact valuable to you, any special requirements..."
          style={styles.textarea}
          rows={5}
        />
      </div>
    </div>
  );

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Welcome to Networking Assistant</h2>
      <p style={styles.subtitle}>Let's set up your preferences to get the most out of your networking event</p>

      <form onSubmit={handleSubmit} style={styles.form}>
        {/* Progress indicator */}
        <div style={styles.progress}>
          <div style={styles.progressBar}>
            <div 
              style={{
                ...styles.progressFill,
                width: `${(step / 3) * 100}%`
              }}
            />
          </div>
          <p style={styles.progressText}>Step {step} of 3</p>
        </div>

        {/* Step content */}
        {step === 1 && renderStep1()}
        {step === 2 && renderStep2()}
        {step === 3 && renderStep3()}

        {/* Navigation buttons */}
        <div style={styles.buttonGroup}>
          {step > 1 && (
            <button
              type="button"
              onClick={() => setStep(step - 1)}
              style={styles.backButton}
            >
              ← Back
            </button>
          )}
          <button
            type="submit"
            disabled={loading}
            style={loading ? { ...styles.submitButton, ...styles.buttonDisabled } : styles.submitButton}
          >
            {step < 3 ? 'Next →' : loading ? 'Saving...' : 'Complete Setup'}
          </button>
        </div>

        {message && (
          <div style={styles.message}>
            {message}
          </div>
        )}
      </form>
    </div>
  );
};

const styles = {
  container: {
    maxWidth: '800px',
    margin: '0 auto',
    padding: '40px 20px',
  },
  title: {
    fontSize: '28px',
    fontWeight: 'bold',
    marginBottom: '10px',
    textAlign: 'center',
  },
  subtitle: {
    fontSize: '16px',
    color: '#666',
    marginBottom: '30px',
    textAlign: 'center',
  },
  form: {
    border: '1px solid #000',
    borderRadius: '4px',
    padding: '30px',
    backgroundColor: '#fff',
  },
  progress: {
    marginBottom: '30px',
  },
  progressBar: {
    width: '100%',
    height: '8px',
    backgroundColor: '#ddd',
    borderRadius: '4px',
    overflow: 'hidden',
    marginBottom: '10px',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#000',
    transition: 'width 0.3s ease',
  },
  progressText: {
    fontSize: '14px',
    color: '#666',
    textAlign: 'center',
  },
  stepTitle: {
    fontSize: '20px',
    fontWeight: 'bold',
    marginBottom: '20px',
  },
  inputGroup: {
    marginBottom: '20px',
  },
  label: {
    display: 'block',
    marginBottom: '8px',
    fontSize: '14px',
    fontWeight: '500',
  },
  input: {
    width: '100%',
    padding: '12px',
    border: '1px solid #000',
    borderRadius: '4px',
    fontSize: '14px',
    fontFamily: 'inherit',
  },
  select: {
    width: '100%',
    padding: '12px',
    border: '1px solid #000',
    borderRadius: '4px',
    fontSize: '14px',
    fontFamily: 'inherit',
    backgroundColor: '#fff',
  },
  textarea: {
    width: '100%',
    padding: '12px',
    border: '1px solid #000',
    borderRadius: '4px',
    fontSize: '14px',
    fontFamily: 'inherit',
    resize: 'vertical',
  },
  checkboxGroup: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '15px',
  },
  checkboxLabel: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '14px',
    cursor: 'pointer',
  },
  checkbox: {
    width: '18px',
    height: '18px',
    cursor: 'pointer',
  },
  buttonGroup: {
    display: 'flex',
    justifyContent: 'space-between',
    marginTop: '30px',
    gap: '10px',
  },
  backButton: {
    padding: '12px 24px',
    backgroundColor: '#666',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    fontSize: '16px',
    fontWeight: '500',
    cursor: 'pointer',
  },
  submitButton: {
    padding: '12px 24px',
    backgroundColor: '#000',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    fontSize: '16px',
    fontWeight: '500',
    cursor: 'pointer',
    marginLeft: 'auto',
  },
  buttonDisabled: {
    backgroundColor: '#999',
    cursor: 'not-allowed',
  },
  message: {
    marginTop: '15px',
    padding: '10px',
    backgroundColor: '#f5f5f5',
    border: '1px solid #000',
    borderRadius: '4px',
    fontSize: '14px',
    textAlign: 'center',
  },
};

export default OnboardingForm;
