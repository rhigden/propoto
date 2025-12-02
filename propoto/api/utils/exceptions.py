"""
Custom exceptions for the Propoto API.

Provides structured error handling with error codes, retry hints, and user-friendly messages.
"""

from typing import Optional, Dict, Any
from enum import Enum


class ErrorCode(str, Enum):
    """Standard error codes for the agent service."""
    # Authentication & Authorization
    AUTH_INVALID_KEY = "AUTH_001"
    AUTH_MISSING_KEY = "AUTH_002"
    AUTH_EXPIRED_KEY = "AUTH_003"
    
    # External Service Errors
    GAMMA_API_ERROR = "EXT_001"
    GAMMA_TIMEOUT = "EXT_002"
    GAMMA_RATE_LIMIT = "EXT_003"
    GAMMA_CREDITS = "EXT_004"
    
    EXA_API_ERROR = "EXT_010"
    EXA_TIMEOUT = "EXT_011"
    EXA_RATE_LIMIT = "EXT_012"
    
    FIRECRAWL_API_ERROR = "EXT_020"
    FIRECRAWL_TIMEOUT = "EXT_021"
    FIRECRAWL_SCRAPE_FAILED = "EXT_022"
    
    MEM0_API_ERROR = "EXT_030"
    MEM0_TIMEOUT = "EXT_031"
    
    CONVEX_API_ERROR = "EXT_040"
    CONVEX_TIMEOUT = "EXT_041"
    CONVEX_MUTATION_FAILED = "EXT_042"
    
    OPENROUTER_API_ERROR = "EXT_050"
    OPENROUTER_TIMEOUT = "EXT_051"
    OPENROUTER_RATE_LIMIT = "EXT_052"
    
    # Validation Errors
    VALIDATION_MISSING_FIELD = "VAL_001"
    VALIDATION_INVALID_URL = "VAL_002"
    VALIDATION_INVALID_FORMAT = "VAL_003"
    VALIDATION_TEMPLATE_NOT_FOUND = "VAL_004"
    VALIDATION_MODEL_NOT_FOUND = "VAL_005"
    
    # Agent Errors
    AGENT_EXECUTION_FAILED = "AGT_001"
    AGENT_TIMEOUT = "AGT_002"
    AGENT_OUTPUT_VALIDATION = "AGT_003"
    
    # Configuration Errors
    CONFIG_MISSING_ENV = "CFG_001"
    CONFIG_INVALID = "CFG_002"
    
    # General Errors
    INTERNAL_ERROR = "INT_001"
    UNKNOWN_ERROR = "INT_999"


class AgentServiceError(Exception):
    """Base exception for all agent service errors."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
        status_code: int = 500,
        retryable: bool = False,
        retry_after_seconds: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.retryable = retryable
        self.retry_after_seconds = retry_after_seconds
        self.details = details or {}
        self.original_error = original_error
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to API response format."""
        response = {
            "error": self.message,
            "error_code": self.error_code.value,
            "retryable": self.retryable,
        }
        
        if self.retry_after_seconds:
            response["retry_after_seconds"] = self.retry_after_seconds
        
        if self.details:
            response["details"] = self.details
        
        return response


# --- Authentication Errors ---

class AuthenticationError(AgentServiceError):
    """Authentication-related errors."""
    
    def __init__(
        self,
        message: str = "Authentication failed",
        error_code: ErrorCode = ErrorCode.AUTH_INVALID_KEY,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=401 if error_code == ErrorCode.AUTH_MISSING_KEY else 403,
            retryable=False,
            details=details
        )


# --- External Service Errors ---

class ExternalServiceError(AgentServiceError):
    """Base class for external service errors."""
    pass


class GammaError(ExternalServiceError):
    """Gamma API related errors."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.GAMMA_API_ERROR,
        retryable: bool = True,
        retry_after_seconds: Optional[int] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=502,
            retryable=retryable,
            retry_after_seconds=retry_after_seconds,
            original_error=original_error
        )


class ExaError(ExternalServiceError):
    """Exa API related errors."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.EXA_API_ERROR,
        retryable: bool = True,
        retry_after_seconds: Optional[int] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=502,
            retryable=retryable,
            retry_after_seconds=retry_after_seconds,
            original_error=original_error
        )


class FirecrawlError(ExternalServiceError):
    """Firecrawl API related errors."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.FIRECRAWL_API_ERROR,
        retryable: bool = True,
        original_error: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=502,
            retryable=retryable,
            original_error=original_error
        )


class Mem0Error(ExternalServiceError):
    """Mem0 API related errors."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.MEM0_API_ERROR,
        retryable: bool = True,
        original_error: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=502,
            retryable=retryable,
            original_error=original_error
        )


class ConvexError(ExternalServiceError):
    """Convex API related errors."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.CONVEX_API_ERROR,
        retryable: bool = True,
        original_error: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=502,
            retryable=retryable,
            original_error=original_error
        )


class OpenRouterError(ExternalServiceError):
    """OpenRouter API related errors."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.OPENROUTER_API_ERROR,
        retryable: bool = True,
        retry_after_seconds: Optional[int] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=502,
            retryable=retryable,
            retry_after_seconds=retry_after_seconds,
            original_error=original_error
        )


# --- Validation Errors ---

class ValidationError(AgentServiceError):
    """Input validation errors."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.VALIDATION_INVALID_FORMAT,
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = details or {}
        if field:
            error_details["field"] = field
        
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=400,
            retryable=False,
            details=error_details
        )


# --- Agent Errors ---

class AgentExecutionError(AgentServiceError):
    """Agent execution errors."""
    
    def __init__(
        self,
        message: str,
        agent_name: str,
        error_code: ErrorCode = ErrorCode.AGENT_EXECUTION_FAILED,
        retryable: bool = True,
        original_error: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=500,
            retryable=retryable,
            details={"agent": agent_name},
            original_error=original_error
        )


# --- Configuration Errors ---

class ConfigurationError(AgentServiceError):
    """Configuration errors (missing env vars, invalid config)."""
    
    def __init__(
        self,
        message: str,
        missing_vars: Optional[list] = None,
        error_code: ErrorCode = ErrorCode.CONFIG_MISSING_ENV
    ):
        details = {}
        if missing_vars:
            details["missing_variables"] = missing_vars
        
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=500,
            retryable=False,
            details=details
        )


# --- Utility Functions ---

def handle_http_status(status_code: int, service_name: str, response_text: str = "") -> AgentServiceError:
    """Convert HTTP status code to appropriate exception."""
    
    service_map = {
        "gamma": (GammaError, ErrorCode.GAMMA_API_ERROR, ErrorCode.GAMMA_RATE_LIMIT, ErrorCode.GAMMA_TIMEOUT),
        "exa": (ExaError, ErrorCode.EXA_API_ERROR, ErrorCode.EXA_RATE_LIMIT, ErrorCode.EXA_TIMEOUT),
        "firecrawl": (FirecrawlError, ErrorCode.FIRECRAWL_API_ERROR, ErrorCode.FIRECRAWL_API_ERROR, ErrorCode.FIRECRAWL_TIMEOUT),
        "mem0": (Mem0Error, ErrorCode.MEM0_API_ERROR, ErrorCode.MEM0_API_ERROR, ErrorCode.MEM0_TIMEOUT),
        "convex": (ConvexError, ErrorCode.CONVEX_API_ERROR, ErrorCode.CONVEX_API_ERROR, ErrorCode.CONVEX_TIMEOUT),
        "openrouter": (OpenRouterError, ErrorCode.OPENROUTER_API_ERROR, ErrorCode.OPENROUTER_RATE_LIMIT, ErrorCode.OPENROUTER_TIMEOUT),
    }
    
    error_class, api_error_code, rate_limit_code, timeout_code = service_map.get(
        service_name.lower(),
        (ExternalServiceError, ErrorCode.UNKNOWN_ERROR, ErrorCode.UNKNOWN_ERROR, ErrorCode.UNKNOWN_ERROR)
    )
    
    if status_code == 401:
        return AuthenticationError(
            f"{service_name} API: Invalid credentials",
            error_code=ErrorCode.AUTH_INVALID_KEY
        )
    elif status_code == 402:
        return error_class(
            f"{service_name} API: Insufficient credits or subscription required",
            error_code=api_error_code,
            retryable=False
        )
    elif status_code == 429:
        return error_class(
            f"{service_name} API: Rate limit exceeded",
            error_code=rate_limit_code,
            retryable=True,
            retry_after_seconds=60
        )
    elif status_code == 408 or status_code == 504:
        return error_class(
            f"{service_name} API: Request timeout",
            error_code=timeout_code,
            retryable=True
        )
    elif status_code >= 500:
        return error_class(
            f"{service_name} API: Server error ({status_code})",
            error_code=api_error_code,
            retryable=True
        )
    else:
        return error_class(
            f"{service_name} API error ({status_code}): {response_text[:200]}",
            error_code=api_error_code,
            retryable=False
        )

