"""
Custom Exception Classes for School Print Request System

Enterprise-grade exception handling providing structured error management
with proper logging, user-friendly messages, and debugging information.

Author: Senior Development Team
Version: 2.0.0
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class PrintSystemError(Exception):
    """
    Base exception class for all print system errors.
    
    Provides structured error handling with:
    - User-friendly error messages
    - Technical details for debugging
    - Error categorization and severity levels
    - Automatic logging integration
    """
    
    def __init__(
        self, 
        message: str, 
        error_code: str = None, 
        details: Dict[str, Any] = None,
        severity: str = 'ERROR'
    ):
        self.message = message
        self.error_code = error_code or self.__class__.__name__.upper()
        self.details = details or {}
        self.severity = severity
        self.timestamp = datetime.utcnow()
        
        # Log the error automatically
        self._log_error()
        
        super().__init__(self.message)
    
    def _log_error(self):
        """Log error with appropriate severity level."""
        log_message = f"[{self.error_code}] {self.message}"
        if self.details:
            log_message += f" | Details: {self.details}"
        
        if self.severity == 'CRITICAL':
            logger.critical(log_message)
        elif self.severity == 'ERROR':
            logger.error(log_message)
        elif self.severity == 'WARNING':
            logger.warning(log_message)
        else:
            logger.info(log_message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            'error': True,
            'error_code': self.error_code,
            'message': self.message,
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }


class ValidationError(PrintSystemError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: str = None, value: Any = None):
        details = {}
        if field:
            details['field'] = field
        if value is not None:
            details['invalid_value'] = str(value)
        
        super().__init__(
            message=message,
            error_code='VALIDATION_ERROR',
            details=details,
            severity='WARNING'
        )


class AuthenticationError(PrintSystemError):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication required", user_id: int = None):
        details = {}
        if user_id:
            details['user_id'] = user_id
        
        super().__init__(
            message=message,
            error_code='AUTH_ERROR',
            details=details,
            severity='WARNING'
        )


class AuthorizationError(PrintSystemError):
    """Raised when user lacks required permissions."""
    
    def __init__(self, message: str = "Insufficient permissions", required_role: str = None):
        details = {}
        if required_role:
            details['required_role'] = required_role
        
        super().__init__(
            message=message,
            error_code='AUTHORIZATION_ERROR',
            details=details,
            severity='WARNING'
        )


class ResourceNotFoundError(PrintSystemError):
    """Raised when requested resource doesn't exist."""
    
    def __init__(self, resource_type: str, resource_id: Any = None):
        message = f"{resource_type} not found"
        details = {'resource_type': resource_type}
        
        if resource_id is not None:
            message += f" with ID: {resource_id}"
            details['resource_id'] = str(resource_id)
        
        super().__init__(
            message=message,
            error_code='RESOURCE_NOT_FOUND',
            details=details,
            severity='WARNING'
        )


class BusinessLogicError(PrintSystemError):
    """Raised when business rules are violated."""
    
    def __init__(self, message: str, rule: str = None, context: Dict[str, Any] = None):
        details = context or {}
        if rule:
            details['violated_rule'] = rule
        
        super().__init__(
            message=message,
            error_code='BUSINESS_LOGIC_ERROR',
            details=details,
            severity='WARNING'
        )


class SystemError(PrintSystemError):
    """Raised for internal system errors."""
    
    def __init__(self, message: str = "Internal system error", operation: str = None):
        details = {}
        if operation:
            details['failed_operation'] = operation
        
        super().__init__(
            message=message,
            error_code='SYSTEM_ERROR',
            details=details,
            severity='ERROR'
        )


class DatabaseError(PrintSystemError):
    """Raised for database operation failures."""
    
    def __init__(self, message: str = "Database operation failed", query: str = None):
        details = {}
        if query:
            details['failed_query'] = query
        
        super().__init__(
            message=message,
            error_code='DATABASE_ERROR',
            details=details,
            severity='ERROR'
        )


class FileOperationError(PrintSystemError):
    """Raised for file system operation failures."""
    
    def __init__(self, message: str, file_path: str = None, operation: str = None):
        details = {}
        if file_path:
            details['file_path'] = file_path
        if operation:
            details['operation'] = operation
        
        super().__init__(
            message=message,
            error_code='FILE_OPERATION_ERROR',
            details=details,
            severity='ERROR'
        )


class ConfigurationError(PrintSystemError):
    """Raised for configuration-related errors."""
    
    def __init__(self, message: str, config_key: str = None):
        details = {}
        if config_key:
            details['config_key'] = config_key
        
        super().__init__(
            message=message,
            error_code='CONFIGURATION_ERROR',
            details=details,
            severity='CRITICAL'
        )


# Utility functions for error handling

def handle_database_error(func):
    """Decorator to handle database errors gracefully."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            raise DatabaseError(
                message=f"Database operation failed: {str(e)}",
                query=getattr(e, 'statement', None)
            )
    return wrapper


def handle_file_operation_error(func):
    """Decorator to handle file operation errors gracefully."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (IOError, OSError) as e:
            raise FileOperationError(
                message=f"File operation failed: {str(e)}",
                file_path=getattr(e, 'filename', None),
                operation=func.__name__
            )
    return wrapper


def create_error_response(error: PrintSystemError, status_code: int = 400) -> tuple:
    """
    Create standardized error response for API endpoints.
    
    Args:
        error: PrintSystemError instance
        status_code: HTTP status code
        
    Returns:
        Tuple of (response_dict, status_code)
    """
    return error.to_dict(), status_code


def log_and_suppress_error(error: Exception, default_return=None, operation: str = None):
    """
    Log error and return default value instead of raising.
    
    Useful for non-critical operations where graceful degradation is preferred.
    """
    if isinstance(error, PrintSystemError):
        # Already logged by the exception itself
        pass
    else:
        logger.error(f"Suppressed error in {operation or 'unknown operation'}: {str(error)}")
    
    return default_return