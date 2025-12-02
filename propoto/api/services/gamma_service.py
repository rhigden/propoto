"""
Gamma API Service v1.0

Official Gamma API Documentation: https://developers.gamma.app/

API Endpoints:
- POST /v1.0/generations - Start a new generation job
- GET /v1.0/generations/{id} - Check generation status
- GET /v1.0/themes - List available themes
- GET /v1.0/folders - List folders

Authentication:
- Header: X-API-Key: sk-gamma-xxxxxxxx
- Requires Pro account or higher

Formats Supported:
- presentation (slides)
- document (long-form)
- webpage (landing page)
- social (social media posts)

Image Options:
- source: "aiGenerated", "webSearch", "none"
- model: "flux-1-pro", "flux-1-schnell" (for AI generated)
- style: custom style description

Note: API v0.2 deprecated on January 16, 2026. Using v1.0.
"""

import os
import httpx
import asyncio
import logging
from typing import Optional, Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Gamma API v1.0 Base URL
GAMMA_API_BASE = "https://public-api.gamma.app/v1.0"


class GammaService:
    """
    Service for generating presentations, documents, and webpages using Gamma API v1.0.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GAMMA_API_KEY")
        if not self.api_key:
            logger.warning("GAMMA_API_KEY not set. Gamma integration will be disabled.")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for Gamma API requests."""
        return {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }

    async def generate_presentation(
        self, 
        proposal_data: Dict[str, Any],
        format: str = "presentation",
        num_cards: int = 7,
        theme_id: Optional[str] = None,
        return_export_urls: bool = True
    ) -> Dict[str, Any]:
        """
        Generates a presentation using the Gamma API v1.0 based on proposal data.
        
        Args:
            proposal_data: Dict containing proposal content (executive_summary, etc.)
            format: "presentation", "document", or "webpage"
            num_cards: Number of slides/cards (default 7 for proposals)
            theme_id: Optional Gamma theme UUID
            return_export_urls: If True, returns dict with all URLs
            
        Returns:
            Dict with gammaUrl, pdfUrl, pptxUrl, or just gammaUrl string for backwards compat.
        """
        if not self.api_key:
            logger.warning("Gamma API key not set, skipping deck generation")
            return {"gammaUrl": None, "pdfUrl": None, "pptxUrl": None} if return_export_urls else None

        # Construct the prompt for Gamma
        prompt = self._construct_proposal_prompt(proposal_data)

        # Build the payload per Gamma API v1.0 spec
        payload = {
            "inputText": prompt,
            "textMode": "generate",  # "generate" = AI writes content, "keep" = use input verbatim
            "format": format,
            "numCards": num_cards,
            "cardSplit": "auto",  # "auto", "none", "horizontal", "vertical"
            "textOptions": {
                "tone": "professional, persuasive",
                "amount": "detailed",
                "language": "en"
            },
            "imageOptions": {
                "source": "aiGenerated",  # "aiGenerated", "webSearch", "none"
                "model": "flux-1-pro",     # Best quality AI images
                "style": "professional, modern, clean"
            },
            "exportAs": "pdf"  # Also generate PDF export
        }
        
        if theme_id:
            payload["themeId"] = theme_id

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Step 1: Start Generation Job
                logger.info(f"Starting Gamma generation: {format} with {num_cards} cards")
                
                resp = await client.post(
                    f"{GAMMA_API_BASE}/generations",
                    json=payload,
                    headers=self._get_headers()
                )
                resp.raise_for_status()
                job_data = resp.json()
                job_id = job_data.get("id")
                
                if not job_id:
                    logger.error(f"No job ID returned from Gamma: {job_data}")
                    return {"gammaUrl": None, "pdfUrl": None, "pptxUrl": None} if return_export_urls else None
                
                logger.info(f"Gamma job started: {job_id}")
                
                # Step 2: Poll for Completion with export URLs
                result = await self._poll_for_completion(client, job_id, return_export_urls=return_export_urls)
                
                return result
                
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e)
            return {"gammaUrl": None, "pdfUrl": None, "pptxUrl": None} if return_export_urls else None
        except httpx.TimeoutException:
            logger.error("Gamma API request timed out")
            return {"gammaUrl": None, "pdfUrl": None, "pptxUrl": None} if return_export_urls else None
        except Exception as e:
            logger.error(f"Unexpected error generating Gamma presentation: {e}", exc_info=True)
            return {"gammaUrl": None, "pdfUrl": None, "pptxUrl": None} if return_export_urls else None

    async def _poll_for_completion(
        self, 
        client: httpx.AsyncClient, 
        job_id: str,
        max_attempts: int = 30,
        poll_interval: int = 5,
        return_export_urls: bool = True
    ) -> Any:
        """
        Poll Gamma API for job completion.
        
        Args:
            client: HTTPX async client
            job_id: Gamma generation job ID
            max_attempts: Max polling attempts (default 30 = 2.5 min)
            poll_interval: Seconds between polls (default 5)
            return_export_urls: If True, return dict with all URLs
            
        Returns:
            Dict with gammaUrl, pdfUrl, pptxUrl if return_export_urls=True, else just gammaUrl string
        """
        for attempt in range(max_attempts):
            await asyncio.sleep(poll_interval)
            
            try:
                status_resp = await client.get(
                    f"{GAMMA_API_BASE}/generations/{job_id}",
                    headers=self._get_headers()
                )
                status_resp.raise_for_status()
                status_data = status_resp.json()
                status = status_data.get("status")
                
                logger.info(f"Gamma status (attempt {attempt + 1}/{max_attempts}): {status}")
                
                if status == "COMPLETED":
                    gamma_url = status_data.get("gammaUrl")
                    pdf_url = status_data.get("pdfUrl")
                    pptx_url = status_data.get("pptxUrl")
                    
                    logger.info(f"Gamma completed successfully: {gamma_url}")
                    if pdf_url:
                        logger.info(f"PDF available: {pdf_url}")
                    if pptx_url:
                        logger.info(f"PPTX available: {pptx_url}")
                    
                    if return_export_urls:
                        return {
                            "gammaUrl": gamma_url,
                            "pdfUrl": pdf_url,
                            "pptxUrl": pptx_url
                        }
                    return gamma_url
                    
                elif status == "FAILED":
                    error_msg = status_data.get("error", "Unknown error")
                    logger.error(f"Gamma generation failed: {error_msg}")
                    if return_export_urls:
                        return {"gammaUrl": None, "pdfUrl": None, "pptxUrl": None}
                    return None
                    
                # Status is likely "PENDING" or "PROCESSING", continue polling
                
            except Exception as e:
                logger.warning(f"Error polling Gamma status: {e}")
                # Continue polling on transient errors
        
        logger.error(f"Gamma generation timed out after {max_attempts * poll_interval} seconds")
        if return_export_urls:
            return {"gammaUrl": None, "pdfUrl": None, "pptxUrl": None}
        return None

    def _handle_http_error(self, e: httpx.HTTPStatusError) -> None:
        """Log appropriate error message based on HTTP status code."""
        status = e.response.status_code
        error_text = e.response.text
        
        if status == 401:
            logger.error("Gamma API: Invalid API key")
        elif status == 402:
            logger.error("Gamma API: Insufficient credits or subscription required")
        elif status == 429:
            logger.error("Gamma API: Rate limit exceeded")
        elif status == 400:
            logger.error(f"Gamma API: Bad request - {error_text}")
        else:
            logger.error(f"Gamma API HTTP error {status}: {error_text}")

    def _construct_proposal_prompt(self, data: Dict[str, Any]) -> str:
        """
        Converts structured proposal data into a prompt optimized for Gamma.
        
        The prompt guides Gamma to create a professional sales proposal deck
        with proper slide structure.
        """
        # Extract fields safely
        prospect_name = data.get("prospect_name", "Client")
        summary = data.get("executive_summary", "")
        situation = data.get("current_situation", "")
        strategy = data.get("proposed_strategy", "")
        why_us = data.get("why_us", "")
        investment = data.get("investment", [])
        next_steps = data.get("next_steps", "")

        # Format pricing tiers
        pricing_text = self._format_pricing_tiers(investment)

        # Construct prompt with clear slide structure
        prompt = f"""Create a professional sales proposal presentation for {prospect_name}.

## Slide 1: Title
Title: "Strategic Proposal for {prospect_name}"
Subtitle: "Transforming Your Digital Presence"

## Slide 2: Executive Summary
{summary}

## Slide 3: Understanding Your Situation
{situation}

## Slide 4: Our Proposed Strategy
{strategy}

## Slide 5: Why Partner With Us
{why_us}

## Slide 6: Investment Options
{pricing_text}

## Slide 7: Next Steps
{next_steps}

Design Notes:
- Use a professional, modern aesthetic
- Include relevant imagery for each section
- Use icons and visual hierarchy for pricing tiers
- End with a clear call-to-action"""

        return prompt

    def _format_pricing_tiers(self, investment: Any) -> str:
        """Format pricing tiers for the prompt."""
        if not investment:
            return "Contact us for custom pricing."
        
        pricing_lines = []
        
        if isinstance(investment, list):
            for tier in investment:
                if isinstance(tier, dict):
                    name = tier.get("name", "Package")
                    price = tier.get("price", "TBD")
                    features = tier.get("features", [])
                else:
                    # Handle Pydantic model
                    name = getattr(tier, "name", "Package")
                    price = getattr(tier, "price", "TBD")
                    features = getattr(tier, "features", [])
                
                feature_list = ", ".join(features) if features else "Custom features"
                pricing_lines.append(f"**{name}** - {price}\n  Includes: {feature_list}")
        
        return "\n\n".join(pricing_lines) if pricing_lines else "Contact us for pricing."

    async def list_themes(self) -> List[Dict[str, Any]]:
        """
        List available Gamma themes.
        
        Returns:
            List of theme objects with id, name, and preview URL
        """
        if not self.api_key:
            return []
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(
                    f"{GAMMA_API_BASE}/themes",
                    headers=self._get_headers()
                )
                resp.raise_for_status()
                return resp.json().get("themes", [])
        except Exception as e:
            logger.error(f"Error listing Gamma themes: {e}")
            return []

    async def list_folders(self) -> List[Dict[str, Any]]:
        """
        List user's Gamma folders.
        
        Returns:
            List of folder objects with id and name
        """
        if not self.api_key:
            return []
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(
                    f"{GAMMA_API_BASE}/folders",
                    headers=self._get_headers()
                )
                resp.raise_for_status()
                return resp.json().get("folders", [])
        except Exception as e:
            logger.error(f"Error listing Gamma folders: {e}")
            return []
