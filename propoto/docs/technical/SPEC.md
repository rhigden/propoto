# Technical Specification: Propoto

**Version:** 3.1  
**Last Updated:** January 2026  
**Status:** Active  
**Owner:** Engineering  
**Companion Doc:** [PRD.md](../product/PRD.md)

---

## 1. System Overview

### 1.1 Purpose

This document defines the technical architecture, APIs, data models, and engineering standards for Propoto — an AI-powered proposal generation system for digital agencies.

**Business Context:** See [PRD Section 4](../product/PRD.md#4-product-strategy) for product strategy and differentiation.

### 1.2 Architecture Principles

| Principle | Rationale |
|-----------|-----------|
| **Stateless backend** | Horizontal scaling for cost efficiency |
| **Multi-tenant by default** | Every record scoped by `orgId` |
| **Graceful degradation** | Core value (proposals) works even when integrations fail |
| **Cost-conscious AI** | Default to free/cheap models, track token usage |
| **Real-time where it matters** | Convex for live updates on proposals |

### 1.3 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              CLIENTS                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                   │
│  │   Web App    │  │ Telegram Bot │  │  Future API  │                   │
│  │  (Next.js)   │  │              │  │   Clients    │                   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                   │
└─────────┼─────────────────┼─────────────────┼───────────────────────────┘
          │                 │                 │
          ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           API GATEWAY                                    │
│                    FastAPI (Python, Async)                               │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                        MIDDLEWARE                                   │ │
│  │  • CORS (configurable origins)                                     │ │
│  │  • API Key Authentication (x-api-key header)                       │ │
│  │  • URL Security Validation (SSRF protection)                       │ │
│  │  • Structured Logging (request context)                            │ │
│  │  • Error Handling (graceful responses)                             │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                         AI AGENTS                                   │ │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐       │ │
│  │  │  Proposal  │ │   Brand    │ │ Knowledge  │ │   Sales    │       │ │
│  │  │   Agent    │ │   Agent    │ │   Agent    │ │   Agent    │       │ │
│  │  └─────┬──────┘ └─────┬──────┘ └─────┬──────┘ └─────┬──────┘       │ │
│  └────────┼──────────────┼──────────────┼──────────────┼──────────────┘ │
└───────────┼──────────────┼──────────────┼──────────────┼────────────────┘
            │              │              │              │
            ▼              ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        EXTERNAL SERVICES                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │OpenRouter│ │  Gamma   │ │Firecrawl │ │   Exa    │ │  Mem0    │      │
│  │  (LLM)   │ │ (Decks)  │ │(Scraping)│ │ (Search) │ │ (Memory) │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
└─────────────────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          DATA LAYER                                      │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                      Convex (Real-time DB)                        │   │
│  │  • proposals  • leads  • knowledge  • assets  • audit_logs       │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.4 Technology Stack

| Layer | Technology | Version | Selection Rationale |
|-------|------------|---------|---------------------|
| **Frontend** | Next.js | 15.0.3 | App Router, Server Actions, fast iteration |
| **Styling** | Tailwind CSS | 4.x | Utility-first, design system flexibility |
| **Components** | shadcn/ui | Latest | Accessible, customizable, no vendor lock-in |
| **Database** | Convex | 1.29.3+ | Real-time sync, serverless, type-safe |
| **Auth** | Clerk | 6.0.0 | Drop-in auth, org management, webhooks |
| **Backend** | FastAPI | 0.115.0+ | Async Python, auto OpenAPI docs |
| **AI Framework** | Pydantic AI | 1.25.0+ | Structured outputs, tool calling |
| **LLM Gateway** | OpenRouter | - | Multi-model access, cost optimization |

**📊 Stack Audit:** See [TECH_STACK_AUDIT.md](./TECH_STACK_AUDIT.md) for detailed version tracking and upgrade recommendations.

---

### 1.5 Frontend Experience Architecture

- **Dashboard shell:** Cursor-inspired thin rail (`Sidebar`), layered gradient/noise background, and constrained content width for focus. Implemented via `DashboardShell` so every dashboard route inherits the same chrome.
- **Composable hero:** `DashboardHeader` renders breadcrumbs, kicker text, and contextual actions (CTA buttons, filters). This keeps navigation consistent between Proposals, Brand Studio, Knowledge, and Sales views.
- **Metric system:** `MetricCard` standardizes stat tiles, icon badges, and deltas. Cards are responsive (single column on mobile, 3-up on desktop) and re-usable in future analytics surfaces.
- **Proposals workspace:** `/dashboard` now uses a two-column grid:
  - **Pipeline panel:** searchable + filterable history (status chips, fuzzy search).
  - **Sticky action rail:** quick composer CTA, insight cards, and recent activity feed.
- **Proposal editor overlay:** Full-height document surface with inline editing, status toggles, download/email tracking, and breadcrumb actions. Powered by shared components (Button/Input/Textarea) plus new editing state hooks.

These shared primitives allow future dashboard pages to pick up the Cursor-like look and feel without duplicating layout code.

---

## 2. Performance Requirements

### 2.1 SLAs (Aligned with PRD Section 8)

| Metric | Target | Measurement | Alert Threshold |
|--------|--------|-------------|-----------------|
| **Proposal generation (text)** | < 15 sec | p95 latency | > 20 sec |
| **Deck generation (Gamma)** | < 60 sec | p95 latency | > 90 sec |
| **API response (non-AI)** | < 200 ms | p95 latency | > 500 ms |
| **Error rate** | < 5% | Errors / total requests | > 5% |
| **Gamma success rate** | > 85% | Successful decks / attempts | < 80% |
| **Uptime** | 99.5% | Monthly availability | < 99% |

### 2.2 Cost Constraints (from PRD Unit Economics)

| Resource | Budget per Proposal | Current Actual |
|----------|---------------------|----------------|
| LLM tokens (OpenRouter) | $0.10 | ~$0.05 (free Grok) |
| Gamma API | $0.15 | ~$0.10 |
| Firecrawl (if used) | $0.05 | ~$0.02 |
| **Total COGS** | **< $0.30** | **~$0.18** |

**Token Management:**
- Default `max_tokens: 2000` for proposal generation
- Monitor via `TokenTracker` utility
- Alert if cost per proposal exceeds $0.25

### 2.3 Scalability Targets

| Phase | Concurrent Users | Proposals/Day | Infrastructure |
|-------|------------------|---------------|----------------|
| Beta | 10 | 50 | Single instance |
| Launch | 100 | 500 | 2 instances |
| Scale | 1,000 | 5,000 | Auto-scaling group |

---

## 3. API Specification

### 3.1 Authentication

All endpoints except `/`, `/health`, and metadata endpoints require:

```http
x-api-key: <AGENT_SERVICE_KEY>
```

**Security Implementation:**
- Key validated on every request via `verify_key` dependency
- Keys stored in environment variables only
- No key rotation mechanism yet (future enhancement)

### 3.2 Core Endpoints

#### 3.2.1 Generate Proposal

**The primary value-generating endpoint.**

```http
POST /agents/proposal/generate
```

**Request:**
```json
{
  "prospect_name": "Acme Corp",
  "prospect_url": "https://acme.com",
  "pain_points": "Low conversion rates, outdated website design",
  "model": "grok",
  "template": "default",
  "deep_scrape": false
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `prospect_name` | string | Yes | Company name |
| `prospect_url` | string | Yes | Website URL (validated for SSRF) |
| `pain_points` | string | Yes | Context for proposal |
| `model` | string | No | LLM model key (default: `grok`) |
| `template` | string | No | Proposal style (default: `default`) |
| `deep_scrape` | boolean | No | Enable website analysis |

**Response (200):**
```json
{
  "success": true,
  "data": {
    "executive_summary": "...",
    "current_situation": "...",
    "proposed_strategy": "...",
    "why_us": "...",
    "investment": [
      {"name": "Starter", "price": "$2,000/mo", "features": ["..."]},
      {"name": "Growth", "price": "$5,000/mo", "features": ["..."]},
      {"name": "Enterprise", "price": "$10,000/mo", "features": ["..."]}
    ],
    "next_steps": "..."
  },
  "presentation_url": "https://gamma.app/docs/...",
  "pdf_url": "https://gamma.app/export/...pdf",
  "pptx_url": "https://gamma.app/export/...pptx",
  "model_used": "x-ai/grok-4.1-fast:free",
  "template_used": "default",
  "deep_scrape_enabled": false
}
```

**Error Responses:**

| Code | Condition | Response |
|------|-----------|----------|
| 400 | Invalid input | `{"detail": "prospect_name is required"}` |
| 400 | Blocked URL | `{"detail": "Internal IP address not allowed"}` |
| 402 | Insufficient credits | `{"detail": "Insufficient OpenRouter credits..."}` |
| 403 | Invalid API key | `{"detail": "Invalid API Key"}` |
| 500 | Generation failed | `{"detail": "Failed to generate proposal: ..."}` |

**Graceful Degradation:**
- If Gamma fails → Returns proposal without `presentation_url`
- If deep scrape fails → Continues with basic generation
- If primary model fails (402) → Falls back to free Grok model

#### 3.2.2 List Models

```http
GET /agents/proposal/models
```

**Response:**
```json
{
  "models": [
    {"key": "grok", "name": "Grok 4.1 Fast (Free)"},
    {"key": "gpt-4o", "name": "GPT-4o"},
    {"key": "claude-sonnet", "name": "Claude 3.5 Sonnet"},
    {"key": "gemini-pro", "name": "Gemini Pro 1.5"},
    {"key": "deepseek", "name": "DeepSeek Chat"}
  ],
  "default": "grok"
}
```

#### 3.2.3 List Templates

```http
GET /agents/proposal/templates
```

**Response:**
```json
{
  "templates": [
    {
      "key": "default",
      "name": "Trojan Horse",
      "description": "Nick Saraev's high-converting methodology",
      "tone": "direct, professional, value-focused"
    },
    {
      "key": "consultative",
      "name": "Consultative Advisor",
      "description": "Educational, trust-building approach",
      "tone": "warm, educational, empathetic"
    }
  ]
}
```

### 3.3 Secondary Endpoints

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| `GET` | `/` | No | Service info |
| `GET` | `/health` | No | Health check with dependency status |
| `POST` | `/agents/brand/generate` | Yes | Generate presentation/document |
| `POST` | `/agents/knowledge/ingest` | Yes | Scrape and analyze URL |
| `POST` | `/agents/sales/find_leads` | Yes | Search for leads |
| `GET` | `/agents/gamma/themes` | Yes | List Gamma themes |
| `GET` | `/agents/brand/voice` | Yes | Get org brand voice |
| `POST` | `/agents/brand/voice` | Yes | Save org brand voice |
| `GET` | `/telegram/status` | No | Bot status |
| `POST` | `/telegram/start` | Yes | Start Telegram bot |
| `POST` | `/telegram/stop` | Yes | Stop Telegram bot |

### 3.4 Frontend API Routes (Next.js)

These routes are hosted on the Next.js frontend (Vercel) rather than the Python backend.

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/p/[id]` | **Proposal Analytics Redirect**. Logs a view in Convex and redirects to the Gamma presentation URL. |

---

## 4. Data Models

### 4.1 Database Schema (Convex)

```typescript
// convex/schema.ts

// Multi-tenant: ALL tables include orgId for data isolation

proposals: defineTable({
  orgId: v.string(),
  prospectName: v.string(),
  prospectUrl: v.string(),
  painPoints: v.string(),
  content: v.any(),              // ProposalOutput JSON
  presentationUrl: v.optional(v.string()),
  pdfUrl: v.optional(v.string()),
  pptxUrl: v.optional(v.string()),
  status: v.string(),            // 'draft' | 'sent'
  views: v.optional(v.number()), // Analytics: View count
  lastViewedAt: v.optional(v.number()), // Analytics: Timestamp
  createdAt: v.number(),
}).index("by_org", ["orgId"])

leads: defineTable({
  orgId: v.string(),
  companyName: v.string(),
  website: v.optional(v.string()),
  score: v.number(),             // 0-100 quality score
  status: v.string(),            // 'new' | 'contacted' | 'qualified'
  data: v.any(),
  lastContactedAt: v.optional(v.number()),
}).index("by_org", ["orgId"])
  .index("by_status", ["orgId", "status"])

knowledge: defineTable({
  orgId: v.string(),
  url: v.string(),
  summary: v.optional(v.string()),
  entities: v.optional(v.any()),
  embedding: v.optional(v.array(v.float64())),
  ingestedAt: v.number(),
}).index("by_org", ["orgId"])
  .vectorIndex("by_embedding", {
    vectorField: "embedding",
    dimensions: 1536,
    filterFields: ["orgId"],
  })

assets: defineTable({
  orgId: v.string(),
  type: v.string(),              // 'presentation' | 'document' | 'webpage'
  url: v.string(),
  prompt: v.string(),
  status: v.string(),            // 'generating' | 'ready' | 'failed'
  createdAt: v.number(),
}).index("by_org", ["orgId"])

users: defineTable({
  tokenIdentifier: v.string(),   // Clerk user ID
  orgId: v.optional(v.string()),
  role: v.optional(v.string()),
  name: v.optional(v.string()),
  email: v.optional(v.string()),
}).index("by_token", ["tokenIdentifier"])
  .index("by_org", ["orgId"])

audit_logs: defineTable({
  orgId: v.string(),
  action: v.string(),
  actorId: v.optional(v.string()),
  details: v.any(),
  timestamp: v.number(),
}).index("by_org", ["orgId"])
```

### 4.2 AI Agent Output Models

```python
# Proposal Agent Output
class ProposalOutput(BaseModel):
    executive_summary: str      # 2-3 sentence hook
    current_situation: str      # Pain diagnosis from research
    proposed_strategy: str      # Unique mechanism (not generic services)
    why_us: str                 # Brief authority/proof statement
    investment: List[PricingTier]  # Exactly 3 tiers
    next_steps: str             # Single clear CTA

class PricingTier(BaseModel):
    name: str                   # "Starter", "Growth", "Enterprise"
    price: str                  # "$X,XXX/mo" format
    features: List[str]         # 3-5 bullet points
```

### 4.3 Multi-Tenancy

**Default Org:** `demo-org-1` (used when no auth context)

**Org Resolution Order:**
1. Clerk session `orgId` (when auth enabled)
2. Request body `orgId` field
3. Default `demo-org-1`

**Data Isolation:** Every Convex query filters by `orgId`. No cross-org data access is possible at the query level.

### 4.4 Convex Functions Reference

**Proposals (`convex/proposals.ts`):**
- `create` - Create new proposal with audit logging
- `list` - List all proposals for an org (most recent first)
- `get` - Get single proposal by ID
- `updateContent` - Update proposal content/metadata with timestamps
- `updateStatus` - Update proposal status (draft/sent) with audit logging
- `trackView` - Increment view count and update lastViewedAt
- `trackExport` - Log PDF/email exports for analytics

**Knowledge (`convex/knowledge.ts`):**
- `create` - Store ingested knowledge with entities and embeddings
- `list` - List all knowledge entries for an org

**Leads (`convex/leads.ts`):**
- `create` - Store discovered lead with score and metadata
- `list` - List all leads for an org, filterable by status
- `updateStatus` - Update lead status (new/contacted/qualified)

**Assets (`convex/assets.ts`):**
- `create` - Store brand-generated asset (presentation/document/webpage)
- `list` - List all assets for an org
- `get` - Get single asset by ID
- `updateStatus` - Update asset generation status

**Audit Logs (`convex/auditLogs.ts`):**
- `log` - Create audit log entry
- `list` - List audit logs for an org
- `getByAction` - Query logs by action type

**Users (`convex/users.ts`):**
- `viewer` - Get current user from Clerk session

**Actions (`convex/actions/agents.ts`):**
- `callAgentService` - Bridge to Python FastAPI agent service

### 4.5 Frontend Pages & Components

**Dashboard Pages (`web/src/app/dashboard/`):**
- `/dashboard` - Main proposals workspace with list, create, and editor views
- `/dashboard/brand` - Brand asset generation (presentations, documents, webpages)
- `/dashboard/knowledge` - URL ingestion and knowledge base management
- `/dashboard/sales` - Lead discovery and qualification interface
- `/dashboard/settings` - Workspace settings, profile, API keys

**Shared Components (`web/src/components/dashboard/`):**
- `DashboardShell` - Main layout with sidebar, background gradients, and grid pattern
- `DashboardHeader` - Reusable page header with breadcrumbs, title, and actions
- `MetricCard` - Stat display component with icon and value
- `ProposalForm` - Proposal generation form with model/template selection
- `ProposalResult` - Full-featured proposal editor with section-by-section editing
- `brand-widget.tsx`, `knowledge-widget.tsx`, `sales-widget.tsx` - Dashboard widgets

**UI Components (`web/src/components/ui/`):**
- `button.tsx`, `card.tsx`, `input.tsx`, `textarea.tsx`, `skeleton.tsx` - shadcn/ui base components

### 4.6 Team Collaboration (RBAC)

**Roles:**
- `admin`: Full access, can manage team members and billing.
- `member`: Can create/edit proposals, view analytics. Cannot manage team.

**Implementation:**
- `users` table stores `role`.
- Middleware/Convex functions check `role` before sensitive actions (e.g., `inviteUser`, `deleteOrg`).

### 4.7 Custom Domains (White-labeling)

**Architecture:**
- **Provider:** Vercel Custom Domains API.
- **Middleware:** Next.js Middleware (`middleware.ts`) rewrites requests.
  - Incoming: `proposals.agency.com/p/123`
  - Rewrite: `app.propoto.com/preview/123?domain=proposals.agency.com`
- **Verification:** Users add CNAME record. We verify via DNS check.

### 4.8 Public API Architecture

**Authentication:**
- Users generate API keys in Dashboard -> Settings -> API.
- Keys format: `pp_live_<random_string>`.
- Stored as SHA-256 hash in `api_keys` table.

**Rate Limiting:**
- Per-key rate limits stored in Redis (or Convex counter).
- Default: 100 requests/minute per org.


---

## 5. AI Agent Architecture

### 5.1 Agent Framework

All agents use **Pydantic AI** with:
- Structured output validation
- Tool calling for external services
- Retry logic via `tenacity`
- Structured logging via `StructuredLogger`

### 5.2 Proposal Agent

**File:** `agents/proposal_agent.py`

**System Prompt Strategy:**
The agent uses the "Trojan Horse" methodology — a sales framework that gives value upfront:

| Section | Purpose | Prompt Guidance |
|---------|---------|-----------------|
| Executive Summary | Hook | "2-3 sentences showing you understand THEIR specific situation" |
| Current Situation | Diagnosis | "Analyze their pain based on the research, not generic problems" |
| Proposed Strategy | Unique Mechanism | "A specific strategy, not 'we do SEO'" |
| Why Us | Authority | "Brief — 1-2 sentences of proof" |
| Investment | Pricing | "3 tiers: foot-in-door, core offering, anchor" |
| Next Steps | CTA | "Single action: 'Book a 15-min call'" |

**Model Selection:**

| Key | Model Path | Cost | Notes |
|-----|------------|------|-------|
| `grok` | `x-ai/grok-4.1-fast:free` | Free | Default, expires Dec 2025 |
| `grok-fast` | `x-ai/grok-4.1-fast:free` | Free | Alias |
| `gpt-4o` | `openai/gpt-4o` | ~$5/1M | High quality |
| `gpt-4o-mini` | `openai/gpt-4o-mini` | ~$0.15/1M | Budget option |
| `claude-sonnet` | `anthropic/claude-3.5-sonnet` | ~$3/1M | Great writing |
| `gemini-pro` | `google/gemini-pro-1.5` | ~$1.25/1M | Long context |
| `deepseek` | `deepseek/deepseek-chat` | ~$0.14/1M | Budget option |

**Template System:**

| Key | Name | Tone | Best For |
|-----|------|------|----------|
| `default` | Trojan Horse | Direct, value-focused | Most agencies |
| `consultative` | Consultative Advisor | Warm, educational | Complex sales |
| `enterprise` | Enterprise Professional | Formal, data-driven | Large companies |
| `startup` | Startup Partner | Energetic, agile | Startups |
| `agency` | Agency Partnership | Collaborative | Agency-to-agency |

### 5.3 Deep Scraping Service

**File:** `services/scraping_service.py`

Enriches proposals with website intelligence when `deep_scrape: true`:

```python
class BusinessIntelligence(BaseModel):
    company_name: str
    industry: str
    value_proposition: str
    target_audience: str
    products_services: List[str]
    key_features: List[str]
    pain_points_identified: List[str]
    competitors_mentioned: List[str]
    social_proof: List[str]
    tech_stack_hints: List[str]
    tone_style: str
```

**Flow:**
1. Firecrawl scrapes prospect URL
2. LLM extracts structured intelligence
3. Intelligence injected into proposal prompt
4. Result: More personalized proposals

### 5.4 Knowledge Agent

**File:** `agents/knowledge.py`

**Purpose:** Scrape and analyze URLs to build organizational intelligence graph.

**Output Model:**
```python
class KnowledgeOutput(BaseModel):
    summary: str
    entities: List[Entity]
    relevance_score: float

class Entity(BaseModel):
    name: str
    type: str  # 'person', 'company', 'product', 'technology', etc.
    details: dict
```

**Flow:**
1. Firecrawl scrapes URL content
2. LLM extracts entities and relationships
3. Stores in Convex with embeddings for RAG
4. Used to enrich future proposals

**Endpoint:** `POST /agents/knowledge/ingest`

### 5.5 Sales Agent

**File:** `agents/sales.py`

**Purpose:** Discover and qualify leads using Exa search.

**Output Model:**
```python
class SalesOutput(BaseModel):
    leads: List[Lead]
    market_summary: str

class Lead(BaseModel):
    company_name: str
    website: str
    description: str
    score: int  # 0-100 quality score
```

**Flow:**
1. Exa API searches for companies matching query
2. LLM scores and qualifies leads
3. Stores in Convex with status tracking
4. Dashboard displays leads with filtering

**Endpoint:** `POST /agents/sales/find_leads`

### 5.6 Brand Agent

**File:** `agents/brand.py`

**Purpose:** Generate brand assets (presentations, documents, webpages) using Gamma API.

**Output Model:**
```python
class BrandAsset(BaseModel):
    url: str  # Gamma presentation/document URL
    format: str  # 'presentation', 'document', 'webpage'
    status: str  # 'generating', 'ready', 'failed'
```

**Flow:**
1. User provides prompt and format selection
2. Gamma API generates asset
3. Stores in Convex assets table
4. Dashboard displays generated assets

**Endpoint:** `POST /agents/brand/generate`

**Brand Voice Memory:**
- `GET /agents/brand/voice` - Retrieve org brand guidelines
- `POST /agents/brand/voice` - Save brand voice configuration
- Uses Mem0 for persistent brand memory per organization

---

## 6. External Integrations

### 6.1 OpenRouter (LLM Gateway)

**Base URL:** `https://openrouter.ai/api/v1`
**Auth:** `Authorization: Bearer <OPENROUTER_API_KEY>`

**Integration Pattern:**
```python
from pydantic_ai.models.openai import OpenAIChatModel

model = OpenAIChatModel("x-ai/grok-4.1-fast:free", provider='openrouter')
```

**Error Handling:**
- 402 (Payment Required) → Fallback to free model
- 429 (Rate Limit) → Exponential backoff
- 5xx → Retry with backoff

### 6.2 Gamma API (Deck Generation)

**Base URL:** `https://public-api.gamma.app/v1.0`
**Auth:** `X-API-Key: <GAMMA_API_KEY>`

**Generation Flow:**
```
POST /generations → {"id": "gen_xxx", "status": "PENDING"}
     ↓
GET /generations/{id} (poll every 5s, max 30 attempts)
     ↓
{"status": "COMPLETED", "gammaUrl": "...", "pdfUrl": "...", "pptxUrl": "..."}
```

**Payload Example:**
```json
{
  "inputText": "Create a sales proposal for...",
  "textMode": "generate",
  "format": "presentation",
  "numCards": 7,
  "textOptions": {"tone": "professional", "amount": "detailed"},
  "imageOptions": {"source": "aiGenerated", "model": "flux-1-pro"},
  "exportAs": "pdf"
}
```

**Graceful Degradation:** If Gamma fails, return proposal without deck URLs.

### 6.3 Firecrawl (Web Scraping)

**Cloud URL:** `https://api.firecrawl.dev`
**Self-Hosted:** Configurable via `FIRECRAWL_API_URL` (default: `http://localhost:3002`)

**Usage:**
```python
app = FirecrawlApp(api_key=key, api_url=url)
result = app.scrape_url(url, params={'formats': ['markdown']})
```

### 6.4 Mem0 (Brand Memory)

**Purpose:** Store per-org brand voice and guidelines

**Usage:**
```python
from mem0 import Memory
memory = Memory(api_key=key)
memory.add(messages=[...], user_id=f"brand_{org_id}")
memory.search(query="brand guidelines", user_id=f"brand_{org_id}")
```

### 6.5 Exa (Lead Search)

**Purpose:** Find leads matching criteria

**Usage:** Via Sales Agent tool `search_leads(query)`

---

## 7. Security

### 7.1 Implemented Security Measures

| Measure | Implementation | Location |
|---------|----------------|----------|
| **API Key Auth** | `x-api-key` header validation | `main.py:verify_key()` |
| **CORS** | Configurable origins | `main.py:CORSMiddleware` |
| **URL Validation** | SSRF protection | `main.py:validate_url_security()` |
| **Multi-tenancy** | orgId on all records | All Convex tables |
| **Secrets Management** | Environment variables only | `.env` files |
| **Audit Logging** | All mutations logged | `convex/auditLogs.ts` |

### 7.2 URL Security Validation

Blocks requests to internal/dangerous URLs:

```python
BLOCKED_IP_RANGES = [
    '10.0.0.0/8',      # Private
    '172.16.0.0/12',   # Private
    '192.168.0.0/16',  # Private
    '127.0.0.0/8',     # Loopback
    '169.254.0.0/16',  # Link-local (cloud metadata)
]

BLOCKED_HOSTNAMES = ['localhost', 'internal', 'metadata']
```

### 7.3 Future Security Enhancements

| Enhancement | Priority | Notes |
|-------------|----------|-------|
| Rate limiting per org | P1 | Prevent abuse |
| Request signing | P2 | Webhook verification |
| Key rotation | P2 | Zero-downtime rotation |
| Input sanitization | P2 | XSS prevention on outputs |
| Encryption at rest | P3 | Convex handles by default |

### 7.4 Rate Limiting
Implemented via `slowapi` (Redis/Memory backed) to prevent abuse.

**Limits:**
- `POST /agents/proposal/generate`: **5/minute**
- `POST /agents/brand/generate`: **5/minute**
- `POST /agents/knowledge/ingest`: **10/minute**
- `POST /agents/sales/find_leads`: **10/minute**

**Response (429):**
```json
{
  "error": "Rate limit exceeded: 5 per 1 minute"
}
```

---

## 8. Error Handling

### 8.1 Retry Strategy

All external API calls use `tenacity`:

```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def external_api_call():
    ...
```

| Service | Max Attempts | Backoff |
|---------|--------------|---------|
| OpenRouter | 3 | 2s → 4s → 8s |
| Gamma | 2 | 2s → 4s |
| Firecrawl | 3 | 2s → 4s → 8s |
| Mem0 | 3 | 2s → 4s → 8s |

### 8.2 Graceful Degradation

| Failure | Degraded Behavior |
|---------|-------------------|
| Gamma API down | Return proposal without deck |
| Mem0 unavailable | Use default brand guidelines |
| Firecrawl fails | Skip deep scrape, generate anyway |
| Primary model 402 | Fallback to free Grok |
| Convex save fails | Log error, return success to user |

### 8.3 Error Response Format

```json
{
  "error": "Human-readable message",
  "error_code": "EXT_001",
  "detail": "Technical detail (if DEBUG=true)",
  "retryable": true,
  "retry_after_seconds": 60
}
```

---

## 9. Observability

### 9.1 Logging

**Logger:** `StructuredLogger` with context tracking

```python
# Automatic context injection
structured_logger.info(
    "Proposal generated",
    prospect_name="Acme",
    model="grok",
    duration_seconds=12.5
)
```

**Log Levels:**
- `DEBUG`: Tool calls, intermediate steps
- `INFO`: Request start/end, success
- `WARNING`: Degraded behavior, fallbacks
- `ERROR`: Failures, exceptions
- `CRITICAL`: Service misconfiguration

### 9.2 Metrics to Track (Future)

| Metric | Type | Purpose |
|--------|------|---------|
| `proposal_generation_seconds` | Histogram | Performance |
| `proposal_generation_total` | Counter | Usage |
| `proposal_generation_errors` | Counter | Reliability |
| `llm_tokens_used` | Counter | Cost tracking |
| `gamma_success_rate` | Gauge | Integration health |

### 9.3 Health Check

```http
GET /health
```

```json
{
  "status": "healthy",
  "environment": {
    "openrouter": true,
    "gamma": true,
    "mem0": false,
    "firecrawl": true,
    "convex": true
  }
}
```

---

## 10. Deployment

### 10.1 Frontend (Next.js)

**Platform:** Vercel (recommended)

```bash
cd web
npm install
npm run build
npm start  # or deploy to Vercel
```

**Environment Variables:**
```env
NEXT_PUBLIC_CONVEX_URL=https://xxx.convex.cloud
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
AGENT_SERVICE_KEY=your-secret-key
```

### 10.2 Backend (FastAPI)

**Platform:** Railway, Render, or Fly.io (recommended)

```bash
cd api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

**Environment Variables:**
```env
OPENROUTER_API_KEY=sk-or-v1-xxx
AGENT_SERVICE_KEY=your-secret-key
GAMMA_API_KEY=sk-gamma-xxx
FIRECRAWL_API_KEY=fc-xxx  # or self-hosted
FIRECRAWL_API_URL=http://localhost:3002  # if self-hosted
MEM0_API_KEY=m0-xxx
EXA_API_KEY=xxx
CORS_ORIGINS=https://yourdomain.com,http://localhost:3000
```

### 10.3 Database (Convex)

```bash
cd web
npx convex dev      # Development
npx convex deploy   # Production
```

### 10.4 Docker (Future)

```dockerfile
# api/Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 11. Testing

### 11.1 Backend Tests

```bash
cd api
pytest tests/ -v
```

**Test Structure:**
```
tests/
├── conftest.py          # Fixtures
├── test_main.py         # API endpoint tests
├── test_agents.py       # Agent unit tests
└── test_e2e_validation.py  # Integration tests
```

### 11.2 Frontend Tests

```bash
cd web
npm test
```

**Coverage Target:** 60% (currently ~10%)

### 11.3 Manual Testing

See [MANUAL_TESTING_GUIDE.md](../testing/MANUAL_TESTING_GUIDE.md) for test scenarios.

---

## 12. Development Workflow

### 12.1 Local Setup

```bash
# Terminal 1: Backend
cd propoto/api
source venv/bin/activate
python main.py

# Terminal 2: Frontend
cd propoto/web
npm run dev

# Terminal 3: Convex
cd propoto/web
npx convex dev
```

### 12.2 Code Standards

| Area | Standard |
|------|----------|
| Python formatting | Black, isort |
| TypeScript formatting | Prettier |
| Linting | ESLint (frontend), Ruff (backend) |
| Types | Strict TypeScript, Pydantic models |
| Git | Conventional commits |

### 12.3 PR Checklist

- [ ] Tests pass
- [ ] No linter errors
- [ ] Types correct
- [ ] Graceful degradation maintained
- [ ] Environment variables documented
- [ ] SPEC.md updated if APIs changed

---

## 13. Known Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| Gamma single source | High | Graceful degradation; consider Puppeteer fallback |
| No rate limiting | Medium | Implement per-org limits |
| Grok free tier expires Dec 2025 | Medium | Model fallback chain implemented |
| No frontend tests | Medium | Add before scaling |
| No distributed tracing | Low | Add OpenTelemetry later |

---

## 14. Changelog

### v3.1 (January 2026)
- Added comprehensive Convex functions documentation (proposals, knowledge, leads, assets, audit logs)
- Documented all frontend dashboard pages (proposals, brand, knowledge, sales, settings)
- Added Knowledge, Sales, and Brand agent architecture details
- Documented shared component system (DashboardShell, DashboardHeader, MetricCard)
- Updated frontend experience architecture with Cursor-inspired design system
- Added proposal editor implementation details (section-by-section editing, status tracking)

### v3.0 (December 2025)
- Restructured to align with PRD v3.0
- Added security section (CORS, SSRF protection)
- Added cost constraints and SLAs
- Removed changelog-style status tracking
- Added deployment and observability sections

### v2.1 (December 2025)
- Added Gamma API v1.0 integration
- Added deep scraping service
- Added brand voice memory
- Added Telegram bot

### v2.0 (November 2025)
- Initial multi-agent architecture
- Convex integration
- Model selection system

---

*This document is maintained by Engineering. For product context, see [PRD.md](../product/PRD.md).*
