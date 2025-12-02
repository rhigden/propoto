from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic import BaseModel, Field
from dataclasses import dataclass
import os
import sys
import httpx
from typing import List, Optional, Any
from tenacity import retry, stop_after_attempt, wait_exponential

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import StructuredLogger, agent_name_var
from utils.exceptions import ExaError, ConvexError, ErrorCode

# Initialize structured logger
structured_logger = StructuredLogger()

# --- Dependencies ---
@dataclass
class SalesDeps:
    exa_api_key: str
    convex_url: str
    convex_token: str

# --- Output Models ---
class Lead(BaseModel):
    company_name: str
    website: Optional[str]
    description: str
    score: int = Field(description="0-100 score of fit")
    status: str = "new"

class SalesOutput(BaseModel):
    leads: List[Lead]
    market_summary: str

# --- Agent Definition ---
# Use Grok 4.1 Fast FREE via OpenRouter (until Dec 3, 2025)
def get_openrouter_model(model_name: str = "x-ai/grok-4.1-fast:free") -> OpenAIChatModel:
    """Create an OpenAI-compatible model pointing to OpenRouter."""
    return OpenAIChatModel(model_name, provider='openrouter')

# Set agent context for logging
agent_name_var.set("sales_agent")

sales_agent = Agent(
    get_openrouter_model(),
    deps_type=SalesDeps,
    output_type=SalesOutput,
    instructions=(
        "You are the Sales Hunter, a senior business development specialist with 15+ years of "
        "experience identifying and qualifying high-value prospects. Your leads directly feed "
        "into a proposal generation system.\n\n"
        
        "=== YOUR MISSION ===\n"
        "Find companies that are the BEST fit for our services, not just any company that matches "
        "the search terms. Quality trumps quantity every time.\n\n"
        
        "=== LEAD DISCOVERY PROCESS ===\n\n"
        
        "**Step 1: Search Interpretation**\n"
        "- Understand the INTENT behind the search query\n"
        "- Identify implicit criteria (industry, company size, tech sophistication)\n"
        "- Consider what makes a company likely to BUY, not just match keywords\n\n"
        
        "**Step 2: Lead Qualification**\n"
        "For each potential lead, assess:\n"
        "- Is this a real company with a legitimate website?\n"
        "- Do they have budget indicators (funding, team size, pricing)?\n"
        "- Is there evidence of growth or need?\n"
        "- Can we actually help them with our services?\n\n"
        
        "**Step 3: Lead Scoring (Be Strict)**\n"
        "Score based on LIKELIHOOD TO CONVERT, not just relevance:\n\n"
        
        "   90-100 (PERFECT FIT):\n"
        "   - Exact match to search criteria\n"
        "   - Clear evidence of budget (funded startup, enterprise, pricing visible)\n"
        "   - Active growth indicators (hiring, expanding, recent news)\n"
        "   - Pain point explicitly mentioned in their content\n"
        "   - Decision maker contactable\n\n"
        
        "   80-89 (EXCELLENT FIT):\n"
        "   - Strong match to criteria\n"
        "   - Reasonable budget assumptions\n"
        "   - Growth trajectory visible\n"
        "   - Implicit pain points detectable\n\n"
        
        "   70-79 (GOOD FIT):\n"
        "   - Relevant match\n"
        "   - Decent company quality\n"
        "   - Some fit indicators\n"
        "   - Worth initial outreach\n\n"
        
        "   60-69 (MODERATE FIT):\n"
        "   - Somewhat relevant\n"
        "   - Unclear budget/need\n"
        "   - May require more research\n"
        "   - Lower priority\n\n"
        
        "   Below 60 (DON'T INCLUDE):\n"
        "   - Don't waste time on poor fits\n"
        "   - Better to return 3 great leads than 10 mediocre ones\n\n"
        
        "=== SCORING FORMULA ===\n"
        "- Query Relevance (30%): How well does their business match the search?\n"
        "- Budget Indicators (25%): Can they afford services? (funding, pricing, scale)\n"
        "- Growth Signals (20%): Are they growing? (hiring, news, expansion)\n"
        "- Need Evidence (15%): Do they show pain points we can solve?\n"
        "- Contactability (10%): Can we reach decision makers?\n\n"
        
        "=== OUTPUT REQUIREMENTS ===\n\n"
        
        "**LEADS (3-10, Quality Over Quantity)**\n"
        "For each lead, provide:\n"
        "- company_name: Exact legal/brand name (not generic descriptions)\n"
        "- website: Full URL (https://...)\n"
        "- description: 1-2 sentences covering:\n"
        "  * What they do\n"
        "  * Why they're a good fit\n"
        "  * Any pain points or opportunities you identified\n"
        "- score: 60-100 (don't include leads below 60)\n"
        "- status: 'new'\n\n"
        
        "**MARKET SUMMARY (3-4 sentences)**\n"
        "Cover:\n"
        "- Overall market size/activity in this space\n"
        "- Common patterns among the leads found\n"
        "- Key opportunities or trends observed\n"
        "- Recommended approach for outreach\n\n"
        
        "=== QUALITY CHECKLIST ===\n"
        "□ All leads are real companies with working websites\n"
        "□ No duplicate companies\n"
        "□ Scores are justified and differentiated (not all the same)\n"
        "□ Descriptions are specific, not generic\n"
        "□ Market summary provides actionable insights\n"
        "□ Better to return fewer high-quality leads than many low-quality ones\n"
    ),
)

# --- Tools ---
@sales_agent.tool
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def search_leads(ctx: RunContext[SalesDeps], query: str) -> str:
    """
    Search for leads using Exa API.
    
    Args:
        query: The search query to find companies
        
    Returns:
        Raw search results in JSON string format
        
    Raises:
        ExaError: If search fails after retries
    """
    if not ctx.deps.exa_api_key:
        structured_logger.error("Exa API key not configured")
        raise ExaError(
            "Exa API key not configured",
            error_code=ErrorCode.CONFIG_MISSING_ENV
        )
    
    try:
        structured_logger.info(f"Starting Exa lead search", query=query)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.exa.ai/search",
                json={
                    "query": query,
                    "numResults": 10,  # Request more, filter later
                    "useAutoprompt": True,
                    "contents": {"text": True} 
                },
                headers={
                    "x-api-key": ctx.deps.exa_api_key,
                    "Content-Type": "application/json"
                }
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Simplify results for the LLM to save tokens
            simplified = []
            for res in result.get("results", []):
                simplified.append({
                    "title": res.get("title"),
                    "url": res.get("url"),
                    "text": res.get("text", "")[:500]  # Truncate text
                })
            
            result_count = len(simplified)
            structured_logger.info(
                f"Exa search completed",
                query=query,
                result_count=result_count
            )
            
            return str(simplified)
    
    except httpx.TimeoutException as e:
        structured_logger.error(f"Timeout searching Exa", query=query)
        raise ExaError(
            "Request timed out while searching Exa",
            error_code=ErrorCode.EXA_TIMEOUT,
            original_error=e
        )
    except httpx.HTTPStatusError as e:
        structured_logger.error(
            f"HTTP error searching Exa",
            query=query,
            status_code=e.response.status_code
        )
        if e.response.status_code == 429:
            raise ExaError(
                "Exa API rate limit exceeded",
                error_code=ErrorCode.EXA_RATE_LIMIT,
                original_error=e
            )
        raise ExaError(
            f"Exa API error (HTTP {e.response.status_code})",
            error_code=ErrorCode.EXA_API_ERROR,
            original_error=e
        )
    except ExaError:
        raise  # Re-raise our custom exceptions
    except Exception as e:
        structured_logger.error(f"Unexpected error searching Exa", query=query, error=str(e))
        raise ExaError(
            f"Error searching Exa: {str(e)}",
            error_code=ErrorCode.EXA_API_ERROR,
            original_error=e
        )

@sales_agent.tool
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def store_leads(ctx: RunContext[SalesDeps], data: SalesOutput) -> str:
    """
    Store the found leads in Convex.
    
    Args:
        data: The sales output containing leads
        
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
        lead_count = len(data.leads)
        structured_logger.info(f"Storing leads to Convex", lead_count=lead_count)
        
        results = {"success": 0, "failed": 0}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for lead in data.leads:
                # Prepare payload for each lead
                payload = {
                    "companyName": lead.company_name,
                    "website": lead.website,
                    "score": lead.score,
                    "status": lead.status,
                    "data": {"description": lead.description}
                }
                
                try:
                    response = await client.post(
                        f"{ctx.deps.convex_url}/api/mutation",
                        json={
                            "path": "leads:create",
                            "args": payload
                        },
                        headers={
                            "Authorization": f"Bearer {ctx.deps.convex_token}",
                            "Content-Type": "application/json"
                        }
                    )
                    
                    if response.status_code == 200:
                        results["success"] += 1
                        structured_logger.debug(
                            f"Lead stored successfully",
                            company_name=lead.company_name
                        )
                    else:
                        results["failed"] += 1
                        structured_logger.warning(
                            f"Failed to store lead",
                            company_name=lead.company_name,
                            status_code=response.status_code,
                            response_text=response.text[:100]
                        )
                except Exception as e:
                    results["failed"] += 1
                    structured_logger.warning(
                        f"Error storing individual lead",
                        company_name=lead.company_name,
                        error=str(e)
                    )
            
            structured_logger.info(
                f"Lead storage completed",
                success_count=results["success"],
                failed_count=results["failed"]
            )
            
            return f"Stored {results['success']} leads. ({results['failed']} failed)"
            
    except httpx.TimeoutException as e:
        structured_logger.error("Timeout storing leads to Convex")
        raise ConvexError(
            "Request timed out while storing leads",
            error_code=ErrorCode.CONVEX_TIMEOUT,
            original_error=e
        )
    except httpx.HTTPStatusError as e:
        structured_logger.error(
            f"HTTP error storing leads",
            status_code=e.response.status_code,
            response_text=e.response.text[:200]
        )
        if e.response.status_code == 401:
            raise ConvexError(
                "Unauthorized - Invalid Convex token",
                error_code=ErrorCode.AUTH_INVALID_KEY,
                original_error=e
            )
        raise ConvexError(
            f"Failed to store leads (HTTP {e.response.status_code})",
            error_code=ErrorCode.CONVEX_API_ERROR,
            original_error=e
        )
    except ConvexError:
        raise  # Re-raise our custom exceptions
    except Exception as e:
        structured_logger.error(f"Unexpected error storing leads", error=str(e))
        raise ConvexError(
            f"Error storing leads: {str(e)}",
            error_code=ErrorCode.CONVEX_API_ERROR,
            original_error=e
        )
