import React, { useState, useRef } from 'react';
import { submitMeeting, extractOCRText } from '../services/api';

/**
 * Component for submitting new meetings with voice recording and photo capture
 */
const MeetingInput = ({ onMeetingSubmitted }) => {
  const [text, setText] = useState('');
  const [location, setLocation] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [parsedInputs, setParsedInputs] = useState(null);
  
  // Voice recording state
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  
  // Photo state
  const [photos, setPhotos] = useState([]); // { file, preview, ocrText, ocrLoading, ocrError }
  const fileInputRef = useRef(null);

  // Voice recording functions
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        setAudioBlob(audioBlob);
        const url = URL.createObjectURL(audioBlob);
        setAudioUrl(url);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error accessing microphone:', error);
      setMessage('Error accessing microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const clearRecording = () => {
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
    }
    setAudioBlob(null);
    setAudioUrl(null);
    audioChunksRef.current = [];
  };

  // Photo capture functions
  const handlePhotoCapture = async (e) => {
    const files = Array.from(e.target.files);
    console.log('[FRONTEND] Photo capture:', files.length, 'file(s) selected');
    
    const newPhotos = files.map((file) => {
      console.log(`[FRONTEND] Photo:`, {
        name: file.name,
        type: file.type,
        size: `${(file.size / 1024).toFixed(2)} KB`
      });
      
      return {
        id: Date.now() + Math.random(), // Unique ID
        file,
        preview: URL.createObjectURL(file),
        ocrText: null,
        ocrLoading: true,
        ocrError: null
      };
    });
    
    // Add photos to state immediately
    setPhotos([...photos, ...newPhotos]);
    console.log('[FRONTEND] Total photos:', photos.length + newPhotos.length);
    
    // Process OCR for each new photo
    newPhotos.forEach(async (photo) => {
      try {
        console.log(`[FRONTEND] Starting OCR for: ${photo.file.name}`);
        const result = await extractOCRText(photo.file);
        
        if (result.success && result.text) {
          console.log(`[FRONTEND] OCR successful for ${photo.file.name}:`, result.text.substring(0, 100));
          
          // Update the photo with OCR text
          setPhotos(prevPhotos => 
            prevPhotos.map(p => 
              p.id === photo.id 
                ? { ...p, ocrText: result.text, ocrLoading: false, ocrError: null }
                : p
            )
          );
        } else {
          console.warn(`[FRONTEND] OCR failed for ${photo.file.name}:`, result.message);
          setPhotos(prevPhotos => 
            prevPhotos.map(p => 
              p.id === photo.id 
                ? { ...p, ocrText: null, ocrLoading: false, ocrError: result.message || 'Failed to extract text' }
                : p
            )
          );
        }
      } catch (error) {
        console.error(`[FRONTEND] OCR error for ${photo.file.name}:`, error);
        setPhotos(prevPhotos => 
          prevPhotos.map(p => 
            p.id === photo.id 
              ? { ...p, ocrText: null, ocrLoading: false, ocrError: 'Error extracting text' }
              : p
          )
        );
      }
    });
  };

  const removePhoto = (id) => {
    const photoToRemove = photos.find(p => p.id === id);
    if (photoToRemove) {
      URL.revokeObjectURL(photoToRemove.preview);
    }
    setPhotos(photos.filter(p => p.id !== id));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!text.trim() && !audioBlob && photos.length === 0) {
      setMessage('Please enter meeting text, record audio, or upload photos');
      return;
    }

    setLoading(true);
    setMessage('');

    // Log submission details
    console.log('[FRONTEND] Submitting meeting with:');
    console.log('  - Text:', text ? `${text.length} characters` : 'None');
    console.log('  - Audio:', audioBlob ? `${(audioBlob.size / 1024).toFixed(2)} KB` : 'None');
    console.log('  - Photos:', photos.length, 'file(s)');
    photos.forEach((photo, index) => {
      console.log(`    Photo ${index + 1}: ${photo.file.name} (${(photo.file.size / 1024).toFixed(2)} KB)`);
    });
    console.log('  - Location:', location || 'None');

    try {
      console.log('[FRONTEND] Sending request to backend...');
      const result = await submitMeeting(text, location || null, audioBlob, photos);
      
      console.log('[FRONTEND] Meeting submission response:', result);
      console.log('[FRONTEND] Meeting ID:', result.meeting_id);
      console.log('[FRONTEND] Person ID:', result.person_id);
      console.log('[FRONTEND] Priority Group:', result.priority_group);
      
      // Store parsed inputs for display
      if (result.parsed_inputs) {
        setParsedInputs({
          ...result.parsed_inputs,
          person: result.person,
          meeting_date: result.meeting_date,
          priority_group: result.priority_group
        });
      }
      
      setMessage(`Meeting processed! Priority: ${result.priority_group}`);
      
      // Clear form after a delay to show parsed inputs
      setTimeout(() => {
        setText('');
        setLocation('');
        clearRecording();
        photos.forEach(photo => {
          URL.revokeObjectURL(photo.preview);
        });
        setPhotos([]);
        setParsedInputs(null);
      }, 5000); // Clear after 5 seconds
      
      // Notify parent component
      if (onMeetingSubmitted) {
        onMeetingSubmitted();
      }
    } catch (error) {
      console.error('[FRONTEND] Error submitting meeting:', error);
      console.error('[FRONTEND] Error details:', error.response?.data || error.message);
      setMessage('Error submitting meeting. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Submit New Meeting</h2>
      <form onSubmit={handleSubmit} style={styles.form}>
        <div style={styles.inputGroup}>
          <label style={styles.label}>Meeting Text (optional)</label>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Enter conversation transcript or meeting notes..."
            style={styles.textarea}
            rows={4}
          />
        </div>

        {/* Voice Recording Section */}
        <div style={styles.inputGroup}>
          <label style={styles.label}>Voice Recording</label>
          <div style={styles.recordingControls}>
            {!isRecording && !audioBlob && (
              <button
                type="button"
                onClick={startRecording}
                style={styles.recordButton}
              >
                🎤 Start Recording
              </button>
            )}
            {isRecording && (
              <button
                type="button"
                onClick={stopRecording}
                style={{ ...styles.recordButton, ...styles.stopButton }}
              >
                ⏹️ Stop Recording
              </button>
            )}
            {audioBlob && (
              <div style={styles.audioPreview}>
                <audio controls src={audioUrl} style={styles.audioPlayer} />
                <button
                  type="button"
                  onClick={clearRecording}
                  style={styles.clearButton}
                >
                  ✕ Clear
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Photo Capture Section */}
        <div style={styles.inputGroup}>
          <label style={styles.label}>Photos (Badge, Business Card, etc.)</label>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            capture="environment"
            multiple
            onChange={handlePhotoCapture}
            style={styles.fileInput}
          />
          {photos.length > 0 && (
            <div>
              <p style={styles.photoInfo}>
                {photos.length} photo(s) selected. OCR will extract text from these images.
              </p>
              <div style={styles.photosPreview}>
                {photos.map((photo) => (
                  <div key={photo.id} style={styles.photoItem}>
                    <img src={photo.preview} alt={`Preview`} style={styles.photoPreview} />
                    <div style={styles.photoDetails}>
                      <p style={styles.photoName}>{photo.file.name}</p>
                      <p style={styles.photoSize}>
                        {(photo.file.size / 1024).toFixed(2)} KB
                      </p>
                    </div>
                    <button
                      type="button"
                      onClick={() => removePhoto(photo.id)}
                      style={styles.removePhotoButton}
                    >
                      ✕
                    </button>
                    {/* OCR Text Display */}
                    <div style={styles.ocrTextContainer}>
                      {photo.ocrLoading && (
                        <div style={styles.ocrLoading}>🔄 Extracting text...</div>
                      )}
                      {photo.ocrError && (
                        <div style={styles.ocrError}>❌ {photo.ocrError}</div>
                      )}
                      {photo.ocrText && (
                        <div style={styles.ocrText}>
                          <div style={styles.ocrTextHeader}>📄 Extracted Text:</div>
                          <div style={styles.ocrTextContent}>{photo.ocrText}</div>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
              <p style={styles.ocrNote}>
                📷 OCR will process these images after submission. Check browser console and backend logs for extraction status.
              </p>
            </div>
          )}
        </div>
        
        <div style={styles.inputGroup}>
          <label style={styles.label}>Location (optional)</label>
          <input
            type="text"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="e.g., Tech Conference 2024"
            style={styles.input}
          />
        </div>

        <button
          type="submit"
          disabled={loading || (!text.trim() && !audioBlob && photos.length === 0)}
          style={loading || (!text.trim() && !audioBlob && photos.length === 0) 
            ? { ...styles.button, ...styles.buttonDisabled } 
            : styles.button}
        >
          {loading ? 'Processing (OCR in progress)...' : 'Submit Meeting'}
        </button>

        {loading && photos.length > 0 && (
          <div style={styles.processingNote}>
            <p>🔄 Processing {photos.length} photo(s) with OCR...</p>
            <p style={styles.processingSubtext}>Check browser console (F12) and backend logs for OCR extraction details</p>
          </div>
        )}

        {message && (
          <div style={styles.message}>
            {message}
          </div>
        )}
      </form>

      {/* Display Parsed Inputs */}
      {parsedInputs && (
        <div style={styles.parsedInputsContainer}>
          <h3 style={styles.parsedInputsTitle}>📋 Parsed Inputs</h3>
          
          {parsedInputs.person && (
            <div style={styles.parsedSection}>
              <h4 style={styles.sectionTitle}>👤 Person Information</h4>
              <div style={styles.parsedContent}>
                <p><strong>Name:</strong> {parsedInputs.person.name || 'Not extracted yet'}</p>
                <p><strong>Company:</strong> {parsedInputs.person.company || 'Not extracted yet'}</p>
                <p><strong>Job Title:</strong> {parsedInputs.person.job_title || 'Not extracted yet'}</p>
              </div>
            </div>
          )}

          {parsedInputs.meeting_text && (
            <div style={styles.parsedSection}>
              <h4 style={styles.sectionTitle}>📝 Meeting Notes</h4>
              <div style={styles.parsedContent}>
                <pre style={styles.preText}>{parsedInputs.meeting_text}</pre>
              </div>
            </div>
          )}

          {parsedInputs.transcription && (
            <div style={styles.parsedSection}>
              <h4 style={styles.sectionTitle}>🎤 Voice Transcription</h4>
              <div style={styles.parsedContent}>
                <pre style={styles.preText}>{parsedInputs.transcription}</pre>
              </div>
            </div>
          )}

          {parsedInputs.ocr_texts && parsedInputs.ocr_texts.length > 0 && (
            <div style={styles.parsedSection}>
              <h4 style={styles.sectionTitle}>📷 OCR Extracted Text</h4>
              {parsedInputs.ocr_texts.map((ocr, index) => (
                <div key={index} style={styles.parsedContent}>
                  <p style={styles.ocrFileName}><strong>From:</strong> {ocr.filename}</p>
                  <pre style={styles.preText}>{ocr.text}</pre>
                </div>
              ))}
            </div>
          )}

          {parsedInputs.location && (
            <div style={styles.parsedSection}>
              <h4 style={styles.sectionTitle}>📍 Location</h4>
              <div style={styles.parsedContent}>
                <p>{parsedInputs.location}</p>
              </div>
            </div>
          )}

          {parsedInputs.meeting_date && (
            <div style={styles.parsedSection}>
              <h4 style={styles.sectionTitle}>🕐 Meeting Timestamp</h4>
              <div style={styles.parsedContent}>
                <p>{new Date(parsedInputs.meeting_date).toLocaleString()}</p>
              </div>
            </div>
          )}

          <div style={styles.parsedSection}>
            <h4 style={styles.sectionTitle}>🏷️ Priority Group</h4>
            <div style={styles.parsedContent}>
              <p style={styles.priorityBadge}>{parsedInputs.priority_group}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const styles = {
  container: {
    maxWidth: '800px',
    margin: '0 auto',
    padding: '20px',
    border: '1px solid #000',
    borderRadius: '4px',
    marginBottom: '30px',
  },
  title: {
    marginBottom: '20px',
    fontSize: '24px',
    fontWeight: 'bold',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
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
  textarea: {
    width: '100%',
    padding: '12px',
    border: '1px solid #000',
    borderRadius: '4px',
    fontSize: '14px',
    fontFamily: 'inherit',
    resize: 'vertical',
  },
  input: {
    width: '100%',
    padding: '12px',
    border: '1px solid #000',
    borderRadius: '4px',
    fontSize: '14px',
    fontFamily: 'inherit',
  },
  button: {
    padding: '12px 24px',
    backgroundColor: '#000',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    fontSize: '16px',
    fontWeight: '500',
    cursor: 'pointer',
    marginTop: '10px',
  },
  buttonDisabled: {
    backgroundColor: '#666',
    cursor: 'not-allowed',
  },
  message: {
    marginTop: '15px',
    padding: '10px',
    backgroundColor: '#f5f5f5',
    border: '1px solid #000',
    borderRadius: '4px',
    fontSize: '14px',
  },
  recordingControls: {
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
  },
  recordButton: {
    padding: '10px 20px',
    backgroundColor: '#000',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    fontSize: '14px',
    cursor: 'pointer',
    width: 'fit-content',
  },
  stopButton: {
    backgroundColor: '#d32f2f',
  },
  audioPreview: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    padding: '10px',
    border: '1px solid #000',
    borderRadius: '4px',
    backgroundColor: '#f5f5f5',
  },
  audioPlayer: {
    flex: 1,
    maxWidth: '400px',
  },
  clearButton: {
    padding: '5px 10px',
    backgroundColor: '#666',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '12px',
  },
  fileInput: {
    width: '100%',
    padding: '10px',
    border: '1px solid #000',
    borderRadius: '4px',
    fontSize: '14px',
    marginBottom: '10px',
  },
  photosPreview: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '10px',
    marginTop: '10px',
  },
  photoItem: {
    position: 'relative',
    width: '200px',
    minHeight: '150px',
    marginBottom: '20px',
  },
  photoPreview: {
    width: '100%',
    height: '100%',
    objectFit: 'cover',
    border: '1px solid #000',
    borderRadius: '4px',
  },
  removePhotoButton: {
    position: 'absolute',
    top: '5px',
    right: '5px',
    backgroundColor: '#d32f2f',
    color: '#fff',
    border: 'none',
    borderRadius: '50%',
    width: '24px',
    height: '24px',
    cursor: 'pointer',
    fontSize: '14px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  photoInfo: {
    fontSize: '14px',
    color: '#666',
    marginBottom: '10px',
    fontStyle: 'italic',
  },
  photoDetails: {
    position: 'absolute',
    bottom: '0',
    left: '0',
    right: '0',
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    color: '#fff',
    padding: '5px',
    fontSize: '11px',
  },
  photoName: {
    margin: '2px 0',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
  },
  photoSize: {
    margin: '2px 0',
    fontSize: '10px',
    opacity: 0.8,
  },
  ocrNote: {
    marginTop: '10px',
    padding: '10px',
    backgroundColor: '#f0f0f0',
    border: '1px solid #000',
    borderRadius: '4px',
    fontSize: '12px',
    color: '#333',
  },
  processingNote: {
    marginTop: '15px',
    padding: '15px',
    backgroundColor: '#fff3cd',
    border: '1px solid #ffc107',
    borderRadius: '4px',
    fontSize: '14px',
  },
  processingSubtext: {
    marginTop: '5px',
    fontSize: '12px',
    color: '#666',
    fontStyle: 'italic',
  },
  ocrTextContainer: {
    marginTop: '10px',
    width: '100%',
  },
  ocrLoading: {
    padding: '8px',
    backgroundColor: '#fff3cd',
    border: '1px solid #ffc107',
    borderRadius: '4px',
    fontSize: '12px',
    color: '#856404',
  },
  ocrError: {
    padding: '8px',
    backgroundColor: '#f8d7da',
    border: '1px solid #f5c6cb',
    borderRadius: '4px',
    fontSize: '12px',
    color: '#721c24',
  },
  ocrText: {
    marginTop: '5px',
    padding: '10px',
    backgroundColor: '#f5f5f5',
    border: '1px solid #000',
    borderRadius: '4px',
    fontSize: '12px',
    maxHeight: '200px',
    overflowY: 'auto',
  },
  ocrTextHeader: {
    fontWeight: 'bold',
    marginBottom: '5px',
    color: '#000',
  },
  ocrTextContent: {
    color: '#333',
    whiteSpace: 'pre-wrap',
    wordBreak: 'break-word',
    lineHeight: '1.4',
  },
  parsedInputsContainer: {
    marginTop: '30px',
    padding: '20px',
    border: '2px solid #000',
    borderRadius: '4px',
    backgroundColor: '#f9f9f9',
  },
  parsedInputsTitle: {
    fontSize: '20px',
    fontWeight: 'bold',
    marginBottom: '20px',
    borderBottom: '2px solid #000',
    paddingBottom: '10px',
  },
  parsedSection: {
    marginBottom: '25px',
    padding: '15px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    backgroundColor: '#fff',
  },
  sectionTitle: {
    fontSize: '16px',
    fontWeight: 'bold',
    marginBottom: '10px',
    color: '#000',
  },
  parsedContent: {
    fontSize: '14px',
    color: '#333',
    lineHeight: '1.6',
  },
  preText: {
    whiteSpace: 'pre-wrap',
    wordBreak: 'break-word',
    fontFamily: 'inherit',
    fontSize: '14px',
    margin: 0,
    padding: '10px',
    backgroundColor: '#f5f5f5',
    border: '1px solid #ddd',
    borderRadius: '4px',
  },
  ocrFileName: {
    fontWeight: 'bold',
    marginBottom: '5px',
    color: '#666',
  },
  priorityBadge: {
    display: 'inline-block',
    padding: '5px 15px',
    backgroundColor: '#000',
    color: '#fff',
    borderRadius: '4px',
    fontWeight: 'bold',
    fontSize: '16px',
  },
};

export default MeetingInput;
