from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app.models import User, PrintRequest
from app.utils.decorators import admin_required
from sqlalchemy import func

bp = Blueprint('reports', __name__, url_prefix='/reports')


@bp.route('/my-report')
@login_required
def my_report():
    """User's personal print report"""
    # Get user's print requests
    requests = PrintRequest.query.filter_by(user_id=current_user.id).all()
    
    # Calculate statistics
    total_requests = len(requests)
    total_pages = sum(r.number_of_pages * r.number_of_copies for r in requests)
    total_documents = len(requests)
    
    # Count by status
    pending = sum(1 for r in requests if r.status == 'pending')
    in_progress = sum(1 for r in requests if r.status == 'in_progress')
    completed = sum(1 for r in requests if r.status == 'completed')
    cancelled = sum(1 for r in requests if r.status == 'cancelled')
    
    # Count by format
    color_pages = sum(r.number_of_pages * r.number_of_copies for r in requests if r.print_format == 'color')
    bw_pages = sum(r.number_of_pages * r.number_of_copies for r in requests if r.print_format == 'bw')
    
    # Count double-sided
    double_sided_pages = sum(r.number_of_pages * r.number_of_copies for r in requests if r.is_double_sided)
    single_sided_pages = sum(r.number_of_pages * r.number_of_copies for r in requests if not r.is_double_sided)
    
    return render_template('reports/my_report.html',
                         requests=requests,
                         total_requests=total_requests,
                         total_pages=total_pages,
                         total_documents=total_documents,
                         pending=pending,
                         in_progress=in_progress,
                         completed=completed,
                         cancelled=cancelled,
                         color_pages=color_pages,
                         bw_pages=bw_pages,
                         double_sided_pages=double_sided_pages,
                         single_sided_pages=single_sided_pages)


@bp.route('/admin-report')
@login_required
@admin_required
def admin_report():
    """Admin report showing all users' print statistics"""
    # Get all users (excluding admins)
    users = User.query.filter_by(is_admin=False).all()
    
    # Calculate stats for each user
    user_stats = []
    for user in users:
        requests = PrintRequest.query.filter_by(user_id=user.id).all()
        
        total_requests = len(requests)
        total_pages = sum(r.number_of_pages * r.number_of_copies for r in requests)
        total_documents = len(requests)
        
        # Count by status
        completed = sum(1 for r in requests if r.status == 'completed')
        pending = sum(1 for r in requests if r.status == 'pending')
        
        # Count by format
        color_pages = sum(r.number_of_pages * r.number_of_copies for r in requests if r.print_format == 'color')
        bw_pages = sum(r.number_of_pages * r.number_of_copies for r in requests if r.print_format == 'bw')
        
        user_stats.append({
            'user': user,
            'total_requests': total_requests,
            'total_pages': total_pages,
            'total_documents': total_documents,
            'completed': completed,
            'pending': pending,
            'color_pages': color_pages,
            'bw_pages': bw_pages,
            'credit_balance': user.print_credit
        })
    
    # Sort by total pages (highest first)
    user_stats.sort(key=lambda x: x['total_pages'], reverse=True)
    
    # Calculate overall statistics
    total_users = len(users)
    total_all_requests = sum(s['total_requests'] for s in user_stats)
    total_all_pages = sum(s['total_pages'] for s in user_stats)
    total_all_documents = sum(s['total_documents'] for s in user_stats)
    total_color_pages = sum(s['color_pages'] for s in user_stats)
    total_bw_pages = sum(s['bw_pages'] for s in user_stats)
    
    return render_template('reports/admin_report.html',
                         user_stats=user_stats,
                         total_users=total_users,
                         total_all_requests=total_all_requests,
                         total_all_pages=total_all_pages,
                         total_all_documents=total_all_documents,
                         total_color_pages=total_color_pages,
                         total_bw_pages=total_bw_pages)
