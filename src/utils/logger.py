"""
Centralized Logging System for AI Video GPT

This module provides a structured logging system with:
- JSON formatting for production
- Console formatting for development
- Automatic log rotation
- Correlation IDs for request tracking
- Performance metrics logging
- Different log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
"""

import logging
import logging.handlers
import json
import os
import time
import uuid
import threading
from datetime import datetime
from functools import wraps
from typing import Dict, Any, Optional, Callable
from contextlib import contextmanager
import sys
import traceback


# Thread-local storage for correlation IDs
_local = threading.local()


class CorrelationIDFilter(logging.Filter):
    """Filter to add correlation ID to log records"""
    
    def filter(self, record):
        correlation_id = getattr(_local, 'correlation_id', None)
        record.correlation_id = correlation_id or 'no-correlation-id'
        return True


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record):
        # Create the base log record
        log_obj = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'correlation_id': getattr(record, 'correlation_id', None),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'thread': record.thread,
            'thread_name': record.threadName,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_obj['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'extra_data'):
            log_obj['extra'] = record.extra_data
        
        # Add performance metrics if present
        if hasattr(record, 'performance_metrics'):
            log_obj['performance'] = record.performance_metrics
        
        # Add request/response data if present
        if hasattr(record, 'request_data'):
            log_obj['request'] = record.request_data
        
        if hasattr(record, 'response_data'):
            log_obj['response'] = record.response_data
        
        return json.dumps(log_obj, ensure_ascii=False)


class ColoredConsoleFormatter(logging.Formatter):
    """Console formatter with color support for development"""
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        # Add colors for console output
        level_color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{level_color}{record.levelname}{self.RESET}"
        
        # Format with correlation ID
        correlation_id = getattr(record, 'correlation_id', 'no-corr-id')
        
        # Create formatted message
        formatted = (
            f"{record.asctime} | "
            f"{record.levelname:8s} | "
            f"{correlation_id[:8]} | "
            f"{record.name:25s} | "
            f"{record.getMessage()}"
        )
        
        # Add exception info if present
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"
        
        return formatted


class PerformanceTimer:
    """Context manager for measuring performance"""
    
    def __init__(self, operation_name: str, logger: logging.Logger, level: int = logging.INFO):
        self.operation_name = operation_name
        self.logger = logger
        self.level = level
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.logger.log(self.level, f"Starting operation: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        
        # Create performance metrics
        metrics = {
            'operation': self.operation_name,
            'duration_seconds': duration,
            'duration_ms': duration * 1000,
            'success': exc_type is None
        }
        
        if exc_type:
            metrics['error_type'] = exc_type.__name__
            metrics['error_message'] = str(exc_val)
        
        # Log with performance metrics
        extra = {'performance_metrics': metrics}
        
        if exc_type:
            self.logger.error(
                f"Operation failed: {self.operation_name} (duration: {duration:.3f}s)",
                extra=extra,
                exc_info=True
            )
        else:
            self.logger.log(
                self.level,
                f"Operation completed: {self.operation_name} (duration: {duration:.3f}s)",
                extra=extra
            )


class AIVideoLogger:
    """Main logger class for AI Video GPT"""
    
    def __init__(self):
        self._loggers: Dict[str, logging.Logger] = {}
        self._configured = False
        self._log_dir = None
        self._environment = None
    
    def configure(
        self,
        log_dir: str = "logs",
        environment: str = "development",
        log_level: str = "INFO",
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        console_output: bool = True
    ):
        """Configure the logging system"""
        
        self._log_dir = log_dir
        self._environment = environment
        
        # Create logs directory
        os.makedirs(log_dir, exist_ok=True)
        
        # Set root logger level
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_level.upper()))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Add correlation ID filter to root logger
        correlation_filter = CorrelationIDFilter()
        root_logger.addFilter(correlation_filter)
        
        # Configure file handler with rotation
        log_file = os.path.join(log_dir, "ai_video_gpt.log")
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        
        # Use JSON formatter for production, regular for development
        if environment == "production":
            file_handler.setFormatter(JSONFormatter())
        else:
            file_formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(correlation_id)s | %(name)-25s | %(message)s'
            )
            file_handler.setFormatter(file_formatter)
        
        root_logger.addHandler(file_handler)
        
        # Configure console handler if requested
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            
            if environment == "production":
                # Simple format for production console
                console_formatter = logging.Formatter(
                    '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
                )
            else:
                # Colored format for development
                console_formatter = ColoredConsoleFormatter(
                    '%(asctime)s | %(levelname)-8s | %(correlation_id)s | %(name)-25s | %(message)s'
                )
            
            console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)
        
        # Configure error file handler for ERROR and CRITICAL logs
        error_file = os.path.join(log_dir, "errors.log")
        error_handler = logging.handlers.RotatingFileHandler(
            error_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        
        if environment == "production":
            error_handler.setFormatter(JSONFormatter())
        else:
            error_formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(correlation_id)s | %(name)-25s | %(message)s\n'
                'Exception: %(pathname)s:%(lineno)d in %(funcName)s\n'
            )
            error_handler.setFormatter(error_formatter)
        
        root_logger.addHandler(error_handler)
        
        self._configured = True
        
        # Log configuration completion
        config_logger = self.get_logger("logger.config")
        config_logger.info(f"Logging system configured for {environment} environment")
        config_logger.info(f"Log directory: {os.path.abspath(log_dir)}")
        config_logger.info(f"Log level: {log_level}")
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger instance for a specific module/component"""
        
        if not self._configured:
            # Auto-configure with defaults if not configured
            self.configure()
        
        if name not in self._loggers:
            self._loggers[name] = logging.getLogger(name)
        
        return self._loggers[name]
    
    @contextmanager
    def correlation_context(self, correlation_id: Optional[str] = None):
        """Context manager to set correlation ID for the current thread"""
        
        if correlation_id is None:
            correlation_id = str(uuid.uuid4())
        
        # Store previous correlation ID
        previous_id = getattr(_local, 'correlation_id', None)
        _local.correlation_id = correlation_id
        
        try:
            yield correlation_id
        finally:
            # Restore previous correlation ID
            if previous_id:
                _local.correlation_id = previous_id
            else:
                if hasattr(_local, 'correlation_id'):
                    delattr(_local, 'correlation_id')
    
    def get_correlation_id(self) -> Optional[str]:
        """Get the current correlation ID"""
        return getattr(_local, 'correlation_id', None)
    
    def set_correlation_id(self, correlation_id: str):
        """Set correlation ID for the current thread"""
        _local.correlation_id = correlation_id
    
    def performance_timer(self, operation_name: str, logger_name: str, level: int = logging.INFO):
        """Create a performance timer context manager"""
        logger = self.get_logger(logger_name)
        return PerformanceTimer(operation_name, logger, level)


# Global logger instance
ai_logger = AIVideoLogger()


def get_logger(name: str) -> logging.Logger:
    """Convenience function to get a logger"""
    return ai_logger.get_logger(name)


def setup_logging(
    log_dir: str = "logs",
    environment: str = None,
    log_level: str = "INFO",
    **kwargs
):
    """Setup logging with environment detection"""
    
    # Auto-detect environment if not specified
    if environment is None:
        if os.getenv('FLASK_ENV') == 'production' or os.getenv('ENVIRONMENT') == 'production':
            environment = 'production'
        else:
            environment = 'development'
    
    ai_logger.configure(
        log_dir=log_dir,
        environment=environment,
        log_level=log_level,
        **kwargs
    )


def log_api_request(func: Callable) -> Callable:
    """Decorator to log API requests and responses"""
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(f"api.{func.__name__}")
        
        # Generate correlation ID for this request
        with ai_logger.correlation_context() as correlation_id:
            
            # Log request
            request_data = {
                'function': func.__name__,
                'args_count': len(args),
                'kwargs': {k: str(v)[:100] for k, v in kwargs.items()},  # Truncate long values
                'correlation_id': correlation_id
            }
            
            logger.info("API request started", extra={'request_data': request_data})
            
            # Execute function with performance timing
            with ai_logger.performance_timer(f"api.{func.__name__}", f"api.{func.__name__}"):
                try:
                    result = func(*args, **kwargs)
                    
                    # Log successful response
                    response_data = {
                        'status': 'success',
                        'result_type': type(result).__name__,
                        'correlation_id': correlation_id
                    }
                    
                    logger.info("API request completed successfully", extra={'response_data': response_data})
                    return result
                    
                except Exception as e:
                    # Log error response
                    response_data = {
                        'status': 'error',
                        'error_type': type(e).__name__,
                        'error_message': str(e),
                        'correlation_id': correlation_id
                    }
                    
                    logger.error("API request failed", extra={'response_data': response_data}, exc_info=True)
                    raise
    
    return wrapper


def log_performance(operation_name: str, logger_name: str = None):
    """Decorator to log function performance"""
    
    def decorator(func: Callable) -> Callable:
        nonlocal logger_name
        if logger_name is None:
            logger_name = f"performance.{func.__module__}.{func.__name__}"
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            with ai_logger.performance_timer(operation_name, logger_name):
                return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def log_exceptions(logger_name: str = None):
    """Decorator to automatically log exceptions"""
    
    def decorator(func: Callable) -> Callable:
        nonlocal logger_name
        if logger_name is None:
            logger_name = f"exceptions.{func.__module__}.{func.__name__}"
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(logger_name)
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(
                    f"Exception in {func.__name__}: {str(e)}",
                    extra={
                        'extra_data': {
                            'function': func.__name__,
                            'module': func.__module__,
                            'args_count': len(args),
                            'exception_type': type(e).__name__
                        }
                    },
                    exc_info=True
                )
                raise
        
        return wrapper
    
    return decorator


# Convenience functions for common operations
def log_video_generation_step(step_name: str, details: Dict[str, Any] = None):
    """Log a video generation step"""
    logger = get_logger("video_generation")
    extra_data = {'step': step_name}
    if details:
        extra_data.update(details)
    
    logger.info(f"Video generation step: {step_name}", extra={'extra_data': extra_data})


def log_api_call(service: str, operation: str, details: Dict[str, Any] = None):
    """Log external API calls"""
    logger = get_logger(f"api_calls.{service}")
    extra_data = {'service': service, 'operation': operation}
    if details:
        extra_data.update(details)
    
    logger.info(f"API call: {service}.{operation}", extra={'extra_data': extra_data})


def log_file_operation(operation: str, file_path: str, details: Dict[str, Any] = None):
    """Log file operations"""
    logger = get_logger("file_operations")
    extra_data = {'operation': operation, 'file_path': file_path}
    if details:
        extra_data.update(details)
    
    logger.debug(f"File operation: {operation} - {file_path}", extra={'extra_data': extra_data})


def log_cost_tracking(service: str, operation: str, cost: float, details: Dict[str, Any] = None):
    """Log cost tracking information"""
    logger = get_logger("cost_tracking")
    extra_data = {
        'service': service,
        'operation': operation,
        'cost': cost,
        'currency': 'USD'
    }
    if details:
        extra_data.update(details)
    
    logger.info(f"Cost tracking: {service}.{operation} - ${cost:.4f}", extra={'extra_data': extra_data})


# Initialize with default configuration if not configured
if not ai_logger._configured:
    setup_logging()