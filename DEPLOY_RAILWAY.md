# 🚀 Deploy to Railway - Quick Guide

**Free Tier**: $5/month credit (~500 hours of uptime)

---

## Step 1: Install Railway CLI

```bash
npm install -g @railway/cli
```

Or using curl:
```bash
bash <(curl -fsSL cli.new)
```

---

## Step 2: Login

```bash
railway login
```

This will open your browser to authenticate.

---

## Step 3: Initialize and Deploy

```bash
cd /home/user/newshii/propoto/api

# Initialize Railway project
railway init

# Link to a new project
railway link

# Deploy
railway up
```

---

## Step 4: Set Environment Variables

### Option 1: Using CLI

```bash
railway variables set OPENROUTER_API_KEY="sk-or-v1-xxx"
railway variables set AGENT_SERVICE_KEY="your-secret-key"
railway variables set EXA_API_KEY="xxx"
railway variables set FIRECRAWL_API_KEY="fc-xxx"
railway variables set NEXT_PUBLIC_CONVEX_URL="https://giddy-jaguar-382.convex.cloud"
railway variables set CONVEX_DEPLOYMENT="prod:giddy-jaguar-382"
railway variables set CORS_ORIGINS="https://your-frontend.vercel.app"
railway variables set PORT="8000"
```

### Option 2: Using Dashboard

1. Go to https://railway.app/dashboard
2. Select your project
3. Click "Variables" tab
4. Add each environment variable:
   - `OPENROUTER_API_KEY`
   - `AGENT_SERVICE_KEY`
   - `EXA_API_KEY`
   - `FIRECRAWL_API_KEY`
   - `NEXT_PUBLIC_CONVEX_URL` = `https://giddy-jaguar-382.convex.cloud`
   - `CONVEX_DEPLOYMENT` = `prod:giddy-jaguar-382`
   - `CORS_ORIGINS` = `https://your-frontend.vercel.app`
   - `PORT` = `8000`

---

## Step 5: Generate Domain

```bash
railway domain
```

Or in the dashboard:
1. Go to your service → Settings
2. Click "Generate Domain"
3. Your API will be at: `https://propoto-api-production.up.railway.app` (or similar)

---

## Alternative: Deploy from GitHub

1. **Push your code to GitHub** (we already have it ready)
2. Go to https://railway.app/new
3. Click "Deploy from GitHub repo"
4. Select `rhigden/propoto`
5. Set root directory to: `propoto/api`
6. Set environment variables in the dashboard
7. Deploy!

---

## Manage Your Deployment

```bash
# View logs
railway logs

# Open in browser
railway open

# Check status
railway status

# Run commands in Railway environment
railway run python --version

# Link to existing project
railway link [projectId]

# Redeploy
railway up
```

---

## Environment Variables Reference

### Required (Keep Secret)
```bash
OPENROUTER_API_KEY=sk-or-v1-xxx
AGENT_SERVICE_KEY=your-secret-key
EXA_API_KEY=xxx
FIRECRAWL_API_KEY=fc-xxx
CORS_ORIGINS=https://your-frontend.vercel.app
```

### Pre-configured (Public)
```bash
NEXT_PUBLIC_CONVEX_URL=https://giddy-jaguar-382.convex.cloud
CONVEX_DEPLOYMENT=prod:giddy-jaguar-382
PORT=8000
```

---

## Cost & Free Tier

**$5/month credit** includes:
- ~500 hours of execution time
- 100GB bandwidth
- 512MB RAM per service
- 1GB disk space

**Tips to maximize free tier:**
- Set sleep schedule (Railway can pause when not in use)
- Monitor usage in dashboard
- Optimize cold starts

---

## Troubleshooting

### Build Fails
- Check `railway.json` is in `propoto/api/`
- Verify `requirements.txt` is correct
- Check logs: `railway logs`

### Service Won't Start
- Verify start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Check environment variables are set
- Review logs for Python errors

### 502 Bad Gateway
- Service might be deploying (wait 1-2 min)
- Check health endpoint: `curl https://your-app.railway.app/health`
- Verify PORT environment variable is set

---

## Testing Your Deployment

### 1. Health Check
```bash
curl https://your-app.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "environment": {
    "openrouter": true,
    "exa": true,
    "firecrawl": true,
    "convex": true
  }
}
```

### 2. Test Proposal Generation
```bash
curl -X POST https://your-app.railway.app/agents/proposal/generate \
  -H "x-api-key: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "prospect_name": "Test Company",
    "prospect_url": "https://example.com",
    "pain_points": "Low conversion rates"
  }'
```

---

## Next Steps

After deploying backend:

1. **Note your Railway URL** (e.g., `https://propoto-api-production.up.railway.app`)
2. **Update CORS_ORIGINS** with your frontend URL when you deploy it
3. **Deploy frontend to Vercel** with `NEXT_PUBLIC_API_URL` set to your Railway URL
4. **Test end-to-end** functionality

---

*Last Updated: January 2026*

