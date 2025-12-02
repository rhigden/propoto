"""
Integration Tests for Full Workflows

Tests complete multi-agent workflows and service integrations.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from agents.proposal_agent import get_proposal_agent, build_enriched_prompt
from agents.knowledge import knowledge_agent, KnowledgeDeps
from agents.sales import sales_agent, SalesDeps
from agents.brand import brand_agent, BrandDeps
from services.gamma_service import GammaService
from services.scraping_service import ScrapingService
from services.brand_memory_service import BrandMemoryService


class TestFullProposalWorkflow:
    """Test complete proposal generation workflow."""
    
    @pytest.mark.asyncio
    async def test_proposal_with_deep_scrape_and_gamma(self):
        """Test proposal generation with deep scraping and Gamma deck."""
        # Mock scraping service
        scraping_service = ScrapingService()
        
        with patch.object(scraping_service, 'analyze_prospect') as mock_scrape:
            from services.scraping_service import BusinessIntelligence
            mock_intel = BusinessIntelligence(
                company_name="Test Corp",
                industry="Technology",
                value_proposition="We build great products",
                target_audience="Enterprises",
                products_services=[],
                key_features=["Feature 1"],
                pain_points_identified=["Low conversion"],
                competitors_mentioned=[],
                social_proof=[],
                tech_stack_hints=[],
                tone_style="professional",
                raw_content="Content..."
            )
            mock_scrape.return_value = mock_intel
            
            # Mock proposal agent
            agent = get_proposal_agent()
            with patch.object(agent, 'run') as mock_agent:
                from agents.proposal_agent import ProposalOutput, PricingTier
                mock_output = ProposalOutput(
                    executive_summary="Test summary",
                    current_situation="Test situation",
                    proposed_strategy="Test strategy",
                    why_us="Test authority",
                    investment=[
                        PricingTier(name="Tier 1", price="$1k", features=["F1"]),
                        PricingTier(name="Tier 2", price="$5k", features=["F2"]),
                        PricingTier(name="Tier 3", price="$10k", features=["F3"])
                    ],
                    next_steps="Test CTA"
                )
                mock_agent.return_value = MagicMock(data=mock_output)
                
                # Mock Gamma service
                with patch.object(GammaService, 'generate_presentation') as mock_gamma:
                    mock_gamma.return_value = {
                        "gammaUrl": "https://gamma.app/docs/test",
                        "pdfUrl": "https://gamma.app/export/test.pdf",
                        "pptxUrl": "https://gamma.app/export/test.pptx"
                    }
                    
                    # Build prompt
                    prompt = build_enriched_prompt(
                        prospect_name="Test Corp",
                        prospect_url="https://test.com",
                        pain_points="Low conversion",
                        website_intel=mock_intel.model_dump(),
                        template_key="default"
                    )
                    
                    # Run agent
                    result = await agent.run(prompt)
                    
                    # Validate
                    assert result.data
                    assert len(result.data.investment) == 3


class TestKnowledgeWorkflow:
    """Test knowledge ingestion workflow."""
    
    @pytest.mark.asyncio
    async def test_knowledge_ingestion_with_storage(self):
        """Test complete knowledge ingestion and storage."""
        deps = KnowledgeDeps(
            firecrawl_api_key="test-key",
            firecrawl_api_url="http://localhost:3002",
            convex_url="https://test.convex.cloud",
            convex_token="test-token"
        )
        
        # Mock Firecrawl
        with patch("agents.knowledge.FirecrawlApp") as MockApp:
            app_instance = MockApp.return_value
            app_instance.scrape_url.return_value = {"markdown": "# Test Content"}
            
            # Mock agent
            with patch.object(knowledge_agent, 'run') as mock_agent:
                from agents.knowledge import KnowledgeOutput, Entity
                mock_output = KnowledgeOutput(
                    summary="Test summary",
                    entities=[
                        Entity(name="Entity 1", type="competitor", details="Details")
                    ],
                    relevance_score=8
                )
                mock_agent.return_value = MagicMock(output=mock_output)
                
                # Mock Convex storage
                with patch("httpx.AsyncClient") as mock_client:
                    client_instance = AsyncMock()
                    mock_client.return_value.__aenter__.return_value = client_instance
                    
                    resp = MagicMock()
                    resp.status_code = 200
                    resp.json.return_value = {"id": "knowledge-123"}
                    resp.raise_for_status = MagicMock()
                    client_instance.post.return_value = resp
                    
                    # Run workflow
                    result = await knowledge_agent.run(
                        "Analyze: https://example.com",
                        deps=deps
                    )
                    
                    assert result.output
                    assert result.output.relevance_score >= 1


class TestBrandMemoryWorkflow:
    """Test brand memory service workflow."""
    
    @pytest.mark.asyncio
    async def test_brand_voice_retrieval_and_usage(self):
        """Test retrieving brand voice and using it in Gamma generation."""
        # Mock brand memory service
        with patch.object(BrandMemoryService, 'get_brand_voice') as mock_get_voice:
            from services.brand_memory_service import BrandVoice
            mock_voice = BrandVoice(
                org_id="test-org",
                company_name="Test Company",
                tagline="Test Tagline",
                brand_colors=["#0000FF", "#FFFFFF"],
                tone_keywords=["professional", "innovative"],
                writing_style="direct"
            )
            mock_get_voice.return_value = mock_voice
            
            # Mock Gamma generation
            with patch("httpx.AsyncClient") as mock_client:
                client_instance = AsyncMock()
                mock_client.return_value.__aenter__.return_value = client_instance
                
                start_resp = MagicMock()
                start_resp.status_code = 200
                start_resp.json.return_value = {"id": "job-123"}
                start_resp.raise_for_status = MagicMock()
                
                status_resp = MagicMock()
                status_resp.status_code = 200
                status_resp.json.return_value = {
                    "status": "COMPLETED",
                    "gammaUrl": "https://gamma.app/docs/test"
                }
                status_resp.raise_for_status = MagicMock()
                
                client_instance.post.return_value = start_resp
                client_instance.get.return_value = status_resp
                
                # Test brand agent with guidelines
                deps = BrandDeps(
                    gamma_api_key="test-key",
                    mem0_api_key="test-mem0"
                )
                
                from agents.brand import get_brand_guidelines, create_gamma_presentation
                from pydantic_ai import RunContext
                
                ctx = MagicMock(spec=RunContext)
                ctx.deps = deps
                
                # Get guidelines
                with patch("services.brand_memory_service.get_brand_memory_service") as mock_service:
                    service_instance = AsyncMock()
                    service_instance.get_brand_voice.return_value = mock_voice
                    mock_service.return_value = service_instance
                    
                    guidelines = await get_brand_guidelines(ctx, org_id="test-org")
                    
                    assert "Test Company" in guidelines or "professional" in guidelines


class TestSalesWorkflow:
    """Test sales lead discovery workflow."""
    
    @pytest.mark.asyncio
    async def test_lead_discovery_and_storage(self):
        """Test complete lead discovery and storage workflow."""
        deps = SalesDeps(
            exa_api_key="test-key",
            convex_url="https://test.convex.cloud",
            convex_token="test-token"
        )
        
        # Mock Exa search
        with patch("httpx.AsyncClient") as mock_client:
            client_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = client_instance
            
            search_resp = MagicMock()
            search_resp.status_code = 200
            search_resp.json.return_value = {
                "results": [
                    {
                        "title": "Acme Corp",
                        "url": "https://acme.com",
                        "text": "Acme Corp is a leading company."
                    }
                ]
            }
            search_resp.raise_for_status = MagicMock()
            client_instance.post.return_value = search_resp
            
            # Mock agent
            with patch.object(sales_agent, 'run') as mock_agent:
                from agents.sales import SalesOutput, Lead
                mock_output = SalesOutput(
                    leads=[
                        Lead(
                            company_name="Acme Corp",
                            website="https://acme.com",
                            description="Leading company",
                            score=85,
                            status="new"
                        )
                    ],
                    market_summary="Strong market"
                )
                mock_agent.return_value = MagicMock(output=mock_output)
                
                # Mock Convex storage
                store_resp = MagicMock()
                store_resp.status_code = 200
                store_resp.raise_for_status = MagicMock()
                client_instance.post.return_value = store_resp
                
                # Run workflow
                result = await sales_agent.run(
                    "Find: digital marketing agencies",
                    deps=deps
                )
                
                assert len(result.output.leads) > 0
                assert result.output.market_summary




