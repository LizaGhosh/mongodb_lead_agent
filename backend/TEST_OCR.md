# How to Test OCR Functionality

## Quick Test Steps

### 1. Prepare a Test Image
- Take a photo of a business card, badge, or name tag
- Or use any image with text (e.g., screenshot, document)
- Save it on your computer

### 2. Test via Frontend
1. Start the backend server:
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn api.main:app --reload
   ```

2. Start the frontend:
   ```bash
   cd frontend
   npm start
   ```

3. In the frontend:
   - Go to "Submit New Meeting"
   - Click on the photo upload input
   - Select your test image
   - Optionally add some text or record audio
   - Click "Submit Meeting"

4. Check backend logs:
   - You should see: `[OCR] Processing image: ...`
   - Then: `[OCR] Successfully extracted text: X characters`
   - And: `[OCR] Extracted text preview: ...`

### 3. Test via API (curl)

```bash
curl -X POST http://localhost:8000/api/meetings \
  -F "text=Test meeting" \
  -F "location=Test Location" \
  -F "photos=@/path/to/your/image.jpg"
```

Replace `/path/to/your/image.jpg` with your actual image path.

### 4. Check MongoDB

After submission, check the `meetings` collection:
- Look for the meeting document
- Check `raw_data.photos` array
- Each photo should have `text_extracted: true` if OCR worked
- The extracted text should be in the `raw_data.text` field

### 5. Verify in Frontend

- Submit a meeting with a photo
- The extracted text from the photo will be used by:
  - Extraction Agent (to extract name, company, title)
  - Summarization Agent (in the summary)
  - Categorization Agent (for scoring)

## Expected Log Output

When OCR works, you'll see:
```
[DATA_COLLECTION] Processing 1 photo(s)
[DATA_COLLECTION] Extracting text from: photo.jpg
[OCR] Processing image: photo.jpg
[OCR] Successfully extracted text: 156 characters
[OCR] Extracted text preview: John Doe, CTO, TechCorp, email@example.com...
[DATA_COLLECTION] OCR successful for photo.jpg: 156 characters
```

## Troubleshooting

**If OCR fails:**
- Check OpenAI API key is set in `.env`
- Check image format is supported (JPEG, PNG, etc.)
- Check backend logs for error messages
- Verify OpenAI account has Vision API access

**Common issues:**
- Model name: If "gpt-4o" doesn't work, try "gpt-4-turbo"
- Image size: Very large images may need resizing
- API limits: Check OpenAI usage limits

## Test Images You Can Use

1. **Business Card**: Photo of a business card with name, company, title, contact info
2. **Name Badge**: Photo of a conference badge
3. **Screenshot**: Screenshot of LinkedIn profile or contact card
4. **Document**: Any document with text

The OCR will extract all visible text from the image and use it for processing.
