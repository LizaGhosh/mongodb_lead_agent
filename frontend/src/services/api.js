/** API service for backend communication */
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  // Don't set Content-Type for multipart/form-data - let browser set it with boundary
});

/**
 * Submit a new meeting for processing
 */
export const submitMeeting = async (text, location = null, audioBlob = null, photos = []) => {
  try {
    console.log('[API] Creating FormData for meeting submission');
    const formData = new FormData();
    
    // Add text if provided
    if (text) {
      formData.append('text', text);
      console.log('[API] Added text to FormData');
    }
    
    // Add location if provided
    if (location) {
      formData.append('location', location);
      console.log('[API] Added location to FormData');
    }
    
    // Add audio file if recorded
    if (audioBlob) {
      formData.append('audio', audioBlob, 'recording.webm');
      console.log('[API] Added audio file to FormData:', audioBlob.size, 'bytes');
    }
    
    // Add photo files
    if (photos.length > 0) {
      console.log(`[API] Adding ${photos.length} photo(s) to FormData for OCR processing`);
      photos.forEach((photo, index) => {
        formData.append('photos', photo.file, photo.file.name || `photo_${index}.jpg`);
        console.log(`[API] Added photo ${index + 1}:`, {
          name: photo.file.name,
          type: photo.file.type,
          size: `${(photo.file.size / 1024).toFixed(2)} KB`
        });
      });
    }
    
    console.log('[API] Sending POST request to /api/meetings');
    console.log('[API] FormData entries:', {
      hasText: !!text,
      hasLocation: !!location,
      hasAudio: !!audioBlob,
      photoCount: photos.length
    });
    
    // For FormData, axios will automatically set Content-Type with boundary
    const response = await api.post('/api/meetings', formData);
    
    console.log('[API] Response received:', {
      success: response.data.success,
      meeting_id: response.data.meeting_id,
      priority_group: response.data.priority_group
    });
    
    if (photos.length > 0) {
      console.log('[API] OCR Processing: Photos were sent to backend');
      console.log('[API] OCR Status: Check backend terminal for OCR extraction logs');
      console.log('[API] Look for logs starting with [OCR] or [DATA_COLLECTION]');
    }
    
    return response.data;
  } catch (error) {
    console.error('[API] Error submitting meeting:', error);
    if (error.response) {
      console.error('[API] Response error:', error.response.data);
      console.error('[API] Status code:', error.response.status);
    }
    throw error;
  }
};

/**
 * Get all meetings grouped by priority (P0, P1, P2)
 */
export const getGroups = async (userId = 'default') => {
  try {
    const response = await api.get(`/api/groups?user_id=${userId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching groups:', error);
    throw error;
  }
};

/**
 * Clear all data from the database
 */
export const clearAllData = async () => {
  try {
    const response = await api.delete('/api/admin/clear-data');
    return response.data;
  } catch (error) {
    console.error('Error clearing data:', error);
    throw error;
  }
};

/**
 * Submit onboarding form data
 */
export const submitOnboarding = async (formData) => {
  try {
    const response = await api.post('/api/onboarding', formData);
    return response.data;
  } catch (error) {
    console.error('Error submitting onboarding:', error);
    throw error;
  }
};

/**
 * Check if user has completed onboarding
 */
export const checkOnboarding = async (userId = 'default') => {
  try {
    const response = await api.get(`/api/onboarding/${userId}`);
    return response.data;
  } catch (error) {
    console.error('Error checking onboarding:', error);
    return { completed: false };
  }
};

/**
 * Reset onboarding for a user
 */
export const resetOnboarding = async (userId = 'default') => {
  try {
    const response = await api.delete(`/api/admin/reset-onboarding/${userId}`);
    return response.data;
  } catch (error) {
    console.error('Error resetting onboarding:', error);
    throw error;
  }
};

/**
 * Extract text from an image using OCR
 */
export const extractOCRText = async (imageFile) => {
  try {
    const formData = new FormData();
    formData.append('image', imageFile);
    
    const response = await api.post('/api/ocr/extract', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  } catch (error) {
    console.error('Error extracting OCR text:', error);
    throw error;
  }
};

export default api;
