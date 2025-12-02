from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from dataclasses import dataclass
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import StructuredLogger, set_request_context, agent_name_var
from utils.exceptions import AgentExecutionError, ValidationError, ErrorCode

# Initialize structured logger
structured_logger = StructuredLogger()

# --- Data Models ---

class ProposalRequest(BaseModel):
    prospect_name: str
    prospect_url: str
    pain_points: str
    # Phase 2: Enhanced options
    model: Optional[str] = None  # Override default model
    template: Optional[str] = None  # Proposal template style
    deep_scrape: Optional[bool] = False  # Enable deep website analysis
    tone: Optional[str] = None  # Custom tone override

class PricingTier(BaseModel):
    name: str = Field(description="Name of the tier (e.g., 'Starter', 'Growth')")
    price: str = Field(description="Price point (e.g., '$1,000/mo')")
    features: List[str] = Field(description="List of features included")

class ProposalOutput(BaseModel):
    executive_summary: str = Field(description="A punchy 2-3 sentence summary of the opportunity.")
    current_situation: str = Field(description="Analysis of their current state and the specific pain point.")
    proposed_strategy: str = Field(description="The unique mechanism or strategy to solve the pain point.")
    why_us: str = Field(description="Brief social proof or authority statement.")
    investment: List[PricingTier] = Field(description="3 pricing tiers: Foot-in-door, Core, Anchor.")
    next_steps: str = Field(description="Clear call to action (e.g., 'Book a 15-min strategy call').")

# --- Proposal Templates ---
PROPOSAL_TEMPLATES = {
    "default": {
        "name": "Trojan Horse",
        "description": "Nick Saraev's high-converting sales methodology",
        "tone": "direct, professional, value-focused",
        "style_notes": "Give value upfront, diagnose real problems, offer specific mechanisms"
    },
    "consultative": {
        "name": "Consultative Advisor",
        "description": "Focused on education and building trust",
        "tone": "educational, empathetic, expert",
        "style_notes": "Position as trusted advisor, heavy on diagnosis, softer close"
    },
    "enterprise": {
        "name": "Enterprise Professional",
        "description": "Formal style for large organizations",
        "tone": "formal, data-driven, strategic",
        "style_notes": "Include ROI projections, reference similar enterprises, formal language"
    },
    "startup": {
        "name": "Startup Partner",
        "description": "Casual, fast-paced for startups",
        "tone": "energetic, casual, growth-focused",
        "style_notes": "Focus on speed, agility, quick wins, growth metrics"
    },
    "agency": {
        "name": "Agency Partnership",
        "description": "B2B agency collaboration style",
        "tone": "collaborative, transparent, process-focused",
        "style_notes": "Emphasize workflow integration, white-label options, partner benefits"
    }
}

# Available models - OpenRouter model names
# These are passed directly to OpenRouter via the OpenAI-compatible API
# FREE models have :free suffix
AVAILABLE_MODELS = {
    "grok": "x-ai/grok-4.1-fast:free",  # FREE until Dec 3, 2025!
    "grok-fast": "x-ai/grok-4.1-fast:free",
    "gpt-4o": "openai/gpt-4o",
    "gpt-4o-mini": "openai/gpt-4o-mini",
    "claude-sonnet": "anthropic/claude-3.5-sonnet",
    "claude-haiku": "anthropic/claude-3-haiku",
    "gemini-pro": "google/gemini-pro-1.5",
    "deepseek": "deepseek/deepseek-chat"
}

# --- Agent Definition ---

# Default model - Grok 4.1 Fast FREE (until Dec 3, 2025)
# Hardcoded to ensure we always use the free model unless explicitly overridden
DEFAULT_MODEL = "x-ai/grok-4.1-fast:free"
# Allow override via env var only if explicitly set (for testing/debugging)
if os.getenv("DEFAULT_MODEL"):
    env_model = os.getenv("DEFAULT_MODEL")
    structured_logger.warning(f"DEFAULT_MODEL env var is set to: {env_model}. Using hardcoded default instead: {DEFAULT_MODEL}")
    # Uncomment the line below if you want to allow env override:
    # DEFAULT_MODEL = env_model

def get_openrouter_model(model_name: str) -> OpenAIChatModel:
    """Create an OpenAI-compatible model pointing to OpenRouter."""
    return OpenAIChatModel(model_name, provider='openrouter')

# Default max_tokens: Set to 2000 to stay within free tier limits
# This is a safe limit that works with Grok 4.1 Fast (free) and most paid models
DEFAULT_MAX_TOKENS = 2000

def get_proposal_agent(model_override: Optional[str] = None) -> Agent:
    """
    Get a proposal agent with the specified or default model.
    
    Args:
        model_override: Model name to use (key from AVAILABLE_MODELS or full path)
        
    Returns:
        Configured proposal agent
        
    Raises:
        ValidationError: If model name is invalid
    """
    # Resolve model name
    if model_override:
        model_name = AVAILABLE_MODELS.get(model_override, model_override)
        # Normalize pydantic-ai format (provider:model) to OpenRouter format (provider/model)
        if ':' in model_name and '/' not in model_name:
            model_name = model_name.replace(':', '/', 1)
        structured_logger.info(f"Using model override: {model_name}")
        
        # Warn if using paid model when free alternative is available
        if model_name in ("openai/gpt-4o", "gpt-4o") and model_override != "gpt-4o":
            structured_logger.warning(f"Using paid model {model_name}. Consider using 'grok' (x-ai/grok-4.1-fast:free) for free alternative.")
    else:
        model_name = DEFAULT_MODEL
        structured_logger.info(f"Using default model: {model_name}")
    
    # Ensure we're using the correct model format for OpenRouter
    if not model_name.startswith(("x-ai/", "openai/", "anthropic/", "google/", "deepseek/")):
        structured_logger.warning(f"Model name '{model_name}' may not be in correct OpenRouter format. Expected format: provider/model")
    
    # Set agent context for logging
    agent_name_var.set("proposal_agent")
    
    # Create OpenRouter-compatible model
    model = get_openrouter_model(model_name)
    
    structured_logger.info(f"Initializing proposal agent with model: {model_name} (OpenRouter provider)")
    
    return Agent(
        model,
        output_type=ProposalOutput,
        instructions=(
            "You are Nick Saraev, an expert agency sales strategist with 10+ years of experience "
            "closing high-ticket deals using the 'Trojan Horse' methodology. You've helped agencies "
            "generate over $50M in new business through compelling, value-first proposals.\n\n"
            
            "YOUR CORE BELIEF: The best proposal isn't about you—it's about making the prospect "
            "feel understood and showing them a clear path to their desired outcome.\n\n"
            
            "=== TROJAN HORSE METHODOLOGY ===\n\n"
            
            "1. **GIVE VALUE FIRST** (The Hook)\n"
            "   - Start with an insight that proves you've done your homework\n"
            "   - Share something they might not know about their own business or market\n"
            "   - Make them think 'Wow, this person really gets it'\n"
            "   - Example: 'Your checkout abandonment rate is likely 60%+ based on your current flow'\n\n"
            
            "2. **DIAGNOSE THE REAL PROBLEM** (The Gap)\n"
            "   - Never accept surface-level pain points at face value\n"
            "   - Dig to the root cause: 'We need more leads' → 'Why?' → 'Low conversion' → 'Why?'\n"
            "   - Quantify the cost of inaction: What are they losing monthly?\n"
            "   - Use the GAP framework: Goal → Actual → Problem\n\n"
            
            "3. **OFFER A MECHANISM** (The Solution)\n"
            "   - NEVER say generic services like 'SEO', 'PPC', 'web design'\n"
            "   - Create a NAMED SYSTEM that sounds proprietary and unique\n"
            "   - Good examples:\n"
            "     * 'The Revenue Velocity Engine' (not 'marketing automation')\n"
            "     * 'The Authority Content System' (not 'content marketing')\n"
            "     * 'The Conversion Cascade Framework' (not 'CRO services')\n"
            "   - Explain the specific steps/phases of your mechanism\n\n"
            
            "=== PROPOSAL STRUCTURE (FOLLOW EXACTLY) ===\n\n"
            
            "**1. EXECUTIVE SUMMARY** (2-3 sentences MAXIMUM)\n"
            "   FORMAT: [Specific Result] + [Timeline] + [Why Now]\n"
            "   EXAMPLE: 'We'll help {prospect_name} increase qualified leads by 40% within 90 days "
            "   using our Authority Pipeline System. Based on our analysis, you're leaving "
            "   approximately $X/month on the table with your current approach.'\n"
            "   - MUST mention a specific metric or outcome\n"
            "   - MUST include a realistic timeline\n"
            "   - MUST reference their business name\n\n"
            
            "**2. CURRENT SITUATION** (3-4 sentences)\n"
            "   FORMAT: [Observation] + [Impact] + [Root Cause] + [Urgency]\n"
            "   - Show deep understanding of their business model\n"
            "   - Agitate the pain: quantify what this is costing them\n"
            "   - Use specific details from website intelligence when available\n"
            "   - Connect their pain to broader business impact\n"
            "   - DO NOT be condescending—be empathetic and understanding\n\n"
            
            "**3. PROPOSED STRATEGY** (4-5 sentences)\n"
            "   FORMAT: [Mechanism Name] + [How It Works] + [Specific Steps] + [Expected Outcome]\n"
            "   - ALWAYS name your mechanism (required)\n"
            "   - Explain the 'how' in plain language\n"
            "   - Break into 3-4 clear phases/steps\n"
            "   - Connect each step to solving their specific pain point\n"
            "   - Be specific and unique—no generic service descriptions\n\n"
            
            "**4. WHY US** (1 sentence only)\n"
            "   FORMAT: [Proof Point] + [Relevance]\n"
            "   - One concrete, verifiable proof point\n"
            "   - Examples: specific results, years of experience, unique qualification\n"
            "   - Make it relevant to their industry/situation\n\n"
            
            "**5. INVESTMENT** (EXACTLY 3 tiers)\n"
            "   TIER 1 - FOOT IN DOOR (30% of core price):\n"
            "     - Name: Something approachable ('Starter', 'Pilot', 'Foundation')\n"
            "     - Price: Low barrier, easy yes ($500-$2,000/mo typically)\n"
            "     - Features: 3-4 quick-win deliverables\n"
            "     - Purpose: Prove value, build trust\n\n"
            
            "   TIER 2 - CORE OFFERING (Reference price):\n"
            "     - Name: Something aspirational ('Growth', 'Accelerator', 'Professional')\n"
            "     - Price: Your ideal engagement ($3,000-$7,500/mo typically)\n"
            "     - Features: 4-5 comprehensive deliverables\n"
            "     - Purpose: Where most clients should land\n\n"
            
            "   TIER 3 - ANCHOR (2-3x core price):\n"
            "     - Name: Something premium ('Enterprise', 'Partnership', 'Unlimited')\n"
            "     - Price: Premium positioning ($10,000-$25,000/mo typically)\n"
            "     - Features: 5-6 features including exclusivity/priority\n"
            "     - Purpose: Makes Tier 2 look reasonable\n\n"
            
            "   PRICING RULES:\n"
            "   - Features must be OUTCOMES, not activities\n"
            "   - Good: 'Guaranteed 10+ qualified leads per month'\n"
            "   - Bad: '4 blog posts per month'\n\n"
            
            "**6. NEXT STEPS** (1 clear instruction)\n"
            "   - Single, specific, low-commitment action\n"
            "   - Good: 'Reply with your preferred tier, and I'll send over a detailed scope'\n"
            "   - Good: 'Book a 15-minute strategy call at [link]'\n"
            "   - Bad: 'Let me know your thoughts'\n\n"
            
            "=== PERSONALIZATION REQUIREMENTS ===\n"
            "- Use {prospect_name} in at least 2 sections\n"
            "- Reference specific details from website intelligence when provided\n"
            "- Match their industry language and terminology\n"
            "- Align tone with their brand style\n"
            "- If they're B2B, use B2B examples; if B2C, use B2C examples\n\n"
            
            "=== QUALITY CHECKLIST (MUST PASS ALL) ===\n"
            "□ Executive summary is 2-3 sentences, no more\n"
            "□ Proposed strategy has a NAMED mechanism\n"
            "□ Exactly 3 pricing tiers with clear price differentiation\n"
            "□ All sections reference the prospect's specific situation\n"
            "□ No generic corporate jargon or filler words\n"
            "□ Pricing features are outcomes, not activities\n"
            "□ Next steps has ONE clear, specific action\n\n"
            
            "=== TONE GUIDELINES ===\n"
            "- Confident but not arrogant\n"
            "- Helpful and consultative, not salesy\n"
            "- Specific and concrete, not vague\n"
            "- Professional but conversational\n"
            "- Urgency without pressure\n"
        )
    )

def get_template_prompt(template_key: str) -> str:
    """Get additional prompt guidance based on template selection."""
    template = PROPOSAL_TEMPLATES.get(template_key, PROPOSAL_TEMPLATES["default"])
    
    template_instructions = {
        "default": """
TEMPLATE: Trojan Horse (Default)
- Lead with value and insights
- Diagnose problems deeply before proposing solutions
- Use mechanism names, not service names
- Be direct and results-focused
""",
        "consultative": """
TEMPLATE: Consultative Advisor
- Position yourself as a trusted expert, not a vendor
- Spend more time on diagnosis (Current Situation section should be longer)
- Use educational language to build understanding
- Softer close - focus on helping them make the right decision
- Include questions that help them think through the problem
""",
        "enterprise": """
TEMPLATE: Enterprise Professional
- Formal, data-driven language
- Include ROI projections and metrics where possible
- Reference similar enterprise clients (without names)
- Emphasize scalability, security, and process
- Longer sections with more detail
- Use business terminology (KPIs, OKRs, etc.)
""",
        "startup": """
TEMPLATE: Startup Partner
- Energetic, fast-paced tone
- Emphasize speed and agility
- Focus on growth metrics and quick wins
- Shorter sections, more concise
- Use startup terminology (MVP, product-market fit, etc.)
- Highlight how you'll help them move fast
""",
        "agency": """
TEMPLATE: Agency Partnership
- Collaborative, transparent tone
- Emphasize workflow integration and process
- Highlight white-label and partnership benefits
- Focus on how you'll make their team more effective
- Use agency terminology (retainers, deliverables, etc.)
- Show understanding of agency business model
"""
    }
    
    return template_instructions.get(template_key, template_instructions["default"])

def build_enriched_prompt(
    prospect_name: str,
    prospect_url: str,
    pain_points: str,
    website_intel: Optional[dict] = None,
    template_key: str = "default"
) -> str:
    """
    Build an enriched prompt using website intelligence.
    
    Args:
        prospect_name: Name of the prospect company
        prospect_url: Their website URL
        pain_points: User-provided pain points
        website_intel: BusinessIntelligence data from scraping
        template_key: Template style to use
        
    Returns:
        Enriched prompt string for the agent
    """
    prompt_parts = [
        f"Prospect Name: {prospect_name}",
        f"Website: {prospect_url}",
        f"Pain Points: {pain_points}"
    ]
    
    # Add template guidance
    prompt_parts.append(get_template_prompt(template_key))
    
    # Add website intelligence if available
    if website_intel:
        intel_parts = [
            "\n--- WEBSITE INTELLIGENCE (Use this to deeply personalize the proposal) ---",
            "IMPORTANT: Reference specific details from this analysis throughout your proposal."
        ]
        
        if website_intel.get("company_name"):
            intel_parts.append(f"Company Name: {website_intel['company_name']}")
        
        if website_intel.get("industry"):
            intel_parts.append(f"Industry: {website_intel['industry']} - Use industry-specific language and examples")
        
        if website_intel.get("tone_style"):
            intel_parts.append(f"Their Brand Tone: {website_intel['tone_style']} - Match this tone in your writing")
        
        if website_intel.get("value_proposition"):
            intel_parts.append(f"Their Value Proposition: {website_intel['value_proposition']} - Reference this in Current Situation")
        
        if website_intel.get("target_audience"):
            intel_parts.append(f"Target Audience: {website_intel['target_audience']} - Show you understand who they serve")
        
        if website_intel.get("key_features"):
            intel_parts.append(f"Their Key Offerings: {', '.join(website_intel['key_features'][:5])} - Reference these to show understanding")
        
        if website_intel.get("pain_points_identified"):
            intel_parts.append(f"Pain Points Detected on Website: {'; '.join(website_intel['pain_points_identified'][:3])} - Use these to enrich the diagnosis")
        
        if website_intel.get("social_proof"):
            intel_parts.append(f"Their Social Proof: {', '.join(website_intel['social_proof'][:3])} - Reference their credibility in Why Us section")
        
        if website_intel.get("tech_stack_hints"):
            intel_parts.append(f"Tech Stack: {', '.join(website_intel['tech_stack_hints'][:5])} - Shows their technical sophistication level")
        
        if website_intel.get("competitors_mentioned"):
            intel_parts.append(f"Competitors Mentioned: {', '.join(website_intel['competitors_mentioned'][:3])} - Understand competitive landscape")
        
        if website_intel.get("raw_content"):
            # Include truncated raw content for context (reduced to save tokens)
            intel_parts.append(f"\nWebsite Content Excerpt (for context):\n{website_intel['raw_content'][:2000]}...")
        
        intel_parts.append("\nACTION: Weave these insights naturally into your proposal. Don't just list them - use them to show deep understanding.")
        
        prompt_parts.append("\n".join(intel_parts))
    
    return "\n\n".join(prompt_parts)


# Legacy compatibility - default agent instance
proposal_agent = get_proposal_agent()

# --- Dependencies ---
@dataclass
class ProposalDeps:
    """Dependencies for enhanced proposal generation."""
    scraping_service: Optional[object] = None
    mem0_client: Optional[object] = None
