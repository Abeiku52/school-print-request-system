from flask import Blueprint, render_template

bp = Blueprint('errors', __name__)


@bp.app_errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return "404 - Page Not Found", 404


@bp.app_errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return "500 - Internal Server Error", 500
