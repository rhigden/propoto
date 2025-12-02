from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import re
import ipaddress
from urllib.parse import urlparse
from urllib.parse import urlparse
from typing import Optional

# Rate Limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# Load environment variables
load_dotenv()

# Import structured logging utilities
from utils.logger import (
    StructuredLogger, 
    TimingContext, 
    TokenTracker,
    set_request_context, 
    get_request_id,
    logger,
    setup_logging
)

# Import custom exceptions
from utils.exceptions import (
    AgentServiceError,
    ValidationError,
    AuthenticationError,
    ConfigurationError,
    ErrorCode
)

# Initialize structured logger
structured_logger = StructuredLogger()

# Initialize Rate Limiter
limiter = Limiter(key_func=get_remote_address)

# --- URL Validation ---
# Blocklist of internal IP ranges and dangerous hostnames
BLOCKED_IP_RANGES = [
    ipaddress.ip_network('10.0.0.0/8'),      # Private
    ipaddress.ip_network('172.16.0.0/12'),   # Private
    ipaddress.ip_network('192.168.0.0/16'),  # Private
    ipaddress.ip_network('127.0.0.0/8'),     # Loopback
    ipaddress.ip_network('169.254.0.0/16'),  # Link-local
    ipaddress.ip_network('::1/128'),         # IPv6 loopback
    ipaddress.ip_network('fc00::/7'),        # IPv6 private
    ipaddress.ip_network('fe80::/10'),       # IPv6 link-local
]

BLOCKED_HOSTNAMES = ['localhost', 'internal', 'metadata', '169.254.169.254']

def validate_url_security(url: str) -> tuple[bool, str]:
    """
    Validate that a URL is safe to scrape (not internal/localhost/cloud metadata).
    
    Returns:
        (is_valid, error_message) tuple
    """
    try:
        parsed = urlparse(url)
        
        # Check scheme
        if parsed.scheme not in ('http', 'https'):
            return False, f"Invalid URL scheme: {parsed.scheme}. Only http/https allowed."
        
        hostname = parsed.hostname
        if not hostname:
            return False, "Invalid URL: no hostname found"
        
        # Check for blocked hostnames
        hostname_lower = hostname.lower()
        for blocked in BLOCKED_HOSTNAMES:
            if blocked in hostname_lower:
                return False, f"Blocked hostname: {hostname}"
        
        # Try to resolve as IP address
        try:
            # Handle both IPv4 and IPv6
            ip = ipaddress.ip_address(hostname)
            for blocked_range in BLOCKED_IP_RANGES:
                if ip in blocked_range:
                    return False, f"Internal IP address not allowed: {hostname}"
        except ValueError:
            # Not an IP address, it's a hostname - that's fine
            pass
        
        return True, ""
        
    except Exception as e:
        return False, f"URL validation error: {str(e)}"

app = FastAPI(
    title="Propoto API",
    description="AI-powered proposal generation for digital agencies",
    version="1.0.0"
)

# --- CORS Configuration ---
# Allow frontend origins in development and production
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# --- Environment Validation ---
def validate_environment():
    """Validate that critical environment variables are set."""
    required_vars = {
        "OPENROUTER_API_KEY": "OpenRouter API key for AI models",
        "AGENT_SERVICE_KEY": "API key for authenticating requests"
    }
    
    optional_vars = {
        # Removed: GAMMA_API_KEY, MEM0_API_KEY (not used - Exa and Firecrawl only)
        "EXA_API_KEY": "Exa API for search",
        "FIRECRAWL_API_KEY": "Firecrawl API for web scraping",
        "NEXT_PUBLIC_CONVEX_URL": "Convex backend URL",
        "CONVEX_DEPLOYMENT": "Convex deployment token"
    }
    
    missing_required = []
    missing_optional = []
    
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_required.append(f"{var} ({description})")
    
    for var, description in optional_vars.items():
        if not os.getenv(var):
            missing_optional.append(f"{var} ({description})")
            logger.warning(f"Optional environment variable not set: {var}")
    
    if missing_required:
        error_msg = "Missing required environment variables:\n" + "\n".join(missing_required)
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    
    if missing_optional:
        logger.info(f"Missing {len(missing_optional)} optional environment variables")
    
    logger.info("Environment validation passed ✓")

# Validate on startup
try:
    validate_environment()
except RuntimeError as e:
    logger.critical(f"Failed to start: {e}")
    # Don't raise in Docker environments, allow service to start
    pass

# --- Security ---
API_KEY = os.getenv("AGENT_SERVICE_KEY")

async def verify_key(request: Request):
    """Verify API key from header."""
    api_key = request.headers.get("x-api-key")
    
    if not API_KEY:
        logger.critical("AGENT_SERVICE_KEY not set in environment!")
        raise HTTPException(status_code=500, detail="Service misconfigured")

    if api_key != API_KEY:
        logger.warning(f"Invalid API key attempted from {request.client.host}")
        raise HTTPException(status_code=403, detail="Invalid API Key")

# --- Exception Handlers ---
@app.exception_handler(AgentServiceError)
async def agent_service_error_handler(request: Request, exc: AgentServiceError):
    """Handler for custom agent service errors."""
    structured_logger.error(
        f"Agent service error: {exc.message}",
        error_code=exc.error_code.value,
        status_code=exc.status_code,
        retryable=exc.retryable
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict()
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    structured_logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "error_code": ErrorCode.INTERNAL_ERROR.value,
            "detail": str(exc) if os.getenv("DEBUG") else "An unexpected error occurred",
            "retryable": False
        }
    )

# --- Request Models ---
class AgentRequest(BaseModel):
    prompt: str
    context: dict = {}

class IngestRequest(BaseModel):
    url: str

# Removed: BrandRequest (Brand agent disabled)

# --- Health Endpoints ---
@app.get("/")
async def root():
    """Root endpoint with service info."""
    return {
        "status": "ok",
        "service": "Propoto API",
        "version": "1.0.0",
        "agents": ["knowledge", "brand"]
    }

@app.get("/health")
async def health():
    """Health check endpoint."""
    env_status = {
        "openrouter": bool(os.getenv("OPENROUTER_API_KEY")),
        "exa": bool(os.getenv("EXA_API_KEY")),
        "firecrawl": bool(os.getenv("FIRECRAWL_API_KEY")),
        "convex": bool(os.getenv("NEXT_PUBLIC_CONVEX_URL"))
    }
    
    return {
        "status": "healthy",
        "environment": env_status
    }

# --- Knowledge Agent Endpoints ---
# --- Knowledge Agent Endpoints ---
from agents.knowledge import knowledge_agent, KnowledgeOutput, KnowledgeDeps

@app.post("/agents/knowledge/ingest")
@limiter.limit("10/minute")
async def ingest_knowledge(req: IngestRequest, request: Request, _: None = Depends(verify_key)):
    """
    Analyze and ingest knowledge from a URL.
    
    Scrapes the URL, extracts entities, and stores in knowledge base.
    Supports self-hosted Firecrawl via FIRECRAWL_API_URL env var.
    """
    try:
        # Input validation
        if not req.url or not req.url.strip():
            raise HTTPException(status_code=400, detail="url is required")
        
        # Validate URL format
        if not req.url.startswith(("http://", "https://")):
            raise HTTPException(status_code=400, detail="url must be a valid HTTP/HTTPS URL")
        
        # Security validation - block internal IPs and dangerous URLs
        is_valid, error_msg = validate_url_security(req.url)
        if not is_valid:
            logger.warning(f"URL security validation failed: {req.url} - {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        logger.info(f"Knowledge ingestion started for: {req.url}")
        
        # Inject dependencies (supports self-hosted Firecrawl)
        deps = KnowledgeDeps(
            firecrawl_api_key=os.getenv("FIRECRAWL_API_KEY", ""),
            firecrawl_api_url=os.getenv("FIRECRAWL_API_URL", "http://localhost:3002"),
            convex_url=os.getenv("NEXT_PUBLIC_CONVEX_URL", ""),
            convex_token=os.getenv("CONVEX_DEPLOYMENT", "")
        )
        
        # Run the agent
        result = await knowledge_agent.run(
            f"Analyze this URL and extract key information: {req.url}",
            deps=deps
        )
        
        logger.info(f"Knowledge ingestion completed for: {req.url}")
        return {
            "success": True,
            "url": req.url,
            "data": result.output
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ingesting knowledge from {req.url}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to ingest knowledge: {str(e)}"
        )

# --- Brand Agent Endpoints ---
# DISABLED: Brand agent requires Gamma/Mem0 which are not in use
# Keeping endpoint structure but returning disabled message
@app.post("/agents/brand/generate")
@limiter.limit("5/minute")
async def generate_brand_asset(request: Request, _: None = Depends(verify_key)):
    """
    Brand agent is disabled - focusing on Exa and Firecrawl only.
    """
    raise HTTPException(
        status_code=503,
        detail="Brand agent is disabled. Currently supporting Proposal, Knowledge, and Sales agents only (Exa + Firecrawl)."
    )

# --- Sales Agent Endpoints ---
from agents.sales import sales_agent, SalesOutput, SalesDeps

@app.post("/agents/sales/find_leads")
@limiter.limit("10/minute")
async def find_leads(req: AgentRequest, request: Request, _: None = Depends(verify_key)):
    """
    Find leads based on a search query.
    
    Uses Exa API to find companies and stores them in Convex.
    """
    try:
        logger.info(f"Sales lead search started for: {req.prompt}")
        
        # Inject dependencies
        deps = SalesDeps(
            exa_api_key=os.getenv("EXA_API_KEY", ""),
            convex_url=os.getenv("NEXT_PUBLIC_CONVEX_URL", ""),
            convex_token=os.getenv("CONVEX_DEPLOYMENT", "")
        )
        
        # Run the agent
        result = await sales_agent.run(
            f"Find leads for: {req.prompt}",
            deps=deps
        )
        
        logger.info(f"Sales lead search completed")
        return {
            "success": True,
            "data": result.output
        }
        
    except Exception as e:
        logger.error(f"Error finding leads: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to find leads: {str(e)}"
        )

# --- Proposal Agent Endpoints ---
from agents.proposal_agent import (
    ProposalRequest,
    get_proposal_agent,
    DEFAULT_MAX_TOKENS,
    build_enriched_prompt,
    AVAILABLE_MODELS,
    PROPOSAL_TEMPLATES,
    DEFAULT_MODEL
)
from services.scraping_service import ScrapingService
# Removed: GammaService import (Gamma integration disabled)

@app.get("/agents/proposal/models")
async def list_models():
    """List available LLM models for proposal generation."""
    # Find the key that matches the default model path
    # Use DEFAULT_MODEL from proposal_agent.py (hardcoded to x-ai/grok-4.1-fast:free)
    default_model_path = DEFAULT_MODEL
    default_key = "grok"  # fallback
    for key, path in AVAILABLE_MODELS.items():
        if path == default_model_path:
            default_key = key
            break
    
    return {
        "models": [
            {"key": key, "name": name}
            for key, name in AVAILABLE_MODELS.items()
        ],
        "default": default_key
    }

@app.get("/agents/proposal/templates")
async def list_templates():
    """List available proposal templates."""
    return {
        "templates": [
            {
                "key": key,
                "name": template["name"],
                "description": template["description"],
                "tone": template["tone"]
            }
            for key, template in PROPOSAL_TEMPLATES.items()
        ]
    }

@app.get("/agents/gamma/themes")
async def list_gamma_themes(_: None = Depends(verify_key)):
    """Gamma integration disabled."""
    raise HTTPException(
        status_code=503,
        detail="Gamma integration is disabled. Currently supporting Exa and Firecrawl only."
    )

# --- Brand Voice Memory Endpoints ---
# DISABLED: Brand memory requires Mem0 which is not in use
@app.get("/agents/brand/voice")
async def get_brand_voice(
    org_id: str = "demo-org-1",
    _: None = Depends(verify_key)
):
    """Brand memory is disabled - Mem0 integration not in use."""
    raise HTTPException(
        status_code=503,
        detail="Brand memory is disabled. Currently supporting Exa and Firecrawl only."
    )

@app.post("/agents/brand/voice")
async def save_brand_voice(
    _: None = Depends(verify_key)
):
    """Brand memory is disabled - Mem0 integration not in use."""
    raise HTTPException(
        status_code=503,
        detail="Brand memory is disabled. Currently supporting Exa and Firecrawl only."
    )

@app.post("/agents/proposal/generate")
@limiter.limit("5/minute")
async def generate_proposal(req: ProposalRequest, request: Request, _: None = Depends(verify_key)):
    """
    Generate a personalized proposal and a Gamma presentation.
    
    Enhanced with:
    - Deep website scraping (when deep_scrape=true)
    - Model selection
    - Template styles
    """
    # Set request context for logging
    request_id = get_request_id()
    set_request_context(request_id=request_id, org_id=getattr(req, 'org_id', 'demo-org-1'))
    
    try:
        with TimingContext("proposal_generation"):
            structured_logger.info(f"Proposal generation started", prospect_name=req.prospect_name)
        
        # Input validation
        if not req.prospect_name or not req.prospect_name.strip():
            raise HTTPException(status_code=400, detail="prospect_name is required")
        if not req.prospect_url or not req.prospect_url.strip():
            raise HTTPException(status_code=400, detail="prospect_url is required")
        if not req.pain_points or not req.pain_points.strip():
            raise HTTPException(status_code=400, detail="pain_points is required")
        
        # Validate URL format
        if not req.prospect_url.startswith(("http://", "https://")):
            raise HTTPException(status_code=400, detail="prospect_url must be a valid HTTP/HTTPS URL")
        
        # Security validation - block internal IPs and dangerous URLs
        is_valid, error_msg = validate_url_security(req.prospect_url)
        if not is_valid:
            logger.warning(f"URL security validation failed: {req.prospect_url} - {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Validate template if provided
        if req.template and req.template not in PROPOSAL_TEMPLATES:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid template. Available: {', '.join(PROPOSAL_TEMPLATES.keys())}"
            )
        
        # Validate model if provided
        if req.model and req.model not in AVAILABLE_MODELS and not req.model.startswith(("x-ai/", "openai/", "anthropic/", "google/", "deepseek/")):
            logger.warning(f"Unknown model requested: {req.model}, using as-is")
        
        # Phase 2: Deep scraping for website intelligence
        website_intel = None
        if req.deep_scrape:
            try:
                logger.info(f"Deep scraping enabled for: {req.prospect_url}")
                scraping_service = ScrapingService()
                intel = await scraping_service.analyze_prospect(req.prospect_url, deep_crawl=True)
                website_intel = intel.model_dump() if intel else None
                if website_intel:
                    logger.info(f"Extracted intelligence: industry={intel.industry}, tone={intel.tone_style}")
            except Exception as scrape_error:
                logger.warning(f"Deep scraping failed for {req.prospect_url}: {str(scrape_error)}")
                # Continue without website intel - graceful degradation
                website_intel = None
        
        # Build enriched prompt with website intel and template
        user_prompt = build_enriched_prompt(
            prospect_name=req.prospect_name,
            prospect_url=req.prospect_url,
            pain_points=req.pain_points,
            website_intel=website_intel,
            template_key=req.template or "default"
        )
        
        # Get agent with selected model
        agent = get_proposal_agent(req.model)
        
        # Run the agent with max_tokens limit to stay within credit budget
        # Default to 2000 tokens (safe limit for free tier)
        model_settings = {"max_tokens": DEFAULT_MAX_TOKENS}
        
        try:
            result = await agent.run(user_prompt, model_settings=model_settings)
            # Access output data - pydantic-ai uses .output or .data depending on version
            proposal_data = getattr(result, 'output', getattr(result, 'data', None))
            if proposal_data is None:
                raise ValueError("Could not access result data - check pydantic-ai version")
        except Exception as agent_error:
            error_str = str(agent_error)
            error_repr = repr(agent_error)
            logger.error(f"Agent execution failed: {error_str}", exc_info=True)
            
            # Check for 402 (Payment Required) error from OpenRouter
            # OpenRouter returns: status_code: 402, body: {'message': '...requires more credits...', 'code': 402}
            is_402_error = (
                "status_code: 402" in error_str or 
                "402" in error_str or 
                "requires more credits" in error_str.lower() or 
                "can only afford" in error_str.lower() or
                "'code': 402" in error_repr or
                '"code": 402' in error_repr
            )
            
            if is_402_error:
                # Try fallback to free Grok model if a paid model was requested
                if req.model and req.model not in ("grok", "grok-fast") and req.model != "x-ai/grok-4.1-fast:free":
                    logger.warning(f"Credits insufficient for {req.model}, falling back to free Grok model")
                    try:
                        # Retry with free Grok model
                        free_agent = get_proposal_agent("grok")
                        result = await free_agent.run(user_prompt, model_settings=model_settings)
                        proposal_data = getattr(result, 'output', getattr(result, 'data', None))
                        if proposal_data is None:
                            raise ValueError("Could not access result data - check pydantic-ai version")
                        logger.info("Successfully generated proposal using free Grok model fallback")
                    except Exception as fallback_error:
                        logger.error(f"Fallback to free model also failed: {str(fallback_error)}", exc_info=True)
                        raise HTTPException(
                            status_code=402,
                            detail=(
                                f"Insufficient OpenRouter credits. Requested model requires more credits than available. "
                                f"Error: {error_str}. "
                                f"Please upgrade your OpenRouter account at https://openrouter.ai/settings/credits "
                                f"or use the free 'grok' model."
                            )
                        )
                else:
                    # Already using free model or no fallback available
                    raise HTTPException(
                        status_code=402,
                        detail=(
                            f"Insufficient OpenRouter credits. Error: {error_str}. "
                            f"Please upgrade your OpenRouter account at https://openrouter.ai/settings/credits"
                        )
                    )
            else:
                # Other errors
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to generate proposal content: {error_str}"
                )
        
        # Gamma integration removed - focusing on Exa and Firecrawl only
        # Proposals are returned as text only (no presentation decks)
        presentation_url = None
        pdf_url = None
        pptx_url = None
        
        logger.info("Proposal generated (text only - Gamma integration disabled)")
        
        structured_logger.info(
            f"Proposal generated successfully",
            prospect_name=req.prospect_name,
            model=req.model or "default",
            deep_scrape_enabled=req.deep_scrape
        )
        
        return {
            "success": True,
            "data": proposal_data,
            "presentation_url": presentation_url,
            "pdf_url": pdf_url,
            "pptx_url": pptx_url,
            "model_used": req.model or DEFAULT_MODEL,
            "template_used": req.template or "default",
            "deep_scrape_enabled": req.deep_scrape
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error generating proposal: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate proposal: {str(e)}"
        )

# --- Telegram Bot Endpoints ---
from services.telegram_bot import get_telegram_bot, TelegramBotService
import asyncio

# Background task for Telegram bot
telegram_bot_task: Optional[asyncio.Task] = None

@app.get("/telegram/status")
async def telegram_status():
    """Get Telegram bot status."""
    bot = get_telegram_bot()
    return {
        "configured": bot.is_configured,
        "running": bot._running,
        "token_set": bool(os.getenv("TELEGRAM_BOT_TOKEN"))
    }

@app.post("/telegram/start")
async def start_telegram_bot(_: None = Depends(verify_key)):
    """Start the Telegram bot."""
    global telegram_bot_task
    
    bot = get_telegram_bot()
    if not bot.is_configured:
        raise HTTPException(
            status_code=400,
            detail="Telegram bot not configured. Set TELEGRAM_BOT_TOKEN environment variable."
        )
    
    if bot._running:
        return {"status": "already_running", "message": "Telegram bot is already running"}
    
    try:
        telegram_bot_task = asyncio.create_task(bot.start())
        return {"status": "started", "message": "Telegram bot started successfully"}
    except Exception as e:
        logger.error(f"Failed to start Telegram bot: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/telegram/stop")
async def stop_telegram_bot(_: None = Depends(verify_key)):
    """Stop the Telegram bot."""
    global telegram_bot_task
    
    bot = get_telegram_bot()
    if not bot._running:
        return {"status": "not_running", "message": "Telegram bot is not running"}
    
    try:
        await bot.stop()
        if telegram_bot_task:
            telegram_bot_task.cancel()
            telegram_bot_task = None
        return {"status": "stopped", "message": "Telegram bot stopped"}
    except Exception as e:
        logger.error(f"Failed to stop Telegram bot: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Starting Propoto API on {host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )
