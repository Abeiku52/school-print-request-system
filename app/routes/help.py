from flask import Blueprint, render_template

bp = Blueprint('help', __name__, url_prefix='/help')

@bp.route('/guide')
def user_guide():
    """Display user guide"""
    return render_template('help/user_guide.html')