"""
Notification Service
Handles creation and management of user notifications
"""

from app import db
from app.models import Notification, PrintRequest
from datetime import datetime
from sqlalchemy import and_


class NotificationService:
    """Service for creating and managing notifications"""
    
    @staticmethod
    def create_status_notification(user_id, request_id, old_status, new_status):
        """
        Create notification when print request status changes
        
        Args:
            user_id: ID of the user to notify
            request_id: ID of the print request
            old_status: Previous status
            new_status: New status
            
        Returns:
            Notification object or None if creation fails
        """
        try:
            # Check for duplicate notification
            existing = Notification.query.filter(
                and_(
                    Notification.user_id == user_id,
                    Notification.request_id == request_id,
                    Notification.status == new_status
                )
            ).first()
            
            if existing:
                return existing
            
            # Get request details for message
            request = PrintRequest.query.get(request_id)
            if not request:
                return None
            
            # Create notification message
            message = NotificationService._create_message(request.request_number, new_status)
            
            # Create notification
            notification = Notification(
                user_id=user_id,
                request_id=request_id,
                message=message,
                notification_type='status_change',
                status=new_status,
                is_read=False,
                created_at=datetime.utcnow()
            )
            
            db.session.add(notification)
            db.session.commit()
            
            return notification
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creating notification: {str(e)}")
            return None
    
    @staticmethod
    def _create_message(request_number, status):
        """Create notification message based on status"""
        messages = {
            'pending': f'Your print request {request_number} is pending review.',
            'in_progress': f'Your print request {request_number} is now in progress.',
            'processing': f'Your print request {request_number} is being processed.',
            'completed': f'Your print request {request_number} is completed and ready for pickup!',
            'cancelled': f'Your print request {request_number} has been cancelled.'
        }
        return messages.get(status, f'Your print request {request_number} status has been updated to {status}.')
    
    @staticmethod
    def get_unread_notifications(user_id, limit=10):
        """
        Get unread notifications for user
        
        Args:
            user_id: ID of the user
            limit: Maximum number of notifications to return
            
        Returns:
            List of Notification objects
        """
        try:
            notifications = Notification.query.filter_by(
                user_id=user_id,
                is_read=False
            ).order_by(
                Notification.created_at.desc()
            ).limit(limit).all()
            
            return notifications
            
        except Exception as e:
            print(f"Error fetching notifications: {str(e)}")
            return []
    
    @staticmethod
    def get_all_notifications(user_id, limit=50):
        """
        Get all notifications for user (read and unread)
        
        Args:
            user_id: ID of the user
            limit: Maximum number of notifications to return
            
        Returns:
            List of Notification objects
        """
        try:
            notifications = Notification.query.filter_by(
                user_id=user_id
            ).order_by(
                Notification.created_at.desc()
            ).limit(limit).all()
            
            return notifications
            
        except Exception as e:
            print(f"Error fetching notifications: {str(e)}")
            return []
    
    @staticmethod
    def mark_as_read(notification_id, user_id=None):
        """
        Mark notification as read
        
        Args:
            notification_id: ID of the notification
            user_id: Optional user ID for authorization check
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            notification = Notification.query.get(notification_id)
            
            if not notification:
                return False
            
            # Verify user owns this notification
            if user_id and notification.user_id != user_id:
                return False
            
            notification.mark_as_read()
            db.session.commit()
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Error marking notification as read: {str(e)}")
            return False
    
    @staticmethod
    def mark_all_as_read(user_id):
        """
        Mark all notifications as read for a user
        
        Args:
            user_id: ID of the user
            
        Returns:
            int: Number of notifications marked as read
        """
        try:
            count = Notification.query.filter_by(
                user_id=user_id,
                is_read=False
            ).update({'is_read': True})
            
            db.session.commit()
            return count
            
        except Exception as e:
            db.session.rollback()
            print(f"Error marking all notifications as read: {str(e)}")
            return 0
    
    @staticmethod
    def get_unread_count(user_id):
        """
        Get count of unread notifications
        
        Args:
            user_id: ID of the user
            
        Returns:
            int: Count of unread notifications
        """
        try:
            count = Notification.query.filter_by(
                user_id=user_id,
                is_read=False
            ).count()
            
            return count
            
        except Exception as e:
            print(f"Error getting unread count: {str(e)}")
            return 0
    
    @staticmethod
    def delete_notification(notification_id, user_id=None):
        """
        Delete a notification
        
        Args:
            notification_id: ID of the notification
            user_id: Optional user ID for authorization check
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            notification = Notification.query.get(notification_id)
            
            if not notification:
                return False
            
            # Verify user owns this notification
            if user_id and notification.user_id != user_id:
                return False
            
            db.session.delete(notification)
            db.session.commit()
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting notification: {str(e)}")
            return False

    
    @staticmethod
    def notify_admins_new_request(request_id):
        """
        Notify all admins when a new print request is submitted
        
        Args:
            request_id: ID of the new print request
            
        Returns:
            int: Number of admins notified
        """
        try:
            from app.models import User
            
            # Get the request
            request = PrintRequest.query.get(request_id)
            if not request:
                return 0
            
            # Get all admin users
            admins = User.query.filter_by(is_admin=True).all()
            
            count = 0
            for admin in admins:
                # Create notification message based on request type
                if request.is_reprint:
                    original_number = request.original_request.request_number if request.original_request else "Unknown"
                    message = f'New reprint request {request.request_number} (original: {original_number}) submitted by {request.user.name}'
                else:
                    message = f'New print request {request.request_number} submitted by {request.user.name}'
                
                # Create notification
                notification = Notification(
                    user_id=admin.id,
                    request_id=request_id,
                    message=message,
                    notification_type='new_request',
                    status='pending',
                    is_read=False,
                    created_at=datetime.utcnow()
                )
                
                db.session.add(notification)
                count += 1
            
            db.session.commit()
            return count
            
        except Exception as e:
            db.session.rollback()
            print(f"Error notifying admins: {str(e)}")
            return 0
