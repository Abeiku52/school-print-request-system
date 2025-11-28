import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

# Import mail after defining it in utils/email.py
from app.utils.email import mail


def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Create upload directories if they don't exist
    with app.app_context():
        upload_folder = app.config['UPLOAD_FOLDER']
        os.makedirs(os.path.join(upload_folder, 'documents'), exist_ok=True)
        os.makedirs(os.path.join(upload_folder, 'profiles'), exist_ok=True)
    
    # Register blueprints
    from app.routes import main, auth, requests, profile, admin, errors
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(requests.bp)
    app.register_blueprint(profile.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(errors.bp)
    
    # Register template helpers
    from app.utils.template_helpers import (
        get_profile_picture_url,
        format_datetime,
        format_date,
        get_status_badge_class,
        get_status_display,
        truncate_text,
        pluralize,
        get_pending_count
    )
    
    app.jinja_env.globals.update(
        get_profile_picture_url=get_profile_picture_url,
        format_datetime=format_datetime,
        format_date=format_date,
        get_status_badge_class=get_status_badge_class,
        get_status_display=get_status_display,
        truncate_text=truncate_text,
        pluralize=pluralize,
        get_pending_count=get_pending_count
    )
    
    return app
