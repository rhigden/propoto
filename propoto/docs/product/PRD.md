# Product Requirements Document: Propoto

**Version:** 3.1  
**Status:** Active  
**Last Updated:** January 2026  
**Owner:** Product Team

---

## 1. Executive Summary

### The Problem (Validated)

Digital agencies lose deals because proposals take too long and look too generic.

**Evidence from Customer Discovery (n=15 agency owners, Nov 2025):**

> "I spend 3 hours researching a prospect, 2 hours writing, and another hour making it look good. Then I lose to someone who responded in 24 hours." — Agency owner, 12 employees

| Pain Point | Frequency | Severity (1-5) |
|------------|-----------|----------------|
| Research takes longer than writing | 12/15 | 4.2 |
| Generic templates hurt close rates | 11/15 | 4.5 |
| No time for custom presentation decks | 9/15 | 3.8 |
| Can't scale without hiring more salespeople | 8/15 | 4.0 |

**Quantified Cost:**
- Average proposal time: **4.5 hours**
- Average agency hourly rate: **$150**
- Cost per proposal: **$675 in labor**
- Win rate on templated proposals: **8-12%**
- Win rate on customized proposals: **25-35%**

### The Solution

Propoto generates personalized, research-backed sales proposals with visual presentation decks in under 60 seconds.

**One-liner:** *"Turn a prospect URL into a $10K proposal in 60 seconds."*

### Why Now

1. **LLM costs collapsed** — GPT-5.1 Mini/GROK 4.1 FAST/Haiku 4.5/GLM 4.6 class models now free/cheap via OpenRouter
2. **Gamma API launched** — First programmatic access to AI presentation generation
3. **Agency market pain is acute** — Economic pressure forcing efficiency gains
4. **AI fatigue setting in** — Generic ChatGPT outputs no longer impress; structured, branded output wins

### Why Us

1. **Integrated stack** — Only solution combining research → writing → visual deck in one flow
2. **Methodology-driven** — Built on proven "Trojan Horse" sales framework (see Section 4)
3. **Agency DNA** — Built by agency operators who lived this pain
4. **Brand memory** — Proposals get better over time as system learns your voice

---

## 2. Market Opportunity

### Total Addressable Market (TAM)

| Segment | Count | Avg. Proposal Software Spend | TAM |
|---------|-------|------------------------------|-----|
| Digital agencies (US) | 45,000 | $3,600/year | $162M |
| Marketing consultants (US) | 120,000 | $1,200/year | $144M |
| Freelance marketers (US) | 500,000 | $300/year | $150M |
| **Total US TAM** | | | **$456M** |

### Serviceable Addressable Market (SAM)

Focus: Digital agencies with 5-50 employees actively sending 10+ proposals/month

- **~12,000 agencies** in this segment
- **$3,600/year** average spend on proposal tools
- **SAM: $43M**

### Serviceable Obtainable Market (SOM) — Year 1

- **Target: 200 paying customers** @ $200/month average
- **SOM: $480K ARR**

### Market Trends Supporting Growth

1. **Proposal software market growing 12% CAGR** (Grand View Research, 2024)
2. **AI adoption in sales tools at 67%** among agencies (HubSpot State of Sales, 2024)
3. **Response time is #1 factor** in agency selection (Agency Spotter survey)

---

## 3. Customer Discovery

### Primary Persona: Agency Sales Leader

**Composite Profile (based on 15 interviews):**

| Attribute | Detail |
|-----------|--------|
| **Role** | Founder, Sales Director, or Business Development Lead |
| **Company Size** | 5-50 employees |
| **Proposals/Month** | 10-30 |
| **Current Tools** | Google Docs + Canva, or PandaDoc/Qwilr |
| **Tech Comfort** | High — uses Notion, Slack, Zapier daily |
| **Budget Authority** | Yes, for tools under $500/month |

**Jobs to Be Done:**
1. Respond to RFPs faster than competitors
2. Look more professional/established than we are
3. Close deals without hiring more salespeople
4. Stop doing repetitive research for every prospect

**Current Workarounds:**
- Copy-paste from old proposals (loses relevance)
- Use ChatGPT for drafts (generic, no visuals)
- Hire junior staff to research (slow, expensive)
- Skip custom decks entirely (hurts win rate)

**Key Quote:**
> "I'd pay $500/month just to never write another proposal intro paragraph. That's the worst part — trying to sound like I know their business when I just skimmed their website." — Sarah K., 15-person agency

### Secondary Persona: Solo Consultant

| Attribute | Detail |
|-----------|--------|
| **Role** | Independent marketing consultant |
| **Proposals/Month** | 3-8 |
| **Current Tools** | Google Docs, Canva free tier |
| **Budget** | $50-150/month for tools |
| **Key Need** | Look like a bigger operation |

**Deprioritized for MVP** — Will revisit in Phase 2 with lower-cost tier.

### Willingness to Pay (from interviews)

| Price Point | % Would Pay | Notes |
|-------------|-------------|-------|
| $99/month | 80% | "No-brainer if it works" |
| $199/month | 60% | "If it saves me 3+ hours per proposal" |
| $299/month | 40% | "Would need to see ROI proof" |
| $499/month | 15% | "Only if unlimited + team features" |

**Recommended launch price: $149/month** (positions as premium, leaves room for enterprise)

---

## 4. Product Strategy

### Core Value Proposition

**For** digital agency sales leaders  
**Who** need to send more proposals without hiring more people  
**Propoto is** an AI proposal generator  
**That** creates personalized, visually polished proposals in 60 seconds  
**Unlike** PandaDoc, Qwilr, or ChatGPT  
**We** combine deep research, proven sales methodology, and automatic deck generation in one integrated flow.

### The "Trojan Horse" Methodology

Our proposal structure is based on the **Trojan Horse framework** popularized by Nick Saraev — a methodology that converts by giving value upfront:

| Section | Purpose | Psychology |
|---------|---------|------------|
| **Executive Summary** | Hook with specific insight about THEIR business | "They actually understand us" |
| **Current Situation** | Diagnose their specific pain (from research) | "They did their homework" |
| **Proposed Strategy** | Unique mechanism — not generic services | "This is different" |
| **Why Us** | Social proof / authority (brief) | "They can deliver" |
| **Investment** | 3 tiers: Foot-in-door, Core, Anchor | Anchoring psychology |
| **Next Steps** | Single clear CTA | Reduce friction |

**Why it works:** The proposal itself demonstrates competence. By showing you understand their business, you've already proven value before the sales call.

### Key Differentiators

| Differentiator | Why It Matters | Defensibility |
|----------------|----------------|---------------|
| **Integrated research** | Competitors require manual input | Firecrawl + LLM pipeline |
| **Auto-generated decks** | No one else has Gamma integration | First-mover + API relationship |
| **Methodology-driven** | Not just AI — structured framework | Prompts encode sales expertise |
| **Brand memory** | Proposals improve over time | Mem0 integration per org |
| **Cursor-inspired workspace** | Familiar, high-focus UI that speeds editing | Reusable component system, rapid iteration |

### What We Will NOT Build

To stay focused, we explicitly deprioritize:

| Feature | Why Not |
|---------|---------|
| **CRM replacement** | Integrate with existing CRMs instead |
| **Contract signing** | PandaDoc/DocuSign already solve this |
| **Invoicing** | Out of scope — proposal tool only |
| **General content writing** | We're proposal-specific, not Jasper |
| **White-label (Phase 1)** | Complexity before PMF |

---

## 5. Competitive Landscape

### Direct Competitors

| Product | Strengths | Weaknesses | Our Advantage |
|---------|-----------|------------|---------------|
| **PandaDoc** | Market leader, e-signatures, CRM integrations | AI features basic, no auto-research, no deck gen | Full automation, better AI |
| **Qwilr** | Beautiful templates, interactive proposals | Manual writing, limited AI, no research | AI-native, research included |
| **Proposify** | Good for teams, approval workflows | Dated UI, no AI, template-dependent | Modern UX, AI-powered |
| **Better Proposals** | Simple, affordable | Very basic, no AI | Full feature set |

### Indirect Competitors

| Product | Threat Level | Why We Win |
|---------|--------------|-----------|
| **ChatGPT + Canva** | High | Integrated flow vs. copy-paste between tools |
| **Custom GPTs** | Medium | Brand memory, Gamma integration, no setup |
| **Jasper** | Low | Generic content vs. proposal-specific |
| **Freelance writers** | Medium | Speed (60 sec vs. 48 hours) |

### Positioning Statement

> "PandaDoc is for sending proposals. AgencyOS is for winning them."

We don't compete on contract management or e-signatures. We compete on **conversion rate** — the quality and speed of the proposal itself.

---

## 6. User Journey

### Primary Flow: Generate a Proposal

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   INPUT     │───▶│   PROCESS   │───▶│   OUTPUT    │───▶│   ACTION    │
│             │    │             │    │             │    │             │
│ • Prospect  │    │ • Scrape    │    │ • Proposal  │    │ • Send      │
│   URL       │    │   website   │    │   text      │    │ • Export    │
│ • Pain      │    │ • Analyze   │    │ • Gamma     │    │ • Edit      │
│   points    │    │   context   │    │   deck      │    │ • Save      │
│ • (Optional)│    │ • Generate  │    │ • PDF/PPTX  │    │             │
│   settings  │    │   content   │    │   links     │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
     10 sec            45-60 sec           Instant           User choice
```

### Success Criteria by Stage

| Stage | User Goal | Success Metric |
|-------|-----------|----------------|
| **Onboarding** | Generate first proposal | Time to first proposal < 5 min |
| **Activation** | Send proposal to real prospect | 1+ proposals sent within 7 days |
| **Engagement** | Regular usage | 3+ proposals/week |
| **Retention** | Continued value | 4+ weeks active |
| **Revenue** | Convert to paid | Trial → Paid conversion > 15% |

---

## 7. Feature Roadmap

### Now (Launched)

| Feature | Purpose | Status |
|---------|---------|--------|
| Core proposal generation | Primary value | ✅ Live |
| Gamma deck integration | Visual differentiation | ✅ Live |
| Model selection (7 LLMs) | Flexibility | ✅ Live |
| Template styles (5) | Customization | ✅ Live |
| Deep website scraping | Better research | ✅ Live |
| Brand voice memory | Personalization | ✅ Live |
| Proposal history | Workflow | ✅ Live |
| PDF/PPTX export | Distribution | ✅ Live |
| Email draft generation | Distribution | ✅ Live |
| Telegram bot | Mobile access | ✅ Live |
| Proposal editor | Allow tweaks before sending | ✅ Live |
| Cursor-inspired dashboard shell | Faster navigation + clarity | ✅ Live |
| Knowledge agent (URL ingestion) | Build intelligence graph | ✅ Live |
| Sales agent (lead discovery) | Find qualified prospects | ✅ Live |
| Brand agent (asset generation) | Create presentations/documents | ✅ Live |
| Audit logging | Security & debugging | ✅ Live |
| Settings page | Workspace management | ✅ Live |
| Multi-tenant architecture | Data isolation by org | ✅ Live |

### Next (Post-MVP)

| Feature | Purpose | Priority |
|---------|---------|----------|
| **HubSpot/Salesforce** | CRM integrations | P1 |
| **Team Collaboration** | Multi-user orgs | P2 |
| **Custom Domain Hosting** | White-label proposals | P2 |
| **Public API Access** | Programmatic access | P2 |

### Not Planned (MVP)

| Feature | Reason |
|---------|--------|
| **E-signatures** | Use DocuSign/PandaDoc |
| **Invoicing** | Out of scope |

---

## 8. Success Metrics

### North Star Metric

**Proposals That Get Replies**

*Why:* Measures actual customer value delivered. A sent proposal that gets a response (positive or negative) proves the proposal was good enough to engage.

*Tracking:* Email open tracking (Phase 2) + self-reported outcomes

### Leading Indicators

| Metric | Target | Why It Matters |
|--------|--------|----------------|
| Time to first proposal | < 5 min | Activation signal |
| Proposals per active user/week | 3+ | Engagement signal |
| Deck generation success rate | > 85% | Feature reliability |
| Generation time | < 60 sec | Core promise |

### Guardrail Metrics

| Metric | Threshold | Action if Breached |
|--------|-----------|-------------------|
| Error rate | < 5% | Investigate immediately |
| LLM cost per proposal | < $0.50 | Optimize prompts or switch models |
| Gamma timeout rate | < 15% | Improve retry logic |

### Business Metrics

| Metric | Target (Month 6) | Target (Month 12) |
|--------|------------------|-------------------|
| Active users | 100 | 500 |
| Paying customers | 50 | 200 |
| MRR | $7,500 | $30,000 |
| Trial → Paid conversion | 15% | 20% |
| Monthly churn | < 8% | < 5% |

---

## 9. Go-to-Market Strategy

### Launch Strategy (Dec 2025 - Jan 2026)

**Phase 1: Private Beta (5 users)**
- Hand-pick 5 agency owners from network
- Daily feedback sessions
- Iterate rapidly on pain points

**Phase 2: Expanded Beta (50 users)**
- Launch on Product Hunt
- Agency community posts (Reddit r/agency, Facebook groups)
- LinkedIn content from founder

**Phase 3: Public Launch**
- Pricing page live
- Free trial (14 days, 10 proposals)
- Content marketing engine running

### Pricing Model

| Tier | Price | Proposals/Month | Features |
|------|-------|-----------------|----------|
| **Starter** | $99/mo | 20 | Core features, 1 user |
| **Growth** | $199/mo | 50 | + Brand memory, templates |
| **Agency** | $399/mo | Unlimited | + Team (5 users), priority support |
| **Enterprise** | Custom | Unlimited | + SSO, custom integrations |

**Free Tier:** 3 proposals (one-time) to demonstrate value

### Distribution Channels

| Channel | Effort | Expected Impact | Timeline |
|---------|--------|-----------------|----------|
| Product Hunt | Medium | 500 signups | Month 1 |
| Agency communities | Low | 200 signups | Ongoing |
| LinkedIn content | Medium | 100 signups/mo | Ongoing |
| SEO (long-term) | High | 500 signups/mo | Month 6+ |
| Affiliate program | Medium | 20% of signups | Month 3+ |
| HubSpot marketplace | High | 300 signups/mo | Month 4+ |

### Key Messaging

**Headline options (to A/B test):**
1. "Generate a $10K proposal in 60 seconds"
2. "Win more deals without hiring more salespeople"
3. "The AI proposal generator for agencies that close"

**Proof points:**
- "60 seconds vs. 4.5 hours"
- "Includes presentation deck"
- "Learns your brand voice"

---

## 10. Unit Economics

### Cost per Proposal Generated

| Component | Cost | Notes |
|-----------|------|-------|
| LLM (OpenRouter) | $0.05 | Grok free tier; $0.15 for GPT-4o |
| Gamma API | $0.10 | Per deck generated |
| Firecrawl | $0.02 | Per scrape |
| Infrastructure | $0.01 | Convex + hosting |
| **Total COGS** | **$0.18** | Per proposal |

### Break-even Analysis

| Tier | Price | COGS (50 proposals) | Gross Margin |
|------|-------|---------------------|--------------|
| Starter | $99 | $3.60 | 96% |
| Growth | $199 | $9.00 | 95% |
| Agency | $399 | $18.00 | 95% |

**Target gross margin: >90%** ✅

### Path to $500K ARR

| Milestone | Customers | ARPU | MRR | ARR |
|-----------|-----------|------|-----|-----|
| Month 3 | 30 | $150 | $4,500 | $54K |
| Month 6 | 80 | $160 | $12,800 | $154K |
| Month 9 | 150 | $175 | $26,250 | $315K |
| Month 12 | 250 | $180 | $45,000 | $540K |

---

## 11. Risks & Mitigations

### Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Gamma API deprecation | Low | Critical | Build fallback to Puppeteer + templates |
| OpenRouter rate limits | Medium | High | Implement aggressive caching, model fallbacks |
| LLM quality degradation | Medium | Medium | Prompt versioning, quality monitoring |

### Market Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| PandaDoc launches similar feature | High | High | Move fast, build brand, focus on quality |
| ChatGPT adds proposal templates | Medium | Medium | Differentiate on integration + methodology |
| Economic downturn reduces agency spend | Medium | Medium | Emphasize ROI, cost savings messaging |

### Operational Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Founder burnout | High | Critical | Maintain sustainable pace, hire help at $15K MRR |
| Customer support overload | Medium | Medium | Build self-serve docs, FAQ, video tutorials |

---

## 12. Open Questions

### Product Questions
1. ~~Should proposals be editable in-app before sending?~~ ✅ **Implemented** — Full editor with section-by-section editing
2. What's the right balance of automation vs. control?
3. ~~Should we track proposal view analytics? (Privacy implications)~~ ✅ **Decided** — Yes, via redirect links (anonymous view count).

### Business Questions
1. When to hire first employee? (Target: $20K MRR)
2. Should we pursue agency partnerships for distribution?
3. Enterprise sales motion — when to start?

### Technical Questions
1. Build vs. buy for proposal hosting/analytics?
2. When to migrate from free LLM tier?

---

## Appendix

### A. Technical Specifications
→ See [SPEC.md](../technical/SPEC.md) for full technical documentation

### B. Customer Interview Notes
→ *To be added: Link to interview recordings/notes*

### C. Competitive Research
→ *To be added: Detailed feature comparison spreadsheet*

### D. Wireframes & Designs
→ *To be added: Figma link*

---

*This is a living document. Last substantive update: January 2026.*
