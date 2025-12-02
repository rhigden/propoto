"""
Deep Scraping Service

Provides intelligent website analysis for proposal generation.
Uses self-hosted Firecrawl to extract business intelligence from prospect websites.
"""

import os
import httpx
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Self-hosted Firecrawl URL
FIRECRAWL_API_URL = os.getenv("FIRECRAWL_API_URL", "http://localhost:3002")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY", "")


class BusinessIntelligence(BaseModel):
    """Extracted business intelligence from website analysis."""
    company_name: str = ""
    industry: str = ""
    value_proposition: str = ""
    target_audience: str = ""
    products_services: List[str] = []
    key_features: List[str] = []
    pain_points_identified: List[str] = []
    competitors_mentioned: List[str] = []
    social_proof: List[str] = []  # testimonials, case studies, logos
    tech_stack_hints: List[str] = []  # detected technologies
    tone_style: str = ""  # corporate, casual, tech-forward, etc.
    raw_content: str = ""


class ScrapingService:
    """
    Service for deep website analysis using Firecrawl.
    Extracts business intelligence to enrich proposals.
    """
    
    def __init__(self, api_url: Optional[str] = None, api_key: Optional[str] = None):
        self.api_url = api_url or FIRECRAWL_API_URL
        self.api_key = api_key or FIRECRAWL_API_KEY
        
    async def scrape_url(self, url: str) -> Optional[str]:
        """
        Scrape a single URL and return markdown content.
        
        Args:
            url: URL to scrape
            
        Returns:
            Markdown content or None if failed
        """
        try:
            logger.info(f"Scraping URL: {url}")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Firecrawl v1 API endpoint
                headers = {"Content-Type": "application/json"}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                
                resp = await client.post(
                    f"{self.api_url}/v1/scrape",
                    json={
                        "url": url,
                        "formats": ["markdown"],
                        "onlyMainContent": True  # Focus on main content, skip nav/footer
                    },
                    headers=headers
                )
                
                if resp.status_code == 200:
                    data = resp.json()
                    markdown = data.get("data", {}).get("markdown", "")
                    logger.info(f"Successfully scraped {url} ({len(markdown)} chars)")
                    return markdown
                else:
                    logger.warning(f"Scrape failed with status {resp.status_code}: {resp.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None

    async def crawl_website(self, url: str, max_pages: int = 5) -> List[str]:
        """
        Crawl multiple pages from a website.
        
        Args:
            url: Starting URL
            max_pages: Maximum pages to crawl
            
        Returns:
            List of markdown content from crawled pages
        """
        try:
            logger.info(f"Crawling website: {url} (max {max_pages} pages)")
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                headers = {"Content-Type": "application/json"}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                
                # Start crawl job
                resp = await client.post(
                    f"{self.api_url}/v1/crawl",
                    json={
                        "url": url,
                        "limit": max_pages,
                        "scrapeOptions": {
                            "formats": ["markdown"],
                            "onlyMainContent": True
                        }
                    },
                    headers=headers
                )
                
                if resp.status_code != 200:
                    logger.warning(f"Crawl start failed: {resp.status_code}")
                    # Fallback to single page scrape
                    content = await self.scrape_url(url)
                    return [content] if content else []
                
                # For sync crawl, results come directly
                data = resp.json()
                
                # Handle async crawl job
                if "id" in data:
                    job_id = data["id"]
                    contents = await self._poll_crawl_job(client, job_id, headers)
                    return contents
                
                # Handle sync results
                results = data.get("data", [])
                return [r.get("markdown", "") for r in results if r.get("markdown")]
                    
        except Exception as e:
            logger.error(f"Error crawling {url}: {e}")
            # Fallback to single page
            content = await self.scrape_url(url)
            return [content] if content else []

    async def _poll_crawl_job(
        self, 
        client: httpx.AsyncClient, 
        job_id: str,
        headers: Dict[str, str],
        max_attempts: int = 30,
        poll_interval: int = 3
    ) -> List[str]:
        """Poll for crawl job completion."""
        import asyncio
        
        for _ in range(max_attempts):
            await asyncio.sleep(poll_interval)
            
            try:
                resp = await client.get(
                    f"{self.api_url}/v1/crawl/{job_id}",
                    headers=headers
                )
                
                if resp.status_code != 200:
                    continue
                    
                data = resp.json()
                status = data.get("status")
                
                if status == "completed":
                    results = data.get("data", [])
                    return [r.get("markdown", "") for r in results if r.get("markdown")]
                elif status == "failed":
                    logger.error(f"Crawl job failed: {data.get('error')}")
                    return []
                    
            except Exception as e:
                logger.warning(f"Error polling crawl job: {e}")
                
        logger.error("Crawl job timed out")
        return []

    async def analyze_prospect(self, url: str, deep_crawl: bool = False) -> BusinessIntelligence:
        """
        Analyze a prospect's website and extract business intelligence.
        
        Args:
            url: Prospect website URL
            deep_crawl: If True, crawl multiple pages for richer data
            
        Returns:
            BusinessIntelligence object with extracted data
        """
        # Get website content
        if deep_crawl:
            contents = await self.crawl_website(url, max_pages=5)
            combined_content = "\n\n---\n\n".join(contents)
        else:
            content = await self.scrape_url(url)
            combined_content = content or ""
        
        if not combined_content:
            logger.warning(f"No content extracted from {url}")
            return BusinessIntelligence(raw_content="")
        
        # Extract intelligence using simple heuristics
        # (In production, you might use an LLM for this)
        intel = self._extract_intelligence(combined_content, url)
        intel.raw_content = combined_content[:10000]  # Truncate for context window
        
        return intel

    def _extract_intelligence(self, content: str, url: str) -> BusinessIntelligence:
        """
        Extract business intelligence from website content.
        Uses heuristics - could be enhanced with LLM analysis.
        """
        import re
        from urllib.parse import urlparse
        
        intel = BusinessIntelligence()
        
        # Extract domain as company name hint
        domain = urlparse(url).netloc.replace("www.", "")
        intel.company_name = domain.split(".")[0].title()
        
        content_lower = content.lower()
        
        # Detect industry keywords
        industry_keywords = {
            "saas": ["saas", "software", "platform", "cloud", "api", "integration"],
            "ecommerce": ["shop", "store", "cart", "checkout", "products", "shipping"],
            "agency": ["agency", "marketing", "digital", "creative", "campaigns"],
            "consulting": ["consulting", "advisory", "strategy", "solutions"],
            "healthcare": ["health", "medical", "patient", "care", "clinical"],
            "fintech": ["finance", "payment", "banking", "invest", "crypto"],
            "education": ["learning", "course", "training", "education", "students"],
            "real estate": ["property", "real estate", "housing", "rental", "mortgage"]
        }
        
        for industry, keywords in industry_keywords.items():
            if any(kw in content_lower for kw in keywords):
                intel.industry = industry
                break
        
        # Extract potential pain points from content
        pain_indicators = [
            "struggling with", "challenge", "problem", "difficult", "pain point",
            "frustrated", "time-consuming", "expensive", "complex", "outdated"
        ]
        
        lines = content.split("\n")
        for line in lines:
            if any(indicator in line.lower() for indicator in pain_indicators):
                if len(line) < 200:  # Reasonable length
                    intel.pain_points_identified.append(line.strip())
                    if len(intel.pain_points_identified) >= 3:
                        break
        
        # Detect tone/style
        if any(word in content_lower for word in ["enterprise", "fortune 500", "corporate"]):
            intel.tone_style = "corporate, enterprise"
        elif any(word in content_lower for word in ["startup", "disrupt", "innovative"]):
            intel.tone_style = "tech-forward, startup"
        elif any(word in content_lower for word in ["fun", "love", "awesome", "🚀"]):
            intel.tone_style = "casual, friendly"
        else:
            intel.tone_style = "professional"
        
        # Extract social proof
        proof_patterns = [
            r"trusted by [\w\s,]+",
            r"\d+\+? (customers|clients|users|companies)",
            r"used by [\w\s,]+",
            r"featured in [\w\s,]+"
        ]
        
        for pattern in proof_patterns:
            matches = re.findall(pattern, content_lower)
            intel.social_proof.extend(matches[:2])
        
        # Detect tech stack hints
        tech_hints = [
            "react", "vue", "angular", "shopify", "wordpress", "hubspot",
            "salesforce", "stripe", "aws", "google cloud", "azure"
        ]
        
        for tech in tech_hints:
            if tech in content_lower:
                intel.tech_stack_hints.append(tech)
        
        # Extract key features mentioned
        feature_patterns = [
            r"(?:features?|benefits?|what we offer|our solution)[\s:]+([^\n]+)",
        ]
        
        for pattern in feature_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches[:5]:
                intel.key_features.append(match.strip())
        
        return intel


# Singleton instance
_scraping_service: Optional[ScrapingService] = None

def get_scraping_service() -> ScrapingService:
    """Get or create scraping service singleton."""
    global _scraping_service
    if _scraping_service is None:
        _scraping_service = ScrapingService()
    return _scraping_service

