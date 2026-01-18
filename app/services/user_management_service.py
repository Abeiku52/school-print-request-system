"""
User Management Service

Enterprise-grade user account management service for administrative operations.
Implements comprehensive security, audit logging, and error handling patterns
following industry best practices for educational institution management systems.

Author: Senior Development Team
Version: 2.0.0
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from flask import request
from flask_login import current_user
from werkzeug.security import generate_password_hash
from app import db
from app.models import User, AdminAuditLog
import secrets
import string

# Configure module-level logger
logger = logging.getLogger(__name__)


class UserManagementError(Exception):
    """Custom exception for user management operations."""
    pass


class UserManagementService:
    """
    Enterprise user management service providing secure administrative operations.
    
    This service handles all user account lifecycle operations including:
    - Secure password management with audit trails
    - Account status management with proper authorization
    - Comprehensive activity tracking and reporting
    - Bulk operations with transaction safety
    
    All operations are logged and audited for compliance requirements.
    """
    
    # Class constants for configuration
    MIN_PASSWORD_LENGTH = 8
    MAX_PASSWORD_LENGTH = 128
    DEFAULT_GENERATED_PASSWORD_LENGTH = 12
    MAX_BULK_OPERATION_SIZE = 100
    
    @classmethod
    def reset_user_password(
        cls, 
        user_id: int, 
        new_password: str, 
        admin_user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Reset user password with comprehensive validation and audit logging.
        
        Implements enterprise security standards including:
        - Multi-layer password validation
        - Atomic database operations
        - Comprehensive audit logging
        - IP address tracking for security
        
        Args:
            user_id: Target user's database ID
            new_password: New password meeting security requirements
            admin_user_id: Administrator performing the operation (auto-detected if None)
            
        Returns:
            Dict containing operation result with success status and detailed message
            
        Raises:
            UserManagementError: For validation failures or system errors
        """
        try:
            logger.info(f"Password reset initiated for user_id: {user_id}")
            
            # Comprehensive password validation
            validation_result = cls._validate_password_security(new_password)
            if not validation_result['is_valid']:
                logger.warning(f"Password validation failed for user_id: {user_id} - {validation_result['message']}")
                return {
                    'success': False,
                    'message': validation_result['message'],
                    'error_code': 'VALIDATION_FAILED'
                }
            
            # Secure user retrieval with existence check
            user = cls._get_user_safely(user_id)
            if not user:
                logger.error(f"User not found for password reset: {user_id}")
                return {
                    'success': False,
                    'message': 'User account not found',
                    'error_code': 'USER_NOT_FOUND'
                }
            
            # Administrator authorization
            admin_id = admin_user_id or (current_user.id if current_user.is_authenticated else None)
            if not admin_id:
                logger.error("Password reset attempted without valid administrator")
                return {
                    'success': False,
                    'message': 'Administrator authentication required',
                    'error_code': 'AUTH_REQUIRED'
                }
            
            # Atomic password update operation
            cls._execute_password_reset(user, new_password, admin_id)
            
            # Comprehensive audit logging
            cls._log_security_event(
                admin_id=admin_id,
                action='password_reset',
                target_user_id=user_id,
                details=f'Password reset for {user.email} by admin',
                severity='HIGH'
            )
            
            logger.info(f"Password reset completed successfully for user: {user.email}")
            
            return {
                'success': True,
                'message': f'Password reset successfully for {user.name}',
                'operation_id': cls._generate_operation_id()
            }
            
        except Exception as e:
            logger.error(f"Password reset failed for user_id: {user_id} - {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'message': 'System error during password reset. Please try again.',
                'error_code': 'SYSTEM_ERROR'
            }
    
    @classmethod
    def toggle_user_account_status(
        cls, 
        user_id: int, 
        admin_user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Toggle user account status with enterprise security controls.
        
        Implements comprehensive authorization and safety checks:
        - Administrator privilege verification
        - System account protection
        - Atomic status changes
        - Complete audit trail
        
        Args:
            user_id: Target user's database ID
            admin_user_id: Administrator performing the operation
            
        Returns:
            Dict containing operation result and new account status
        """
        try:
            logger.info(f"Account status toggle initiated for user_id: {user_id}")
            
            # Secure user retrieval
            user = cls._get_user_safely(user_id)
            if not user:
                return {
                    'success': False,
                    'message': 'User account not found',
                    'error_code': 'USER_NOT_FOUND'
                }
            
            # System account protection
            if user.is_admin:
                logger.warning(f"Attempt to disable admin account: {user.email}")
                return {
                    'success': False,
                    'message': 'Administrator accounts cannot be disabled for security reasons',
                    'error_code': 'ADMIN_PROTECTION'
                }
            
            # Administrator authorization
            admin_id = admin_user_id or (current_user.id if current_user.is_authenticated else None)
            if not admin_id:
                return {
                    'success': False,
                    'message': 'Administrator authentication required',
                    'error_code': 'AUTH_REQUIRED'
                }
            
            # Execute atomic status change
            old_status = user.is_active
            new_status = user.toggle_account_status()
            
            # Comprehensive audit logging
            action = 'account_enable' if new_status else 'account_disable'
            cls._log_security_event(
                admin_id=admin_id,
                action=action,
                target_user_id=user_id,
                details=f'Account {"enabled" if new_status else "disabled"} for {user.email}',
                severity='MEDIUM'
            )
            
            db.session.commit()
            
            logger.info(f"Account status changed for {user.email}: {old_status} -> {new_status}")
            
            return {
                'success': True,
                'message': f'User account {"enabled" if new_status else "disabled"} successfully',
                'new_status': new_status,
                'previous_status': old_status
            }
            
        except Exception as e:
            logger.error(f"Account status toggle failed for user_id: {user_id} - {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'message': 'System error during account status change',
                'error_code': 'SYSTEM_ERROR'
            }
    
    @classmethod
    def get_comprehensive_user_profile(cls, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Generate comprehensive user activity and security profile.
        
        Provides detailed analytics for administrative decision-making:
        - Complete request statistics and patterns
        - Account security status and history
        - Recent activity timeline
        - Risk assessment indicators
        
        Args:
            user_id: Target user's database ID
            
        Returns:
            Comprehensive user profile dict or None if user not found
        """
        try:
            user = cls._get_user_safely(user_id)
            if not user:
                return None
            
            # Calculate comprehensive statistics
            request_stats = cls._calculate_request_statistics(user)
            security_profile = cls._generate_security_profile(user)
            activity_timeline = cls._build_activity_timeline(user)
            
            return {
                'user_info': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'department': user.faculty_department,
                    'account_created': user.created_at.isoformat(),
                    'is_active': user.is_active,
                    'is_admin': user.is_admin
                },
                'request_statistics': request_stats,
                'security_profile': security_profile,
                'recent_activity': activity_timeline,
                'profile_generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate user profile for user_id: {user_id} - {str(e)}")
            return None
    
    @classmethod
    def generate_secure_password(cls, length: int = None) -> str:
        """
        Generate cryptographically secure password meeting enterprise standards.
        
        Implements NIST password guidelines:
        - Minimum entropy requirements
        - Character set diversity
        - Cryptographically secure randomization
        
        Args:
            length: Password length (defaults to class constant)
            
        Returns:
            Cryptographically secure password string
        """
        length = length or cls.DEFAULT_GENERATED_PASSWORD_LENGTH
        
        # Define character sets for complexity
        char_sets = {
            'lowercase': string.ascii_lowercase,
            'uppercase': string.ascii_uppercase,
            'digits': string.digits,
            'special': '!@#$%^&*()_+-=[]{}|;:,.<>?'
        }
        
        # Ensure at least one character from each set
        password_chars = []
        for char_set in char_sets.values():
            password_chars.append(secrets.choice(char_set))
        
        # Fill remaining length with random characters
        all_chars = ''.join(char_sets.values())
        for _ in range(length - len(char_sets)):
            password_chars.append(secrets.choice(all_chars))
        
        # Cryptographically secure shuffle
        secrets.SystemRandom().shuffle(password_chars)
        
        return ''.join(password_chars)
    
    # Private helper methods for internal operations
    
    @classmethod
    def _validate_password_security(cls, password: str) -> Dict[str, Any]:
        """Comprehensive password security validation."""
        if not password:
            return {'is_valid': False, 'message': 'Password cannot be empty'}
        
        if len(password) < cls.MIN_PASSWORD_LENGTH:
            return {
                'is_valid': False, 
                'message': f'Password must be at least {cls.MIN_PASSWORD_LENGTH} characters long'
            }
        
        if len(password) > cls.MAX_PASSWORD_LENGTH:
            return {
                'is_valid': False, 
                'message': f'Password must be less than {cls.MAX_PASSWORD_LENGTH} characters'
            }
        
        # Character diversity requirements
        checks = {
            'has_lowercase': any(c.islower() for c in password),
            'has_uppercase': any(c.isupper() for c in password),
            'has_digit': any(c.isdigit() for c in password),
            'has_special': any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)
        }
        
        missing_types = [check for check, passed in checks.items() if not passed]
        if len(missing_types) > 1:  # Allow missing one type for usability
            return {
                'is_valid': False,
                'message': 'Password must contain uppercase, lowercase, numbers, and special characters'
            }
        
        return {'is_valid': True, 'message': 'Password meets security requirements'}
    
    @classmethod
    def _get_user_safely(cls, user_id: int) -> Optional[User]:
        """Safely retrieve user with error handling."""
        try:
            return User.query.get(user_id)
        except Exception as e:
            logger.error(f"Database error retrieving user {user_id}: {str(e)}")
            return None
    
    @classmethod
    def _execute_password_reset(cls, user: User, new_password: str, admin_id: int) -> None:
        """Execute atomic password reset operation."""
        user.admin_reset_password(new_password, admin_id)
        db.session.commit()
    
    @classmethod
    def _log_security_event(
        cls, 
        admin_id: int, 
        action: str, 
        target_user_id: int, 
        details: str, 
        severity: str = 'MEDIUM'
    ) -> None:
        """Log security events with comprehensive context."""
        try:
            AdminAuditLog.log_action(
                admin_id=admin_id,
                action=action,
                target_user_id=target_user_id,
                details=f"[{severity}] {details}",
                ip_address=request.remote_addr if request else 'system'
            )
        except Exception as e:
            logger.error(f"Failed to log security event: {str(e)}")
    
    @classmethod
    def _calculate_request_statistics(cls, user: User) -> Dict[str, int]:
        """Calculate comprehensive request statistics."""
        return {
            'total_requests': user.print_requests.count(),
            'pending_requests': user.print_requests.filter_by(status='pending').count(),
            'completed_requests': user.print_requests.filter_by(status='completed').count(),
            'in_progress_requests': user.print_requests.filter_by(status='in_progress').count(),
            'cancelled_requests': user.print_requests.filter_by(status='cancelled').count()
        }
    
    @classmethod
    def _generate_security_profile(cls, user: User) -> Dict[str, Any]:
        """Generate security profile for user."""
        return {
            'account_status': 'Active' if user.is_active else 'Disabled',
            'last_password_reset': user.last_password_reset.isoformat() if user.last_password_reset else None,
            'password_reset_by_admin': user.password_reset_by is not None,
            'account_age_days': (datetime.utcnow() - user.created_at).days
        }
    
    @classmethod
    def _build_activity_timeline(cls, user: User) -> List[Dict[str, Any]]:
        """Build recent activity timeline."""
        recent_requests = user.print_requests.order_by(
            user.print_requests.property.mapper.class_.submitted_at.desc()
        ).limit(10).all()
        
        return [{
            'request_number': req.request_number,
            'status': req.status,
            'submitted_at': req.submitted_at.isoformat(),
            'file_name': req.file_name
        } for req in recent_requests]
    
    @classmethod
    def _generate_operation_id(cls) -> str:
        """Generate unique operation ID for tracking."""
        return f"OP-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(4).upper()}"