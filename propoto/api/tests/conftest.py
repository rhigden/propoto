import pytest
from fastapi.testclient import TestClient
import os
from unittest.mock import patch

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
