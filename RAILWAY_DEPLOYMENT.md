# Railway Deployment Guide

This guide will help you deploy the Networking Assistant application to Railway.

## Prerequisites

1. A Railway account (sign up at [railway.app](https://railway.app))
2. MongoDB Atlas account with connection string
3. OpenAI API key (optional, for AI features)
4. GitHub account (for connecting repository)

## Deployment Steps

### Option 1: Deploy via Railway Dashboard (Recommended)

1. **Go to Railway Dashboard**
   - Visit [railway.app](https://railway.app)
   - Sign in with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your `mongodb_lead_agent` repository
   - Railway will auto-detect the project structure

3. **Configure Backend Service**
   - Railway should auto-detect the backend as a Python service
   - If not, add a new service and select the `backend` directory
   - Set the root directory to `backend`
   - Railway will automatically:
     - Detect `requirements.txt`
     - Install Python dependencies
     - Run the service using the Procfile

4. **Set Environment Variables**
   - Go to your service → Variables tab
   - Add the following environment variables:
     - `MONGODB_URI` - Your MongoDB Atlas connection string
     - `OPENAI_API_KEY` - Your OpenAI API key
     - `ALLOWED_ORIGINS` - Your frontend URL (optional, defaults to `*`)
     - `PORT` - Railway sets this automatically, but you can override if needed

5. **Deploy Frontend (Separate Service)**
   - Add a new service for the frontend
   - Set root directory to `frontend`
   - Railway will detect it as a Node.js service
   - Add build command: `npm install && npm run build`
   - Add start command: `npx serve -s build -l $PORT`
   - Or use Railway's static site deployment

6. **Generate Domain**
   - Railway automatically provides a domain
   - Go to Settings → Generate Domain
   - Copy the domain URL

7. **Update Frontend API URL**
   - In Railway, go to your frontend service
   - Add environment variable:
     - `REACT_APP_API_URL` - Your backend Railway URL (e.g., `https://your-backend.railway.app`)

### Option 2: Deploy via Railway CLI

1. **Install Railway CLI**
   ```bash
   npm i -g @railway/cli
   ```

2. **Login to Railway**
   ```bash
   railway login
   ```

3. **Initialize Project**
   ```bash
   cd mongodb_lead_agent
   railway init
   ```

4. **Link to Existing Project (or create new)**
   ```bash
   railway link
   ```

5. **Set Environment Variables**
   ```bash
   railway variables set MONGODB_URI=your_mongodb_connection_string
   railway variables set OPENAI_API_KEY=your_openai_api_key
   ```

6. **Deploy Backend**
   ```bash
   cd backend
   railway up
   ```

7. **Deploy Frontend (in new terminal)**
   ```bash
   cd frontend
   railway up
   ```

## Project Structure for Railway

Railway will deploy this as two separate services:

```
mongodb_lead_agent/
├── backend/              # Backend service (Python/FastAPI)
│   ├── Procfile         # Railway start command
│   ├── requirements.txt # Python dependencies
│   └── api/main.py      # FastAPI app
│
└── frontend/            # Frontend service (React)
    ├── package.json     # Node.js dependencies
    └── build/           # Built static files (after build)
```

## Configuration Files

### Backend Service
- **Root Directory**: `backend`
- **Build Command**: (Auto-detected from requirements.txt)
- **Start Command**: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
- **Port**: Railway sets `$PORT` automatically

### Frontend Service
- **Root Directory**: `frontend`
- **Build Command**: `npm install && npm run build`
- **Start Command**: `npx serve -s build -l $PORT` (or use Railway static hosting)
- **Environment Variables**: `REACT_APP_API_URL` (backend URL)

## Environment Variables

### Backend Service
- `MONGODB_URI` (Required) - MongoDB Atlas connection string
- `OPENAI_API_KEY` (Required) - OpenAI API key
- `ALLOWED_ORIGINS` (Optional) - Comma-separated CORS origins
- `PORT` (Auto-set by Railway) - Server port

### Frontend Service
- `REACT_APP_API_URL` (Required) - Backend API URL
- `PORT` (Auto-set by Railway) - Server port

## Post-Deployment

### 1. Run Database Setup

After deployment, you'll need to run the database setup script. You can do this by:

**Option A: Using Railway CLI**
```bash
cd backend
railway run python scripts/setup_database.py
```

**Option B: Using Railway Shell**
- Go to your backend service in Railway dashboard
- Click on the service → Open Shell
- Run: `python scripts/setup_database.py`

### 2. Test the Deployment

- Backend API: `https://your-backend.railway.app/api/health`
- Frontend: `https://your-frontend.railway.app`

### 3. Update CORS Settings

If your frontend and backend are on different domains, update `ALLOWED_ORIGINS` in backend environment variables with your frontend URL.

## Railway-Specific Features

### Custom Domains
- Go to Settings → Domains
- Add your custom domain
- Railway will provide DNS configuration

### Environment Variables
- Set per-service or project-wide
- Use Railway dashboard or CLI
- Secrets are encrypted

### Logs
- View real-time logs in Railway dashboard
- Or use CLI: `railway logs`

### Monitoring
- Railway provides built-in monitoring
- View metrics in the dashboard

## Troubleshooting

### Common Issues

1. **Port Binding Error**
   - Make sure your app uses `$PORT` environment variable
   - Railway sets this automatically

2. **Build Failures**
   - Check Railway logs for specific errors
   - Ensure all dependencies are in `requirements.txt` or `package.json`

3. **MongoDB Connection Issues**
   - Verify `MONGODB_URI` is set correctly
   - Ensure MongoDB Atlas allows connections from Railway IPs (or use 0.0.0.0/0)

4. **CORS Errors**
   - Set `ALLOWED_ORIGINS` environment variable with your frontend URL
   - Or set to `*` for development

5. **Frontend Can't Reach Backend**
   - Set `REACT_APP_API_URL` in frontend service to your backend Railway URL
   - Ensure backend service is running

### Viewing Logs

```bash
# View backend logs
railway logs --service backend

# View frontend logs
railway logs --service frontend

# Follow logs in real-time
railway logs --follow
```

## Cost Considerations

- Railway offers a free tier with $5 credit monthly
- Pay-as-you-go pricing after free tier
- Check [railway.app/pricing](https://railway.app/pricing) for current rates

## Advantages of Railway

- ✅ Simple deployment process
- ✅ Automatic HTTPS
- ✅ Built-in monitoring
- ✅ Easy environment variable management
- ✅ Support for multiple services
- ✅ Custom domains
- ✅ No cold starts (unlike serverless)

## Migration from Vercel

If migrating from Vercel:

1. Remove Vercel-specific files (optional):
   - `vercel.json`
   - `api/index.py` (Vercel serverless entry point)
   - `api/requirements.txt`

2. Update environment variables in Railway

3. Update frontend `REACT_APP_API_URL` to Railway backend URL

4. Redeploy both services
