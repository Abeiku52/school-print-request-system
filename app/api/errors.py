from flask import jsonify
from app.api import bp


@bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404


@bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


@bp.errorhandler(403)
def forbidden(error):
    return jsonify({'error': 'Forbidden'}), 403


@bp.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400
