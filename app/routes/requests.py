from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from app import db
from app.models import PrintRequest
from app.forms import PrintRequestForm
from app.utils import save_document, flash_form_errors, get_file_path
import os

bp = Blueprint('requests', __name__, url_prefix='/requests')


@bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard showing all print requests"""
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Show 10 requests per page
    
    # Get paginated requests for current user
    pagination = PrintRequest.query.filter_by(user_id=current_user.id)\
        .order_by(PrintRequest.submitted_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    requests = pagination.items
    
    # Get counts by status (all requests, not just current page)
    all_requests = PrintRequest.query.filter_by(user_id=current_user.id).all()
    pending_count = sum(1 for r in all_requests if r.status == 'pending')
    in_progress_count = sum(1 for r in all_requests if r.status == 'in_progress')
    completed_count = sum(1 for r in all_requests if r.status == 'completed')
    
    return render_template('requests/dashboard.html', 
                         requests=requests,
                         pagination=pagination,
                         pending_count=pending_count,
                         in_progress_count=in_progress_count,
                         completed_count=completed_count)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_request():
    """Create new print request"""
    form = PrintRequestForm()
    
    if form.validate_on_submit():
        # Handle file upload
        file = form.file.data
        success, message, file_path = save_document(file, current_user.id)
        
        if not success:
            flash(message, 'error')
            return render_template('requests/new_request.html', form=form)
        
        # Generate unique request number
        request_number = PrintRequest.generate_request_number()
        
        # Create print request
        print_request = PrintRequest(
            request_number=request_number,
            user_id=current_user.id,
            file_path=file_path,
            file_name=file.filename,
            number_of_pages=form.number_of_pages.data,
            page_range=form.page_range.data.strip() if form.page_range.data else None,
            number_of_copies=form.number_of_copies.data,
            is_double_sided=form.is_double_sided.data,
            print_format='color' if form.is_color.data else 'bw',
            paper_size=form.paper_size.data,
            is_stapled=form.is_stapled.data,
            is_laminated=form.is_laminated.data,
            clarifying_message=form.clarifying_message.data,
            status='pending'
        )
        
        # Save to database
        db.session.add(print_request)
        db.session.commit()
        
        flash(f'Print request submitted successfully! Request number: {request_number}', 'success')
        return redirect(url_for('requests.view_request', request_id=print_request.id))
    
    # Flash form errors if validation failed
    if form.errors:
        flash_form_errors(form)
    
    return render_template('requests/new_request.html', form=form)


@bp.route('/<int:request_id>')
@login_required
def view_request(request_id):
    """View specific print request"""
    # Get request and verify ownership
    print_request = PrintRequest.query.get_or_404(request_id)
    
    # Check if user owns this request or is admin
    if print_request.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to view this request.', 'error')
        return redirect(url_for('requests.dashboard'))
    
    return render_template('requests/view_request.html', request=print_request)


@bp.route('/<int:request_id>/cancel', methods=['POST'])
@login_required
def cancel_request(request_id):
    """Cancel a print request"""
    # Get request and verify ownership
    print_request = PrintRequest.query.get_or_404(request_id)
    
    # Check if user owns this request
    if print_request.user_id != current_user.id:
        flash('You do not have permission to cancel this request.', 'error')
        return redirect(url_for('requests.dashboard'))
    
    # Only allow cancellation of pending requests
    if print_request.status != 'pending':
        flash('Only pending requests can be cancelled.', 'warning')
        return redirect(url_for('requests.view_request', request_id=request_id))
    
    # Update status to cancelled
    print_request.update_status('cancelled')
    db.session.commit()
    
    flash('Print request cancelled successfully.', 'success')
    return redirect(url_for('requests.dashboard'))


@bp.route('/<int:request_id>/download')
@login_required
def download_file(request_id):
    """Download the file for a print request"""
    # Get request and verify ownership or admin
    print_request = PrintRequest.query.get_or_404(request_id)
    
    # Check if user owns this request or is admin
    if print_request.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to download this file.', 'error')
        return redirect(url_for('requests.dashboard'))
    
    # Get file path
    file_path = get_file_path(print_request.file_path)
    
    # Check if file exists
    if not os.path.exists(file_path):
        flash('File not found.', 'error')
        return redirect(url_for('requests.view_request', request_id=request_id))
    
    # Send file
    return send_file(
        file_path,
        as_attachment=True,
        download_name=print_request.file_name
    )


# Notification endpoints for web interface
@bp.route('/api/notifications/unread')
@login_required
def get_unread_notifications():
    """Get unread notifications for current user (web interface)"""
    from app.services import NotificationService
    from flask import jsonify
    
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


@bp.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Mark a notification as read (web interface)"""
    from app.services import NotificationService
    from flask import jsonify
    
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


@bp.route('/api/notifications/read-all', methods=['POST'])
@login_required
def mark_all_notifications_read():
    """Mark all notifications as read (web interface)"""
    from app.services import NotificationService
    from flask import jsonify
    
    try:
        count = NotificationService.mark_all_as_read(current_user.id)
        
        return jsonify({
            'message': f'{count} notifications marked as read',
            'count': count
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
