"""
Tests for error handling across the API.

Tests validation errors, service failures, and graceful degradation.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
import os

# Set mock env vars BEFORE importing app
os.environ["OPENROUTER_API_KEY"] = "mock-or-key"
os.environ["AGENT_SERVICE_KEY"] = "mock-secret-key"
os.environ["GAMMA_API_KEY"] = "mock-gamma-key"
os.environ["MEM0_API_KEY"] = "mock-mem0-key"
os.environ["FIRECRAWL_API_KEY"] = "mock-firecrawl-key"
os.environ["NEXT_PUBLIC_CONVEX_URL"] = "https://mock.convex.cloud"
os.environ["CONVEX_DEPLOYMENT"] = "mock-deployment"

from main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers():
    return {"x-api-key": "mock-secret-key"}


class TestValidationErrors:
    """Test input validation error handling."""
    
    def test_proposal_missing_prospect_name(self, client, auth_headers):
        """Test proposal endpoint with missing prospect_name."""
        response = client.post(
            "/agents/proposal/generate",
            headers=auth_headers,
            json={
                "prospect_url": "https://example.com",
                "pain_points": "Test pain points"
            }
        )
        # Pydantic will catch this as validation error
        assert response.status_code in [400, 422]
        
    def test_proposal_missing_url(self, client, auth_headers):
        """Test proposal endpoint with missing URL."""
        response = client.post(
            "/agents/proposal/generate",
            headers=auth_headers,
            json={
                "prospect_name": "Test Corp",
                "pain_points": "Test pain points"
            }
        )
        assert response.status_code in [400, 422]
        
    def test_proposal_empty_prospect_name(self, client, auth_headers):
        """Test proposal endpoint with empty prospect_name."""
        response = client.post(
            "/agents/proposal/generate",
            headers=auth_headers,
            json={
                "prospect_name": "",
                "prospect_url": "https://example.com",
                "pain_points": "Test pain points"
            }
        )
        assert response.status_code == 400
        assert "prospect_name" in response.json().get("detail", "").lower()
        
    def test_proposal_invalid_url(self, client, auth_headers):
        """Test proposal endpoint with invalid URL format."""
        response = client.post(
            "/agents/proposal/generate",
            headers=auth_headers,
            json={
                "prospect_name": "Test Corp",
                "prospect_url": "not-a-url",
                "pain_points": "Test pain points"
            }
        )
        assert response.status_code == 400
        assert "url" in response.json().get("detail", "").lower()
        
    def test_proposal_invalid_template(self, client, auth_headers):
        """Test proposal endpoint with invalid template."""
        response = client.post(
            "/agents/proposal/generate",
            headers=auth_headers,
            json={
                "prospect_name": "Test Corp",
                "prospect_url": "https://example.com",
                "pain_points": "Test pain points",
                "template": "nonexistent_template"
            }
        )
        assert response.status_code == 400
        assert "template" in response.json().get("detail", "").lower()
        
    def test_knowledge_ingest_missing_url(self, client, auth_headers):
        """Test knowledge ingest with missing URL."""
        response = client.post(
            "/agents/knowledge/ingest",
            headers=auth_headers,
            json={}
        )
        assert response.status_code in [400, 422]
        
    def test_knowledge_ingest_empty_url(self, client, auth_headers):
        """Test knowledge ingest with empty URL."""
        response = client.post(
            "/agents/knowledge/ingest",
            headers=auth_headers,
            json={"url": ""}
        )
        assert response.status_code == 400
        
    def test_knowledge_ingest_invalid_url(self, client, auth_headers):
        """Test knowledge ingest with invalid URL."""
        response = client.post(
            "/agents/knowledge/ingest",
            headers=auth_headers,
            json={"url": "not-a-url"}
        )
        assert response.status_code == 400


class TestAuthenticationErrors:
    """Test authentication error handling."""
    
    def test_missing_api_key(self, client):
        """Test request without API key."""
        response = client.post(
            "/agents/proposal/generate",
            json={
                "prospect_name": "Test",
                "prospect_url": "https://test.com",
                "pain_points": "Test"
            }
        )
        assert response.status_code == 403
        
    def test_invalid_api_key(self, client):
        """Test request with invalid API key."""
        response = client.post(
            "/agents/proposal/generate",
            headers={"x-api-key": "invalid-key"},
            json={
                "prospect_name": "Test",
                "prospect_url": "https://test.com",
                "pain_points": "Test"
            }
        )
        assert response.status_code == 403
        
    def test_empty_api_key(self, client):
        """Test request with empty API key."""
        response = client.post(
            "/agents/proposal/generate",
            headers={"x-api-key": ""},
            json={
                "prospect_name": "Test",
                "prospect_url": "https://test.com",
                "pain_points": "Test"
            }
        )
        assert response.status_code == 403


class TestServiceFailures:
    """Test handling of external service failures."""
    
    @pytest.mark.asyncio
    async def test_gamma_failure_graceful_degradation(self, client, auth_headers):
        """Test that Gamma failure returns proposal without deck."""
        with patch("main.get_proposal_agent") as mock_get_agent:
            # Mock successful proposal generation
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
            
            mock_agent = MagicMock()
            mock_agent.run = AsyncMock(return_value=MagicMock(data=mock_output))
            mock_get_agent.return_value = mock_agent
            
            # Mock Gamma to fail
            with patch("main.GammaService") as mock_gamma_class:
                mock_gamma = MagicMock()
                mock_gamma.generate_presentation = AsyncMock(
                    side_effect=Exception("Gamma API Error")
                )
                mock_gamma_class.return_value = mock_gamma
                
                response = client.post(
                    "/agents/proposal/generate",
                    headers=auth_headers,
                    json={
                        "prospect_name": "Test Corp",
                        "prospect_url": "https://example.com",
                        "pain_points": "Low conversion rates"
                    }
                )
                
                # Should still succeed with proposal data
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["data"] is not None
                # Gamma URL should be None due to failure
                assert data["presentation_url"] is None
                
    @pytest.mark.asyncio
    async def test_scraping_failure_graceful_degradation(self, client, auth_headers):
        """Test that scraping failure still generates proposal."""
        with patch("main.get_proposal_agent") as mock_get_agent:
            from agents.proposal_agent import ProposalOutput, PricingTier
            mock_output = ProposalOutput(
                executive_summary="Test",
                current_situation="Test",
                proposed_strategy="Test",
                why_us="Test",
                investment=[
                    PricingTier(name="T1", price="$1k", features=["F"]),
                    PricingTier(name="T2", price="$2k", features=["F"]),
                    PricingTier(name="T3", price="$3k", features=["F"])
                ],
                next_steps="CTA"
            )
            
            mock_agent = MagicMock()
            mock_agent.run = AsyncMock(return_value=MagicMock(data=mock_output))
            mock_get_agent.return_value = mock_agent
            
            # Mock scraping to fail
            with patch("main.ScrapingService") as mock_scraping_class:
                mock_scraping = MagicMock()
                mock_scraping.analyze_prospect = AsyncMock(
                    side_effect=Exception("Scraping failed")
                )
                mock_scraping_class.return_value = mock_scraping
                
                # Mock Gamma to succeed
                with patch("main.GammaService") as mock_gamma_class:
                    mock_gamma = MagicMock()
                    mock_gamma.generate_presentation = AsyncMock(
                        return_value={"gammaUrl": "https://gamma.app/test"}
                    )
                    mock_gamma_class.return_value = mock_gamma
                    
                    response = client.post(
                        "/agents/proposal/generate",
                        headers=auth_headers,
                        json={
                            "prospect_name": "Test Corp",
                            "prospect_url": "https://example.com",
                            "pain_points": "Low conversion",
                            "deep_scrape": True
                        }
                    )
                    
                    # Should still succeed
                    assert response.status_code == 200


class TestErrorResponseFormat:
    """Test error response format consistency."""
    
    def test_validation_error_format(self, client, auth_headers):
        """Test that validation errors follow consistent format."""
        response = client.post(
            "/agents/proposal/generate",
            headers=auth_headers,
            json={
                "prospect_name": "",
                "prospect_url": "https://example.com",
                "pain_points": "Test"
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        
    def test_auth_error_format(self, client):
        """Test that auth errors follow consistent format."""
        response = client.post(
            "/agents/proposal/generate",
            headers={"x-api-key": "wrong"},
            json={
                "prospect_name": "Test",
                "prospect_url": "https://test.com",
                "pain_points": "Test"
            }
        )
        
        assert response.status_code == 403
        data = response.json()
        assert "detail" in data


class TestRateLimiting:
    """Test rate limit error handling (if implemented)."""
    
    def test_rate_limit_response_format(self):
        """Test that rate limit errors include retry info."""
        from utils.exceptions import GammaError, ErrorCode
        
        error = GammaError(
            "Rate limit exceeded",
            error_code=ErrorCode.GAMMA_RATE_LIMIT,
            retry_after_seconds=60
        )
        
        response = error.to_dict()
        
        assert response["retryable"] is True
        assert response["retry_after_seconds"] == 60
        # Error code EXT_003 is for GAMMA_RATE_LIMIT
        assert response["error_code"] == ErrorCode.GAMMA_RATE_LIMIT.value

