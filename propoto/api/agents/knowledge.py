from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic import BaseModel, Field
from dataclasses import dataclass
import os
import sys
import httpx
from typing import List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from firecrawl import FirecrawlApp

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import StructuredLogger, agent_name_var
from utils.exceptions import FirecrawlError, ConvexError, ErrorCode

# Initialize structured logger
structured_logger = StructuredLogger()

# Self-hosted Firecrawl URL (defaults to local Docker instance)
FIRECRAWL_API_URL = os.getenv("FIRECRAWL_API_URL", "http://localhost:3002")

# --- Dependencies ---
@dataclass
class KnowledgeDeps:
    firecrawl_api_key: str
    firecrawl_api_url: str
    convex_url: str
    convex_token: str

# --- Output Models ---
class Entity(BaseModel):
    name: str
    type: str = Field(description="competitor, feature, pricing, or other")
    details: str

class KnowledgeOutput(BaseModel):
    summary: str
    entities: List[Entity]
    relevance_score: int = Field(description="1-10 score of relevance to our business")

# --- Agent Definition ---
# Use Grok 4.1 Fast FREE via OpenRouter (until Dec 3, 2025)
def get_openrouter_model(model_name: str = "x-ai/grok-4.1-fast:free") -> OpenAIChatModel:
    """Create an OpenAI-compatible model pointing to OpenRouter."""
    return OpenAIChatModel(model_name, provider='openrouter')

# Set agent context for logging
agent_name_var.set("knowledge_agent")

knowledge_agent = Agent(
    get_openrouter_model(),
    deps_type=KnowledgeDeps,
    output_type=KnowledgeOutput,
    instructions=(
        "You are the Knowledge Librarian, a senior competitive intelligence analyst with expertise "
        "in extracting actionable business intelligence from web content. Your analysis directly "
        "feeds into high-value sales proposals.\n\n"
        
        "=== YOUR MISSION ===\n"
        "Transform raw website content into structured intelligence that helps sales teams "
        "create deeply personalized, highly converting proposals.\n\n"
        
        "=== ANALYSIS FRAMEWORK ===\n\n"
        
        "**1. ENTITY EXTRACTION (Primary Focus)**\n\n"
        
        "   COMPETITOR entities:\n"
        "   - Direct competitors mentioned by name\n"
        "   - Alternative solutions they compare against\n"
        "   - Market positioning relative to competitors\n"
        "   - Include: name, market position, key differentiator\n\n"
        
        "   FEATURE entities:\n"
        "   - Core product/service capabilities\n"
        "   - Unique selling propositions\n"
        "   - Technical specifications\n"
        "   - Include: feature name, description, user benefit\n\n"
        
        "   PRICING entities:\n"
        "   - Explicit pricing when shown\n"
        "   - Pricing models (subscription, one-time, usage-based)\n"
        "   - Tier names and structures\n"
        "   - Include: tier name, price point, included features\n\n"
        
        "   OTHER entities (important intelligence):\n"
        "   - Notable clients/logos (social proof)\n"
        "   - Technology partners/integrations\n"
        "   - Key team members mentioned\n"
        "   - Industry certifications/awards\n"
        "   - Funding/growth indicators\n\n"
        
        "**2. RELEVANCE SCORING (Be Precise)**\n\n"
        
        "   Score 9-10 (CRITICAL - Must extract):\n"
        "   - Exact pricing information\n"
        "   - Named competitors with comparison data\n"
        "   - Unique value propositions\n"
        "   - Customer pain points explicitly stated\n"
        "   - ROI claims or case study results\n\n"
        
        "   Score 7-8 (VERY USEFUL):\n"
        "   - Target audience description\n"
        "   - Feature lists with benefits\n"
        "   - Integration partners\n"
        "   - Notable customer logos\n\n"
        
        "   Score 5-6 (MODERATELY USEFUL):\n"
        "   - General company description\n"
        "   - Tech stack indicators\n"
        "   - Team size/structure hints\n"
        "   - Industry focus areas\n\n"
        
        "   Score 3-4 (CONTEXTUAL):\n"
        "   - Company history\n"
        "   - General content topics\n"
        "   - Blog/resource topics\n\n"
        
        "   Score 1-2 (LOW VALUE):\n"
        "   - Navigation elements\n"
        "   - Generic marketing copy\n"
        "   - Unrelated content\n\n"
        
        "**3. SUMMARY REQUIREMENTS**\n"
        "   - 2-3 sentences maximum\n"
        "   - Lead with the most actionable insight\n"
        "   - Include: industry, main offering, target customer\n"
        "   - Note any unique angles for proposals\n\n"
        
        "=== QUALITY STANDARDS ===\n"
        "□ Extract 5-15 entities (not fewer, not more)\n"
        "□ Each entity has specific, concrete details\n"
        "□ Include actual names, numbers, and facts\n"
        "□ Relevance score is justified by content\n"
        "□ Summary captures the 'so what' for sales\n\n"
        
        "=== OUTPUT FORMAT ===\n"
        "Always return structured JSON matching the KnowledgeOutput schema:\n"
        "- summary: string (2-3 sentences)\n"
        "- entities: list of Entity objects\n"
        "- relevance_score: integer 1-10\n"
    ),
)

# --- Tools ---
@knowledge_agent.tool
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def scrape_url(ctx: RunContext[KnowledgeDeps], url: str) -> str:
    """
    Scrape the content of a URL using Firecrawl (self-hosted or cloud).
    
    Args:
        url: The URL to scrape
        
    Returns:
        Markdown content from the URL
        
    Raises:
        FirecrawlError: If scraping fails after retries
    """
    try:
        structured_logger.info(f"Starting URL scrape", url=url)
        
        # Use self-hosted Firecrawl if URL is provided, otherwise use API key
        firecrawl_url = ctx.deps.firecrawl_api_url or FIRECRAWL_API_URL
        
        # For self-hosted Firecrawl, API key is optional
        if firecrawl_url and firecrawl_url != "https://api.firecrawl.dev":
            # Self-hosted instance - API key optional
            structured_logger.debug(f"Using self-hosted Firecrawl", firecrawl_url=firecrawl_url)
            app = FirecrawlApp(api_key=ctx.deps.firecrawl_api_key or "fc-optional", api_url=firecrawl_url)
        else:
            # Cloud instance - API key required
            if not ctx.deps.firecrawl_api_key:
                structured_logger.error("Firecrawl API key not set for cloud instance")
                raise FirecrawlError(
                    "Firecrawl API key not configured",
                    error_code=ErrorCode.CONFIG_MISSING_ENV
                )
            app = FirecrawlApp(api_key=ctx.deps.firecrawl_api_key)
        
        # Scrape the URL with fallback handling
        result = None
        try:
            # Try passing params directly (v1 style)
            result = app.scrape_url(url, params={'formats': ['markdown']})
        except (TypeError, AttributeError):
            # Fallback for older versions or different signatures
            try:
                result = app.scrape(url, formats=['markdown'])
            except TypeError:
                result = app.scrape(url, params={'formats': ['markdown']})
        
        if not result or 'markdown' not in result:
            structured_logger.warning(f"No markdown content returned", url=url)
            return f"Warning: Could not extract markdown from {url}"
        
        markdown_content = result['markdown']
        content_length = len(markdown_content)
        structured_logger.info(
            f"URL scraped successfully",
            url=url,
            content_length=content_length
        )
        
        return markdown_content
        
    except httpx.TimeoutException as e:
        structured_logger.error(f"Timeout scraping URL", url=url)
        raise FirecrawlError(
            f"Request timed out while scraping {url}",
            error_code=ErrorCode.FIRECRAWL_TIMEOUT,
            original_error=e
        )
    except httpx.HTTPStatusError as e:
        structured_logger.error(
            f"HTTP error scraping URL",
            url=url,
            status_code=e.response.status_code
        )
        raise FirecrawlError(
            f"HTTP {e.response.status_code} while scraping {url}",
            error_code=ErrorCode.FIRECRAWL_API_ERROR,
            original_error=e
        )
    except FirecrawlError:
        raise  # Re-raise our custom exceptions
    except Exception as e:
        structured_logger.error(f"Unexpected error scraping URL", url=url, error=str(e))
        raise FirecrawlError(
            f"Error scraping URL: {str(e)}",
            error_code=ErrorCode.FIRECRAWL_SCRAPE_FAILED,
            original_error=e
        )

@knowledge_agent.tool
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def store_knowledge(ctx: RunContext[KnowledgeDeps], data: KnowledgeOutput) -> str:
    """
    Store the extracted knowledge in Convex.
    
    Args:
        data: The knowledge output to store
        
    Returns:
        Success or error message
        
    Raises:
        ConvexError: If storage fails after retries
    """
    if not ctx.deps.convex_url or not ctx.deps.convex_token:
        structured_logger.error("Convex credentials not configured")
        raise ConvexError(
            "Convex URL or token not configured",
            error_code=ErrorCode.CONFIG_MISSING_ENV
        )
    
    try:
        entity_count = len(data.entities)
        structured_logger.info(
            f"Storing knowledge to Convex",
            entity_count=entity_count,
            relevance_score=data.relevance_score
        )
        
        # Prepare the payload
        payload = {
            "summary": data.summary,
            "entities": [
                {
                    "name": entity.name,
                    "type": entity.type,
                    "details": entity.details
                }
                for entity in data.entities
            ],
            "relevance_score": data.relevance_score
        }
        
        # Call Convex mutation
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{ctx.deps.convex_url}/api/mutation",
                json={
                    "path": "knowledge:create",
                    "args": payload
                },
                headers={
                    "Authorization": f"Bearer {ctx.deps.convex_token}",
                    "Content-Type": "application/json"
                }
            )
            
            response.raise_for_status()
            result = response.json()
            
            knowledge_id = result.get('id', 'unknown')
            structured_logger.info(
                f"Knowledge stored successfully",
                knowledge_id=knowledge_id,
                entity_count=entity_count
            )
            return f"Stored successfully. Knowledge ID: {knowledge_id}"
            
    except httpx.TimeoutException as e:
        structured_logger.error("Timeout storing knowledge to Convex")
        raise ConvexError(
            "Request timed out while storing knowledge",
            error_code=ErrorCode.CONVEX_TIMEOUT,
            original_error=e
        )
    except httpx.HTTPStatusError as e:
        structured_logger.error(
            f"HTTP error storing knowledge",
            status_code=e.response.status_code,
            response_text=e.response.text[:200]
        )
        if e.response.status_code == 401:
            raise ConvexError(
                "Unauthorized - Invalid Convex token",
                error_code=ErrorCode.AUTH_INVALID_KEY,
                original_error=e
            )
        elif e.response.status_code == 404:
            raise ConvexError(
                "Convex mutation not found",
                error_code=ErrorCode.CONVEX_MUTATION_FAILED,
                original_error=e
            )
        else:
            raise ConvexError(
                f"Failed to store knowledge (HTTP {e.response.status_code})",
                error_code=ErrorCode.CONVEX_API_ERROR,
                original_error=e
            )
    except ConvexError:
        raise  # Re-raise our custom exceptions
    except Exception as e:
        structured_logger.error(f"Unexpected error storing knowledge", error=str(e))
        raise ConvexError(
            f"Error storing knowledge: {str(e)}",
            error_code=ErrorCode.CONVEX_API_ERROR,
            original_error=e
        )
