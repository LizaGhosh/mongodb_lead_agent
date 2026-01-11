# Vercel Deployment Guide

This guide will help you deploy the Networking Assistant application to Vercel.

## Prerequisites

1. A Vercel account (sign up at [vercel.com](https://vercel.com))
2. MongoDB Atlas account with connection string
3. OpenAI API key (optional, for AI features)

## Deployment Steps

### 1. Install Vercel CLI (Optional)

```bash
npm i -g vercel
```

### 2. Set Up Environment Variables

You'll need to set the following environment variables in Vercel:

**Required:**
- `MONGODB_URI` - Your MongoDB Atlas connection string
- `OPENAI_API_KEY` - Your OpenAI API key (optional but recommended)

**Optional:**
- `ALLOWED_ORIGINS` - Comma-separated list of allowed CORS origins (default: `*`)
- `REACT_APP_API_URL` - Frontend API URL (auto-set by Vercel, but can override)

### 3. Deploy via Vercel Dashboard

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your Git repository (GitHub, GitLab, or Bitbucket)
3. Vercel will auto-detect the configuration from `vercel.json`
4. Add your environment variables in the project settings
5. Click "Deploy"

### 4. Deploy via CLI

```bash
# From the project root
vercel

# Follow the prompts:
# - Set up and deploy? Yes
# - Which scope? (select your account)
# - Link to existing project? No (first time) or Yes (updates)
# - Project name? (press enter for default)
# - Directory? (press enter for current directory)
# - Override settings? No

# Set environment variables
vercel env add MONGODB_URI
vercel env add OPENAI_API_KEY

# Deploy to production
vercel --prod
```

### 5. Configure Environment Variables in Vercel Dashboard

1. Go to your project on Vercel
2. Navigate to **Settings** → **Environment Variables**
3. Add the following:
   - `MONGODB_URI`: Your MongoDB connection string
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `ALLOWED_ORIGINS`: Your frontend URL (e.g., `https://your-app.vercel.app`)

### 6. Update Frontend API URL

After deployment, update the frontend to use the Vercel API URL:

1. Go to **Settings** → **Environment Variables**
2. Add `REACT_APP_API_URL` with your Vercel API URL (e.g., `https://your-app.vercel.app/api`)

Or the frontend will automatically use the same domain for API calls.

## Project Structure for Vercel

```
mongodb_lead_agent/
├── api/                    # Serverless function entry point
│   ├── index.py           # FastAPI app wrapper
│   └── requirements.txt   # Python dependencies
├── backend/               # Backend source code
├── frontend/              # React frontend
├── vercel.json            # Vercel configuration
└── .vercelignore          # Files to exclude from deployment
```

## Post-Deployment

### 1. Run Database Setup

After first deployment, you'll need to run the database setup script. You can do this by:

1. Using Vercel's serverless function to run it once
2. Or running it locally with the production MongoDB URI

### 2. Test the Deployment

- Frontend: `https://your-app.vercel.app`
- API Health: `https://your-app.vercel.app/api/health`
- API Root: `https://your-app.vercel.app/api`

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all Python dependencies are in `api/requirements.txt`
2. **CORS Errors**: Set `ALLOWED_ORIGINS` environment variable with your frontend URL
3. **MongoDB Connection**: Verify `MONGODB_URI` is set correctly and MongoDB Atlas allows connections from Vercel IPs
4. **Build Failures**: Check Vercel build logs for specific errors

### Viewing Logs

```bash
# View function logs
vercel logs

# View logs for specific function
vercel logs --follow
```

## Notes

- The backend runs as serverless functions on Vercel
- File logging is disabled in serverless mode (logs go to Vercel console)
- Make sure MongoDB Atlas network access allows Vercel IPs (or use 0.0.0.0/0 for development)
- Cold starts may occur on first request after inactivity
