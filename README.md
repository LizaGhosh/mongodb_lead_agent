# Networking Assistant - Multi-Agent System

A multi-agent networking assistant that collects meeting data, extracts information, categorizes contacts by priority, and provides conversation summaries. Uses MongoDB Atlas for agent coordination.

## Architecture

- **5 Agents**: Data Collection, Extraction, Summarization, Categorization, Orchestrator
- **MongoDB Atlas**: Agent registry, task queue, context management
- **FastAPI Backend**: REST API for agent coordination
- **React Frontend**: Simple black & white UI

## Quick Start

### Backend

1. Navigate to backend:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```
MONGODB_URI=your_mongodb_connection_string
OPENAI_API_KEY=your_openai_api_key
```

5. Setup database:
```bash
python scripts/setup_database.py
```

6. Run server:
```bash
uvicorn api.main:app --reload
```

Backend runs on `http://localhost:8000`

### Frontend

1. Navigate to frontend:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm start
```

Frontend runs on `http://localhost:3000`

## Usage

1. Submit meeting text in the frontend
2. Backend processes through agents:
   - Data Collection → Extraction → Summarization → Categorization
3. View results grouped by priority (P0, P1, P2)

## API Endpoints

- `POST /api/meetings` - Submit new meeting
- `GET /api/groups` - Get meetings grouped by priority

## Project Structure

```
backend/
  ├── agents/          # Agent implementations
  ├── api/             # FastAPI routes
  ├── database/        # MongoDB connection
  ├── services/        # Shared services
  └── scripts/         # Setup scripts

frontend/
  ├── src/
  │   ├── components/  # React components
  │   └── services/    # API client
```

## Requirements

- Python 3.8+
- Node.js 16+
- MongoDB Atlas account
- OpenAI API key (optional, for AI features)
