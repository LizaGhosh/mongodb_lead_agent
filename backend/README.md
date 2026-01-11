# Networking Assistant Backend

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
```

Then edit `.env` and add your credentials:
```
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
OPENAI_API_KEY=your_openai_api_key
```

**Important:** 
- Get your MongoDB connection string from [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
- Get your OpenAI API key from [OpenAI Platform](https://platform.openai.com/api-keys)
- The app will show clear error messages if MongoDB connection fails

3. Setup database:
```bash
python scripts/setup_database.py
```

4. Run server:
```bash
uvicorn api.main:app --reload
```

API will be available at `http://localhost:8000`
