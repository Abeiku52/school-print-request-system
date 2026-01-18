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
    is_active = db.Column(db.Boolean, default=True, nullable=False)  # Account status
    last_password_reset = db.Column(db.DateTime, nullable=True)  # Track password resets
    password_reset_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Admin who reset password
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    print_requests = db.relationship('PrintRequest', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    admin_preferences = db.relationship('AdminPreferences', backref='admin_user', lazy='dynamic', cascade='all, delete-orphan')
    password_resets_performed = db.relationship('User', backref='password_reset_admin', remote_side=[id])
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        self.last_password_reset = datetime.utcnow()
    
    def admin_reset_password(self, password, admin_user_id):
        """Reset password by admin with tracking"""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        self.last_password_reset = datetime.utcnow()
        self.password_reset_by = admin_user_id
    
    def is_account_active(self):
        """Check if account is active"""
        return self.is_active
    
    def toggle_account_status(self):
        """Toggle account active status"""
        self.is_active = not self.is_active
        return self.is_active
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_pending_requests_count(self):
        """Get count of pending print requests"""
        return self.print_requests.filter_by(status='pending').count()
    
    def get_completed_requests_count(self):
        """Get count of completed print requests"""
        return self.print_requests.filter_by(status='completed').count()
    
    def is_account_active(self):
        """Check if account is active"""
        return self.is_active
    
    def toggle_account_status(self):
        """Toggle account active status"""
        self.is_active = not self.is_active
        return self.is_active
    
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
    
    # Reprint tracking
    original_request_id = db.Column(db.Integer, db.ForeignKey('print_requests.id'), nullable=True, index=True)
    is_reprint = db.Column(db.Boolean, default=False, nullable=False, index=True)
    reprint_count = db.Column(db.Integer, default=0, nullable=False)
    
    # Relationships
    original_request = db.relationship('PrintRequest', remote_side=[id], backref='reprints')
    
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
    
    def update_status(self, new_status, create_notification=True):
        """
        Update request status and timestamp
        Optionally creates a notification for the user
        
        Args:
            new_status: The new status to set
            create_notification: Whether to create a notification (default: True)
        """
        old_status = self.status
        self.status = new_status
        self.updated_at = datetime.utcnow()
        
        # Create notification if status changed and flag is True
        if create_notification and old_status != new_status:
            try:
                from app.services import NotificationService
                NotificationService.create_status_notification(
                    self.user_id,
                    self.id,
                    old_status,
                    new_status
                )
            except Exception as e:
                # Log error but don't fail the status update
                print(f"Warning: Failed to create notification: {str(e)}")
    
    def can_be_reprinted(self):
        """Check if this request can be reprinted"""
        from app.utils import get_file_path
        import os
        
        return (self.status == 'completed' and 
                os.path.exists(get_file_path(self.file_path)))
    
    def increment_reprint_count(self):
        """Increment the reprint count for this request"""
        self.reprint_count += 1
    
    def get_reprint_display_name(self):
        """Get display name for reprint requests"""
        if self.is_reprint and self.original_request:
            return f"Reprint of {self.original_request.request_number}"
        return self.request_number
    
    def __repr__(self):
        return f'<PrintRequest {self.request_number}>'


class CreditTransaction(db.Model):
    """Track all credit transactions"""
    __tablename__ = 'credit_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)  # Positive for credit, negative for debit
    balance_after = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # 'credit' or 'debit'
    description = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<CreditTransaction {self.id}: {self.amount}>'


class Notification(db.Model):
    """Notification model for user alerts"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    request_id = db.Column(db.Integer, db.ForeignKey('print_requests.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), default='status_change', nullable=False)
    status = db.Column(db.String(20), nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    print_request = db.relationship('PrintRequest', backref='notifications')
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
    
    def get_status_display(self):
        """Get human-readable status"""
        status_map = {
            'pending': 'Pending',
            'in_progress': 'In Progress',
            'processing': 'Processing',
            'completed': 'Completed',
            'cancelled': 'Cancelled'
        }
        return status_map.get(self.status, self.status.title())
    
    def __repr__(self):
        return f'<Notification {self.id}: {self.notification_type} for Request {self.request_id}>'


class AdminAuditLog(db.Model):
    """Audit log for administrative actions"""
    __tablename__ = 'admin_audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    action = db.Column(db.String(100), nullable=False)  # e.g., 'password_reset', 'account_disable'
    target_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    target_request_id = db.Column(db.Integer, db.ForeignKey('print_requests.id'), nullable=True)
    details = db.Column(db.Text, nullable=True)  # Additional context in JSON format
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    ip_address = db.Column(db.String(45), nullable=True)  # Support IPv6
    
    # Relationships
    admin_user = db.relationship('User', foreign_keys=[admin_id], backref='audit_logs_created')
    target_user = db.relationship('User', foreign_keys=[target_user_id], backref='audit_logs_received')
    target_request = db.relationship('PrintRequest', backref='audit_logs')
    
    @staticmethod
    def log_action(admin_id, action, target_user_id=None, target_request_id=None, details=None, ip_address=None):
        """Create an audit log entry"""
        log_entry = AdminAuditLog(
            admin_id=admin_id,
            action=action,
            target_user_id=target_user_id,
            target_request_id=target_request_id,
            details=details,
            ip_address=ip_address
        )
        db.session.add(log_entry)
        return log_entry
    
    def __repr__(self):
        return f'<AdminAuditLog {self.id}: {self.action} by Admin {self.admin_id}>'


class AdminPreferences(db.Model):
    """Store admin dashboard preferences"""
    __tablename__ = 'admin_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True, index=True)
    dashboard_layout = db.Column(db.JSON, nullable=True)  # Widget visibility and layout
    default_filters = db.Column(db.JSON, nullable=True)  # Saved filter settings
    items_per_page = db.Column(db.Integer, default=10, nullable=False)  # Pagination preference
    show_statistics = db.Column(db.Boolean, default=True, nullable=False)  # Show/hide stats widgets
    show_recent_requests = db.Column(db.Boolean, default=True, nullable=False)  # Show/hide recent requests
    show_pending_requests = db.Column(db.Boolean, default=True, nullable=False)  # Show/hide pending requests
    auto_refresh_interval = db.Column(db.Integer, default=30, nullable=False)  # Auto-refresh interval in seconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    @staticmethod
    def get_or_create_preferences(admin_id):
        """Get existing preferences or create default ones"""
        preferences = AdminPreferences.query.filter_by(admin_id=admin_id).first()
        if not preferences:
            preferences = AdminPreferences(admin_id=admin_id)
            db.session.add(preferences)
            db.session.commit()
        return preferences
    
    def update_preferences(self, **kwargs):
        """Update preferences with provided values"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
    
    def __repr__(self):
        return f'<AdminPreferences {self.id}: Admin {self.admin_id}>'
