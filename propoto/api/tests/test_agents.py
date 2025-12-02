import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from agents.brand import create_gamma_presentation, BrandDeps
from agents.sales import search_leads, store_leads, SalesDeps, SalesOutput, Lead
from agents.knowledge import scrape_url, KnowledgeDeps
from pydantic_ai import RunContext

# --- Fixtures ---

@pytest.fixture
def mock_brand_ctx():
    deps = BrandDeps(gamma_api_key="mock-gamma", mem0_api_key="mock-mem0")
    ctx = MagicMock(spec=RunContext)
    ctx.deps = deps
    return ctx

@pytest.fixture
def mock_sales_ctx():
    deps = SalesDeps(exa_api_key="mock-exa", convex_url="https://mock.convex", convex_token="mock-token")
    ctx = MagicMock(spec=RunContext)
    ctx.deps = deps
    return ctx

@pytest.fixture
def mock_knowledge_ctx():
    deps = KnowledgeDeps(
        firecrawl_api_key="mock-fc", 
        firecrawl_api_url="http://localhost:3002",
        convex_url="https://mock.convex", 
        convex_token="mock-token"
    )
    ctx = MagicMock(spec=RunContext)
    ctx.deps = deps
    return ctx

# --- Brand Agent Tests ---

@pytest.mark.asyncio
async def test_create_gamma_presentation_success(mock_brand_ctx):
    with patch("httpx.AsyncClient") as mock_client:
        # Mock client instance
        client_instance = AsyncMock()
        mock_client.return_value.__aenter__.return_value = client_instance
        
        # Mock responses
        start_resp = MagicMock()
        start_resp.status_code = 200
        start_resp.json.return_value = {"id": "job-123"}
        start_resp.raise_for_status = MagicMock() # Sync method
        
        status_resp = MagicMock()
        status_resp.status_code = 200
        status_resp.json.return_value = {
            "status": "COMPLETED", 
            "gammaUrl": "https://gamma.app/deck/123",
            "pdfUrl": "https://gamma.app/deck/123.pdf"
        }
        status_resp.raise_for_status = MagicMock() # Sync method

        # Configure side_effect for multiple calls
        # First call is POST (start), subsequent are GET (poll)
        client_instance.post.return_value = start_resp
        client_instance.get.return_value = status_resp
        
        # Mock get_brand_guidelines (internal tool call)
        with patch("agents.brand.get_brand_guidelines", new_callable=AsyncMock) as mock_get_guidelines:
            mock_get_guidelines.return_value = "Brand Guidelines: Blue and White"
            
            result = await create_gamma_presentation(mock_brand_ctx, "Test Deck")
            
            assert "✅ Presentation created successfully" in result
            assert "https://gamma.app/deck/123" in result
            
            # Verify payload
            call_args = client_instance.post.call_args
            assert call_args is not None
            payload = call_args[1]["json"]
            assert payload["format"] == "presentation"
            assert "Test Deck" in payload["inputText"]

@pytest.mark.asyncio
async def test_create_gamma_presentation_no_key():
    """Test that missing Gamma API key raises appropriate error."""
    from utils.exceptions import GammaError
    
    ctx = MagicMock(spec=RunContext)
    ctx.deps = BrandDeps(gamma_api_key="", mem0_api_key="")
    
    with pytest.raises(Exception) as exc_info:
        await create_gamma_presentation(ctx, "Test")
    
    # Should raise a GammaError (wrapped in RetryError due to tenacity)
    # The underlying error should be about missing API key
    assert "Gamma" in str(exc_info.value) or "key" in str(exc_info.value).lower()

# --- Sales Agent Tests ---

@pytest.mark.asyncio
async def test_search_leads_success(mock_sales_ctx):
    with patch("httpx.AsyncClient") as mock_client:
        client_instance = AsyncMock()
        mock_client.return_value.__aenter__.return_value = client_instance
        
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {
            "results": [
                {"title": "Acme Inc", "url": "https://acme.com", "text": "We make anvils."}
            ]
        }
        resp.raise_for_status = MagicMock()
        
        client_instance.post.return_value = resp
        
        result = await search_leads(mock_sales_ctx, "Find anvil makers")
        
        assert "Acme Inc" in result
        assert "https://acme.com" in result

@pytest.mark.asyncio
async def test_store_leads_success(mock_sales_ctx):
    with patch("httpx.AsyncClient") as mock_client:
        client_instance = AsyncMock()
        mock_client.return_value.__aenter__.return_value = client_instance
        
        client_instance.post.return_value.status_code = 200
        
        leads = [
            Lead(company_name="Acme", description="Anvils", score=90, website="https://acme.com")
        ]
        output = SalesOutput(leads=leads, market_summary="Good market")
        
        result = await store_leads(mock_sales_ctx, output)
        
        assert "Stored 1 leads" in result
        
        # Verify Convex call
        call_args = client_instance.post.call_args
        assert call_args is not None
        assert "leads:create" in str(call_args) # Check path in json body

# --- Knowledge Agent Tests ---

@pytest.mark.asyncio
async def test_scrape_url_success(mock_knowledge_ctx):
    with patch("agents.knowledge.FirecrawlApp") as MockApp:
        app_instance = MockApp.return_value
        # Mock the scrape_url method which returns a dict with 'markdown' key
        app_instance.scrape_url.return_value = {"markdown": "# Content"}
        # Also mock scrape method as fallback
        app_instance.scrape.return_value = {"markdown": "# Content"}
        
        result = await scrape_url(mock_knowledge_ctx, "https://example.com")
        
        assert "# Content" in result or result == "# Content"
        # Verify FirecrawlApp was called
        MockApp.assert_called()
