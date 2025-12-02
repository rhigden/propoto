# 🚀 Render Deployment Guide - Propoto API

**Quick deployment guide for Render.com**

---

## ✅ Prerequisites

- GitHub repository with your code
- Render.com account (free tier available)
- API keys ready (OpenRouter, Exa, Firecrawl)

---

## 🎯 Method 1: Blueprint Deployment (Recommended)

### Step 1: Push to GitHub

```bash
cd /home/user/newshii
git add propoto/api/render.yaml
git commit -m "Add Render deployment configuration"
git push
```

### Step 2: Deploy via Blueprint

1. Go to https://dashboard.render.com/new/blueprint
2. Click "Connect GitHub" and authorize Render
3. Select your repository
4. Render will detect `propoto/api/render.yaml`
5. Review the configuration and click "Apply"

### Step 3: Set Environment Variables

After the service is created:

1. Go to your service → **Environment** tab
2. Add these **secret** environment variables:

   ```
   OPENROUTER_API_KEY=sk-or-v1-xxx
   AGENT_SERVICE_KEY=your-secret-key (generate a strong random string)
   EXA_API_KEY=xxx
   FIRECRAWL_API_KEY=fc-xxx
   CORS_ORIGINS=https://your-frontend.vercel.app
   ```

   **Note**: 
   - `NEXT_PUBLIC_CONVEX_URL` and `CONVEX_DEPLOYMENT` are already set in `render.yaml`
   - Set `CORS_ORIGINS` after you deploy the frontend to Vercel

3. Click "Save Changes"

### Step 4: Deploy

Render will automatically start deploying. Wait for it to complete.

**Your backend URL will be**: `https://propoto-api.onrender.com` (or your custom name)

---

## 🛠️ Method 2: Manual Setup

### Step 1: Create Web Service

1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Select the repository

### Step 2: Configure Service

- **Name**: `propoto-api`
- **Region**: Choose closest to your users
- **Branch**: `main` (or your default branch)
- **Root Directory**: `propoto/api`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Step 3: Set Environment Variables

Add these environment variables:

```
OPENROUTER_API_KEY=sk-or-v1-xxx
AGENT_SERVICE_KEY=your-secret-key (generate strong random string)
EXA_API_KEY=xxx
FIRECRAWL_API_KEY=fc-xxx
NEXT_PUBLIC_CONVEX_URL=https://giddy-jaguar-382.convex.cloud
CONVEX_DEPLOYMENT=prod:giddy-jaguar-382
CORS_ORIGINS=https://your-frontend.vercel.app
PORT=8000
```

### Step 4: Deploy

Click "Create Web Service" and wait for deployment to complete.

---

## 🔍 Verify Deployment

### 1. Check Health Endpoint

```bash
curl https://propoto-api.onrender.com/health
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
curl -X POST https://propoto-api.onrender.com/agents/proposal/generate \
  -H "x-api-key: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "prospect_name": "Test Company",
    "prospect_url": "https://example.com",
    "pain_points": "Low conversion rates"
  }'
```

---

## ⚙️ Configuration Details

### render.yaml

The `render.yaml` file in `propoto/api/` includes:
- Build and start commands
- Pre-configured Convex URLs
- Environment variable placeholders

### Port Configuration

Render automatically sets the `PORT` environment variable. The app uses:
```python
port = int(os.getenv("PORT", 8000))
```

So it will automatically use Render's assigned port.

---

## 🔒 Security Notes

1. **AGENT_SERVICE_KEY**: Generate a strong random string:
   ```bash
   openssl rand -hex 32
   ```

2. **CORS_ORIGINS**: Update after frontend deployment:
   - Add your Vercel URL: `https://your-app.vercel.app`
   - Or use wildcard for testing: `*` (not recommended for production)

3. **API Keys**: Never commit API keys to Git. Use Render's environment variables.

---

## 📊 Monitoring

### View Logs

1. Go to your service in Render dashboard
2. Click "Logs" tab
3. View real-time logs

### Health Checks

Render automatically monitors your service. If it becomes unhealthy, Render will restart it.

---

## 🐛 Troubleshooting

### Build Fails

- Check logs for Python version issues
- Verify `requirements.txt` is correct
- Ensure root directory is `propoto/api`

### Service Won't Start

- Check start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Verify all environment variables are set
- Check logs for import errors

### 502 Bad Gateway

- Service might be spinning down (free tier)
- Check logs for errors
- Verify health endpoint works: `/health`

### CORS Errors

- Update `CORS_ORIGINS` with your frontend URL
- Restart the service after updating env vars

---

## 💰 Free Tier Limitations

Render's free tier:
- Services spin down after 15 minutes of inactivity
- First request after spin-down takes ~30 seconds
- 750 hours/month free (enough for 24/7 single service)

**Upgrade to paid** for:
- Always-on services
- Custom domains
- Better performance

---

## ✅ Next Steps

After backend is deployed:

1. **Note your backend URL**: `https://propoto-api.onrender.com`
2. **Deploy frontend to Vercel** (see DEPLOY_NOW.md)
3. **Update CORS_ORIGINS** with your Vercel URL
4. **Update frontend env vars** with backend URL
5. **Test end-to-end**

---

*Last Updated: January 2026*

