from wtforms.validators import ValidationError
from flask import current_app
import os


class FileRequired:
    """Validator to ensure a file is uploaded"""
    
    def __init__(self, message=None):
        self.message = message or 'Please upload a file'
    
    def __call__(self, form, field):
        if not field.data:
            raise ValidationError(self.message)


class FileSizeLimit:
    """Validator to check file size"""
    
    def __init__(self, max_size_mb=50, message=None):
        self.max_size_mb = max_size_mb
        self.message = message or f'File size must not exceed {max_size_mb}MB'
    
    def __call__(self, form, field):
        if field.data:
            file = field.data
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            
            max_size_bytes = self.max_size_mb * 1024 * 1024
            if file_size > max_size_bytes:
                raise ValidationError(self.message)


class FileExtension:
    """Validator to check file extension"""
    
    def __init__(self, allowed_extensions, message=None):
        self.allowed_extensions = allowed_extensions
        self.message = message or f'Allowed file types: {", ".join(allowed_extensions)}'
    
    def __call__(self, form, field):
        if field.data:
            filename = field.data.filename
            if '.' not in filename:
                raise ValidationError('File must have an extension')
            
            ext = filename.rsplit('.', 1)[1].lower()
            if ext not in self.allowed_extensions:
                raise ValidationError(self.message)


class ImageDimensions:
    """Validator to check image dimensions"""
    
    def __init__(self, min_width=None, min_height=None, max_width=None, max_height=None, message=None):
        self.min_width = min_width
        self.min_height = min_height
        self.max_width = max_width
        self.max_height = max_height
        self.message = message
    
    def __call__(self, form, field):
        if field.data:
            try:
                from PIL import Image
                image = Image.open(field.data)
                width, height = image.size
                field.data.seek(0)  # Reset file pointer
                
                if self.min_width and width < self.min_width:
                    raise ValidationError(self.message or f'Image width must be at least {self.min_width}px')
                
                if self.min_height and height < self.min_height:
                    raise ValidationError(self.message or f'Image height must be at least {self.min_height}px')
                
                if self.max_width and width > self.max_width:
                    raise ValidationError(self.message or f'Image width must not exceed {self.max_width}px')
                
                if self.max_height and height > self.max_height:
                    raise ValidationError(self.message or f'Image height must not exceed {self.max_height}px')
                    
            except Exception as e:
                raise ValidationError('Invalid image file')


class PasswordStrength:
    """Validator to check password strength"""
    
    def __init__(self, require_uppercase=True, require_lowercase=True, 
                 require_digit=True, require_special=False, message=None):
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digit = require_digit
        self.require_special = require_special
        self.message = message
    
    def __call__(self, form, field):
        password = field.data
        errors = []
        
        if self.require_uppercase and not any(c.isupper() for c in password):
            errors.append('one uppercase letter')
        
        if self.require_lowercase and not any(c.islower() for c in password):
            errors.append('one lowercase letter')
        
        if self.require_digit and not any(c.isdigit() for c in password):
            errors.append('one digit')
        
        if self.require_special and not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            errors.append('one special character')
        
        if errors:
            if self.message:
                raise ValidationError(self.message)
            else:
                raise ValidationError(f'Password must contain at least {", ".join(errors)}')
