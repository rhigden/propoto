# Quick Test Reference Card

## 🚀 Quick Start Commands

### Start Backend
```bash
cd propoto/api
source venv/bin/activate
python main.py
```

### Start Frontend
```bash
cd propoto/web
npm run dev
```

### Health Check
```bash
curl http://localhost:8000/health
```

---

## 📍 URLs

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 🔑 API Key Header

All protected endpoints require:
```
x-api-key: your-secret-key-here
```

---

## 🧪 Quick Test Commands

### 1. Generate Proposal
```bash
curl -X POST http://localhost:8000/agents/proposal/generate \
  -H "x-api-key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prospect_name": "Acme Corp",
    "prospect_url": "https://acme.com",
    "pain_points": "Low conversion rates"
  }'
```

### 2. Ingest Knowledge
```bash
curl -X POST http://localhost:8000/agents/knowledge/ingest \
  -H "x-api-key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

### 3. Generate Brand Asset
```bash
curl -X POST http://localhost:8000/agents/brand/generate \
  -H "x-api-key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "AI marketing platform pitch deck",
    "format": "presentation",
    "num_cards": 10
  }'
```

### 4. Find Leads
```bash
curl -X POST http://localhost:8000/agents/sales/find_leads \
  -H "x-api-key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "digital marketing agencies"}'
  }'
```

### 5. Telegram Bot
```bash
# Start Bot
curl -X POST http://localhost:8000/telegram/start \
  -H "x-api-key: YOUR_KEY"

# Check Status
curl http://localhost:8000/telegram/status
```

---

## ✅ Quick Checklist

### Backend
- [ ] Health check returns 200
- [ ] Authentication works (403 without key)
- [ ] Proposal generation completes
- [ ] Knowledge ingestion works
- [ ] Brand generation works
- [ ] Telegram bot starts/stops

### Frontend
- [ ] Landing page loads
- [ ] Dashboard accessible
- [ ] Navigation works
- [ ] Proposal form submits
- [ ] Results display correctly

---

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| Port 8000 in use | `lsof -i :8000` then kill process |
| Port 3000 in use | `lsof -i :3000` then kill process |
| Module not found | `pip install -r requirements.txt` or `npm install` |
| API key error | Check `.env` file |
| CORS error | Check backend CORS config |

---

## 📊 Expected Response Times

- **Health Check:** < 100ms
- **Proposal Generation:** 30-90s
- **Knowledge Ingestion:** 10-30s
- **Brand Asset:** 60-180s
- **Lead Discovery:** 15-45s
- **Telegram Response:** 2-5s

---

## 🔍 Debug Commands

```bash
# Check backend logs
tail -f /tmp/api_server.log

# Check if services are running
ps aux | grep python
ps aux | grep node

# Test API connectivity
curl -v http://localhost:8000/health

# Check environment variables
cd propoto/api && cat .env
cd propoto/web && cat .env.local
```

---

**See [MANUAL_TESTING_GUIDE.md](./MANUAL_TESTING_GUIDE.md) for complete details.**


