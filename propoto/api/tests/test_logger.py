"""
Tests for structured logging utilities.

Covers context variables, formatters, and timing context.
"""

import pytest
import json
import logging
from unittest.mock import patch, MagicMock
from utils.logger import (
    StructuredLogger,
    TimingContext,
    TokenTracker,
    set_request_context,
    get_request_id,
    request_id_var,
    org_id_var,
    agent_name_var,
    JSONFormatter,
    ColoredFormatter,
)


class TestContextVariables:
    """Test context variable management."""
    
    def setup_method(self):
        """Reset context vars before each test."""
        request_id_var.set(None)
        org_id_var.set(None)
        agent_name_var.set(None)
        
    def test_set_request_context(self):
        """Test setting request context."""
        set_request_context(request_id="req-123", org_id="org-456")
        
        assert request_id_var.get() == "req-123"
        assert org_id_var.get() == "org-456"
        
    def test_get_request_id_generates_new(self):
        """Test that get_request_id generates new ID if not set."""
        request_id_var.set(None)
        
        request_id = get_request_id()
        
        assert request_id is not None
        assert len(request_id) == 8  # First 8 chars of UUID
        
    def test_get_request_id_returns_existing(self):
        """Test that get_request_id returns existing ID."""
        request_id_var.set("existing-id")
        
        request_id = get_request_id()
        
        assert request_id == "existing-id"


class TestStructuredLogger:
    """Test StructuredLogger class."""
    
    def setup_method(self):
        """Reset context vars before each test."""
        request_id_var.set(None)
        org_id_var.set(None)
        agent_name_var.set(None)
        
    def test_format_message_with_context(self):
        """Test message formatting with context."""
        request_id_var.set("req-123")
        org_id_var.set("org-456")
        
        message = StructuredLogger._format_message("Test message")
        
        assert "[request_id=req-123 org_id=org-456]" in message
        assert "Test message" in message
        
    def test_format_message_without_context(self):
        """Test message formatting without context."""
        message = StructuredLogger._format_message("Test message")
        
        assert message == "Test message"
        
    def test_get_context_returns_all_vars(self):
        """Test that _get_context returns all set variables."""
        request_id_var.set("req")
        org_id_var.set("org")
        agent_name_var.set("agent")
        
        # Note: _get_context doesn't include agent_name by default
        context = StructuredLogger._get_context()
        
        assert context.get("request_id") == "req"
        assert context.get("org_id") == "org"


class TestJSONFormatter:
    """Test JSON log formatter."""
    
    def test_format_basic_record(self):
        """Test formatting a basic log record."""
        formatter = JSONFormatter()
        
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        result = formatter.format(record)
        data = json.loads(result)
        
        assert data["level"] == "INFO"
        assert data["message"] == "Test message"
        assert data["logger"] == "test"
        assert "timestamp" in data
        
    def test_format_with_context(self):
        """Test formatting with context variables."""
        formatter = JSONFormatter()
        request_id_var.set("req-json-123")
        
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test",
            args=(),
            exc_info=None
        )
        
        result = formatter.format(record)
        data = json.loads(result)
        
        assert data["request_id"] == "req-json-123"
        
        # Cleanup
        request_id_var.set(None)


class TestColoredFormatter:
    """Test colored log formatter."""
    
    def test_format_includes_level_color(self):
        """Test that format includes level name."""
        formatter = ColoredFormatter()
        
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        result = formatter.format(record)
        
        assert "INFO" in result
        assert "Test message" in result
        
    def test_format_with_context(self):
        """Test format includes context variables."""
        formatter = ColoredFormatter()
        request_id_var.set("req-color-123")
        org_id_var.set("org-color")
        
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test",
            args=(),
            exc_info=None
        )
        
        result = formatter.format(record)
        
        assert "req=req-color-123" in result
        assert "org=org-color" in result
        
        # Cleanup
        request_id_var.set(None)
        org_id_var.set(None)


class TestTimingContext:
    """Test TimingContext context manager."""
    
    def test_timing_context_tracks_duration(self):
        """Test that timing context tracks duration."""
        import time
        
        with TimingContext("test_operation") as timer:
            time.sleep(0.1)  # 100ms
            
        assert timer.duration >= 0.1
        assert timer.duration < 0.2  # Allow some slack
        
    def test_timing_context_logs(self):
        """Test that timing context logs start and end."""
        with patch.object(StructuredLogger, 'debug') as mock_debug:
            with patch.object(StructuredLogger, 'info') as mock_info:
                with TimingContext("test_op"):
                    pass
                    
                # Should log completion (info is called in __exit__)
                assert mock_info.called or mock_debug.called


class TestTokenTracker:
    """Test TokenTracker class."""
    
    def test_record_usage_basic(self):
        """Test basic token usage recording."""
        tracker = TokenTracker()
        
        tracker.record_usage(prompt_tokens=100, completion_tokens=50)
        
        assert tracker.prompt_tokens == 100
        assert tracker.completion_tokens == 50
        assert tracker.total_tokens == 150
        
    def test_record_usage_accumulates(self):
        """Test that usage accumulates across calls."""
        tracker = TokenTracker()
        
        tracker.record_usage(prompt_tokens=100, completion_tokens=50)
        tracker.record_usage(prompt_tokens=200, completion_tokens=100)
        
        assert tracker.prompt_tokens == 300
        assert tracker.completion_tokens == 150
        assert tracker.total_tokens == 450
        
    def test_free_model_no_cost(self):
        """Test that free models have zero cost."""
        tracker = TokenTracker()
        
        tracker.record_usage(
            prompt_tokens=1000,
            completion_tokens=1000,
            model="grok-4.1-fast:free"
        )
        
        assert tracker.cost_estimate == 0.0
        
    def test_paid_model_has_cost(self):
        """Test that paid models have non-zero cost."""
        tracker = TokenTracker()
        
        tracker.record_usage(
            prompt_tokens=1_000_000,  # 1M tokens
            completion_tokens=1_000_000,
            model="gpt-4o"
        )
        
        # Should have some cost estimate
        assert tracker.cost_estimate > 0


class TestLoggerIntegration:
    """Integration tests for logging system."""
    
    def test_logger_with_full_context(self):
        """Test logging with full context set."""
        set_request_context(request_id="int-req", org_id="int-org")
        agent_name_var.set("int-agent")
        
        # Just verify no exceptions
        StructuredLogger.info("Integration test message")
        StructuredLogger.warning("Warning message")
        StructuredLogger.error("Error message")
        
        # Cleanup
        request_id_var.set(None)
        org_id_var.set(None)
        agent_name_var.set(None)

