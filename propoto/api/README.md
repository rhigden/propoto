# Python Agents Service

AI-powered agent service for knowledge management and brand asset creation, built with FastAPI and Pydantic AI.

## Features

### 🧠 Knowledge Agent
- Web scraping with Firecrawl
- Entity extraction (competitors, features, pricing)
- Automatic storage in Convex knowledge base
- Relevance scoring

### 🎨 Brand Agent  
- Presentation/document/webpage generation via Gamma API
- Brand guidelines from Mem0 memory
- AI-powered content and images
- PDF/PPTX export support

## Quick Start

### 1. Install Dependencies

```bash
cd python-agents
pip install -r requirements.txt
```

### 2. Configure Environment

Copy and configure your `.env` file:

```bash
# Required
OPENROUTER_API_KEY=sk-or-v1-xxx
AGENT_SERVICE_KEY=your-secret-key

# Optional (but recommended)
GAMMA_API_KEY=sk-gamma-xxx
MEM0_API_KEY=m0-xxx
FIRE_CRAWL_API_KEY=fc-xxx
NEXT_PUBLIC_CONVEX_URL=https://xxx.convex.cloud
CONVEX_DEPLOYMENT=xxx
EXA_API_KEY=xxx
```

### 3. Run the Service

```bash
python main.py
```

Server starts at: `http://0.0.0.0:8000`

## API Endpoints

### Health Check
```bash
GET /health
```

### Knowledge Ingestion
```bash
POST /agents/knowledge/ingest
Headers: x-api-key: your-secret-key
Body: {
  "url": "https://example.com/article"
}
```

### Brand Asset Generation
```bash
POST /agents/brand/generate
Headers: x-api-key: your-secret-key
Body: {
  "prompt": "Create a pitch deck for AI SaaS product",
  "format": "presentation",
  "num_cards": 10,
  "tone": "professional, innovative",
  "image_style": "photorealistic, modern"
}
```

## Architecture

```
python-agents/
├── agents/
│   ├── knowledge.py    # Knowledge Librarian agent
│   └── brand.py        # Brand Designer agent
├── main.py             # FastAPI server
├── requirements.txt    # Python dependencies
└── .env               # Environment variables
```

## Production Features

✅ **Robust Error Handling**  
- HTTP status code handling (401, 429, 402, etc.)
- Graceful fallbacks for missing API keys
- Detailed error messages

✅ **Retry Logic**  
- Exponential backoff with tenacity
- Configurable retry attempts
- Automatic recovery from transient failures

✅ **Logging**  
- Structured logging with timestamps
- Request/response tracking
- Error stack traces in debug mode

✅ **Validation**  
- Environment variable validation on startup
- Request model validation with Pydantic
- API key authentication

## Dependencies

- **FastAPI** - Modern web framework
- **Pydantic AI** - Agent orchestration
- **Firecrawl** - Web scraping
- **Mem0** - Long-term memory
- **Gamma API** - Presentation generation
- **Tenacity** - Retry logic
- **httpx** - Async HTTP client

## Development

### Install in development mode
```bash
pip install -e .
```

### Run with auto-reload
```bash
uvicorn main:app --reload --port 8000
```

### View API docs
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Integration with Convex

The service integrates with your Convex backend via the `/agents.ts` action:

```typescript
// In Convex
await ctx.runAction(api.actions.agents.callAgentService, {
  agent: "knowledge",
  action: "ingest",
  payload: { url: "https://example.com" },
  orgId: "org_123"
});
```

## Troubleshooting

### "Firecrawl API Key not set"
- Set `FIRE_CRAWL_API_KEY` in `.env`
- Or sign up at https://firecrawl.dev

### "Gamma API Key not set"
- Set `GAMMA_API_KEY` in `.env`  
- Requires Gamma Pro/Ultra subscription

### "Rate limit exceeded"
- Retry logic handles this automatically
- Check your API subscription limits

## License

MIT
