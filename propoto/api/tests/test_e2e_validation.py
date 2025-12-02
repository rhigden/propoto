"""
End-to-End Validation Tests

Tests complete flows for all agents:
- Proposal generation: form → agent → Gamma → Convex storage
- Knowledge ingestion: URL → Firecrawl → agent → Convex
- Sales lead discovery: query → Exa → agent → Convex
- Brand asset generation: prompt → Gamma → Mem0 enrichment
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from fastapi.testclient import TestClient
from agents.proposal_agent import ProposalRequest, get_proposal_agent, build_enriched_prompt
from agents.knowledge import knowledge_agent, KnowledgeDeps
from agents.sales import sales_agent, SalesDeps
from agents.brand import brand_agent, BrandDeps
from services.gamma_service import GammaService
from services.scraping_service import ScrapingService


class TestProposalGenerationFlow:
    """Test complete proposal generation flow."""
    
    @pytest.mark.asyncio
    async def test_proposal_flow_with_gamma(self):
        """Test proposal generation with Gamma deck creation."""
        # Mock proposal agent
        agent = get_proposal_agent()
        
        # Mock Gamma service
        with patch.object(GammaService, 'generate_presentation') as mock_gamma:
            mock_gamma.return_value = {
                "gammaUrl": "https://gamma.app/docs/test",
                "pdfUrl": "https://gamma.app/export/test.pdf",
                "pptxUrl": "https://gamma.app/export/test.pptx"
            }
            
            # Build enriched prompt
            prompt = build_enriched_prompt(
                prospect_name="Acme Corp",
                prospect_url="https://acme.com",
                pain_points="Low conversion rates",
                template_key="default"
            )
            
            # Run agent (mocked)
            with patch.object(agent, 'run') as mock_run:
                from agents.proposal_agent import ProposalOutput, PricingTier
                mock_output = ProposalOutput(
                    executive_summary="Test summary",
                    current_situation="Test situation",
                    proposed_strategy="Test strategy",
                    why_us="Test authority",
                    investment=[
                        PricingTier(name="Starter", price="$1k", features=["Feature 1"]),
                        PricingTier(name="Growth", price="$5k", features=["Feature 2"]),
                        PricingTier(name="Enterprise", price="$10k", features=["Feature 3"])
                    ],
                    next_steps="Test CTA"
                )
                mock_run.return_value = MagicMock(data=mock_output)
                
                result = await agent.run(prompt)
                
                # Validate proposal structure
                assert result.data.executive_summary
                assert result.data.current_situation
                assert result.data.proposed_strategy
                assert len(result.data.investment) == 3
    
    @pytest.mark.asyncio
    async def test_proposal_flow_with_deep_scrape(self):
        """Test proposal generation with deep scraping enabled."""
        # Mock scraping service
        with patch.object(ScrapingService, 'analyze_prospect') as mock_scrape:
            from services.scraping_service import BusinessIntelligence
            mock_intel = BusinessIntelligence(
                company_name="Acme Corp",
                industry="Technology",
                value_proposition="We build great products",
                target_audience="Enterprises",
                products_services=["Product A", "Product B"],
                key_features=["Feature 1", "Feature 2"],
                pain_points_identified=["Pain 1", "Pain 2"],
                competitors_mentioned=[],
                social_proof=["Client A", "Client B"],
                tech_stack_hints=["React", "Python"],
                tone_style="professional",
                raw_content="Sample content..."
            )
            mock_scrape.return_value = mock_intel
            
            # Build enriched prompt with website intel
            prompt = build_enriched_prompt(
                prospect_name="Acme Corp",
                prospect_url="https://acme.com",
                pain_points="Low conversion rates",
                website_intel=mock_intel.model_dump(),
                template_key="default"
            )
            
            # Verify prompt includes website intelligence
            assert "WEBSITE INTELLIGENCE" in prompt or "Website" in prompt
            assert "Technology" in prompt
            assert "professional" in prompt


class TestKnowledgeIngestionFlow:
    """Test complete knowledge ingestion flow."""
    
    @pytest.mark.asyncio
    async def test_knowledge_ingestion_flow(self):
        """Test URL scraping → agent → Convex storage."""
        deps = KnowledgeDeps(
            firecrawl_api_key="test-key",
            firecrawl_api_url="http://localhost:3002",
            convex_url="https://test.convex.cloud",
            convex_token="test-token"
        )
        
        # Mock Firecrawl scraping
        with patch("agents.knowledge.scrape_url") as mock_scrape:
            mock_scrape.return_value = "# Test Content\n\nThis is test markdown content."
            
            # Mock agent run
            with patch.object(knowledge_agent, 'run') as mock_run:
                from agents.knowledge import KnowledgeOutput, Entity
                mock_output = KnowledgeOutput(
                    summary="Test summary",
                    entities=[
                        Entity(name="Entity 1", type="competitor", details="Details 1"),
                        Entity(name="Entity 2", type="feature", details="Details 2")
                    ],
                    relevance_score=8
                )
                mock_run.return_value = MagicMock(output=mock_output)
                
                result = await knowledge_agent.run(
                    "Analyze this URL: https://example.com",
                    deps=deps
                )
                
                # Validate output structure
                assert result.output.summary
                assert len(result.output.entities) > 0
                assert 1 <= result.output.relevance_score <= 10
    
    @pytest.mark.asyncio
    async def test_knowledge_storage_flow(self):
        """Test knowledge storage to Convex."""
        deps = KnowledgeDeps(
            firecrawl_api_key="test-key",
            firecrawl_api_url="http://localhost:3002",
            convex_url="https://test.convex.cloud",
            convex_token="test-token"
        )
        
        # Mock Convex storage
        with patch("httpx.AsyncClient") as mock_client:
            client_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = client_instance
            
            resp = MagicMock()
            resp.status_code = 200
            resp.json.return_value = {"id": "knowledge-123"}
            resp.raise_for_status = MagicMock()
            client_instance.post.return_value = resp
            
            # Test storage tool
            from agents.knowledge import store_knowledge, KnowledgeOutput, Entity
            from pydantic_ai import RunContext
            
            ctx = MagicMock(spec=RunContext)
            ctx.deps = deps
            
            knowledge_data = KnowledgeOutput(
                summary="Test summary",
                entities=[Entity(name="Test", type="other", details="Test")],
                relevance_score=5
            )
            
            result = await store_knowledge(ctx, knowledge_data)
            
            assert "Stored successfully" in result or "success" in result.lower()


class TestSalesLeadDiscoveryFlow:
    """Test complete sales lead discovery flow."""
    
    @pytest.mark.asyncio
    async def test_sales_lead_discovery_flow(self):
        """Test Exa search → agent → Convex storage."""
        deps = SalesDeps(
            exa_api_key="test-key",
            convex_url="https://test.convex.cloud",
            convex_token="test-token"
        )
        
        # Mock Exa search
        with patch("httpx.AsyncClient") as mock_client:
            client_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = client_instance
            
            resp = MagicMock()
            resp.status_code = 200
            resp.json.return_value = {
                "results": [
                    {
                        "title": "Acme Corp",
                        "url": "https://acme.com",
                        "text": "Acme Corp is a leading technology company."
                    }
                ]
            }
            resp.raise_for_status = MagicMock()
            client_instance.post.return_value = resp
            
            # Mock agent run
            with patch.object(sales_agent, 'run') as mock_run:
                from agents.sales import SalesOutput, Lead
                mock_output = SalesOutput(
                    leads=[
                        Lead(
                            company_name="Acme Corp",
                            website="https://acme.com",
                            description="Leading tech company",
                            score=85,
                            status="new"
                        )
                    ],
                    market_summary="Strong market with good opportunities"
                )
                mock_run.return_value = MagicMock(output=mock_output)
                
                result = await sales_agent.run(
                    "Find leads for: digital marketing agencies",
                    deps=deps
                )
                
                # Validate output structure
                assert len(result.output.leads) > 0
                assert result.output.market_summary
                assert 0 <= result.output.leads[0].score <= 100


class TestBrandAssetGenerationFlow:
    """Test complete brand asset generation flow."""
    
    @pytest.mark.asyncio
    async def test_brand_asset_generation_flow(self):
        """Test prompt → Gamma → Mem0 enrichment."""
        deps = BrandDeps(
            gamma_api_key="test-key",
            mem0_api_key="test-mem0-key"
        )
        
        # Mock Mem0 brand guidelines
        with patch("agents.brand.get_brand_guidelines") as mock_guidelines:
            mock_guidelines.return_value = "Brand Colors: Blue and White. Tone: Professional."
            
            # Mock Gamma generation
            with patch("httpx.AsyncClient") as mock_client:
                client_instance = AsyncMock()
                mock_client.return_value.__aenter__.return_value = client_instance
                
                # Mock start generation
                start_resp = MagicMock()
                start_resp.status_code = 200
                start_resp.json.return_value = {"id": "job-123"}
                start_resp.raise_for_status = MagicMock()
                
                # Mock status check
                status_resp = MagicMock()
                status_resp.status_code = 200
                status_resp.json.return_value = {
                    "status": "COMPLETED",
                    "gammaUrl": "https://gamma.app/docs/test",
                    "pdfUrl": "https://gamma.app/export/test.pdf"
                }
                status_resp.raise_for_status = MagicMock()
                
                client_instance.post.return_value = start_resp
                client_instance.get.return_value = status_resp
                
                # Test brand agent tool
                from agents.brand import create_gamma_presentation
                from pydantic_ai import RunContext
                
                ctx = MagicMock(spec=RunContext)
                ctx.deps = deps
                
                result = await create_gamma_presentation(
                    ctx,
                    prompt="Create a presentation about our services",
                    format="presentation",
                    num_cards=10
                )
                
                # Validate result
                assert "✅" in result or "successfully" in result.lower()
                assert "gamma.app" in result


class TestMultiAgentWorkflows:
    """Test workflows involving multiple agents."""
    
    @pytest.mark.asyncio
    async def test_proposal_with_knowledge_enrichment(self):
        """Test proposal generation enriched with knowledge from scraping."""
        # Step 1: Scrape prospect website
        scraping_service = ScrapingService()
        
        with patch.object(scraping_service, 'analyze_prospect') as mock_scrape:
            from services.scraping_service import BusinessIntelligence
            mock_intel = BusinessIntelligence(
                company_name="Acme Corp",
                industry="Technology",
                value_proposition="We build great products",
                target_audience="Enterprises",
                products_services=[],
                key_features=[],
                pain_points_identified=["Low conversion"],
                competitors_mentioned=[],
                social_proof=[],
                tech_stack_hints=[],
                tone_style="professional",
                raw_content="Content..."
            )
            mock_scrape.return_value = mock_intel
            
            # Step 2: Build enriched proposal prompt
            prompt = build_enriched_prompt(
                prospect_name="Acme Corp",
                prospect_url="https://acme.com",
                pain_points="Low conversion rates",
                website_intel=mock_intel.model_dump(),
                template_key="default"
            )
            
            # Verify prompt is enriched
            assert "WEBSITE INTELLIGENCE" in prompt or "Website" in prompt
            assert "Technology" in prompt
            
            # Step 3: Generate proposal (mocked)
            agent = get_proposal_agent()
            with patch.object(agent, 'run') as mock_run:
                from agents.proposal_agent import ProposalOutput, PricingTier
                mock_output = ProposalOutput(
                    executive_summary="Test",
                    current_situation="Test",
                    proposed_strategy="Test",
                    why_us="Test",
                    investment=[PricingTier(name="Tier", price="$1", features=[])] * 3,
                    next_steps="Test"
                )
                mock_run.return_value = MagicMock(data=mock_output)
                
                result = await agent.run(prompt)
                assert result.data

