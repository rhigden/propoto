import pytest
from fastapi.testclient import TestClient
from main import app, verify_key
from unittest.mock import patch, MagicMock

# Override dependency to bypass auth
app.dependency_overrides[verify_key] = lambda: None

client = TestClient(app)

def test_rate_limit_proposal_generation():
    # We need to mock the actual agent execution to avoid calling external APIs
    with patch("main.get_proposal_agent") as mock_get_agent:
        mock_agent_instance = MagicMock()
        mock_agent_instance.run.return_value = MagicMock(data={"executive_summary": "test"})
        mock_get_agent.return_value = mock_agent_instance
        
        with patch("main.GammaService") as mock_gamma:
            mock_gamma.return_value.generate_presentation.return_value = "http://gamma.app/test"
            
            # The limit is 5/minute
            # Make 5 allowed requests
            for i in range(5):
                response = client.post(
                    "/agents/proposal/generate",
                    json={
                        "prospect_name": f"Test {i}",
                        "prospect_url": "http://example.com",
                        "pain_points": "test"
                    }
                )
                # We might get other errors (like 500 if mocks aren't perfect) but NOT 429 yet
                # Actually, since we mocked the agent, it should return 200
                assert response.status_code != 429, f"Request {i+1} failed with 429. Status: {response.status_code}, Body: {response.text}"

            # The 6th request should fail with 429
            response = client.post(
                "/agents/proposal/generate",
                json={
                    "prospect_name": "Test 6",
                    "prospect_url": "http://example.com",
                    "pain_points": "test"
                }
            )
            assert response.status_code == 429
            assert "Rate limit exceeded" in response.text
