"""
BE-015: Structured JSON logging configuration

Provides structured logging with JSON format for stdout,
supporting info/warn/error levels and request-id tracking.
"""
import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict, Optional
from contextvars import ContextVar

# Context variable for storing request ID across async contexts
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.
    
    Outputs logs in JSON format to stdout with the following fields:
    - timestamp: ISO 8601 formatted timestamp
    - level: Log level (INFO, WARNING, ERROR, etc.)
    - logger: Logger name
    - message: Log message
    - request_id: Request ID if available (from context)
    - module: Module name
    - function: Function name
    - line: Line number
    - extra: Any extra fields passed to the log call
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON string"""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add request_id if available
        request_id = request_id_var.get()
        if request_id:
            log_data["request_id"] = request_id
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add any extra fields
        if hasattr(record, 'extra_fields'):
            log_data.update(record.extra_fields)
        
        return json.dumps(log_data, ensure_ascii=False)


def setup_logging(
    level: str = "INFO",
    logger_name: str = "ohmatdyt_crm"
) -> logging.Logger:
    """
    Setup structured JSON logging for the application.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        logger_name: Name of the logger
    
    Returns:
        Configured logger instance
    
    Example:
        >>> logger = setup_logging(level="INFO")
        >>> logger.info("Application started", extra={'extra_fields': {'version': '0.1.0'}})
        {"timestamp":"2025-10-30T12:00:00.000Z","level":"INFO","logger":"ohmatdyt_crm",...}
    """
    # Get or create logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create console handler with JSON formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    console_handler.setFormatter(JSONFormatter())
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def get_logger(name: str = "ohmatdyt_crm") -> logging.Logger:
    """
    Get configured logger instance.
    
    Args:
        name: Logger name
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def set_request_id(request_id: str) -> None:
    """
    Set request ID in context for current async context.
    
    Args:
        request_id: Unique request identifier
    """
    request_id_var.set(request_id)


def get_request_id() -> Optional[str]:
    """
    Get request ID from current async context.
    
    Returns:
        Request ID if available, None otherwise
    """
    return request_id_var.get()


def clear_request_id() -> None:
    """Clear request ID from current async context"""
    request_id_var.set(None)
