from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.forms import ProfileUpdateForm
from app.utils import save_profile_picture, delete_file, flash_form_errors
import os

bp = Blueprint('profile', __name__, url_prefix='/profile')


@bp.route('/')
@login_required
def view_profile():
    """View user profile"""
    # Get user statistics
    total_requests = current_user.print_requests.count()
    pending_requests = current_user.print_requests.filter_by(status='pending').count()
    completed_requests = current_user.print_requests.filter_by(status='completed').count()
    
    return render_template('profile/view.html', 
                         user=current_user,
                         total_requests=total_requests,
                         pending_requests=pending_requests,
                         completed_requests=completed_requests)


@bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile"""
    form = ProfileUpdateForm()
    
    if form.validate_on_submit():
        # Update name
        current_user.name = form.name.data
        
        # Handle profile picture upload
        if form.profile_picture.data:
            # Delete old profile picture if exists
            if current_user.profile_picture:
                delete_file(current_user.profile_picture)
            
            # Save new profile picture
            success, message, file_path = save_profile_picture(
                form.profile_picture.data, 
                current_user.id
            )
            
            if success:
                current_user.profile_picture = file_path
                flash('Profile picture updated successfully!', 'success')
            else:
                flash(message, 'error')
        
        # Save changes
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile.view_profile'))
    
    # Flash form errors if validation failed
    if form.errors:
        flash_form_errors(form)
    
    # Pre-fill form with current data
    if request.method == 'GET':
        form.name.data = current_user.name
    
    return render_template('profile/edit.html', form=form)


@bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password"""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate current password
        if not current_user.check_password(current_password):
            flash('Current password is incorrect.', 'error')
            return render_template('profile/change_password.html')
        
        # Validate new password
        if len(new_password) < 6:
            flash('New password must be at least 6 characters long.', 'error')
            return render_template('profile/change_password.html')
        
        # Validate password confirmation
        if new_password != confirm_password:
            flash('New passwords do not match.', 'error')
            return render_template('profile/change_password.html')
        
        # Update password
        current_user.set_password(new_password)
        db.session.commit()
        
        flash('Password changed successfully!', 'success')
        return redirect(url_for('profile.view_profile'))
    
    return render_template('profile/change_password.html')


@bp.route('/delete-picture', methods=['POST'])
@login_required
def delete_picture():
    """Delete profile picture"""
    if current_user.profile_picture:
        # Delete file from storage
        delete_file(current_user.profile_picture)
        
        # Remove from database
        current_user.profile_picture = None
        db.session.commit()
        
        flash('Profile picture deleted successfully.', 'success')
    else:
        flash('No profile picture to delete.', 'info')
    
    return redirect(url_for('profile.edit_profile'))
