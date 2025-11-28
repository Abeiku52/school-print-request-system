from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """Home page"""
    # Redirect to dashboard if logged in, otherwise to login
    if current_user.is_authenticated:
        return redirect(url_for('requests.dashboard'))
    return redirect(url_for('auth.login'))


@bp.route('/about')
def about():
    """About page"""
    return render_template('main/about.html')
