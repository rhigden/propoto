"""
Tests for custom exception classes.

Covers error codes, exception hierarchy, and API response formatting.
"""

import pytest
from utils.exceptions import (
    AgentServiceError,
    AuthenticationError,
    ValidationError,
    GammaError,
    ExaError,
    FirecrawlError,
    Mem0Error,
    ConvexError,
    OpenRouterError,
    AgentExecutionError,
    ConfigurationError,
    ErrorCode,
    handle_http_status,
)


class TestAgentServiceError:
    """Test base exception class."""
    
    def test_basic_error_creation(self):
        """Test creating a basic error."""
        error = AgentServiceError("Test error")
        assert error.message == "Test error"
        assert error.error_code == ErrorCode.UNKNOWN_ERROR
        assert error.status_code == 500
        assert error.retryable is False
        
    def test_error_with_all_params(self):
        """Test error with all parameters."""
        error = AgentServiceError(
            message="Rate limit exceeded",
            error_code=ErrorCode.GAMMA_RATE_LIMIT,
            status_code=429,
            retryable=True,
            retry_after_seconds=60,
            details={"limit": 100, "current": 150}
        )
        assert error.message == "Rate limit exceeded"
        assert error.error_code == ErrorCode.GAMMA_RATE_LIMIT
        assert error.status_code == 429
        assert error.retryable is True
        assert error.retry_after_seconds == 60
        assert error.details == {"limit": 100, "current": 150}
        
    def test_to_dict_basic(self):
        """Test converting error to dict."""
        error = AgentServiceError("Test error")
        result = error.to_dict()
        
        assert result["error"] == "Test error"
        assert result["error_code"] == "INT_999"  # UNKNOWN_ERROR
        assert result["retryable"] is False
        assert "retry_after_seconds" not in result
        
    def test_to_dict_with_retry(self):
        """Test dict conversion with retry info."""
        error = AgentServiceError(
            message="Rate limited",
            retryable=True,
            retry_after_seconds=30
        )
        result = error.to_dict()
        
        assert result["retryable"] is True
        assert result["retry_after_seconds"] == 30
        
    def test_to_dict_with_details(self):
        """Test dict conversion with extra details."""
        error = AgentServiceError(
            message="Error",
            details={"field": "email", "reason": "invalid"}
        )
        result = error.to_dict()
        
        assert result["details"]["field"] == "email"
        assert result["details"]["reason"] == "invalid"


class TestAuthenticationError:
    """Test authentication error class."""
    
    def test_default_error(self):
        """Test default authentication error."""
        error = AuthenticationError()
        assert error.message == "Authentication failed"
        assert error.status_code == 403
        assert error.retryable is False
        
    def test_missing_key_error(self):
        """Test missing API key error."""
        error = AuthenticationError(
            message="API key is required",
            error_code=ErrorCode.AUTH_MISSING_KEY
        )
        assert error.status_code == 401
        assert error.error_code == ErrorCode.AUTH_MISSING_KEY


class TestValidationError:
    """Test validation error class."""
    
    def test_basic_validation_error(self):
        """Test basic validation error."""
        error = ValidationError("Invalid input")
        assert error.status_code == 400
        assert error.retryable is False
        
    def test_validation_error_with_field(self):
        """Test validation error with field name."""
        error = ValidationError(
            message="URL is required",
            field="prospect_url"
        )
        result = error.to_dict()
        assert result["details"]["field"] == "prospect_url"


class TestExternalServiceErrors:
    """Test external service error classes."""
    
    def test_gamma_error(self):
        """Test Gamma error."""
        error = GammaError("Generation failed")
        assert error.status_code == 502
        assert error.retryable is True
        assert error.error_code == ErrorCode.GAMMA_API_ERROR
        
    def test_gamma_error_not_retryable(self):
        """Test non-retryable Gamma error."""
        error = GammaError(
            "Invalid API key",
            retryable=False
        )
        assert error.retryable is False
        
    def test_exa_error(self):
        """Test Exa error."""
        error = ExaError("Search failed")
        assert error.status_code == 502
        assert error.error_code == ErrorCode.EXA_API_ERROR
        
    def test_firecrawl_error(self):
        """Test Firecrawl error."""
        error = FirecrawlError("Scrape failed")
        assert error.status_code == 502
        assert error.error_code == ErrorCode.FIRECRAWL_API_ERROR
        
    def test_mem0_error(self):
        """Test Mem0 error."""
        error = Mem0Error("Memory save failed")
        assert error.status_code == 502
        assert error.error_code == ErrorCode.MEM0_API_ERROR
        
    def test_convex_error(self):
        """Test Convex error."""
        error = ConvexError("Mutation failed")
        assert error.status_code == 502
        assert error.error_code == ErrorCode.CONVEX_API_ERROR
        
    def test_openrouter_error_with_retry(self):
        """Test OpenRouter error with retry."""
        error = OpenRouterError(
            "Rate limit exceeded",
            error_code=ErrorCode.OPENROUTER_RATE_LIMIT,
            retry_after_seconds=60
        )
        assert error.retry_after_seconds == 60
        assert error.retryable is True


class TestAgentExecutionError:
    """Test agent execution error class."""
    
    def test_agent_error_includes_name(self):
        """Test that agent error includes agent name."""
        error = AgentExecutionError(
            message="Agent failed",
            agent_name="proposal_agent"
        )
        assert error.details["agent"] == "proposal_agent"
        assert error.status_code == 500


class TestConfigurationError:
    """Test configuration error class."""
    
    def test_missing_vars_error(self):
        """Test configuration error with missing vars."""
        error = ConfigurationError(
            message="Missing required environment variables",
            missing_vars=["OPENROUTER_API_KEY", "GAMMA_API_KEY"]
        )
        assert "OPENROUTER_API_KEY" in error.details["missing_variables"]
        assert error.retryable is False


class TestHandleHttpStatus:
    """Test HTTP status code handler utility."""
    
    def test_401_returns_auth_error(self):
        """Test 401 returns authentication error."""
        error = handle_http_status(401, "gamma")
        assert isinstance(error, AuthenticationError)
        assert error.error_code == ErrorCode.AUTH_INVALID_KEY
        
    def test_402_returns_service_error(self):
        """Test 402 returns service-specific error."""
        error = handle_http_status(402, "gamma")
        assert isinstance(error, GammaError)
        assert error.retryable is False  # Payment issues aren't retryable
        
    def test_429_rate_limit(self):
        """Test 429 returns rate limit error."""
        error = handle_http_status(429, "exa")
        assert isinstance(error, ExaError)
        assert error.error_code == ErrorCode.EXA_RATE_LIMIT
        assert error.retryable is True
        assert error.retry_after_seconds == 60
        
    def test_timeout_status(self):
        """Test timeout status codes."""
        error = handle_http_status(504, "firecrawl")
        assert isinstance(error, FirecrawlError)
        assert error.error_code == ErrorCode.FIRECRAWL_TIMEOUT
        assert error.retryable is True
        
    def test_500_server_error(self):
        """Test 500 returns retryable error."""
        error = handle_http_status(500, "convex")
        assert isinstance(error, ConvexError)
        assert error.retryable is True
        
    def test_unknown_service(self):
        """Test unknown service returns base error."""
        error = handle_http_status(500, "unknown_service")
        assert error.error_code == ErrorCode.UNKNOWN_ERROR


class TestErrorCodes:
    """Test error code values."""
    
    def test_error_code_format(self):
        """Test error codes follow expected format."""
        # Auth codes start with AUTH_
        assert ErrorCode.AUTH_INVALID_KEY.value.startswith("AUTH_")
        
        # External service codes start with EXT_
        assert ErrorCode.GAMMA_API_ERROR.value.startswith("EXT_")
        
        # Validation codes start with VAL_
        assert ErrorCode.VALIDATION_MISSING_FIELD.value.startswith("VAL_")
        
        # Agent codes start with AGT_
        assert ErrorCode.AGENT_EXECUTION_FAILED.value.startswith("AGT_")
        
        # Config codes start with CFG_
        assert ErrorCode.CONFIG_MISSING_ENV.value.startswith("CFG_")
        
        # Internal codes start with INT_
        assert ErrorCode.INTERNAL_ERROR.value.startswith("INT_")
        
    def test_all_error_codes_unique(self):
        """Test all error codes are unique."""
        values = [code.value for code in ErrorCode]
        assert len(values) == len(set(values)), "Duplicate error codes found"

