# 🚀 Propoto Production Deployment Guide

**Status**: Simplified to Exa + Firecrawl only (Gamma & Mem0 removed)  
**Last Updated**: January 2026

---

## 📋 Pre-Deployment Checklist

- [x] Remove Gamma integration (presentation generation disabled)
- [x] Remove Mem0 integration (brand memory disabled)
- [x] Keep Exa (lead discovery) and Firecrawl (web scraping)
- [x] Dockerfile created for backend
- [ ] Frontend deployment configured
- [ ] Backend deployment configured
- [ ] Environment variables set
- [ ] Convex production deployment
- [ ] Domain configured

---

## 🏗️ Architecture Overview

**Simplified Stack:**
- **Frontend**: Next.js 15 (Vercel)
- **Backend**: FastAPI (Railway/Render/Fly.io)
- **Database**: Convex (production deployment)
- **External Services**: OpenRouter (LLM), Exa (leads), Firecrawl (scraping)

**Removed Services:**
- ❌ Gamma API (presentation generation)
- ❌ Mem0 (brand memory)

---

## 🔧 Backend Deployment

### Option 1: Railway (Recommended)

1. **Create Railway Project**
   ```bash
   # Install Railway CLI
   npm i -g @railway/cli
   railway login
   ```

2. **Deploy from Dockerfile**
   ```bash
   cd propoto/api
   railway init
   railway up
   ```

3. **Set Environment Variables** (Railway Dashboard → Variables)
   ```
   OPENROUTER_API_KEY=sk-or-v1-xxx
   AGENT_SERVICE_KEY=your-secret-key
   EXA_API_KEY=xxx
   FIRECRAWL_API_KEY=fc-xxx
   NEXT_PUBLIC_CONVEX_URL=https://xxx.convex.cloud
   CONVEX_DEPLOYMENT=xxx
   CORS_ORIGINS=https://yourdomain.com
   PORT=8000
   ```

### Option 2: Render

1. **Create Web Service** (Render Dashboard)
2. **Connect GitHub Repository**
3. **Build Settings**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. **Set Environment Variables** (same as Railway)

### Option 3: Fly.io

```bash
cd propoto/api
fly launch
fly secrets set OPENROUTER_API_KEY=sk-or-v1-xxx
fly secrets set AGENT_SERVICE_KEY=your-secret-key
# ... set other vars
fly deploy
```

### Docker Build (Local Testing)

```bash
cd propoto/api
docker build -t propoto-api .
docker run -p 8000:8000 --env-file .env propoto-api
```

---

## 🌐 Frontend Deployment (Vercel)

1. **Connect GitHub Repository** to Vercel
2. **Configure Build Settings**:
   - Framework Preset: Next.js
   - Root Directory: `propoto/web`
   - Build Command: `npm run build`
   - Output Directory: `.next`

3. **Environment Variables** (Vercel Dashboard → Settings → Environment Variables):
   ```
   NEXT_PUBLIC_CONVEX_URL=https://xxx.convex.cloud
   NEXT_PUBLIC_API_URL=https://api.yourdomain.com
   AGENT_SERVICE_KEY=your-secret-key (server-side only)
   ```

4. **Deploy**
   ```bash
   # Or push to main branch (auto-deploy)
   vercel --prod
   ```

---

## 🗄️ Convex Production Deployment

```bash
cd propoto/web
npx convex deploy --prod
```

**Verify:**
- Production deployment URL matches `NEXT_PUBLIC_CONVEX_URL`
- Schema indexes are created
- Multi-tenancy (`orgId` isolation) is working

---

## 🔒 Security Checklist

- [ ] Rotate `AGENT_SERVICE_KEY` for production (use strong random string)
- [ ] Set `CORS_ORIGINS` to production domain only
- [ ] Verify `orgId` isolation in Convex queries
- [ ] Review rate limits (`slowapi` config)
- [ ] Enable HTTPS only (Vercel/Railway do this automatically)
- [ ] Review environment variable access (no secrets in frontend)

---

## 🧪 Post-Deployment Testing

### 1. Health Check
```bash
curl https://api.yourdomain.com/health
# Expected: {"status": "healthy", "environment": {"openrouter": true, "exa": true, "firecrawl": true, "convex": true}}
```

### 2. Proposal Generation
```bash
curl -X POST https://api.yourdomain.com/agents/proposal/generate \
  -H "x-api-key: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "prospect_name": "Test Company",
    "prospect_url": "https://example.com",
    "pain_points": "Low conversion rates"
  }'
```

### 3. Knowledge Ingestion (Firecrawl)
```bash
curl -X POST https://api.yourdomain.com/agents/knowledge/ingest \
  -H "x-api-key: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

### 4. Lead Discovery (Exa)
```bash
curl -X POST https://api.yourdomain.com/agents/sales/find_leads \
  -H "x-api-key: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "marketing agencies in San Francisco"}'
```

---

## 📊 Monitoring

### Backend Logs
- **Railway**: Dashboard → Deployments → Logs
- **Render**: Dashboard → Logs
- **Fly.io**: `fly logs`

### Frontend Logs
- **Vercel**: Dashboard → Deployments → Logs

### Health Monitoring
Set up uptime monitoring (UptimeRobot, Better Uptime) to ping `/health` endpoint.

---

## 🐛 Troubleshooting

### Backend Issues

**502 Bad Gateway**
- Check backend is running: `curl https://api.yourdomain.com/health`
- Verify environment variables are set
- Check logs for errors

**403 Invalid API Key**
- Verify `AGENT_SERVICE_KEY` matches in frontend and backend
- Check `x-api-key` header is being sent

**500 Internal Server Error**
- Check OpenRouter API key is valid
- Verify Exa/Firecrawl API keys are set
- Review backend logs for stack traces

### Frontend Issues

**API Connection Failed**
- Verify `NEXT_PUBLIC_API_URL` is correct
- Check CORS settings allow frontend domain
- Verify backend is accessible

**Convex Connection Failed**
- Verify `NEXT_PUBLIC_CONVEX_URL` is production deployment
- Check Convex deployment is active

---

## 📝 Environment Variables Reference

### Backend (Required)
```bash
OPENROUTER_API_KEY      # LLM gateway (required)
AGENT_SERVICE_KEY       # API authentication (required)
EXA_API_KEY            # Lead discovery (required)
FIRECRAWL_API_KEY      # Web scraping (required)
NEXT_PUBLIC_CONVEX_URL # Convex deployment URL (required)
CONVEX_DEPLOYMENT      # Convex deployment token (required)
CORS_ORIGINS           # Allowed origins (required)
```

### Backend (Optional)
```bash
FIRECRAWL_API_URL      # Self-hosted Firecrawl (default: http://localhost:3002)
TELEGRAM_BOT_TOKEN     # Telegram bot (optional)
PORT                   # Server port (default: 8000)
HOST                   # Server host (default: 0.0.0.0)
DEBUG                  # Debug mode (default: false)
```

### Frontend (Required)
```bash
NEXT_PUBLIC_CONVEX_URL # Convex deployment URL
NEXT_PUBLIC_API_URL    # Backend API URL
AGENT_SERVICE_KEY      # Server-side only (for API calls)
```

---

## 🚀 Quick Deploy Commands

### Full Stack Deployment

```bash
# 1. Deploy Convex
cd propoto/web
npx convex deploy --prod

# 2. Deploy Backend (Railway)
cd ../api
railway up

# 3. Deploy Frontend (Vercel)
cd ../web
vercel --prod
```

---

## ✅ Post-Launch Checklist

- [ ] All health checks passing
- [ ] Proposal generation working
- [ ] Knowledge ingestion working (Firecrawl)
- [ ] Lead discovery working (Exa)
- [ ] Frontend can connect to backend
- [ ] Frontend can connect to Convex
- [ ] Multi-tenancy isolation verified
- [ ] Rate limiting active
- [ ] Error handling graceful
- [ ] Monitoring alerts configured

---

## 📞 Support

For deployment issues:
1. Check logs (backend + frontend)
2. Verify environment variables
3. Test health endpoints
4. Review error messages

**Production URLs:**
- Frontend: `https://app.yourdomain.com`
- Backend: `https://api.yourdomain.com`
- Convex: `https://xxx.convex.cloud`

---

*Last Updated: January 2026 | Status: Ready for Production*

