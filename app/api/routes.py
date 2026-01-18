from flask import jsonify, request
from app.api import bp
from app.models import User, PrintRequest, Notification
from app import db
from app.api.auth import token_required
from app.services import NotificationService
from datetime import datetime


@bp.route('/health', methods=['GET'])
def health_check():
    """API health check"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    })


@bp.route('/users', methods=['GET'])
@token_required
def get_users(current_user):
    """Get all users (admin only)"""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    users = User.query.all()
    return jsonify({
        'users': [{
            'id': u.id,
            'name': u.name,
            'email': u.email,
            'department': u.faculty_department,
            'is_admin': u.is_admin
        } for u in users]
    })


@bp.route('/users/<int:user_id>', methods=['GET'])
@token_required
def get_user(current_user, user_id):
    """Get specific user"""
    if not current_user.is_admin and current_user.id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get_or_404(user_id)
    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'department': user.faculty_department,
        'is_admin': user.is_admin,
        'created_at': user.created_at.isoformat()
    })


@bp.route('/requests', methods=['GET'])
@token_required
def get_requests(current_user):
    """Get print requests"""
    if current_user.is_admin:
        requests = PrintRequest.query.order_by(PrintRequest.submitted_at.desc()).all()
    else:
        requests = current_user.print_requests.order_by(PrintRequest.submitted_at.desc()).all()
    
    return jsonify({
        'requests': [{
            'id': r.id,
            'request_number': r.request_number,
            'document_name': r.document_name,
            'pages': r.number_of_pages,
            'copies': r.number_of_copies,
            'status': r.status,
            'submitted_at': r.submitted_at.isoformat()
        } for r in requests]
    })


@bp.route('/requests/<int:request_id>', methods=['GET'])
@token_required
def get_request(current_user, request_id):
    """Get specific print request"""
    print_request = PrintRequest.query.get_or_404(request_id)
    
    if not current_user.is_admin and print_request.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({
        'id': print_request.id,
        'request_number': print_request.request_number,
        'document_name': print_request.document_name,
        'pages': print_request.number_of_pages,
        'copies': print_request.number_of_copies,
        'color': print_request.print_format == 'color',
        'double_sided': print_request.is_double_sided,
        'status': print_request.status,
        'submitted_at': print_request.submitted_at.isoformat(),
        'user': {
            'id': print_request.user.id,
            'name': print_request.user.name,
            'email': print_request.user.email
        }
    })


@bp.route('/stats', methods=['GET'])
@token_required
def get_stats(current_user):
    """Get statistics"""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    total_users = User.query.filter_by(is_admin=False).count()
    total_requests = PrintRequest.query.count()
    pending_requests = PrintRequest.query.filter_by(status='pending').count()
    completed_requests = PrintRequest.query.filter_by(status='completed').count()
    
    return jsonify({
        'total_users': total_users,
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'completed_requests': completed_requests
    })


@bp.route('/notifications/unread', methods=['GET'])
@token_required
def get_unread_notifications(current_user):
    """Get unread notifications for current user"""
    try:
        limit = request.args.get('limit', 10, type=int)
        notifications = NotificationService.get_unread_notifications(current_user.id, limit=limit)
        
        return jsonify({
            'notifications': [{
                'id': n.id,
                'message': n.message,
                'status': n.status,
                'request_number': n.print_request.request_number,
                'request_id': n.request_id,
                'created_at': n.created_at.isoformat(),
                'is_read': n.is_read
            } for n in notifications],
            'count': len(notifications)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/notifications', methods=['GET'])
@token_required
def get_all_notifications(current_user):
    """Get all notifications for current user"""
    try:
        limit = request.args.get('limit', 50, type=int)
        notifications = NotificationService.get_all_notifications(current_user.id, limit=limit)
        
        return jsonify({
            'notifications': [{
                'id': n.id,
                'message': n.message,
                'status': n.status,
                'request_number': n.print_request.request_number,
                'request_id': n.request_id,
                'created_at': n.created_at.isoformat(),
                'is_read': n.is_read
            } for n in notifications],
            'count': len(notifications)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@token_required
def mark_notification_read(current_user, notification_id):
    """Mark a notification as read"""
    try:
        success = NotificationService.mark_as_read(notification_id, current_user.id)
        
        if success:
            return jsonify({
                'message': 'Notification marked as read',
                'notification_id': notification_id
            })
        else:
            return jsonify({'error': 'Notification not found or unauthorized'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/notifications/read-all', methods=['POST'])
@token_required
def mark_all_notifications_read(current_user):
    """Mark all notifications as read for current user"""
    try:
        count = NotificationService.mark_all_as_read(current_user.id)
        
        return jsonify({
            'message': f'{count} notifications marked as read',
            'count': count
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/notifications/count', methods=['GET'])
@token_required
def get_notification_count(current_user):
    """Get unread notification count"""
    try:
        count = NotificationService.get_unread_count(current_user.id)
        
        return jsonify({
            'unread_count': count
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/notifications/<int:notification_id>', methods=['DELETE'])
@token_required
def delete_notification(current_user, notification_id):
    """Delete a notification"""
    try:
        success = NotificationService.delete_notification(notification_id, current_user.id)
        
        if success:
            return jsonify({
                'message': 'Notification deleted',
                'notification_id': notification_id
            })
        else:
            return jsonify({'error': 'Notification not found or unauthorized'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
