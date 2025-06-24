"""
Advanced logging utility for Financial Investment Advisor Agent
Provides structured logging, performance metrics, and security event tracking
"""

import logging
import logging.handlers
import json
import time
import traceback
from datetime import datetime
from typing import Dict, Any, Optional
from functools import wraps
from pathlib import Path
import os

class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        # Create base log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'lineno', 'funcName', 'created', 
                          'msecs', 'relativeCreated', 'thread', 'threadName', 
                          'processName', 'process', 'message', 'exc_info', 'exc_text', 'stack_info']:
                log_entry[key] = value
        
        return json.dumps(log_entry)

class SecurityLogger:
    """Dedicated logger for security events"""
    
    def __init__(self):
        self.logger = logging.getLogger("security")
    
    def log_api_access(self, endpoint: str, user_id: Optional[str] = None, 
                      ip_address: Optional[str] = None, success: bool = True):
        """Log API access events"""
        self.logger.info(
            "API access",
            extra={
                "event_type": "api_access",
                "endpoint": endpoint,
                "user_id": user_id,
                "ip_address": ip_address,
                "success": success
            }
        )
    
    def log_authentication_attempt(self, user_id: str, success: bool, 
                                 ip_address: Optional[str] = None):
        """Log authentication attempts"""
        level = logging.INFO if success else logging.WARNING
        self.logger.log(
            level,
            f"Authentication {'successful' if success else 'failed'}",
            extra={
                "event_type": "authentication",
                "user_id": user_id,
                "success": success,
                "ip_address": ip_address
            }
        )
    
    def log_data_access(self, data_type: str, user_id: Optional[str] = None, 
                       action: str = "read"):
        """Log sensitive data access"""
        self.logger.info(
            f"Data access: {action} {data_type}",
            extra={
                "event_type": "data_access",
                "data_type": data_type,
                "action": action,
                "user_id": user_id
            }
        )

class PerformanceLogger:
    """Logger for performance metrics"""
    
    def __init__(self):
        self.logger = logging.getLogger("performance")
    
    def log_request_time(self, endpoint: str, duration: float, status_code: int):
        """Log request performance"""
        level = logging.WARNING if duration > 2.0 else logging.INFO
        self.logger.log(
            level,
            f"Request completed: {endpoint}",
            extra={
                "event_type": "request_performance",
                "endpoint": endpoint,
                "duration_seconds": duration,
                "status_code": status_code,
                "slow_request": duration > 2.0
            }
        )
    
    def log_database_query(self, query_type: str, duration: float, 
                          table: Optional[str] = None):
        """Log database query performance"""
        level = logging.WARNING if duration > 1.0 else logging.INFO
        self.logger.log(
            level,
            f"Database query: {query_type}",
            extra={
                "event_type": "database_performance",
                "query_type": query_type,
                "duration_seconds": duration,
                "table": table,
                "slow_query": duration > 1.0
            }
        )

def setup_logging(log_level: str = "INFO", log_file: str = "app.log", 
                 structured: bool = True, max_bytes: int = 10485760, 
                 backup_count: int = 5) -> Dict[str, logging.Logger]:
    """
    Set up comprehensive logging for the application
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Base log file path
        structured: Whether to use structured JSON logging
        max_bytes: Maximum file size before rotation (default 10MB)
        backup_count: Number of backup files to keep
    
    Returns:
        Dictionary of configured loggers
    """
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Create formatters
    if structured:
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Application log file handler (rotating)
    app_handler = logging.handlers.RotatingFileHandler(
        log_dir / log_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    app_handler.setFormatter(formatter)
    root_logger.addHandler(app_handler)
    
    # Security log handler
    security_handler = logging.handlers.RotatingFileHandler(
        log_dir / "security.log",
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    security_handler.setFormatter(formatter)
    security_logger = logging.getLogger("security")
    security_logger.addHandler(security_handler)
    security_logger.setLevel(logging.INFO)
    
    # Performance log handler
    performance_handler = logging.handlers.RotatingFileHandler(
        log_dir / "performance.log",
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    performance_handler.setFormatter(formatter)
    performance_logger = logging.getLogger("performance")
    performance_logger.addHandler(performance_handler)
    performance_logger.setLevel(logging.INFO)
    
    # Error log handler (errors only)
    error_handler = logging.handlers.RotatingFileHandler(
        log_dir / "errors.log",
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)
    root_logger.addHandler(error_handler)
    
    return {
        "app": logging.getLogger("app"),
        "security": SecurityLogger(),
        "performance": PerformanceLogger(),
        "api": logging.getLogger("api"),
        "agents": logging.getLogger("agents"),
        "services": logging.getLogger("services")
    }

def log_execution_time(logger: Optional[logging.Logger] = None):
    """Decorator to log function execution time"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            func_logger = logger or logging.getLogger(func.__module__)
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                func_logger.info(
                    f"Function completed: {func.__name__}",
                    extra={
                        "function": func.__name__,
                        "duration_seconds": duration,
                        "module": func.__module__
                    }
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                func_logger.error(
                    f"Function failed: {func.__name__}",
                    extra={
                        "function": func.__name__,
                        "duration_seconds": duration,
                        "module": func.__module__,
                        "error": str(e)
                    },
                    exc_info=True
                )
                raise
        
        return wrapper
    return decorator

def log_api_call(endpoint: str, method: str = "GET"):
    """Decorator to log API calls with timing"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            logger = logging.getLogger("api")
            
            logger.info(
                f"API call started: {method} {endpoint}",
                extra={
                    "event_type": "api_start",
                    "endpoint": endpoint,
                    "method": method
                }
            )
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                logger.info(
                    f"API call completed: {method} {endpoint}",
                    extra={
                        "event_type": "api_complete",
                        "endpoint": endpoint,
                        "method": method,
                        "duration_seconds": duration,
                        "status": "success"
                    }
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"API call failed: {method} {endpoint}",
                    extra={
                        "event_type": "api_error",
                        "endpoint": endpoint,
                        "method": method,
                        "duration_seconds": duration,
                        "status": "error",
                        "error": str(e)
                    },
                    exc_info=True
                )
                raise
        
        return wrapper
    return decorator

# Initialize loggers globally
_loggers = None

def get_logger(name: str = "app") -> logging.Logger:
    """Get a named logger instance"""
    global _loggers
    if _loggers is None:
        _loggers = setup_logging(
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_file=os.getenv("LOG_FILE", "app.log"),
            structured=os.getenv("STRUCTURED_LOGGING", "true").lower() == "true"
        )
    
    if name in _loggers:
        return _loggers[name]
    else:
        return logging.getLogger(name)

# Convenience functions
def get_security_logger() -> SecurityLogger:
    """Get the security logger instance"""
    global _loggers
    if _loggers is None:
        get_logger()  # Initialize loggers
    return _loggers["security"]

def get_performance_logger() -> PerformanceLogger:
    """Get the performance logger instance"""
    global _loggers
    if _loggers is None:
        get_logger()  # Initialize loggers
    return _loggers["performance"] 