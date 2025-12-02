# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project Overview

**Rhigden's digital workspace** for building **Snyto (The AgencyOS)** - AI Agency business.  
**Mission**: $500k ARR by Dec 2026

---

## Repository Structure

```
newshii/
├── propoto/          # Main Product - AI Proposal Generator (ACTIVE ⭐)
├── Synto_P0/         # Knowledge Management (Obsidian vault)
├── knowledge_base/    # Technical Reference
└── CLAUDE.md         # This file
```

---

## Main Project: propoto/

**AI proposal generator** for digital agencies. Generates proposals in <60s with Gamma decks.

### Tech Stack

**Frontend**: Next.js 15.0.3, React 18.3.1, TypeScript 5.x, Tailwind CSS 4.x, Convex 1.29.3+, Clerk 6.0.0  
**Backend**: FastAPI 0.115.0+, Python 3.12+, Pydantic AI 1.25.0+  
**Services**: OpenRouter, Gamma API v1.0, Firecrawl, Mem0, Exa

### Quick Start

```bash
# Frontend
cd propoto/web && npm run dev          # http://localhost:3000

# Backend  
cd propoto/api && python main.py       # http://localhost:8000

# Database
cd propoto/web && npx convex dev
```

### Key Directories

- `propoto/web/src/` - Next.js frontend (App Router)
- `propoto/web/convex/` - Convex DB schema & functions
- `propoto/api/agents/` - AI agents (proposal, brand, knowledge, sales)
- `propoto/api/services/` - External integrations (Gamma, Firecrawl, Mem0)
- `propoto/docs/` - Documentation (organized in subfolders)

### AI Agents

| Agent | Purpose |
|-------|---------|
| **Proposal** | Generate sales proposals (Trojan Horse methodology, 7 LLMs, 5 templates) |
| **Brand** | Create Gamma presentations from proposals |
| **Knowledge** | Scrape & analyze URLs for business intelligence |
| **Sales** | Discover leads via Exa search |

### Status: Phase 1 MVP ✅ Complete

**Features**: Proposal generation, Gamma decks, model selection, deep scraping, brand memory, proposal history, dashboard, Telegram bot  
**Remaining**: Audit logging, direct PDF export, email drafts, Clerk auth (Phase 2)

---

## Development Guidelines

### Multi-tenancy
Always scope by `orgId`. Default: `"demo-org-1"`. All Convex queries must filter by `orgId`.

### API Auth
All agent endpoints require: `x-api-key: <AGENT_SERVICE_KEY>` header.

### Gamma API
- Base: `https://public-api.gamma.app/v1.0`
- Auth: `X-API-Key: sk-gamma-xxxxx`
- Flow: POST `/generations` → poll GET `/generations/{id}` every 5s

### Error Handling
- Graceful degradation: Gamma fails → return proposal without deck
- Retry: All APIs use `tenacity` exponential backoff
- SSRF protection: URL validation blocks private IPs

---

## Important Files

| File | Purpose |
|------|---------|
| `propoto/docs/product/PRD.md` | Product requirements v3.0 |
| `propoto/docs/technical/SPEC.md` | Technical spec v3.0 |
| `propoto/docs/technical/TECH_STACK_AUDIT.md` | Stack versions & audit |
| `propoto/api/main.py` | FastAPI routes & middleware |
| `propoto/api/agents/proposal_agent.py` | Core proposal generation |
| `propoto/web/convex/schema.ts` | Database schema (multi-tenant) |

---

## Environment Variables

**Required**:
```env
OPENROUTER_API_KEY=sk-or-v1-xxx
AGENT_SERVICE_KEY=your-secret
```

**Optional**:
```env
GAMMA_API_KEY=sk-gamma-xxx
MEM0_API_KEY=m0-xxx
EXA_API_KEY=xxx
FIRECRAWL_API_KEY=fc-xxx
NEXT_PUBLIC_CONVEX_URL=xxx
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Documentation

**Hub**: `propoto/docs/README.md`

**Key Docs**:
- `product/PRD.md` - Product requirements
- `technical/SPEC.md` - Technical architecture
- `technical/TECH_STACK_AUDIT.md` - Stack audit
- `gtm/` - Go-to-market, sales, marketing
- `operations/` - Pricing, competitive intel, customer success
- `launch/` - Launch checklist, pitch deck
- `testing/` - Testing guides

---

## Code Standards

**Python**: Black, isort, Ruff, Pydantic models, pytest  
**TypeScript**: Prettier, ESLint 9, strict mode, Jest 30

---

## Architecture Principles

1. Stateless backend (horizontal scaling)
2. Multi-tenant by default (`orgId` scoped)
3. Graceful degradation (core works if integrations fail)
4. Cost-conscious AI (default to free/cheap models)
5. Real-time where it matters (Convex)

---

## Builder Psychology

**Two Mountains**: Systems (building, shipping, revenue) + Soul (anxiety management, Deep Work)  
**Anti-Perfectionism**: Break tasks >1hr into 15-min micro-sprints

---

*Last Updated: January 2026 | Status: Phase 1 MVP Complete*
