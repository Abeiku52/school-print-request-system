import os
import secrets
from datetime import datetime
from werkzeug.utils import secure_filename
from PIL import Image
from flask import current_app


def allowed_file(filename, allowed_extensions):
    """Check if file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def validate_file_size(file, max_size_mb=50):
    """Validate file size (in MB)"""
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # Reset file pointer
    
    max_size_bytes = max_size_mb * 1024 * 1024
    return file_size <= max_size_bytes


def generate_unique_filename(original_filename):
    """Generate a unique filename while preserving extension"""
    # Get file extension
    ext = ''
    if '.' in original_filename:
        ext = original_filename.rsplit('.', 1)[1].lower()
    
    # Generate unique name with timestamp and random string
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    random_string = secrets.token_hex(8)
    
    if ext:
        return f"{timestamp}_{random_string}.{ext}"
    return f"{timestamp}_{random_string}"


def save_document(file, user_id):
    """
    Save uploaded document file
    
    Args:
        file: FileStorage object from request.files
        user_id: ID of the user uploading the file
    
    Returns:
        tuple: (success: bool, message: str, file_path: str or None)
    """
    if not file:
        return False, "No file provided", None
    
    # Check if file has a filename
    if file.filename == '':
        return False, "No file selected", None
    
    # Validate file extension
    allowed_extensions = current_app.config['ALLOWED_DOCUMENT_EXTENSIONS']
    if not allowed_file(file.filename, allowed_extensions):
        return False, f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}", None
    
    # Validate file size
    if not validate_file_size(file, max_size_mb=50):
        return False, "File size exceeds 50MB limit", None
    
    try:
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        unique_filename = generate_unique_filename(original_filename)
        
        # Create user-specific directory
        upload_folder = current_app.config['UPLOAD_FOLDER']
        user_folder = os.path.join(upload_folder, 'documents', str(user_id))
        os.makedirs(user_folder, exist_ok=True)
        
        # Save file
        file_path = os.path.join(user_folder, unique_filename)
        file.save(file_path)
        
        # Return relative path for database storage
        relative_path = os.path.join('documents', str(user_id), unique_filename)
        
        return True, "File uploaded successfully", relative_path
        
    except Exception as e:
        return False, f"Error saving file: {str(e)}", None


def save_profile_picture(file, user_id):
    """
    Save and process profile picture
    
    Args:
        file: FileStorage object from request.files
        user_id: ID of the user uploading the picture
    
    Returns:
        tuple: (success: bool, message: str, file_path: str or None)
    """
    if not file:
        return False, "No file provided", None
    
    if file.filename == '':
        return False, "No file selected", None
    
    # Validate file extension
    allowed_extensions = current_app.config['ALLOWED_IMAGE_EXTENSIONS']
    if not allowed_file(file.filename, allowed_extensions):
        return False, f"Invalid image type. Allowed types: {', '.join(allowed_extensions)}", None
    
    # Validate file size (max 5MB for images)
    if not validate_file_size(file, max_size_mb=5):
        return False, "Image size exceeds 5MB limit", None
    
    try:
        # Generate unique filename
        unique_filename = f"user_{user_id}_{secrets.token_hex(8)}.jpg"
        
        # Create profiles directory
        upload_folder = current_app.config['UPLOAD_FOLDER']
        profiles_folder = os.path.join(upload_folder, 'profiles')
        os.makedirs(profiles_folder, exist_ok=True)
        
        file_path = os.path.join(profiles_folder, unique_filename)
        
        # Open and process image
        image = Image.open(file)
        
        # Convert to RGB if necessary (handles PNG with transparency)
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        
        # Resize to 200x200 (square)
        image = image.resize((200, 200), Image.Resampling.LANCZOS)
        
        # Save as JPEG
        image.save(file_path, 'JPEG', quality=85, optimize=True)
        
        # Return relative path for database storage
        relative_path = os.path.join('profiles', unique_filename)
        
        return True, "Profile picture uploaded successfully", relative_path
        
    except Exception as e:
        return False, f"Error processing image: {str(e)}", None


def get_file_path(relative_path):
    """
    Get absolute file path from relative path
    
    Args:
        relative_path: Relative path stored in database
    
    Returns:
        str: Absolute file path
    """
    upload_folder = current_app.config['UPLOAD_FOLDER']
    return os.path.join(upload_folder, relative_path)


def delete_file(relative_path):
    """
    Delete a file from storage
    
    Args:
        relative_path: Relative path stored in database
    
    Returns:
        bool: True if deleted successfully, False otherwise
    """
    try:
        file_path = get_file_path(relative_path)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        print(f"Error deleting file: {e}")
        return False


def get_file_size(relative_path):
    """
    Get file size in bytes
    
    Args:
        relative_path: Relative path stored in database
    
    Returns:
        int: File size in bytes, or 0 if file doesn't exist
    """
    try:
        file_path = get_file_path(relative_path)
        if os.path.exists(file_path):
            return os.path.getsize(file_path)
        return 0
    except Exception:
        return 0


def format_file_size(size_bytes):
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: File size in bytes
    
    Returns:
        str: Formatted file size (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"
