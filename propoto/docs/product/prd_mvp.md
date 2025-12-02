# Product Requirements Document: Propoto (MVP)

**Version:** 1.0 (MVP Focus)
**Status:** Active
**Last Updated:** January 2026
**Owner:** Product Team

---

## 1. Executive Summary

### The Problem
Digital agencies lose deals because proposals take too long and look too generic.
- **Average proposal time:** 4.5 hours
- **Cost per proposal:** $675 in labor
- **Win rate (templated):** 8-12%

### The Solution
Propoto generates personalized, research-backed sales proposals with visual presentation decks in under 60 seconds.
**One-liner:** *"Turn a prospect URL into a $10K proposal in 60 seconds."*

### Why Us
1.  **Integrated stack:** Research → Writing → Visual Deck in one flow.
2.  **Methodology-driven:** Built on the "Trojan Horse" sales framework.
3.  **Brand memory:** System learns your voice over time.

---

## 2. Core Value Proposition

**For** digital agency sales leaders
**Who** need to send more proposals without hiring more people
**Propoto is** an AI proposal generator
**That** creates personalized, visually polished proposals in 60 seconds
**Unlike** PandaDoc, Qwilr, or ChatGPT
**We** combine deep research, proven sales methodology, and automatic deck generation in one integrated flow.

---

## 3. User Journey (MVP Flow)

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   INPUT     │───▶│   PROCESS   │───▶│   OUTPUT    │───▶│   ACTION    │
│             │    │             │    │             │    │             │
│ • Prospect  │    │ • Scrape    │    │ • Proposal  │    │ • Send      │
│   URL       │    │   website   │    │   text      │    │ • Export    │
│ • Pain      │    │ • Analyze   │    │ • Gamma     │    │ • Edit      │
│   points    │    │   context   │    │   deck      │    │ • Save      │
│ • Settings  │    │ • Generate  │    │ • PDF/PPTX  │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
     10 sec            45-60 sec           Instant           User choice
```

---

## 4. Feature Set (MVP)

### ✅ Core Capabilities (Live)

| Feature | Purpose | Status |
|---------|---------|--------|
| **Core proposal generation** | Primary value | ✅ Live |
| **Gamma deck integration** | Visual differentiation | ✅ Live |
| **Model selection** | Flexibility (7 LLMs) | ✅ Live |
| **Template styles** | Customization (5 styles) | ✅ Live |
| **Deep website scraping** | Better research | ✅ Live |
| **Brand voice memory** | Personalization | ✅ Live |
| **Proposal history** | Workflow | ✅ Live |
| **PDF/PPTX export** | Distribution | ✅ Live |
| **Email draft generation** | Distribution | ✅ Live |
| **Proposal analytics** | View tracking via redirect | ✅ Live |
| **Proposal editor** | Allow tweaks before sending | ✅ Live |

### ✅ AI Agents (Live)

| Agent | Purpose | Status |
|-------|---------|--------|
| **Knowledge Agent** | Ingest URLs to build intelligence graph | ✅ Live |
| **Sales Agent** | Find qualified prospects via Exa | ✅ Live |
| **Brand Agent** | Create standalone presentations/docs | ✅ Live |

### ✅ Integrations (Live)

| Feature | Purpose | Status |
|---------|---------|--------|
| **Telegram Bot** | Mobile access to agents | ✅ Live |

### ✅ Infrastructure (Live)

| Component | Purpose | Status |
|-----------|---------|--------|
| **Multi-tenancy** | Data isolation by org | ✅ Live |
| **Rate Limiting** | Prevent abuse | ✅ Live |
| **Audit Logging** | Security & debugging | ✅ Live |

---

## 5. Success Metrics (MVP)

### North Star
**Proposals That Get Replies**

### Key Performance Indicators
1.  **Time to first proposal:** < 5 min
2.  **Generation time:** < 60 sec
3.  **Deck generation success rate:** > 85%
4.  **Error rate:** < 5%

---

## 6. Unit Economics

| Component | Cost | Notes |
|-----------|------|-------|
| LLM (OpenRouter) | $0.05 | Grok free tier / GPT-4o mix |
| Gamma API | $0.10 | Per deck generated |
| Firecrawl | $0.02 | Per scrape |
| Infrastructure | $0.01 | Convex + hosting |
| **Total COGS** | **$0.18** | **Per proposal** |

**Target Gross Margin:** >90% ✅

---

## 7. Known Limitations (MVP)

These features are explicitly **NOT** in the MVP:
-   No CRM integrations (HubSpot/Salesforce).
-   No E-signatures (Use DocuSign/PandaDoc).
-   No Team Collaboration (Single user per org for now).
-   No Custom Domains.
-   No Public API.

---

## 8. Next Steps (Post-MVP Polish)

1.  **Editor Improvements**: Add more formatting options.
2.  **Onboarding**: Create a guided tour for new users.
3.  **Dashboard Polish**: Improve interactivity of Sales/Knowledge widgets.
