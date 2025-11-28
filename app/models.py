from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager
import secrets
import string


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    """User model for staff members"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    faculty_department = db.Column(db.String(100), nullable=False)
    profile_picture = db.Column(db.String(255), nullable=True)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    print_requests = db.relationship('PrintRequest', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_pending_requests_count(self):
        """Get count of pending print requests"""
        return self.print_requests.filter_by(status='pending').count()
    
    def get_completed_requests_count(self):
        """Get count of completed print requests"""
        return self.print_requests.filter_by(status='completed').count()
    
    def __repr__(self):
        return f'<User {self.email}>'


class PrintRequest(db.Model):
    """Print request model"""
    __tablename__ = 'print_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    request_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # File information
    file_path = db.Column(db.String(255), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    
    # Print specifications
    number_of_pages = db.Column(db.Integer, nullable=False)
    page_range = db.Column(db.String(255), nullable=True)  # e.g., "1-5, 8, 10-15" or None for all pages
    number_of_copies = db.Column(db.Integer, nullable=False)
    is_double_sided = db.Column(db.Boolean, default=False, nullable=False)
    print_format = db.Column(db.String(10), nullable=False)  # 'bw' or 'color'
    paper_size = db.Column(db.String(5), nullable=False)  # 'A4', 'A3', 'A5'
    is_stapled = db.Column(db.Boolean, default=False, nullable=False)
    is_laminated = db.Column(db.Boolean, default=False, nullable=False)
    clarifying_message = db.Column(db.Text, nullable=True)
    
    # Status tracking
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending, in_progress, completed, cancelled
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    @staticmethod
    def generate_request_number():
        """Generate a unique request number"""
        timestamp = datetime.utcnow().strftime('%Y%m%d')
        random_part = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        return f'PR-{timestamp}-{random_part}'
    
    def get_status_badge_class(self):
        """Get CSS class for status badge"""
        status_classes = {
            'pending': 'badge-pending',
            'in_progress': 'badge-in-progress',
            'completed': 'badge-completed',
            'cancelled': 'badge-cancelled'
        }
        return status_classes.get(self.status, 'badge-default')
    
    def get_total_pages(self):
        """Calculate total pages to be printed"""
        return self.number_of_pages * self.number_of_copies
    
    def get_formatted_page_range(self):
        """Get formatted page range for display"""
        from app.utils.page_range_parser import format_page_range, parse_page_range
        if not self.page_range:
            return "All pages"
        try:
            pages = parse_page_range(self.page_range)
            return format_page_range(pages) if pages else "All pages"
        except:
            return self.page_range  # Return raw string if parsing fails
    
    def update_status(self, new_status):
        """Update request status and timestamp"""
        self.status = new_status
        self.updated_at = datetime.utcnow()
    
    def __repr__(self):
        return f'<PrintRequest {self.request_number}>'
