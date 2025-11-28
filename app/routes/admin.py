from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required
from app import db
from app.utils.decorators import admin_required
from app.models import PrintRequest, User
from app.utils import get_file_path
import os

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard overview"""
    # Get statistics
    total_requests = PrintRequest.query.count()
    pending_count = PrintRequest.query.filter_by(status='pending').count()
    in_progress_count = PrintRequest.query.filter_by(status='in_progress').count()
    completed_count = PrintRequest.query.filter_by(status='completed').count()
    total_users = User.query.filter_by(is_admin=False).count()
    
    # Get recent requests
    recent_requests = PrintRequest.query.order_by(PrintRequest.submitted_at.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html',
                         total_requests=total_requests,
                         pending_count=pending_count,
                         in_progress_count=in_progress_count,
                         completed_count=completed_count,
                         total_users=total_users,
                         recent_requests=recent_requests)


@bp.route('/requests')
@login_required
@admin_required
def admin_requests():
    """Admin view of all print requests"""
    # Get filter from query params
    status_filter = request.args.get('status', 'all')
    
    # Base query
    query = PrintRequest.query
    
    # Apply filter
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    # Get all requests
    all_requests = query.order_by(PrintRequest.submitted_at.desc()).all()
    
    # Group by status for display
    pending = [r for r in all_requests if r.status == 'pending']
    in_progress = [r for r in all_requests if r.status == 'in_progress']
    completed = [r for r in all_requests if r.status == 'completed']
    cancelled = [r for r in all_requests if r.status == 'cancelled']
    
    return render_template('admin/requests.html',
                         all_requests=all_requests,
                         pending=pending,
                         in_progress=in_progress,
                         completed=completed,
                         cancelled=cancelled,
                         status_filter=status_filter)


@bp.route('/request/<int:request_id>')
@login_required
@admin_required
def view_request(request_id):
    """Admin view of specific request"""
    from app.forms import StatusUpdateForm
    print_request = PrintRequest.query.get_or_404(request_id)
    form = StatusUpdateForm()
    form.status.data = print_request.status
    return render_template('admin/view_request.html', request=print_request, form=form)


@bp.route('/request/<int:request_id>/status', methods=['POST'])
@login_required
@admin_required
def update_status(request_id):
    """Update request status"""
    from app.utils.email import send_status_update_email
    
    print_request = PrintRequest.query.get_or_404(request_id)
    
    # Get new status from form
    new_status = request.form.get('status')
    admin_notes = request.form.get('admin_notes', '').strip()
    
    # Validate status
    valid_statuses = ['pending', 'in_progress', 'completed', 'cancelled']
    if new_status not in valid_statuses:
        flash('Invalid status selected.', 'error')
        return redirect(url_for('admin.view_request', request_id=request_id))
    
    # Update status
    old_status = print_request.status
    print_request.update_status(new_status)
    
    # Update admin notes if provided
    if admin_notes:
        print_request.admin_notes = admin_notes
    
    db.session.commit()
    
    # Send email notification to user
    try:
        send_status_update_email(print_request.user, print_request, old_status, new_status)
        flash(f'Request status updated from "{old_status}" to "{new_status}". Email notification sent to {print_request.user.name}.', 'success')
    except Exception as e:
        flash(f'Request status updated from "{old_status}" to "{new_status}". Warning: Email notification failed.', 'warning')
        print(f'Email error: {str(e)}')
    
    # Redirect based on referrer
    if request.referrer and 'admin/requests' in request.referrer:
        return redirect(url_for('admin.admin_requests'))
    return redirect(url_for('admin.view_request', request_id=request_id))


@bp.route('/request/<int:request_id>/download')
@login_required
@admin_required
def download_file(request_id):
    """Download request file"""
    print_request = PrintRequest.query.get_or_404(request_id)
    
    # Get file path
    file_path = get_file_path(print_request.file_path)
    
    # Check if file exists
    if not os.path.exists(file_path):
        flash('File not found.', 'error')
        return redirect(url_for('admin.view_request', request_id=request_id))
    
    # Send file
    return send_file(
        file_path,
        as_attachment=True,
        download_name=print_request.file_name
    )


@bp.route('/users')
@login_required
@admin_required
def users():
    """View all users"""
    all_users = User.query.filter_by(is_admin=False).order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=all_users)


@bp.route('/user/<int:user_id>')
@login_required
@admin_required
def view_user(user_id):
    """View specific user and their requests"""
    user = User.query.get_or_404(user_id)
    user_requests = PrintRequest.query.filter_by(user_id=user_id)\
        .order_by(PrintRequest.submitted_at.desc()).all()
    
    return render_template('admin/view_user.html', user=user, requests=user_requests)
