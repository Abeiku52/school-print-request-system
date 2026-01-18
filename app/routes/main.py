from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """Home page"""
    # Redirect to appropriate dashboard based on user type
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('requests.dashboard'))
    return redirect(url_for('auth.login'))


@bp.route('/about')
def about():
    """About page"""
    return render_template('main/about.html')
