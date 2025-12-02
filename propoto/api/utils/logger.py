"""
Structured logging utilities for agents.

Provides context-aware logging with orgId, requestId, and token tracking.
Supports both human-readable and JSON log formats for production observability.
"""

import logging
import time
import uuid
import json
import sys
import os
from typing import Optional, Dict, Any
from contextvars import ContextVar
from datetime import datetime

# Context variables for request tracking
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
org_id_var: ContextVar[Optional[str]] = ContextVar('org_id', default=None)
agent_name_var: ContextVar[Optional[str]] = ContextVar('agent_name', default=None)

# Environment configuration
LOG_FORMAT = os.getenv("LOG_FORMAT", "text")  # "text" or "json"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


class JSONFormatter(logging.Formatter):
    """JSON log formatter for production environments."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add context variables
        request_id = request_id_var.get()
        org_id = org_id_var.get()
        agent_name = agent_name_var.get()
        
        if request_id:
            log_entry["request_id"] = request_id
        if org_id:
            log_entry["org_id"] = org_id
        if agent_name:
            log_entry["agent"] = agent_name
        
        # Add extra fields from record
        if hasattr(record, '__dict__'):
            extra_fields = {
                k: v for k, v in record.__dict__.items()
                if k not in ['name', 'msg', 'args', 'created', 'filename', 'funcName',
                            'levelname', 'levelno', 'lineno', 'module', 'msecs',
                            'pathname', 'process', 'processName', 'relativeCreated',
                            'stack_info', 'exc_info', 'exc_text', 'thread', 'threadName',
                            'message', 'taskName']
            }
            if extra_fields:
                log_entry["extra"] = extra_fields
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry)


class ColoredFormatter(logging.Formatter):
    """Colored log formatter for development."""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        # Add color
        color = self.COLORS.get(record.levelname, self.RESET)
        
        # Build context prefix
        context_parts = []
        request_id = request_id_var.get()
        org_id = org_id_var.get()
        agent_name = agent_name_var.get()
        
        if request_id:
            context_parts.append(f"req={request_id}")
        if org_id:
            context_parts.append(f"org={org_id}")
        if agent_name:
            context_parts.append(f"agent={agent_name}")
        
        context_str = f"[{' '.join(context_parts)}] " if context_parts else ""
        
        # Format timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return f"{color}{timestamp} {record.levelname:8}{self.RESET} {context_str}{record.getMessage()}"


def setup_logging():
    """Configure logging based on environment."""
    logger = logging.getLogger("snyto_agents")
    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    
    if LOG_FORMAT == "json":
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(ColoredFormatter())
    
    logger.addHandler(handler)
    
    # Also configure root logger for third-party libraries
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.WARNING)  # Reduce noise from libraries
    
    return logger


# Initialize logger on import
logger = setup_logging()

class StructuredLogger:
    """Logger that adds structured context to log messages."""
    
    @staticmethod
    def _get_context() -> Dict[str, Any]:
        """Get current request context."""
        context = {}
        request_id = request_id_var.get()
        org_id = org_id_var.get()
        
        if request_id:
            context["request_id"] = request_id
        if org_id:
            context["org_id"] = org_id
        
        return context
    
    @staticmethod
    def _format_message(message: str, **kwargs) -> str:
        """Format message with context."""
        context = StructuredLogger._get_context()
        if context:
            context_str = " ".join([f"{k}={v}" for k, v in context.items()])
            return f"[{context_str}] {message}"
        return message
    
    @staticmethod
    def info(message: str, **kwargs):
        """Log info message with context."""
        logger.info(StructuredLogger._format_message(message, **kwargs), extra=kwargs)
    
    @staticmethod
    def warning(message: str, **kwargs):
        """Log warning message with context."""
        logger.warning(StructuredLogger._format_message(message, **kwargs), extra=kwargs)
    
    @staticmethod
    def error(message: str, **kwargs):
        """Log error message with context."""
        logger.error(StructuredLogger._format_message(message, **kwargs), extra=kwargs)
    
    @staticmethod
    def debug(message: str, **kwargs):
        """Log debug message with context."""
        logger.debug(StructuredLogger._format_message(message, **kwargs), extra=kwargs)


class TokenTracker:
    """Track token usage for agent calls."""
    
    def __init__(self):
        self.total_tokens = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.cost_estimate = 0.0
    
    def record_usage(self, prompt_tokens: int, completion_tokens: int, model: str = "grok-4.1-fast:free"):
        """Record token usage for a model call."""
        self.prompt_tokens += prompt_tokens
        self.completion_tokens += completion_tokens
        self.total_tokens = self.prompt_tokens + self.completion_tokens
        
        # Rough cost estimates (per 1M tokens)
        # Grok 4.1 Fast FREE: $0
        # GPT-4o: ~$5/$15 (input/output)
        # Claude 3.5 Sonnet: ~$3/$15
        cost_per_1m = {
            "grok-4.1-fast:free": 0.0,
            "x-ai/grok-4.1-fast:free": 0.0,
            "gpt-4o": 5.0,  # input
            "openai/gpt-4o": 5.0,
            "claude-3.5-sonnet": 3.0,
            "anthropic/claude-3.5-sonnet": 3.0,
        }
        
        # Check full model name first, then base name
        if model in cost_per_1m:
            input_cost = cost_per_1m[model]
        else:
            # Try base name (before colon for free variants)
            model_base = model.split(":")[0] if ":" in model else model
            input_cost = cost_per_1m.get(model_base, 1.0)  # Default $1 per 1M
        
        output_cost = input_cost * 3  # Rough estimate
        
        self.cost_estimate += (prompt_tokens / 1_000_000) * input_cost
        self.cost_estimate += (completion_tokens / 1_000_000) * output_cost
    
    def log_summary(self, agent_name: str):
        """Log token usage summary."""
        StructuredLogger.info(
            f"Token usage for {agent_name}",
            prompt_tokens=self.prompt_tokens,
            completion_tokens=self.completion_tokens,
            total_tokens=self.total_tokens,
            cost_estimate=f"${self.cost_estimate:.4f}"
        )


class TimingContext:
    """Context manager for timing operations."""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        StructuredLogger.debug(f"Starting {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        StructuredLogger.info(
            f"Completed {self.operation_name}",
            duration_seconds=f"{duration:.2f}",
            operation=self.operation_name
        )
        return False
    
    @property
    def duration(self) -> float:
        """Get duration in seconds."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0


def set_request_context(request_id: Optional[str] = None, org_id: Optional[str] = None):
    """Set request context for logging."""
    if request_id:
        request_id_var.set(request_id)
    if org_id:
        org_id_var.set(org_id)


def get_request_id() -> str:
    """Get or create request ID."""
    request_id = request_id_var.get()
    if not request_id:
        request_id = str(uuid.uuid4())[:8]
        request_id_var.set(request_id)
    return request_id

