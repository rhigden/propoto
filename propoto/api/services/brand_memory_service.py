"""
Brand Memory Service

Manages per-org brand voice and guidelines using Mem0.
Each organization can store their own brand voice, colors, tone, and style.
"""

import os
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mem0 API configuration
MEM0_API_KEY = os.getenv("MEM0_API_KEY")


class BrandVoice(BaseModel):
    """Brand voice configuration for an organization."""
    org_id: str
    company_name: Optional[str] = None
    tagline: Optional[str] = None
    brand_colors: List[str] = []  # Hex colors
    primary_color: Optional[str] = None
    tone_keywords: List[str] = []  # e.g., "professional", "friendly", "innovative"
    writing_style: Optional[str] = None  # e.g., "formal", "casual", "technical"
    target_audience: Optional[str] = None
    key_messages: List[str] = []
    avoid_phrases: List[str] = []  # Words/phrases to avoid
    preferred_phrases: List[str] = []  # Preferred vocabulary
    custom_guidelines: Optional[str] = None


class BrandMemoryService:
    """
    Service for managing per-org brand voice using Mem0.
    Falls back to defaults when Mem0 is not configured.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or MEM0_API_KEY
        self._mem0_client = None
        
    def _get_client(self):
        """Lazy-load Mem0 client."""
        if self._mem0_client is None and self.api_key:
            try:
                from mem0 import Memory
                self._mem0_client = Memory(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Mem0 client: {e}")
        return self._mem0_client
    
    def _get_user_id(self, org_id: str) -> str:
        """Generate consistent user ID for org brand storage."""
        return f"brand_{org_id}"
    
    async def get_brand_voice(self, org_id: str) -> BrandVoice:
        """
        Get brand voice configuration for an organization.
        
        Args:
            org_id: Organization ID
            
        Returns:
            BrandVoice configuration
        """
        client = self._get_client()
        
        if not client:
            logger.warning(f"Mem0 not configured, using default brand voice for org {org_id}")
            return self._get_default_brand_voice(org_id)
        
        try:
            user_id = self._get_user_id(org_id)
            
            # Search for brand-related memories
            results = client.search(
                query="brand voice colors tone style guidelines audience",
                user_id=user_id,
                limit=10
            )
            
            if not results:
                logger.info(f"No brand voice found for org {org_id}, using defaults")
                return self._get_default_brand_voice(org_id)
            
            # Parse results into BrandVoice
            brand_voice = self._parse_brand_memories(org_id, results)
            logger.info(f"Retrieved brand voice for org {org_id}")
            return brand_voice
            
        except Exception as e:
            logger.error(f"Error retrieving brand voice: {e}")
            return self._get_default_brand_voice(org_id)
    
    async def save_brand_voice(self, brand_voice: BrandVoice) -> bool:
        """
        Save brand voice configuration for an organization.
        
        Args:
            brand_voice: BrandVoice configuration to save
            
        Returns:
            True if saved successfully
        """
        client = self._get_client()
        
        if not client:
            logger.error("Mem0 not configured, cannot save brand voice")
            return False
        
        try:
            user_id = self._get_user_id(brand_voice.org_id)
            
            # Build comprehensive brand message
            messages = self._build_brand_messages(brand_voice)
            
            for message in messages:
                client.add(
                    messages=[{"role": "user", "content": message}],
                    user_id=user_id
                )
            
            logger.info(f"Saved brand voice for org {brand_voice.org_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving brand voice: {e}")
            return False
    
    async def update_brand_element(
        self, 
        org_id: str, 
        element: str, 
        value: Any
    ) -> bool:
        """
        Update a specific brand element.
        
        Args:
            org_id: Organization ID
            element: Element name (e.g., "tone", "colors")
            value: New value
            
        Returns:
            True if updated successfully
        """
        client = self._get_client()
        
        if not client:
            logger.error("Mem0 not configured")
            return False
        
        try:
            user_id = self._get_user_id(org_id)
            
            # Format the update as a memory
            if isinstance(value, list):
                value_str = ", ".join(str(v) for v in value)
            else:
                value_str = str(value)
            
            message = f"Brand {element}: {value_str}"
            
            client.add(
                messages=[{"role": "user", "content": message}],
                user_id=user_id
            )
            
            logger.info(f"Updated brand {element} for org {org_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating brand element: {e}")
            return False
    
    def get_brand_prompt(self, brand_voice: BrandVoice) -> str:
        """
        Generate a prompt string from brand voice for LLM consumption.
        
        Args:
            brand_voice: BrandVoice configuration
            
        Returns:
            Formatted prompt string
        """
        parts = []
        
        if brand_voice.company_name:
            parts.append(f"Company: {brand_voice.company_name}")
        
        if brand_voice.tagline:
            parts.append(f"Tagline: {brand_voice.tagline}")
        
        if brand_voice.tone_keywords:
            parts.append(f"Tone: {', '.join(brand_voice.tone_keywords)}")
        
        if brand_voice.writing_style:
            parts.append(f"Writing Style: {brand_voice.writing_style}")
        
        if brand_voice.target_audience:
            parts.append(f"Target Audience: {brand_voice.target_audience}")
        
        if brand_voice.key_messages:
            parts.append(f"Key Messages: {'; '.join(brand_voice.key_messages)}")
        
        if brand_voice.preferred_phrases:
            parts.append(f"Use phrases like: {', '.join(brand_voice.preferred_phrases)}")
        
        if brand_voice.avoid_phrases:
            parts.append(f"Avoid: {', '.join(brand_voice.avoid_phrases)}")
        
        if brand_voice.custom_guidelines:
            parts.append(f"Additional Guidelines: {brand_voice.custom_guidelines}")
        
        return "\n".join(parts) if parts else "Use professional, clear language."
    
    def _get_default_brand_voice(self, org_id: str) -> BrandVoice:
        """Return default brand voice configuration."""
        return BrandVoice(
            org_id=org_id,
            tone_keywords=["professional", "clear", "value-focused"],
            writing_style="direct and conversational",
            custom_guidelines="Focus on value proposition and clear calls to action."
        )
    
    def _parse_brand_memories(self, org_id: str, memories: List[Dict]) -> BrandVoice:
        """Parse Mem0 memories into BrandVoice structure."""
        brand_voice = BrandVoice(org_id=org_id)
        
        for memory in memories:
            content = memory.get("memory", "").lower()
            
            # Parse different brand elements from memories
            if "color" in content:
                # Extract hex colors
                import re
                colors = re.findall(r'#[0-9a-fA-F]{6}', content)
                brand_voice.brand_colors.extend(colors)
                if colors and not brand_voice.primary_color:
                    brand_voice.primary_color = colors[0]
            
            if "tone" in content:
                # Extract tone keywords
                tone_keywords = ["professional", "friendly", "innovative", "casual", 
                               "formal", "technical", "playful", "authoritative"]
                for kw in tone_keywords:
                    if kw in content:
                        brand_voice.tone_keywords.append(kw)
            
            if "style" in content:
                if "formal" in content:
                    brand_voice.writing_style = "formal"
                elif "casual" in content:
                    brand_voice.writing_style = "casual"
                elif "technical" in content:
                    brand_voice.writing_style = "technical"
            
            if "avoid" in content:
                # Collect avoidance phrases
                pass  # Would need more sophisticated parsing
            
            if "audience" in content:
                brand_voice.target_audience = content
        
        return brand_voice
    
    def _build_brand_messages(self, brand_voice: BrandVoice) -> List[str]:
        """Build Mem0 messages from BrandVoice."""
        messages = []
        
        if brand_voice.company_name:
            messages.append(f"Our company name is {brand_voice.company_name}")
        
        if brand_voice.tagline:
            messages.append(f"Our tagline is: {brand_voice.tagline}")
        
        if brand_voice.brand_colors:
            messages.append(f"Brand colors: {', '.join(brand_voice.brand_colors)}")
        
        if brand_voice.tone_keywords:
            messages.append(f"Our brand tone is {', '.join(brand_voice.tone_keywords)}")
        
        if brand_voice.writing_style:
            messages.append(f"We write in a {brand_voice.writing_style} style")
        
        if brand_voice.target_audience:
            messages.append(f"Our target audience is {brand_voice.target_audience}")
        
        if brand_voice.key_messages:
            for msg in brand_voice.key_messages:
                messages.append(f"Key message: {msg}")
        
        if brand_voice.avoid_phrases:
            messages.append(f"Avoid using: {', '.join(brand_voice.avoid_phrases)}")
        
        if brand_voice.preferred_phrases:
            messages.append(f"Prefer using: {', '.join(brand_voice.preferred_phrases)}")
        
        if brand_voice.custom_guidelines:
            messages.append(f"Brand guideline: {brand_voice.custom_guidelines}")
        
        return messages


# Singleton instance
_brand_memory_service: Optional[BrandMemoryService] = None

def get_brand_memory_service() -> BrandMemoryService:
    """Get or create brand memory service singleton."""
    global _brand_memory_service
    if _brand_memory_service is None:
        _brand_memory_service = BrandMemoryService()
    return _brand_memory_service

