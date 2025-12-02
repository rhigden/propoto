# Manual Testing Guide - Snyto (AgencyOS)

Complete guide for manually testing the AgencyOS application, including both frontend and backend components.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Starting the Services](#starting-the-services)
4. [Backend API Testing](#backend-api-testing)
5. [Frontend Testing](#frontend-testing)
6. [End-to-End Workflows](#end-to-end-workflows)
7. [Error Scenarios](#error-scenarios)
8. [Performance Testing](#performance-testing)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools
- **Node.js** 18+ and npm
- **Python** 3.12+
- **curl** or **Postman** for API testing
- **Modern browser** (Chrome, Firefox, Edge)
- **Terminal/Command Line** access

### Required API Keys
- ✅ `OPENROUTER_API_KEY` - For LLM access (required)
- ✅ `AGENT_SERVICE_KEY` - API authentication (required)
- ⚠️ `GAMMA_API_KEY` - For presentation generation (optional, but recommended)
- ⚠️ `MEM0_API_KEY` - For brand memory (optional)
- ⚠️ `FIRECRAWL_API_KEY` - For web scraping (optional)
- ⚠️ `EXA_API_KEY` - For lead discovery (optional)
- ⚠️ `NEXT_PUBLIC_CONVEX_URL` - Convex backend URL (optional)
- ⚠️ `CONVEX_DEPLOYMENT` - Convex deployment token (optional)

---

## Environment Setup

### 1. Backend Environment

Navigate to the API directory and set up environment variables:

```bash
cd /home/user/newshii/propoto/api

# Create or edit .env file
nano .env
```

**Minimum required `.env` file:**
```env
# Required
OPENROUTER_API_KEY=sk-or-v1-your-key-here
AGENT_SERVICE_KEY=your-secret-key-here

# Optional (but recommended for full functionality)
GAMMA_API_KEY=sk-gamma-your-key-here
MEM0_API_KEY=m0-your-key-here
FIRECRAWL_API_KEY=fc-your-key-here
EXA_API_KEY=your-exa-key-here
NEXT_PUBLIC_CONVEX_URL=https://your-deployment.convex.cloud
CONVEX_DEPLOYMENT=your-deployment-token

# Server Configuration
PORT=8000
HOST=0.0.0.0
LOG_FORMAT=text
LOG_LEVEL=INFO
```

### 2. Frontend Environment

Navigate to the web directory:

```bash
cd /home/user/newshii/propoto/web

# Create or edit .env.local file
nano .env.local
```

**Frontend `.env.local` file:**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_CONVEX_URL=https://your-deployment.convex.cloud
```

---

## Starting the Services

### Step 1: Start Backend API

**Terminal 1 - Backend:**
```bash
cd /home/user/newshii/propoto/api

# Activate virtual environment (if using venv)
source venv/bin/activate

# Install dependencies (first time only)
pip install -r requirements.txt

# Start the server
python main.py
# OR with auto-reload:
uvicorn main:app --reload --port 8000
```

**Expected Output:**
```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Verify Backend is Running:**
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "environment": {
    "openrouter": true,
    "gamma": true,
    "mem0": true,
    "firecrawl": true,
    "convex": true
  }
}
```

### Step 2: Start Frontend

**Terminal 2 - Frontend:**
```bash
cd /home/user/newshii/propoto/web

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

**Expected Output:**
```
▲ Next.js 15.0.3
- Local:        http://localhost:3000
- Ready in 2.3s
```

**Verify Frontend is Running:**
Open browser: `http://localhost:3000`

---

## Backend API Testing

### 1. Health Check Endpoint

**Test:** Verify service is running

```bash
curl http://localhost:8000/health
```

**Expected:** 200 OK with environment status

**Test:** Root endpoint
```bash
curl http://localhost:8000/
```

**Expected:** Service info with available agents

---

### 2. Authentication Testing

**Test:** Missing API Key
```bash
curl -X POST http://localhost:8000/agents/proposal/generate \
  -H "Content-Type: application/json" \
  -d '{"prospect_name": "Test", "prospect_url": "https://example.com", "pain_points": "Test"}'
```

**Expected:** 403 Forbidden
```json
{
  "detail": "Invalid API Key"
}
```

**Test:** Invalid API Key
```bash
curl -X POST http://localhost:8000/agents/proposal/generate \
  -H "x-api-key: wrong-key" \
  -H "Content-Type: application/json" \
  -d '{"prospect_name": "Test", "prospect_url": "https://example.com", "pain_points": "Test"}'
```

**Expected:** 403 Forbidden

---

### 3. Proposal Generation Endpoint

**Test:** Basic Proposal Generation

```bash
curl -X POST http://localhost:8000/agents/proposal/generate \
  -H "x-api-key: your-secret-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "prospect_name": "Acme Corp",
    "prospect_url": "https://acme.com",
    "pain_points": "Low conversion rates, high customer acquisition cost"
  }'
```

**What to Verify:**
- ✅ Status code: 200 OK
- ✅ Response includes `success: true`
- ✅ `data` object contains:
  - `executive_summary` (2-3 sentences)
  - `current_situation` (3-4 sentences)
  - `proposed_strategy` (4-5 sentences with named mechanism)
  - `why_us` (1 sentence)
  - `investment` (exactly 3 pricing tiers)
  - `next_steps` (1 clear action)
- ✅ `presentation_url` (Gamma URL if Gamma API key is set)
- ✅ `model_used` field
- ✅ `template_used` field

**Test:** Proposal with Deep Scraping

```bash
curl -X POST http://localhost:8000/agents/proposal/generate \
  -H "x-api-key: your-secret-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "prospect_name": "TechStart Inc",
    "prospect_url": "https://techstart.com",
    "pain_points": "Need to scale marketing operations",
    "deep_scrape": true,
    "template": "startup"
  }'
```

**What to Verify:**
- ✅ Website intelligence is extracted
- ✅ Proposal references specific details from website
- ✅ Template style matches "startup" (energetic, fast-paced)

**Test:** Proposal with Custom Model

```bash
curl -X POST http://localhost:8000/agents/proposal/generate \
  -H "x-api-key: your-secret-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "prospect_name": "Enterprise Co",
    "prospect_url": "https://enterprise.com",
    "pain_points": "Digital transformation",
    "model": "gpt-4o",
    "template": "enterprise"
  }'
```

**What to Verify:**
- ✅ Uses specified model
- ✅ Template style is formal/enterprise

**Test:** Invalid Input Validation

```bash
# Missing prospect_name
curl -X POST http://localhost:8000/agents/proposal/generate \
  -H "x-api-key: your-secret-key-here" \
  -H "Content-Type: application/json" \
  -d '{"prospect_url": "https://example.com", "pain_points": "Test"}'
```

**Expected:** 400 Bad Request with validation error

```bash
# Invalid URL format
curl -X POST http://localhost:8000/agents/proposal/generate \
  -H "x-api-key: your-secret-key-here" \
  -H "Content-Type: application/json" \
  -d '{"prospect_name": "Test", "prospect_url": "not-a-url", "pain_points": "Test"}'
```

**Expected:** 400 Bad Request

---

### 4. Knowledge Agent Endpoint

**Test:** Knowledge Ingestion

```bash
curl -X POST http://localhost:8000/agents/knowledge/ingest \
  -H "x-api-key: your-secret-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com"
  }'
```

**What to Verify:**
- ✅ Status code: 200 OK
- ✅ Response includes:
  - `summary` (2-3 sentences)
  - `entities` array (5-15 items)
  - `relevance_score` (1-10)
- ✅ Entities have: `name`, `type`, `details`
- ✅ Entity types: `competitor`, `feature`, `pricing`, `other`

**Test:** Invalid URL

```bash
curl -X POST http://localhost:8000/agents/knowledge/ingest \
  -H "x-api-key: your-secret-key-here" \
  -H "Content-Type: application/json" \
  -d '{"url": "not-a-url"}'
```

**Expected:** 400 Bad Request

---

### 5. Brand Agent Endpoint

**Test:** Generate Presentation

```bash
curl -X POST http://localhost:8000/agents/brand/generate \
  -H "x-api-key: your-secret-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a pitch deck for AI-powered marketing automation platform",
    "format": "presentation",
    "num_cards": 10,
    "tone": "professional, innovative",
    "image_style": "photorealistic, modern"
  }'
```

**What to Verify:**
- ✅ Status code: 200 OK
- ✅ Response includes:
  - `success: true`
  - `data.asset_type: "presentation"`
  - `data.url` (Gamma URL)
  - `data.description`

**Test:** Generate Document

```bash
curl -X POST http://localhost:8000/agents/brand/generate \
  -H "x-api-key: your-secret-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a case study document about successful client engagement",
    "format": "document",
    "num_cards": 15
  }'
```

**What to Verify:**
- ✅ `asset_type: "document"`
- ✅ URL is accessible

---

### 6. Sales Agent Endpoint

**Test:** Find Leads

```bash
curl -X POST http://localhost:8000/agents/sales/find_leads \
  -H "x-api-key: your-secret-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Find digital marketing agencies in San Francisco"
  }'
```

**What to Verify:**
- ✅ Status code: 200 OK
- ✅ Response includes:
  - `leads` array (3-10 items)
  - `market_summary` (3-4 sentences)
- ✅ Each lead has:
  - `company_name`
  - `website`
  - `description`
  - `score` (0-100)
  - `status: "new"`

---

### 7. Brand Voice Endpoints

**Test:** Get Brand Voice

```bash
curl -X GET "http://localhost:8000/agents/brand/voice?org_id=demo-org-1" \
  -H "x-api-key: your-secret-key-here"
```

**What to Verify:**
- ✅ Returns brand voice configuration
- ✅ Includes prompt text

**Test:** Save Brand Voice

```bash
curl -X POST http://localhost:8000/agents/brand/voice \
  -H "x-api-key: your-secret-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "org_id": "demo-org-1",
    "company_name": "AgencyOS",
    "tagline": "AI-Powered Agency Operations",
    "brand_colors": ["#3B82F6", "#8B5CF6"],
    "tone_keywords": ["professional", "innovative", "value-focused"],
    "writing_style": "direct and conversational",
    "target_audience": "Digital agency owners and marketing directors"
  }'
```

**What to Verify:**
- ✅ `success: true`
- ✅ Brand voice is saved

---

### 8. API Documentation

**Test:** Swagger UI

Open in browser: `http://localhost:8000/docs`

**What to Verify:**
- ✅ All endpoints are listed
- ✅ Can test endpoints directly from UI
- ✅ Request/response schemas are visible

**Test:** ReDoc

Open in browser: `http://localhost:8000/redoc`

**What to Verify:**
- ✅ Clean documentation interface
- ✅ All endpoints documented

---

## Frontend Testing

### 1. Landing Page (`http://localhost:3000`)

**Visual Checks:**
- ✅ Page loads without errors
- ✅ Background effects render correctly
- ✅ "AgencyOS" branding is visible
- ✅ Headline: "Generate $10K Proposals in 60 Seconds"
- ✅ Stats section shows: 60s, 3x, 95%
- ✅ Three feature cards are displayed
- ✅ "Try It Free" and "Launch App" buttons work
- ✅ Footer is visible

**Functional Checks:**
- ✅ Click "Launch App" → navigates to `/dashboard`
- ✅ Click "Try It Free" → navigates to `/dashboard`
- ✅ Click "See How It Works" → scrolls to features section

---

### 2. Dashboard (`http://localhost:3000/dashboard`)

**Visual Checks:**
- ✅ Sidebar is visible on the left
- ✅ Topbar is visible at the top
- ✅ Main content area is visible
- ✅ Navigation items are displayed:
  - Dashboard
  - Knowledge
  - Brand
  - Sales
  - Settings

**Functional Checks:**

**Sidebar:**
- ✅ Click collapse button → sidebar collapses to icon-only
- ✅ Click expand button → sidebar expands
- ✅ Click "Knowledge" → navigates to `/dashboard/knowledge`
- ✅ Active page is highlighted
- ✅ Logo/branding is visible

**Topbar:**
- ✅ User info/profile is displayed (if auth enabled)
- ✅ Any action buttons work

---

### 3. Proposal Generation Page

**Test:** Generate Proposal

1. Navigate to dashboard
2. Fill in form:
   - **Prospect Name:** "Acme Corporation"
   - **Website URL:** "https://acme.com"
   - **Pain Points:** "Low conversion rates, high customer acquisition cost"
3. Click "Generate Proposal"

**What to Verify:**
- ✅ Loading state appears
- ✅ Proposal is generated (30-60 seconds)
- ✅ Proposal sections are displayed:
  - Executive Summary
  - Current Situation
  - Proposed Strategy
  - Why Us
  - Investment (3 tiers)
  - Next Steps
- ✅ Gamma presentation link is available (if Gamma API key set)
- ✅ PDF/PPTX download links work (if available)
- ✅ Proposal can be copied/saved

**Test:** Deep Scrape Option

1. Enable "Deep Scrape" toggle
2. Generate proposal

**What to Verify:**
- ✅ Takes longer (scraping + generation)
- ✅ Proposal references specific website details
- ✅ More personalized content

**Test:** Template Selection

1. Select different template (e.g., "Enterprise", "Startup")
2. Generate proposal

**What to Verify:**
- ✅ Tone/style matches selected template
- ✅ Enterprise: formal, data-driven
- ✅ Startup: energetic, fast-paced

---

### 4. Knowledge Page (`/dashboard/knowledge`)

**Test:** Ingest Knowledge

1. Enter URL: `https://example.com`
2. Click "Ingest Knowledge"

**What to Verify:**
- ✅ Loading state appears
- ✅ Knowledge is extracted
- ✅ Summary is displayed
- ✅ Entities list is shown:
  - Competitors
  - Features
  - Pricing
  - Other intelligence
- ✅ Relevance score is displayed (1-10)
- ✅ Knowledge is stored (if Convex configured)

**Test:** View Stored Knowledge

1. Check if knowledge list is displayed
2. Click on a knowledge item

**What to Verify:**
- ✅ Details are shown
- ✅ Entities are listed
- ✅ Can filter/search

---

### 5. Brand Page (`/dashboard/brand`)

**Test:** Generate Brand Asset

1. Enter prompt: "Create a pitch deck for AI marketing platform"
2. Select format: "Presentation"
3. Set number of cards: 10
4. Click "Generate"

**What to Verify:**
- ✅ Loading state appears
- ✅ Generation takes 1-3 minutes
- ✅ Gamma URL is provided
- ✅ Can open in new tab
- ✅ Asset is viewable

**Test:** Brand Voice Configuration

1. Navigate to brand voice settings
2. Fill in:
   - Company name
   - Tagline
   - Brand colors
   - Tone keywords
   - Writing style
3. Save

**What to Verify:**
- ✅ Brand voice is saved
- ✅ Used in subsequent generations
- ✅ Can be retrieved later

---

### 6. Sales Page (`/dashboard/sales`)

**Test:** Find Leads

1. Enter search query: "digital marketing agencies in San Francisco"
2. Click "Find Leads"

**What to Verify:**
- ✅ Loading state appears
- ✅ Leads are found (3-10)
- ✅ Each lead shows:
  - Company name
  - Website
  - Description
  - Score (0-100)
- ✅ Market summary is displayed
- ✅ Leads can be saved/exported

---

### 7. Settings Page (`/dashboard/settings`)

**What to Verify:**
- ✅ Settings form is displayed
- ✅ Can update preferences
- ✅ Changes are saved
- ✅ API keys can be configured (if applicable)

---

## End-to-End Workflows

### Workflow 1: Complete Proposal Generation

1. **Start Services**
   - Backend: `http://localhost:8000`
   - Frontend: `http://localhost:3000`

2. **Navigate to Dashboard**
   - Open `http://localhost:3000/dashboard`

3. **Generate Proposal**
   - Enter prospect details
   - Enable deep scrape
   - Select template
   - Click "Generate"

4. **Verify Results**
   - Proposal is complete
   - All sections present
   - Gamma presentation available
   - Can download PDF

5. **Save/Export**
   - Copy proposal text
   - Download presentation
   - Save to Convex (if configured)

---

### Workflow 2: Knowledge → Proposal

1. **Ingest Knowledge**
   - Go to Knowledge page
   - Scrape competitor website
   - Review extracted entities

2. **Use Knowledge in Proposal**
   - Go to Proposal page
   - Generate proposal
   - Verify it references knowledge

---

### Workflow 3: Lead Discovery → Proposal

1. **Find Leads**
   - Go to Sales page
   - Search for companies
   - Review leads

2. **Generate Proposal for Lead**
   - Select a lead
   - Use lead info to generate proposal
   - Verify personalization

---

## Error Scenarios

### Test: Missing API Keys

**Backend:**
- Remove `OPENROUTER_API_KEY` from `.env`
- Restart backend
- Try to generate proposal

**Expected:**
- ✅ Service starts (graceful degradation)
- ✅ Error message indicates missing key
- ✅ Health check shows `openrouter: false`

### Test: Invalid API Key

**Backend:**
- Use wrong `AGENT_SERVICE_KEY`
- Try to access protected endpoint

**Expected:**
- ✅ 403 Forbidden
- ✅ Clear error message

### Test: Network Timeout

**Backend:**
- Use invalid URL for scraping
- Try knowledge ingestion

**Expected:**
- ✅ Timeout after reasonable time
- ✅ Error message returned
- ✅ Service remains stable

### Test: Rate Limiting

**Backend:**
- Make many rapid requests
- Check for rate limit handling

**Expected:**
- ✅ Rate limit errors include retry info
- ✅ Service doesn't crash
- ✅ Can retry after delay

---

## Performance Testing

### Test: Response Times

**Backend:**
```bash
time curl -X POST http://localhost:8000/agents/proposal/generate \
  -H "x-api-key: your-key" \
  -H "Content-Type: application/json" \
  -d '{"prospect_name": "Test", "prospect_url": "https://example.com", "pain_points": "Test"}'
```

**Expected:**
- ✅ Proposal generation: 30-90 seconds
- ✅ Knowledge ingestion: 10-30 seconds
- ✅ Brand asset: 60-180 seconds

### Test: Concurrent Requests

**Backend:**
- Make 5 simultaneous proposal requests
- Monitor server stability

**Expected:**
- ✅ All requests complete
- ✅ No crashes
- ✅ Proper error handling

---

---

## 9. Telegram Bot Testing

### 1. Bot Management

**Test:** Start Bot
```bash
curl -X POST http://localhost:8000/telegram/start \
  -H "x-api-key: your-secret-key-here"
```
**Expected:**
- ✅ Status: 200 OK
- ✅ Message: "Telegram bot started successfully"

**Test:** Check Status
```bash
curl http://localhost:8000/telegram/status
```
**Expected:**
- ✅ `running: true`
- ✅ `configured: true`

**Test:** Stop Bot
```bash
curl -X POST http://localhost:8000/telegram/stop \
  -H "x-api-key: your-secret-key-here"
```
**Expected:**
- ✅ Status: 200 OK
- ✅ Message: "Telegram bot stopped"

### 2. Bot Interaction (In Telegram App)

**Test:** Start Command
- Send: `/start`
- **Expected:** Welcome message with available commands.

**Test:** Research Command
- Send: `/research digital marketing trends`
- **Expected:**
  - "🔍 Searching for..." message
  - List of search results with summaries
  - "✅ Research complete" message

**Test:** Proposal Command
- Send: `/proposal Acme Corp https://acme.com`
- **Expected:**
  - "✍️ Generating proposal..." message
  - "Please describe the pain points..." prompt
- Send: "Low conversion rates"
- **Expected:**
  - "Generating proposal..."
  - Full proposal text sent in chunks
  - "✅ Proposal generated!" message

**Test:** Help Command
- Send: `/help`
- **Expected:** List of commands and usage instructions.

---

## 10. Troubleshooting


### Issue: Backend won't start

**Check:**
1. Python version: `python --version` (should be 3.12+)
2. Dependencies: `pip install -r requirements.txt`
3. Environment variables: Check `.env` file
4. Port availability: `lsof -i :8000`

**Solution:**
```bash
# Check logs
tail -f /tmp/api_server.log

# Restart with verbose logging
LOG_LEVEL=DEBUG python main.py
```

---

### Issue: Frontend won't start

**Check:**
1. Node version: `node --version` (should be 18+)
2. Dependencies: `npm install`
3. Port availability: `lsof -i :3000`

**Solution:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run dev
```

---

### Issue: API calls fail

**Check:**
1. Backend is running: `curl http://localhost:8000/health`
2. API key is correct
3. CORS is configured (if needed)
4. Network connectivity

**Solution:**
```bash
# Test with curl first
curl -v http://localhost:8000/health

# Check browser console for errors
# Check network tab in DevTools
```

---

### Issue: Proposal generation fails

**Check:**
1. OpenRouter API key is valid
2. API credits/quota available
3. Model is available
4. Check backend logs

**Solution:**
```bash
# Check logs
tail -f /tmp/api_server.log

# Test with simpler request
# Verify API key in OpenRouter dashboard
```

---

## Test Checklist

### Backend API
- [ ] Health check works
- [ ] Authentication works
- [ ] Proposal generation works
- [ ] Knowledge ingestion works
- [ ] Brand asset generation works
- [ ] Sales lead discovery works
- [ ] Brand voice CRUD works
- [ ] Error handling works
- [ ] Validation works
- [ ] API docs accessible

### Frontend
- [ ] Landing page loads
- [ ] Dashboard loads
- [ ] Navigation works
- [ ] Proposal generation works
- [ ] Knowledge ingestion works
- [ ] Brand asset generation works
- [ ] Sales lead discovery works
- [ ] Settings page works
- [ ] Responsive design works
- [ ] Error messages display

### Integration
- [ ] Frontend → Backend communication works
- [ ] Data persistence works (if Convex configured)
- [ ] File downloads work
- [ ] External links work

---

## Quick Test Commands

### Backend Health Check
```bash
curl http://localhost:8000/health | jq
```

### Generate Test Proposal
```bash
curl -X POST http://localhost:8000/agents/proposal/generate \
  -H "x-api-key: $AGENT_SERVICE_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prospect_name": "Test Corp",
    "prospect_url": "https://example.com",
    "pain_points": "Testing the system"
  }' | jq
```

### Test Knowledge Ingestion
```bash
curl -X POST http://localhost:8000/agents/knowledge/ingest \
  -H "x-api-key: $AGENT_SERVICE_KEY" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}' | jq
```

---

## Notes

- **API Keys:** Keep your API keys secure. Never commit them to version control.
- **Rate Limits:** Be aware of API rate limits, especially for OpenRouter and Gamma.
- **Costs:** Monitor API usage costs, especially for paid models.
- **Logs:** Check logs regularly for errors and performance issues.
- **Updates:** Keep dependencies updated for security and features.

---

## Support

If you encounter issues:
1. Check logs: `tail -f /tmp/api_server.log`
2. Review error messages
3. Verify environment variables
4. Check API key validity
5. Review this guide's troubleshooting section

---

**Last Updated:** December 1, 2025
**Version:** 1.0.0

