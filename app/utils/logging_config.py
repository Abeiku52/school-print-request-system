"""
Logging Configuration for School Print Request System

Enterprise-grade logging setup with structured logging, multiple handlers,
and appropriate log levels for different environments.

Author: Senior Development Team
Version: 2.0.0
"""

import logging
import logging.handlers
import os
from datetime import datetime
from typing import Dict, Any
import json


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter that outputs structured JSON logs for better parsing
    and analysis in production environments.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception information if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        if hasattr(record, 'ip_address'):
            log_entry['ip_address'] = record.ip_address
        
        return json.dumps(log_entry, ensure_ascii=False)


class DevelopmentFormatter(logging.Formatter):
    """
    Human-readable formatter for development environments.
    """
    
    def __init__(self):
        super().__init__(
            fmt='%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-15s:%(lineno)-3d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )


def setup_logging(app_config: Dict[str, Any] = None) -> None:
    """
    Configure comprehensive logging for the application.
    
    Sets up multiple handlers:
    - Console handler for development
    - File handler for persistent logging
    - Rotating file handler for production
    - Error-specific handler for critical issues
    
    Args:
        app_config: Application configuration dictionary
    """
    
    # Determine environment and log level
    environment = os.getenv('FLASK_ENV', 'development')
    log_level = os.getenv('LOG_LEVEL', 'INFO' if environment == 'production' else 'DEBUG')
    
    # Create logs directory if it doesn't exist
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console Handler (for development)
    if environment == 'development':
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(DevelopmentFormatter())
        root_logger.addHandler(console_handler)
    
    # Application Log Handler (general application logs)
    app_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(log_dir, 'application.log'),
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    app_handler.setLevel(logging.INFO)
    
    if environment == 'production':
        app_handler.setFormatter(StructuredFormatter())
    else:
        app_handler.setFormatter(DevelopmentFormatter())
    
    root_logger.addHandler(app_handler)
    
    # Error Log Handler (errors and critical issues only)
    error_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(log_dir, 'errors.log'),
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=10,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(StructuredFormatter())
    root_logger.addHandler(error_handler)
    
    # Security Log Handler (authentication, authorization, admin actions)
    security_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(log_dir, 'security.log'),
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=20,  # Keep more security logs
        encoding='utf-8'
    )
    security_handler.setLevel(logging.INFO)
    security_handler.setFormatter(StructuredFormatter())
    
    # Create security logger
    security_logger = logging.getLogger('security')
    security_logger.addHandler(security_handler)
    security_logger.setLevel(logging.INFO)
    security_logger.propagate = False  # Don't propagate to root logger
    
    # Configure specific loggers
    configure_application_loggers()
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured for {environment} environment with level {log_level}")


def configure_application_loggers() -> None:
    """Configure specific loggers for different application components."""
    
    # Database operations logger
    db_logger = logging.getLogger('sqlalchemy.engine')
    db_logger.setLevel(logging.WARNING)  # Only log warnings and errors
    
    # Flask request logger
    flask_logger = logging.getLogger('werkzeug')
    flask_logger.setLevel(logging.WARNING)  # Reduce noise in development
    
    # Application component loggers
    component_loggers = [
        'app.services',
        'app.routes',
        'app.models',
        'app.utils'
    ]
    
    for logger_name in component_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)


def get_security_logger() -> logging.Logger:
    """Get the security-specific logger for audit events."""
    return logging.getLogger('security')


def log_security_event(
    event_type: str,
    user_id: int = None,
    ip_address: str = None,
    details: Dict[str, Any] = None,
    severity: str = 'INFO'
) -> None:
    """
    Log security-related events with structured information.
    
    Args:
        event_type: Type of security event (login, logout, admin_action, etc.)
        user_id: ID of the user involved in the event
        ip_address: IP address of the request
        details: Additional event details
        severity: Log severity level
    """
    security_logger = get_security_logger()
    
    # Create structured log entry
    log_data = {
        'event_type': event_type,
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'severity': severity
    }
    
    if user_id:
        log_data['user_id'] = user_id
    if ip_address:
        log_data['ip_address'] = ip_address
    if details:
        log_data['details'] = details
    
    # Log with appropriate level
    level = getattr(logging, severity.upper(), logging.INFO)
    security_logger.log(level, json.dumps(log_data, ensure_ascii=False))


def log_user_action(
    action: str,
    user_id: int,
    resource_type: str = None,
    resource_id: str = None,
    ip_address: str = None,
    success: bool = True
) -> None:
    """
    Log user actions for audit trail.
    
    Args:
        action: Action performed (create, update, delete, view, etc.)
        user_id: ID of the user performing the action
        resource_type: Type of resource affected
        resource_id: ID of the resource affected
        ip_address: IP address of the request
        success: Whether the action was successful
    """
    details = {
        'action': action,
        'success': success
    }
    
    if resource_type:
        details['resource_type'] = resource_type
    if resource_id:
        details['resource_id'] = resource_id
    
    log_security_event(
        event_type='user_action',
        user_id=user_id,
        ip_address=ip_address,
        details=details,
        severity='INFO' if success else 'WARNING'
    )


def log_admin_action(
    action: str,
    admin_id: int,
    target_user_id: int = None,
    details: Dict[str, Any] = None,
    ip_address: str = None
) -> None:
    """
    Log administrative actions for compliance and audit.
    
    Args:
        action: Administrative action performed
        admin_id: ID of the administrator
        target_user_id: ID of the user being affected (if applicable)
        details: Additional action details
        ip_address: IP address of the request
    """
    admin_details = {
        'admin_action': action,
        'admin_id': admin_id
    }
    
    if target_user_id:
        admin_details['target_user_id'] = target_user_id
    if details:
        admin_details.update(details)
    
    log_security_event(
        event_type='admin_action',
        user_id=admin_id,
        ip_address=ip_address,
        details=admin_details,
        severity='HIGH'
    )


# Context manager for request logging
class RequestLoggingContext:
    """Context manager to add request-specific information to logs."""
    
    def __init__(self, request_id: str, user_id: int = None, ip_address: str = None):
        self.request_id = request_id
        self.user_id = user_id
        self.ip_address = ip_address
        self.old_factory = None
    
    def __enter__(self):
        self.old_factory = logging.getLogRecordFactory()
        
        def record_factory(*args, **kwargs):
            record = self.old_factory(*args, **kwargs)
            record.request_id = self.request_id
            if self.user_id:
                record.user_id = self.user_id
            if self.ip_address:
                record.ip_address = self.ip_address
            return record
        
        logging.setLogRecordFactory(record_factory)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.setLogRecordFactory(self.old_factory)