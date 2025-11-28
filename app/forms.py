from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, IntegerField, TextAreaField, RadioField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, NumberRange
from flask_wtf.file import FileField, FileAllowed
from app.models import User

# Faculty department choices
FACULTY_DEPARTMENTS = [
    ('Elementary School', 'Elementary School'),
    ('Middle School', 'Middle School'),
    ('High School', 'High School'),
    ('IT Department', 'IT Department'),
    ('Business Office', 'Business Office'),
    ('Procurement', 'Procurement'),
    ('Facilities', 'Facilities'),
    ('HR', 'HR'),
    ('Advancement & Communications', 'Advancement & Communications'),
    ('HOS Office', 'HOS Office')
]


class LoginForm(FlaskForm):
    """User login form"""
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])
    remember_me = BooleanField('Remember Me')


class RegistrationForm(FlaskForm):
    """User registration form"""
    card_id = StringField('Card ID', validators=[
        DataRequired(message='Card ID is required'),
        Length(min=3, max=50, message='Card ID must be between 3 and 50 characters')
    ])
    name = StringField('Full Name', validators=[
        DataRequired(message='Name is required'),
        Length(min=2, max=100, message='Name must be between 2 and 100 characters')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address')
    ])
    faculty_department = SelectField('Faculty Department', 
        choices=FACULTY_DEPARTMENTS,
        validators=[DataRequired(message='Please select a department')]
    )
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=6, message='Password must be at least 6 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ])
    
    def validate_email(self, email):
        """Check if email already exists"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email is already registered. Please use a different email.')
    
    def validate_card_id(self, card_id):
        """Check if card ID already exists"""
        user = User.query.filter_by(card_id=card_id.data).first()
        if user:
            raise ValidationError('This Card ID is already registered. Please use a different Card ID.')


class PrintRequestForm(FlaskForm):
    """Print request submission form"""
    file = FileField('Document to Print', validators=[
        DataRequired(message='Please upload at least one file'),
        FileAllowed(['pdf', 'doc', 'docx'], 'Only PDF, DOC, and DOCX files are allowed')
    ], render_kw={'multiple': True})
    number_of_pages = IntegerField('Number of Pages', validators=[
        DataRequired(message='Please specify number of pages'),
        NumberRange(min=1, max=1000, message='Number of pages must be between 1 and 1000')
    ])
    page_range = StringField('Page Range (Optional)', 
        validators=[Length(max=255, message='Page range must not exceed 255 characters')],
        render_kw={'placeholder': 'e.g., 1-5, 8, 10-15 (leave empty for all pages)'}
    )
    number_of_copies = IntegerField('Number of Copies', validators=[
        DataRequired(message='Please specify number of copies'),
        NumberRange(min=1, max=100, message='Number of copies must be between 1 and 100')
    ])
    is_double_sided = BooleanField('Double-Sided Printing')
    print_format = RadioField('Print Format', 
        choices=[('bw', 'Black & White'), ('color', 'Color')],
        default='bw',
        validators=[DataRequired(message='Please select a print format')]
    )
    paper_size = SelectField('Paper Size',
        choices=[('A4', 'A4'), ('A3', 'A3'), ('A5', 'A5')],
        default='A4',
        validators=[DataRequired(message='Please select a paper size')]
    )
    is_stapled = BooleanField('Stapled')
    is_laminated = BooleanField('Laminated')
    clarifying_message = TextAreaField('Additional Instructions', validators=[
        Length(max=500, message='Message must not exceed 500 characters')
    ])
    
    def validate_page_range(self, field):
        """Validate page range format"""
        if field.data and field.data.strip():
            from app.utils.page_range_parser import validate_page_range
            is_valid, error_message = validate_page_range(field.data)
            if not is_valid:
                raise ValidationError(f'Invalid page range: {error_message}')


class ProfileUpdateForm(FlaskForm):
    """Profile update form"""
    name = StringField('Full Name', validators=[
        DataRequired(message='Name is required'),
        Length(min=2, max=100, message='Name must be between 2 and 100 characters')
    ])
    profile_picture = FileField('Profile Picture', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Only image files are allowed')
    ]) 



class StatusUpdateForm(FlaskForm):
    """Admin status update form"""
    status = SelectField('Status',
        choices=[
            ('pending', 'Pending'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled')
        ],
        validators=[DataRequired(message='Please select a status')]
    )
