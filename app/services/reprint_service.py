"""
Reprint Service
Handles creation and management of reprint requests
"""

from app import db
from app.models import PrintRequest, User
from app.services import NotificationService
from datetime import datetime
import os


class ReprintService:
    """Service for creating and managing reprint requests"""
    
    @staticmethod
    def validate_reprint_eligibility(request_id, user_id=None):
        """
        Validate if a request can be reprinted
        
        Args:
            request_id: ID of the original request
            user_id: Optional user ID for authorization check
            
        Returns:
            tuple: (is_eligible, error_message, original_request)
        """
        try:
            # Get the original request
            original_request = PrintRequest.query.get(request_id)
            if not original_request:
                return False, "Original request not found", None
            
            # Check user authorization
            if user_id and original_request.user_id != user_id:
                # Allow admins to reprint any request
                user = User.query.get(user_id)
                if not user or not user.is_admin:
                    return False, "You don't have permission to reprint this request", None
            
            # Check if request can be reprinted
            if not original_request.can_be_reprinted():
                if original_request.status != 'completed':
                    return False, "Only completed requests can be reprinted", None
                else:
                    return False, "Document file no longer exists", None
            
            return True, None, original_request
            
        except Exception as e:
            return False, f"Error validating reprint eligibility: {str(e)}", None
    
    @staticmethod
    def get_reprint_form_data(original_request_id):
        """
        Get form data for reprint request
        
        Args:
            original_request_id: ID of the original request
            
        Returns:
            dict: Form data for pre-population
        """
        try:
            original_request = PrintRequest.query.get(original_request_id)
            if not original_request:
                return None
            
            return {
                'file_name': original_request.file_name,
                'number_of_pages': original_request.number_of_pages,
                'page_range': original_request.page_range,
                'number_of_copies': original_request.number_of_copies,
                'is_double_sided': original_request.is_double_sided,
                'is_color': original_request.print_format == 'color',
                'paper_size': original_request.paper_size,
                'is_stapled': original_request.is_stapled,
                'is_laminated': original_request.is_laminated,
                'clarifying_message': ''  # Clear message for new request
            }
            
        except Exception as e:
            print(f"Error getting reprint form data: {str(e)}")
            return None
    
    @staticmethod
    def create_reprint_request(original_request_id, user_id, form_data):
        """
        Create a new reprint request
        
        Args:
            original_request_id: ID of the original request
            user_id: ID of the user creating the reprint
            form_data: Dictionary containing form data
            
        Returns:
            tuple: (success, message, reprint_request)
        """
        try:
            # Validate eligibility
            is_eligible, error_message, original_request = ReprintService.validate_reprint_eligibility(
                original_request_id, user_id
            )
            
            if not is_eligible:
                return False, error_message, None
            
            # Generate unique request number
            request_number = PrintRequest.generate_request_number()
            
            # Create reprint request
            reprint_request = PrintRequest(
                request_number=request_number,
                user_id=user_id,
                file_path=original_request.file_path,  # Reuse same file
                file_name=original_request.file_name,
                number_of_pages=form_data.get('number_of_pages', original_request.number_of_pages),
                page_range=form_data.get('page_range', original_request.page_range),
                number_of_copies=form_data.get('number_of_copies', original_request.number_of_copies),
                is_double_sided=form_data.get('is_double_sided', original_request.is_double_sided),
                print_format='color' if form_data.get('is_color', False) else 'bw',
                paper_size=form_data.get('paper_size', original_request.paper_size),
                is_stapled=form_data.get('is_stapled', original_request.is_stapled),
                is_laminated=form_data.get('is_laminated', original_request.is_laminated),
                clarifying_message=form_data.get('clarifying_message', ''),
                status='pending',
                # Reprint-specific fields
                original_request_id=original_request_id,
                is_reprint=True
            )
            
            # Save to database
            db.session.add(reprint_request)
            
            # Increment reprint count on original request
            original_request.increment_reprint_count()
            
            # Commit changes
            db.session.commit()
            
            # Notify administrators about new reprint request
            try:
                NotificationService.notify_admins_new_request(reprint_request.id)
            except Exception as e:
                # Log error but don't fail the reprint creation
                print(f"Warning: Failed to notify admins about reprint request: {str(e)}")
            
            return True, f"Reprint request created successfully! Request number: {request_number}", reprint_request
            
        except Exception as e:
            db.session.rollback()
            error_msg = f"Error creating reprint request: {str(e)}"
            print(error_msg)
            return False, error_msg, None
    
    @staticmethod
    def get_reprint_history(original_request_id):
        """
        Get all reprint requests for an original request
        
        Args:
            original_request_id: ID of the original request
            
        Returns:
            list: List of reprint requests
        """
        try:
            reprints = PrintRequest.query.filter_by(
                original_request_id=original_request_id,
                is_reprint=True
            ).order_by(PrintRequest.submitted_at.desc()).all()
            
            return reprints
            
        except Exception as e:
            print(f"Error getting reprint history: {str(e)}")
            return []
    
    @staticmethod
    def get_user_reprints(user_id, limit=None):
        """
        Get all reprint requests by a user
        
        Args:
            user_id: ID of the user
            limit: Optional limit on number of results
            
        Returns:
            list: List of reprint requests
        """
        try:
            query = PrintRequest.query.filter_by(
                user_id=user_id,
                is_reprint=True
            ).order_by(PrintRequest.submitted_at.desc())
            
            if limit:
                query = query.limit(limit)
            
            return query.all()
            
        except Exception as e:
            print(f"Error getting user reprints: {str(e)}")
            return []