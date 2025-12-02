# 🚀 Propoto Production Deployment - Quick Guide

**Status**: Convex deployed ✅ | Backend & Frontend pending

---

## ✅ Step 1: Convex - COMPLETE

**Production URL**: `https://giddy-jaguar-382.convex.cloud`

**Action Required**: Update your environment variables:
```bash
NEXT_PUBLIC_CONVEX_URL=https://giddy-jaguar-382.convex.cloud
CONVEX_DEPLOYMENT=prod:giddy-jaguar-382
```

---

## 🔧 Step 2: Deploy Backend API to Render

### Method 1: Using Render Blueprint (Easiest)

1. **Push to GitHub** (if not already):
   ```bash
   git add .
   git commit -m "Add Render configuration"
   git push
   ```

2. **Deploy via Blueprint**:
   - Go to https://dashboard.render.com/new/blueprint
   - Connect your GitHub repository
   - Render will detect `propoto/api/render.yaml`
   - Click "Apply" to create the service

3. **Set Secret Environment Variables** in Render Dashboard:
   - Go to your service → Environment
   - Add these variables (click "Add Environment Variable"):
     ```
     OPENROUTER_API_KEY=sk-or-v1-xxx
     AGENT_SERVICE_KEY=your-secret-key (generate a strong random string)
     EXA_API_KEY=xxx
     FIRECRAWL_API_KEY=fc-xxx
     CORS_ORIGINS=https://your-frontend-domain.vercel.app
     ```
   - Note: `NEXT_PUBLIC_CONVEX_URL` and `CONVEX_DEPLOYMENT` are already set in render.yaml

4. **Deploy**: Render will automatically deploy after you set the variables

### Method 2: Manual Setup

1. Go to https://render.com and create account/login
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `propoto-api`
   - **Root Directory**: `propoto/api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. **Set Environment Variables**:
   ```
   OPENROUTER_API_KEY=sk-or-v1-xxx
   AGENT_SERVICE_KEY=your-secret-key (generate strong random string)
   EXA_API_KEY=xxx
   FIRECRAWL_API_KEY=fc-xxx
   NEXT_PUBLIC_CONVEX_URL=https://giddy-jaguar-382.convex.cloud
   CONVEX_DEPLOYMENT=prod:giddy-jaguar-382
   CORS_ORIGINS=https://your-frontend-domain.vercel.app
   PORT=8000
   ```
6. Click "Create Web Service" to deploy

### Get Your Backend URL

After deployment, Render will provide a URL like:
- `https://propoto-api.onrender.com` (free tier)
- Or your custom domain if configured

**Important**: Update `CORS_ORIGINS` with your actual frontend URL after Vercel deployment.

---

### Alternative: Railway or Fly.io

**Railway**:
```bash
cd propoto/api
npm i -g @railway/cli
railway login
railway init
railway up
# Then set env vars in Railway dashboard
```

**Fly.io**:
```bash
cd propoto/api
fly launch
fly secrets set OPENROUTER_API_KEY=sk-or-v1-xxx
fly secrets set AGENT_SERVICE_KEY=your-secret-key
fly secrets set EXA_API_KEY=xxx
fly secrets set FIRECRAWL_API_KEY=fc-xxx
fly secrets set NEXT_PUBLIC_CONVEX_URL=https://giddy-jaguar-382.convex.cloud
fly secrets set CONVEX_DEPLOYMENT=prod:giddy-jaguar-382
fly secrets set CORS_ORIGINS=https://your-frontend-domain.vercel.app
fly deploy
```

---

## 🌐 Step 3: Deploy Frontend to Vercel

1. **Login to Vercel** (if not already):
   ```bash
   cd propoto/web
   vercel login
   ```

2. **Deploy**:
   ```bash
   vercel --prod
   ```

3. **Set Environment Variables** in Vercel Dashboard:
   - Go to your project → Settings → Environment Variables
   - Add:
     ```
     NEXT_PUBLIC_CONVEX_URL=https://giddy-jaguar-382.convex.cloud
     NEXT_PUBLIC_API_URL=https://propoto-api.onrender.com (or your Render URL)
     AGENT_SERVICE_KEY=your-secret-key (same as backend)
     ```

4. **Redeploy** if you added env vars after first deploy:
   ```bash
   vercel --prod
   ```

---

## 🧪 Step 4: Test Production

### 1. Health Check
```bash
curl https://propoto-api.onrender.com/health
# Expected: {"status": "healthy", "environment": {...}}
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

### 3. Test Frontend
- Visit your Vercel URL
- Try generating a proposal
- Verify it saves to Convex

---

## 📝 Environment Variables Summary

### Backend (Render)
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

### Frontend (Vercel)
```
NEXT_PUBLIC_CONVEX_URL=https://giddy-jaguar-382.convex.cloud
NEXT_PUBLIC_API_URL=https://propoto-api.onrender.com
AGENT_SERVICE_KEY=your-secret-key (server-side only)
```

---

## ✅ Post-Deployment Checklist

- [ ] Backend health endpoint returns 200
- [ ] Frontend loads without errors
- [ ] Proposal generation works
- [ ] Knowledge ingestion works (Firecrawl)
- [ ] Lead discovery works (Exa)
- [ ] Multi-tenancy isolation verified
- [ ] CORS configured correctly
- [ ] Environment variables set in all platforms

---

## 🎉 You're Live!

Once all steps are complete, your Propoto app will be running in production!

**Production URLs:**
- Frontend: `https://your-app.vercel.app`
- Backend: `https://propoto-api.onrender.com` (or your custom Render domain)
- Convex: `https://giddy-jaguar-382.convex.cloud`

---

*Last Updated: January 2026*

