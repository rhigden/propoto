"""
Utilities module for Propoto API.

Exports structured logging, exception handling, and helper utilities.
"""

from .logger import (
    StructuredLogger,
    TimingContext,
    TokenTracker,
    set_request_context,
    get_request_id,
    logger,
    setup_logging,
    request_id_var,
    org_id_var,
    agent_name_var,
)

from .exceptions import (
    # Base exceptions
    AgentServiceError,
    ErrorCode,
    
    # Authentication
    AuthenticationError,
    
    # External services
    ExternalServiceError,
    GammaError,
    ExaError,
    FirecrawlError,
    Mem0Error,
    ConvexError,
    OpenRouterError,
    
    # Validation
    ValidationError,
    
    # Agent errors
    AgentExecutionError,
    
    # Configuration
    ConfigurationError,
    
    # Utilities
    handle_http_status,
)

__all__ = [
    # Logger
    "StructuredLogger",
    "TimingContext",
    "TokenTracker",
    "set_request_context",
    "get_request_id",
    "logger",
    "setup_logging",
    "request_id_var",
    "org_id_var",
    "agent_name_var",
    
    # Exceptions
    "AgentServiceError",
    "ErrorCode",
    "AuthenticationError",
    "ExternalServiceError",
    "GammaError",
    "ExaError",
    "FirecrawlError",
    "Mem0Error",
    "ConvexError",
    "OpenRouterError",
    "ValidationError",
    "AgentExecutionError",
    "ConfigurationError",
    "handle_http_status",
]

