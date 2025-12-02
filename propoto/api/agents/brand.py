from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic import BaseModel, Field
from dataclasses import dataclass
import os
import sys
import httpx
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential
from mem0 import Memory

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import StructuredLogger, agent_name_var
from utils.exceptions import GammaError, Mem0Error, ErrorCode

# Initialize structured logger
structured_logger = StructuredLogger()

# --- Dependencies ---
@dataclass
class BrandDeps:
    gamma_api_key: str
    mem0_api_key: str

# --- Output Models ---
class BrandAsset(BaseModel):
    asset_type: str = Field(description="presentation, document, or webpage")
    url: str
    description: str

# --- Agent Definition ---
# Use Grok 4.1 Fast FREE via OpenRouter (until Dec 3, 2025)
def get_openrouter_model(model_name: str = "x-ai/grok-4.1-fast:free") -> OpenAIChatModel:
    """Create an OpenAI-compatible model pointing to OpenRouter."""
    return OpenAIChatModel(model_name, provider='openrouter')

# Set agent context for logging
agent_name_var.set("brand_agent")

brand_agent = Agent(
    get_openrouter_model(),
    deps_type=BrandDeps,
    output_type=BrandAsset,
    instructions=(
        "You are the Brand Designer, an expert creative director with 15+ years of experience "
        "creating compelling visual presentations and brand assets. You use Gamma to create "
        "professional, visually stunning presentations, documents, and webpages.\n\n"
        
        "=== YOUR CREATIVE PHILOSOPHY ===\n"
        "- Form follows function: Design supports the message, not the other way around\n"
        "- Less is more: Clean, focused layouts beat cluttered slides\n"
        "- Consistency is key: Maintain brand identity throughout\n"
        "- Story-driven: Every presentation should tell a compelling narrative\n\n"
        
        "=== GAMMA CAPABILITIES ===\n"
        "- AI-powered content generation from prompts\n"
        "- AI-generated images using flux-1-pro model\n"
        "- Professional themes and layouts\n"
        "- PDF export for sharing\n\n"
        
        "=== ASSET TYPES ===\n"
        "1. **presentation**: Slide decks for pitches, proposals, reports\n"
        "2. **document**: Long-form content like case studies, whitepapers\n"
        "3. **webpage**: Landing pages and microsite content\n\n"
        
        "=== DESIGN BEST PRACTICES ===\n"
        "- Use 7-10 slides for presentations (not more)\n"
        "- One key message per slide\n"
        "- Visual hierarchy: Headlines > Subheads > Body\n"
        "- Incorporate brand colors and tone when available\n"
        "- End with clear call-to-action\n\n"
        
        "=== OUTPUT REQUIREMENTS ===\n"
        "Return a BrandAsset with:\n"
        "- asset_type: 'presentation', 'document', or 'webpage'\n"
        "- url: The Gamma URL where the asset can be viewed\n"
        "- description: Brief summary of what was created\n"
    ),
)

# --- Tools ---
@brand_agent.tool
@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=2, max=10))
async def create_gamma_presentation(
    ctx: RunContext[BrandDeps], 
    prompt: str, 
    theme_id: str = None, 
    num_cards: int = 10,
    format: str = "presentation",
    tone: str = "professional, innovative",
    image_style: str = "photorealistic, modern"
) -> str:
    """
    Create a presentation, document, or webpage using Gamma API.
    
    Args:
        prompt: The content/topic for the asset.
        theme_id: Optional UUID of a Gamma theme.
        num_cards: Number of slides/sections (default 10).
        format: 'presentation', 'document', or 'webpage'.
        tone: Desired tone for the content.
        image_style: Style for AI-generated images.
        
    Returns:
        URL to the created asset or error message.
        
    Raises:
        GammaError: If generation fails after retries.
    """
    if not ctx.deps.gamma_api_key:
        structured_logger.error("Gamma API key not configured")
        raise GammaError(
            "Gamma API key not configured",
            error_code=ErrorCode.CONFIG_MISSING_ENV,
            retryable=False
        )
    
    # Get brand guidelines to enrich the prompt (with org context if available)
    org_id = getattr(ctx, 'org_id', 'demo-org-1') if hasattr(ctx, 'org_id') else 'demo-org-1'
    brand_guidelines = await get_brand_guidelines(ctx, org_id=org_id)
    enriched_prompt = f"{prompt}\n\nBrand Guidelines:\n{brand_guidelines}"
    
    headers = {
        "X-API-Key": ctx.deps.gamma_api_key,
        "Content-Type": "application/json"
    }
    
    # Construct comprehensive payload
    payload = {
        "inputText": enriched_prompt,
        "textMode": "generate",
        "format": format,
        "numCards": num_cards,
        "cardSplit": "auto",
        "textOptions": {
            "tone": tone,
            "amount": "detailed",
            "language": "en"
        },
        "imageOptions": {
            "source": "aiGenerated",
            "model": "flux-1-pro",
            "style": image_style
        },
        "exportAs": "pdf"
    }
    
    if theme_id:
        payload["themeId"] = theme_id
    
    try:
        structured_logger.info(
            f"Starting Gamma generation",
            format=format,
            num_cards=num_cards,
            tone=tone
        )
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 1. Start Generation
            resp = await client.post(
                "https://public-api.gamma.app/v1.0/generations", 
                json=payload, 
                headers=headers
            )
            resp.raise_for_status()
            job_data = resp.json()
            job_id = job_data.get("id")
            
            if not job_id:
                structured_logger.error(f"No job ID in Gamma response", response=job_data)
                raise GammaError(
                    "No job ID returned from Gamma",
                    error_code=ErrorCode.GAMMA_API_ERROR
                )

            structured_logger.info(f"Gamma job started", job_id=job_id)

            # 2. Poll for Completion (30 attempts × 5 seconds = 2.5 minutes)
            for attempt in range(30):
                await asyncio.sleep(5)
                
                status_resp = await client.get(
                    f"https://public-api.gamma.app/v1.0/generations/{job_id}",
                    headers=headers
                )
                status_resp.raise_for_status()
                status_data = status_resp.json()
                status = status_data.get("status")
                
                structured_logger.debug(
                    f"Gamma status poll",
                    job_id=job_id,
                    attempt=attempt + 1,
                    status=status
                )
                
                if status == "COMPLETED":
                    gamma_url = status_data.get("gammaUrl")
                    pdf_url = status_data.get("pdfUrl")
                    
                    structured_logger.info(
                        f"Gamma generation completed",
                        job_id=job_id,
                        gamma_url=gamma_url,
                        has_pdf=bool(pdf_url)
                    )
                    
                    result = f"✅ {format.capitalize()} created successfully!\n"
                    result += f"View: {gamma_url}\n"
                    if pdf_url:
                        result += f"PDF: {pdf_url}"
                    return result
                    
                elif status == "FAILED":
                    error_msg = status_data.get("error", "Unknown error")
                    structured_logger.error(
                        f"Gamma generation failed",
                        job_id=job_id,
                        error=error_msg
                    )
                    raise GammaError(
                        f"Generation failed: {error_msg}",
                        error_code=ErrorCode.GAMMA_API_ERROR,
                        retryable=False
                    )
            
            structured_logger.warning(f"Gamma generation timed out", job_id=job_id)
            raise GammaError(
                "Generation timed out after 2.5 minutes",
                error_code=ErrorCode.GAMMA_TIMEOUT
            )
            
    except httpx.HTTPStatusError as e:
        error_text = e.response.text[:200]
        status_code = e.response.status_code
        
        structured_logger.error(
            f"Gamma API HTTP error",
            status_code=status_code,
            error_text=error_text
        )
        
        if status_code == 401:
            raise GammaError(
                "Invalid Gamma API key",
                error_code=ErrorCode.AUTH_INVALID_KEY,
                retryable=False,
                original_error=e
            )
        elif status_code == 429:
            raise GammaError(
                "Gamma rate limit exceeded",
                error_code=ErrorCode.GAMMA_RATE_LIMIT,
                retry_after_seconds=60,
                original_error=e
            )
        elif status_code == 402:
            raise GammaError(
                "Insufficient Gamma credits",
                error_code=ErrorCode.GAMMA_CREDITS,
                retryable=False,
                original_error=e
            )
        else:
            raise GammaError(
                f"Gamma API error ({status_code}): {error_text}",
                error_code=ErrorCode.GAMMA_API_ERROR,
                original_error=e
            )
            
    except httpx.TimeoutException as e:
        structured_logger.error("Gamma API request timed out")
        raise GammaError(
            "Request timed out",
            error_code=ErrorCode.GAMMA_TIMEOUT,
            original_error=e
        )
        
    except GammaError:
        raise  # Re-raise our custom exceptions
        
    except Exception as e:
        structured_logger.error(f"Unexpected error creating Gamma asset", error=str(e))
        raise GammaError(
            f"Unexpected error: {str(e)}",
            error_code=ErrorCode.GAMMA_API_ERROR,
            original_error=e
        )

@brand_agent.tool
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def get_brand_guidelines(ctx: RunContext[BrandDeps], org_id: str = "demo-org-1") -> str:
    """
    Retrieve brand guidelines from Mem0 using BrandMemoryService.
    
    Args:
        org_id: Organization ID to retrieve brand voice for (defaults to demo-org-1)
    
    Returns:
        Brand guidelines as a formatted string, or default guidelines if Mem0 not configured.
    """
    if not ctx.deps.mem0_api_key:
        structured_logger.warning(
            f"Mem0 API key not set, using default brand guidelines",
            org_id=org_id
        )
        return _get_default_guidelines()
    
    try:
        structured_logger.info(f"Fetching brand guidelines from Mem0", org_id=org_id)
        
        # Use BrandMemoryService for better organization support
        from services.brand_memory_service import get_brand_memory_service
        
        service = get_brand_memory_service()
        brand_voice = await service.get_brand_voice(org_id)
        
        # Format brand voice into guidelines string
        guidelines_parts = []
        
        if brand_voice.company_name:
            guidelines_parts.append(f"Company: {brand_voice.company_name}")
        
        if brand_voice.tagline:
            guidelines_parts.append(f"Tagline: {brand_voice.tagline}")
        
        if brand_voice.brand_colors:
            colors_str = ", ".join(brand_voice.brand_colors[:5])
            guidelines_parts.append(f"Brand Colors: {colors_str}")
        elif brand_voice.primary_color:
            guidelines_parts.append(f"Primary Color: {brand_voice.primary_color}")
        
        if brand_voice.tone_keywords:
            tone_str = ", ".join(brand_voice.tone_keywords)
            guidelines_parts.append(f"Tone: {tone_str}")
        
        if brand_voice.writing_style:
            guidelines_parts.append(f"Writing Style: {brand_voice.writing_style}")
        
        if brand_voice.target_audience:
            guidelines_parts.append(f"Target Audience: {brand_voice.target_audience}")
        
        if brand_voice.key_messages:
            messages_str = "; ".join(brand_voice.key_messages[:3])
            guidelines_parts.append(f"Key Messages: {messages_str}")
        
        if brand_voice.avoid_phrases:
            avoid_str = ", ".join(brand_voice.avoid_phrases[:5])
            guidelines_parts.append(f"Avoid Phrases: {avoid_str}")
        
        if brand_voice.preferred_phrases:
            preferred_str = ", ".join(brand_voice.preferred_phrases[:5])
            guidelines_parts.append(f"Preferred Phrases: {preferred_str}")
        
        if brand_voice.custom_guidelines:
            guidelines_parts.append(f"Custom Guidelines: {brand_voice.custom_guidelines}")
        
        if guidelines_parts:
            guidelines = "\n".join(guidelines_parts)
            structured_logger.info(
                f"Brand guidelines retrieved",
                org_id=org_id,
                element_count=len(guidelines_parts)
            )
            return guidelines
        else:
            structured_logger.info(
                f"No brand guidelines found, using defaults",
                org_id=org_id
            )
            return _get_default_guidelines()
            
    except ImportError:
        structured_logger.warning(
            "BrandMemoryService not available, falling back to direct Mem0",
            org_id=org_id
        )
        # Fallback to direct Mem0 access
        try:
            mem0_client = Memory(api_key=ctx.deps.mem0_api_key)
            results = mem0_client.search(
                query="brand guidelines colors tone voice style",
                user_id=f"brand_{org_id}"
            )
            
            if results and len(results) > 0:
                guidelines = "\n".join([
                    result.get("memory", "")
                    for result in results[:3]
                ])
                structured_logger.info(
                    f"Brand guidelines retrieved via direct Mem0",
                    org_id=org_id,
                    memory_count=len(results)
                )
                return guidelines
        except Exception as e:
            structured_logger.error(
                f"Error in Mem0 fallback",
                org_id=org_id,
                error=str(e)
            )
    
    except Exception as e:
        structured_logger.error(
            f"Error fetching brand guidelines",
            org_id=org_id,
            error=str(e)
        )
        return _get_default_guidelines()

def _get_default_guidelines() -> str:
    """Get default brand guidelines when Mem0 is not available."""
    return (
        "Brand Colors: Professional palette (blues, grays, whites)\n"
        "Tone: Professional, innovative, value-focused\n"
        "Writing Style: Direct, clear, no corporate jargon\n"
        "Target Audience: Business decision-makers"
    )

@brand_agent.tool
async def save_brand_guideline(
    ctx: RunContext[BrandDeps],
    guideline: str,
    org_id: str = "demo-org-1"
) -> str:
    """
    Save a new brand guideline to Mem0 using BrandMemoryService.
    
    Args:
        guideline: The brand guideline to save
        org_id: Organization ID (defaults to demo-org-1)
        
    Returns:
        Success or error message
        
    Raises:
        Mem0Error: If saving fails
    """
    if not ctx.deps.mem0_api_key:
        structured_logger.error("Mem0 API key not configured", org_id=org_id)
        raise Mem0Error(
            "Mem0 API key not configured",
            error_code=ErrorCode.CONFIG_MISSING_ENV
        )
    
    try:
        structured_logger.info(
            f"Saving brand guideline to Mem0",
            org_id=org_id,
            guideline_length=len(guideline)
        )
        
        # Try using BrandMemoryService first
        try:
            from services.brand_memory_service import get_brand_memory_service, BrandVoice
            
            service = get_brand_memory_service()
            
            # Get existing brand voice or create new
            brand_voice = await service.get_brand_voice(org_id)
            
            # Update custom guidelines
            if not brand_voice.custom_guidelines:
                brand_voice.custom_guidelines = guideline
            else:
                brand_voice.custom_guidelines += f"\n\n{guideline}"
            
            # Save updated brand voice
            success = await service.save_brand_voice(brand_voice)
            
            if success:
                structured_logger.info(
                    f"Brand guideline saved via BrandMemoryService",
                    org_id=org_id
                )
                return f"✅ Brand guideline saved to memory for org {org_id}: {guideline[:100]}..."
            else:
                raise Mem0Error(
                    "BrandMemoryService save returned False",
                    error_code=ErrorCode.MEM0_API_ERROR
                )
                
        except ImportError:
            structured_logger.warning(
                "BrandMemoryService not available, using direct Mem0",
                org_id=org_id
            )
            # Fallback to direct Mem0 access
            mem0_client = Memory(api_key=ctx.deps.mem0_api_key)
            
            result = mem0_client.add(
                messages=[{"role": "user", "content": guideline}],
                user_id=f"brand_{org_id}"
            )
            
            structured_logger.info(
                f"Brand guideline saved via direct Mem0",
                org_id=org_id,
                result=str(result)[:100]
            )
            return f"✅ Brand guideline saved to memory: {guideline[:100]}..."
        
    except Mem0Error:
        raise  # Re-raise our custom exceptions
    except Exception as e:
        structured_logger.error(
            f"Error saving brand guideline",
            org_id=org_id,
            error=str(e)
        )
        raise Mem0Error(
            f"Error saving guideline: {str(e)}",
            error_code=ErrorCode.MEM0_API_ERROR,
            original_error=e
        )
