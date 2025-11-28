"""
Template helper functions
"""
from flask import url_for
import os


def get_profile_picture_url(user):
    """
    Get URL for user's profile picture
    
    Args:
        user: User object
    
    Returns:
        str: URL to profile picture or default avatar
    """
    if user.profile_picture:
        # Return URL to uploaded profile picture
        return url_for('static', filename=f'uploads/{user.profile_picture}')
    else:
        # Return default avatar
        return url_for('static', filename='images/default-avatar.png')


def format_datetime(dt, format='%B %d, %Y at %I:%M %p'):
    """
    Format datetime for display
    
    Args:
        dt: datetime object
        format: strftime format string
    
    Returns:
        str: Formatted datetime string
    """
    if dt is None:
        return 'N/A'
    return dt.strftime(format)


def format_date(dt, format='%B %d, %Y'):
    """
    Format date for display
    
    Args:
        dt: datetime object
        format: strftime format string
    
    Returns:
        str: Formatted date string
    """
    if dt is None:
        return 'N/A'
    return dt.strftime(format)


def get_status_badge_class(status):
    """
    Get CSS class for status badge
    
    Args:
        status: Status string
    
    Returns:
        str: CSS class name
    """
    status_classes = {
        'pending': 'badge-warning',
        'in_progress': 'badge-info',
        'completed': 'badge-success',
        'cancelled': 'badge-secondary'
    }
    return status_classes.get(status, 'badge-default')


def get_status_display(status):
    """
    Get display text for status
    
    Args:
        status: Status string
    
    Returns:
        str: Display text
    """
    status_display = {
        'pending': 'Pending',
        'in_progress': 'In Progress',
        'completed': 'Completed',
        'cancelled': 'Cancelled'
    }
    return status_display.get(status, status.title())


def truncate_text(text, length=50, suffix='...'):
    """
    Truncate text to specified length
    
    Args:
        text: Text to truncate
        length: Maximum length
        suffix: Suffix to add if truncated
    
    Returns:
        str: Truncated text
    """
    if not text:
        return ''
    
    if len(text) <= length:
        return text
    
    return text[:length].rsplit(' ', 1)[0] + suffix


def pluralize(count, singular, plural=None):
    """
    Return singular or plural form based on count
    
    Args:
        count: Number to check
        singular: Singular form
        plural: Plural form (defaults to singular + 's')
    
    Returns:
        str: Singular or plural form
    """
    if plural is None:
        plural = singular + 's'
    
    return singular if count == 1 else plural


def get_pending_count():
    """
    Get count of pending print requests
    
    Returns:
        int: Number of pending requests
    """
    from app.models import PrintRequest
    return PrintRequest.query.filter_by(status='pending').count()
