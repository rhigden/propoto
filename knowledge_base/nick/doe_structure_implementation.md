# DOE Structure - Implementation Guide

> **Framework by**: Nick Saraev
> **Purpose**: Building reliable, self-improving agentic workflows
> **Complexity**: Intermediate to Advanced

---

## Overview

The **DOE Structure** (Directive, Orchestration, Execution) is a three-layer architecture for creating agentic workflows that are both flexible and reliable.

### The Problem It Solves

Traditional AI automation faces a key challenge:
- **Pure LLM approaches**: Flexible but unreliable (hallucination, inconsistency)
- **Pure code approaches**: Reliable but inflexible (hard to modify, no reasoning)

**DOE bridges this gap** by splitting responsibilities across three specialized layers.

---

## Layer 1: Directive

### What It Is
Natural language instructions that define the high-level goals and constraints of the workflow.

### Characteristics
- Written in plain English (or any natural language)
- Focuses on "what" and "why", not "how"
- Can be modified without touching code
- Acts as the SOP (Standard Operating Procedure)

### Example Directives

#### Lead Generation Directive
```
GOAL: Find qualified B2B SaaS leads in Toronto

CRITERIA:
- Company size: 10-100 employees
- Industry: Marketing agencies or tech startups
- Recent funding or growth signals
- Has a contact form or email

ACTIONS:
1. Search for companies matching criteria
2. Validate contact information
3. Score leads based on fit
4. Add high-scoring leads to CRM
5. Flag for review if uncertain

CONSTRAINTS:
- Only scrape publicly available data
- Respect robots.txt
- Maximum 100 leads per day
```

#### Customer Support Directive
```
GOAL: Respond to customer support tickets efficiently

RESPONSE CRITERIA:
- Simple questions: Auto-respond using knowledge base
- Technical issues: Create ticket for engineering
- Billing questions: Escalate to finance
- Urgent (keyword: "urgent", "critical"): Flag immediately

TONE:
- Professional and friendly
- Empathetic to customer frustration
- Concise but complete

CONSTRAINTS:
- Never promise specific timelines
- Don't make refund decisions (escalate)
- Response within 5 minutes for urgent tickets
```

### Best Practices
1. **Be Specific**: Clear criteria reduce agent confusion
2. **Include Examples**: Show what success looks like
3. **Set Constraints**: Define what the agent should NOT do
4. **Version Control**: Track directive changes over time
5. **Iterate Based on Results**: Refine as you see agent behavior

---

## Layer 2: Orchestration

### What It Is
An AI agent (powered by an LLM) that interprets directives and coordinates the workflow.

### The Reasoning Loop

```
┌─────────────────────────────────────────┐
│   1. READ DIRECTIVE                     │
│   - Parse goals and constraints         │
│   - Understand current context          │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│   2. CHOOSE ACTION                      │
│   - Evaluate available tools            │
│   - Select most appropriate next step   │
│   - Consider past results               │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│   3. EXECUTE ACTION                     │
│   - Call execution layer tools          │
│   - Pass parameters                     │
│   - Handle responses                    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│   4. EVALUATE RESULTS                   │
│   - Did action achieve sub-goal?        │
│   - What changed in the environment?    │
│   - Need to continue or complete?       │
└──────────────┬──────────────────────────┘
               │
               │
       ┌───────┴────────┐
       │                │
   CONTINUE?        COMPLETE
       │                │
       └────► LOOP      └─► END
```

### Orchestrator Responsibilities

| Task | Description | Example |
|------|-------------|---------|
| **Decision Making** | Choose which tool to use next | "Use scraper for company data, then use enrichment API for contact info" |
| **Error Handling** | Retry, skip, or escalate when tools fail | "Scraper failed, try alternative data source" |
| **Context Management** | Remember what's been done | "Already checked 50 companies, 48 to go" |
| **Adaptation** | Adjust strategy based on results | "Low success rate with Method A, switch to Method B" |
| **Quality Control** | Validate outputs before proceeding | "Email format invalid, re-run extraction" |

### Tools Available to Orchestrator

The orchestrator should have access to:
- **Execution layer functions** (see Layer 3)
- **Memory/state storage** (to track progress)
- **External APIs** (when deterministic tools aren't available)
- **Human escalation** (for edge cases)

### Implementation Options

#### Option 1: LLM with Function Calling
```python
# Pseudocode
tools = [
    scrape_google_maps,
    enrich_contact_data,
    score_lead,
    add_to_crm,
    send_alert
]

response = llm.chat(
    messages=[directive, current_context],
    tools=tools,
    model="gpt-4"
)

# LLM decides which function to call
chosen_tool = response.tool_calls[0]
result = execute_tool(chosen_tool)
```

#### Option 2: Custom Agent Framework
```python
# Using frameworks like LangChain, AutoGPT, etc.
from langchain.agents import AgentExecutor

agent = create_agent(
    directive=directive,
    tools=execution_tools,
    memory=ConversationBufferMemory()
)

agent.run(task="Generate 100 qualified leads")
```

#### Option 3: Antigravity Platform
- Visual agent builder
- Built-in reasoning loops
- Integrated testing tools
- (Recommended by Nick Saraev)

---

## Layer 3: Execution

### What It Is
Deterministic, reliable code (usually Python scripts) that performs the actual work.

### Why Separate Execution?

| Aspect | LLM Execution | Code Execution |
|--------|---------------|----------------|
| **Reliability** | ⚠️ Variable (hallucination risk) | ✅ Consistent |
| **Speed** | 🐌 Slow (API calls) | ⚡ Fast |
| **Cost** | 💰 Expensive (per token) | 💵 Cheap (computational) |
| **Auditability** | ❓ Hard to debug | ✅ Clear logs and traces |

**Key Principle**: Push heavy lifting to code, use LLM only for reasoning.

### Example Execution Functions

#### Web Scraping
```python
def scrape_google_maps(query: str, location: str, max_results: int) -> List[dict]:
    """
    Scrapes business data from Google Maps.
    
    DETERMINISTIC: Same inputs = same outputs
    RELIABLE: Handles rate limits, retries on failure
    TESTABLE: Clear inputs/outputs
    """
    results = []
    
    # Use established scraping library
    scraper = GoogleMapsScraper()
    scraper.set_rate_limit(delay=2)  # Respect rate limits
    
    try:
        raw_data = scraper.search(
            query=query,
            location=location,
            max_results=max_results
        )
        
        # Clean and standardize data
        for business in raw_data:
            results.append({
                'name': business.name,
                'address': business.address,
                'phone': clean_phone_number(business.phone),
                'website': business.website,
                'rating': business.rating,
                'timestamp': datetime.now().isoformat()
            })
    
    except RateLimitError:
        log_error("Rate limit hit, waiting...")
        time.sleep(60)
        return scrape_google_maps(query, location, max_results)  # Retry
    
    except Exception as e:
        log_error(f"Scraping failed: {str(e)}")
        return []
    
    return results
```

#### Lead Scoring
```python
def score_lead(company_data: dict, criteria: dict) -> dict:
    """
    Scores a lead based on predefined criteria.
    
    DETERMINISTIC: Clear, rule-based scoring
    NO LLM: Pure logic, fast and reliable
    """
    score = 0
    reasons = []
    
    # Employee count scoring
    employee_count = company_data.get('employee_count', 0)
    if criteria['min_employees'] <= employee_count <= criteria['max_employees']:
        score += 30
        reasons.append(f"Employee count ({employee_count}) in target range")
    
    # Industry match
    if company_data.get('industry') in criteria['target_industries']:
        score += 25
        reasons.append(f"Industry match: {company_data['industry']}")
    
    # Recent funding signal
    if company_data.get('recent_funding'):
        score += 20
        reasons.append("Recent funding round")
    
    # Website quality (has blog, careers page)
    website_signals = analyze_website(company_data.get('website'))
    if website_signals['has_blog']:
        score += 10
        reasons.append("Active blog (content marketing signal)")
    
    # Contact availability
    if company_data.get('email') or company_data.get('contact_form'):
        score += 15
        reasons.append("Contact information available")
    
    return {
        'company_name': company_data.get('name'),
        'score': score,
        'grade': get_grade(score),  # A/B/C/D/F
        'reasons': reasons,
        'data': company_data
    }

def get_grade(score: int) -> str:
    """Convert numeric score to letter grade"""
    if score >= 80: return 'A'
    if score >= 60: return 'B'
    if score >= 40: return 'C'
    if score >= 20: return 'D'
    return 'F'
```

#### CRM Integration
```python
def add_to_crm(lead_data: dict, crm_credentials: dict) -> bool:
    """
    Adds lead to CRM system.
    
    DETERMINISTIC: Uses official API
    ERROR HANDLING: Clear success/failure
    """
    crm_client = CRMClient(
        api_key=crm_credentials['api_key'],
        org_id=crm_credentials['org_id']
    )
    
    try:
        contact_id = crm_client.contacts.create(
            first_name=lead_data.get('contact_first_name', 'Unknown'),
            last_name=lead_data.get('contact_last_name', ''),
            email=lead_data.get('email'),
            company=lead_data.get('company_name'),
            phone=lead_data.get('phone'),
            custom_fields={
                'lead_score': lead_data.get('score'),
                'source': 'agentic_workflow',
                'acquired_date': datetime.now().isoformat()
            }
        )
        
        log_success(f"Added lead {contact_id} to CRM")
        return True
        
    except DuplicateContactError:
        log_warning(f"Contact already exists: {lead_data.get('email')}")
        return False
        
    except APIError as e:
        log_error(f"CRM API error: {str(e)}")
        return False
```

### Execution Layer Best Practices

1. **Pure Functions**: Same input → same output
2. **Error Handling**: Try/except with clear error types
3. **Logging**: Comprehensive logs for debugging
4. **Testing**: Unit tests for all functions
5. **Rate Limiting**: Respect API limits, external site robots.txt
6. **Retries**: Automatic retry for transient failures
7. **Idempotency**: Safe to run multiple times
8. **Documentation**: Clear docstrings with examples

---

## Putting It All Together

### Complete Example: Lead Generation Workflow

#### 1. Directive (Natural Language)
```
GOAL: Generate 50 qualified B2B SaaS leads daily

TARGET PROFILE:
- Marketing agencies in Toronto
- 10-50 employees
- Founded in last 5 years
- Active social media presence

PROCESS:
1. Search Google Maps for "marketing agency toronto"
2. Enrich each result with company data
3. Score leads (only save A and B grades)
4. Add to HubSpot CRM
5. Send daily summary report

QUALITY GATES:
- Minimum lead score: 60/100
- Must have valid email or contact form
- No duplicates in CRM
```

#### 2. Orchestration (AI Agent Logic)
```python
# The AI agent interprets the directive and orchestrates

def orchestrate_lead_generation(directive):
    """
    Agent reasoning loop for lead generation
    """
    # Parse directive
    target_count = 50
    min_score = 60
    
    leads_generated = 0
    attempts = 0
    
    while leads_generated < target_count and attempts < 200:
        # STEP 1: Choose action based on state
        if attempts < 100:
            action = "scrape_google_maps"
        else:
            # Switch strategy if not working
            action = "scrape_linkedin"
        
        # STEP 2: Execute action via execution layer
        if action == "scrape_google_maps":
            raw_companies = scrape_google_maps(
                query="marketing agency",
                location="Toronto",
                max_results=10
            )
        
        # STEP 3: Process results
        for company in raw_companies:
            attempts += 1
            
            # Enrich data
            enriched = enrich_company_data(company)
            
            # Score lead
            score_result = score_lead(enriched, directive.criteria)
            
            # STEP 4: Evaluate and decide
            if score_result['score'] >= min_score:
                # Check for duplicates
                if not check_crm_duplicate(enriched['email']):
                    # Add to CRM
                    success = add_to_crm(score_result, crm_creds)
                    
                    if success:
                        leads_generated += 1
                        log_success(f"Added lead {leads_generated}/50")
        
        # Adaptive behavior: if low success rate, adjust
        if attempts > 50 and leads_generated < 10:
            log_warning("Low conversion rate, adjusting criteria")
            min_score = 50  # Loosen criteria
    
    # Send summary
    send_summary_report(leads_generated, attempts)
    
    return {
        'leads_generated': leads_generated,
        'attempts': attempts,
        'success_rate': leads_generated / attempts
    }
```

#### 3. Execution (Deterministic Functions)
```python
# All the heavy lifting functions defined in Layer 3 section:
# - scrape_google_maps()
# - enrich_company_data()
# - score_lead()
# - check_crm_duplicate()
# - add_to_crm()
# - send_summary_report()
```

---

## Benefits of DOE Structure

### ✅ Reliability
- Critical operations run on tested, deterministic code
- Reduce LLM hallucination to near-zero for execution
- Predictable outcomes for business processes

### ✅ Flexibility
- Change business logic by editing directives (no code changes)
- Agent adapts to new situations automatically
- Easy to experiment with different strategies

### ✅ Maintainability
- Clear separation of concerns
- Easy to debug: check which layer failed
- Can improve each layer independently

### ✅ Scalability
- Execution layer can be optimized for speed
- Add new tools without rewriting orchestrator
- Parallel processing where appropriate

### ✅ Cost Efficiency
- Minimize expensive LLM calls
- Use LLM only for high-value reasoning
- Cheap compute for execution layer

---

## Common Pitfalls & Solutions

| Pitfall | Problem | Solution |
|---------|---------|----------|
| **Vague Directives** | Agent doesn't understand goals | Be extremely specific, include examples |
| **Too Much in Orchestrator** | Slow, expensive, unreliable | Move logic to execution layer |
| **No Error Handling** | Workflow crashes on failure | Comprehensive try/except in execution layer |
| **Poor Logging** | Can't debug issues | Log everything with timestamps and context |
| **No Quality Gates** | Bad data propagates | Validate outputs at each step |
| **Tight Coupling** | Hard to modify or test | Keep layers independent with clear interfaces |

---

## Implementation Checklist

### Phase 1: Directive Design
- [ ] Define clear, specific goals
- [ ] List all criteria and constraints
- [ ] Include examples of success/failure
- [ ] Set quality thresholds
- [ ] Define escalation rules

### Phase 2: Execution Layer
- [ ] Identify all required functions
- [ ] Write deterministic, testable code
- [ ] Add comprehensive error handling
- [ ] Create unit tests
- [ ] Document all functions
- [ ] Set up logging infrastructure

### Phase 3: Orchestration Layer
- [ ] Choose agent framework/platform
- [ ] Connect to execution layer tools
- [ ] Implement reasoning loop
- [ ] Add memory/state management
- [ ] Test decision-making logic
- [ ] Set up monitoring

### Phase 4: Integration & Testing
- [ ] Run end-to-end tests
- [ ] Monitor for errors and edge cases
- [ ] Measure success metrics
- [ ] Iterate on directive based on results
- [ ] Optimize execution layer bottlenecks
- [ ] Document learnings

---

## Real-World Examples

### Example 1: Content Research Agent

**Directive**: "Find 10 trending topics in AI automation weekly"

**Orchestration**: Agent decides which sources to check, in what order, and which topics qualify as "trending"

**Execution**: 
- `scrape_reddit(subreddit='automation')`
- `scrape_twitter(hashtag='AIautomation')`
- `analyze_sentiment(posts)`
- `rank_topics(criteria)`

### Example 2: Customer Support Automation

**Directive**: "Respond to Tier 1 support tickets within 5 minutes"

**Orchestration**: Agent reads ticket, determines category, chooses response strategy

**Execution**:
- `fetch_tickets(priority='high')`
- `search_knowledge_base(query)`
- `generate_response(template, context)`
- `send_email(recipient, content)`

### Example 3: Sales Outreach

**Directive**: "Send 100 personalized cold emails daily to qualified leads"

**Orchestration**: Agent matches leads to templates, personalizes based on company data

**Execution**:
- `get_leads_from_crm(filters)`
- `enrich_lead(company_name)`
- `generate_email(template, lead_data)`
- `send_via_instantly(email, campaign_id)`

---

## Next Steps

1. **Start Simple**: Begin with one-layer workflows, add DOE structure as needed
2. **Focus on Execution First**: Build reliable tools before adding AI orchestration
3. **Iterate on Directives**: Refine based on agent behavior
4. **Monitor Closely**: Watch for errors, hallucinations, unexpected behavior
5. **Scale Gradually**: Prove value with small workflow before scaling

---

## Additional Resources

- Nick Saraev's "AGENTIC WORKFLOWS: Full Beginner's Guide" (YouTube, Nov 25, 2025)
- Google Antigravity documentation
- LangChain agent frameworks
- n8n workflow automation platform

---

*Last Updated: November 30, 2025*
*Framework Credit: Nick Saraev*
