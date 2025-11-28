"""
Helper functions for form rendering and validation
"""
from flask import flash


def flash_form_errors(form):
    """
    Flash all form validation errors
    
    Args:
        form: FlaskForm instance with errors
    """
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{getattr(form, field).label.text}: {error}", 'error')


def get_form_errors_dict(form):
    """
    Get form errors as a dictionary for JSON responses
    
    Args:
        form: FlaskForm instance with errors
    
    Returns:
        dict: Field names mapped to error messages
    """
    errors = {}
    for field, error_list in form.errors.items():
        errors[field] = error_list
    return errors


def validate_print_request_data(form_data):
    """
    Additional validation for print request data
    
    Args:
        form_data: Dictionary of form data
    
    Returns:
        tuple: (is_valid: bool, errors: list)
    """
    errors = []
    
    # Validate number of pages
    pages = form_data.get('number_of_pages', 0)
    if pages < 1:
        errors.append('Number of pages must be at least 1')
    elif pages > 1000:
        errors.append('Number of pages cannot exceed 1000')
    
    # Validate number of copies
    copies = form_data.get('number_of_copies', 0)
    if copies < 1:
        errors.append('Number of copies must be at least 1')
    elif copies > 100:
        errors.append('Number of copies cannot exceed 100')
    
    # Validate print format
    print_format = form_data.get('print_format')
    if print_format not in ['bw', 'color']:
        errors.append('Invalid print format selected')
    
    # Validate paper size
    paper_size = form_data.get('paper_size')
    if paper_size not in ['A4', 'A3', 'A5']:
        errors.append('Invalid paper size selected')
    
    return len(errors) == 0, errors


def calculate_print_cost(number_of_pages, number_of_copies, print_format, paper_size, is_double_sided):
    """
    Calculate estimated print cost (for future use)
    
    Args:
        number_of_pages: Number of pages in document
        number_of_copies: Number of copies to print
        print_format: 'bw' or 'color'
        paper_size: 'A4', 'A3', or 'A5'
        is_double_sided: Boolean for double-sided printing
    
    Returns:
        float: Estimated cost
    """
    # Base costs per page
    base_costs = {
        'bw': {'A4': 0.05, 'A3': 0.10, 'A5': 0.03},
        'color': {'A4': 0.25, 'A3': 0.50, 'A5': 0.15}
    }
    
    # Get base cost
    cost_per_page = base_costs.get(print_format, {}).get(paper_size, 0.05)
    
    # Calculate total pages
    total_pages = number_of_pages * number_of_copies
    
    # Apply double-sided discount (saves paper)
    if is_double_sided:
        total_pages = total_pages * 0.6  # 40% discount for double-sided
    
    return round(total_pages * cost_per_page, 2)


def get_print_summary(request_data):
    """
    Generate a human-readable summary of print request
    
    Args:
        request_data: Dictionary or PrintRequest object
    
    Returns:
        dict: Summary information
    """
    if hasattr(request_data, '__dict__'):
        # Convert object to dict
        data = {
            'number_of_pages': request_data.number_of_pages,
            'number_of_copies': request_data.number_of_copies,
            'print_format': request_data.print_format,
            'paper_size': request_data.paper_size,
            'is_double_sided': request_data.is_double_sided,
            'is_stapled': request_data.is_stapled,
            'is_laminated': request_data.is_laminated
        }
    else:
        data = request_data
    
    total_pages = data['number_of_pages'] * data['number_of_copies']
    
    summary = {
        'total_pages': total_pages,
        'print_format_display': 'Color' if data['print_format'] == 'color' else 'Black & White',
        'paper_size_display': data['paper_size'],
        'orientation_display': 'Double-Sided' if data['is_double_sided'] else 'Single-Sided',
        'finishing': []
    }
    
    if data.get('is_stapled'):
        summary['finishing'].append('Stapled')
    if data.get('is_laminated'):
        summary['finishing'].append('Laminated')
    
    summary['finishing_display'] = ', '.join(summary['finishing']) if summary['finishing'] else 'None'
    
    return summary
