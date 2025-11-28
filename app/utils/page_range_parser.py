"""
Page range parsing and validation utilities
"""
import re


def parse_page_range(page_range_str):
    """
    Parse a page range string into a list of page numbers.
    
    Supports formats:
    - Single pages: "5"
    - Ranges: "1-10"
    - Combinations: "1-5, 8, 10-15"
    - Empty string: returns None (print all pages)
    
    Args:
        page_range_str: String representing page range(s)
    
    Returns:
        list: List of page numbers, or None if empty string
    
    Raises:
        ValueError: If the format is invalid
    """
    if not page_range_str or page_range_str.strip() == '':
        return None  # Print all pages
    
    # Remove all whitespace
    page_range_str = page_range_str.replace(' ', '')
    
    pages = set()
    
    # Split by comma
    parts = page_range_str.split(',')
    
    for part in parts:
        if not part:
            continue
            
        # Check if it's a range (contains hyphen)
        if '-' in part:
            # Parse range
            range_parts = part.split('-')
            if len(range_parts) != 2:
                raise ValueError(f"Invalid range format: {part}")
            
            try:
                start = int(range_parts[0])
                end = int(range_parts[1])
            except ValueError:
                raise ValueError(f"Invalid page numbers in range: {part}")
            
            if start < 1 or end < 1:
                raise ValueError(f"Page numbers must be positive: {part}")
            
            if start > end:
                raise ValueError(f"Invalid range (start > end): {part}")
            
            # Add all pages in range
            pages.update(range(start, end + 1))
        else:
            # Single page
            try:
                page = int(part)
            except ValueError:
                raise ValueError(f"Invalid page number: {part}")
            
            if page < 1:
                raise ValueError(f"Page numbers must be positive: {part}")
            
            pages.add(page)
    
    return sorted(list(pages))


def validate_page_range(page_range_str):
    """
    Validate a page range string without parsing.
    
    Args:
        page_range_str: String representing page range(s)
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not page_range_str or page_range_str.strip() == '':
        return (True, None)  # Empty is valid (print all)
    
    try:
        parse_page_range(page_range_str)
        return (True, None)
    except ValueError as e:
        return (False, str(e))


def format_page_range(pages):
    """
    Format a list of page numbers into a compact string representation.
    
    Args:
        pages: List of page numbers
    
    Returns:
        str: Formatted page range string (e.g., "1-5, 8, 10-15")
    """
    if not pages:
        return "All pages"
    
    pages = sorted(set(pages))
    ranges = []
    start = pages[0]
    end = pages[0]
    
    for i in range(1, len(pages)):
        if pages[i] == end + 1:
            end = pages[i]
        else:
            if start == end:
                ranges.append(str(start))
            else:
                ranges.append(f"{start}-{end}")
            start = pages[i]
            end = pages[i]
    
    # Add the last range
    if start == end:
        ranges.append(str(start))
    else:
        ranges.append(f"{start}-{end}")
    
    return ", ".join(ranges)


def count_pages_in_range(page_range_str):
    """
    Count the number of pages in a page range string.
    
    Args:
        page_range_str: String representing page range(s)
    
    Returns:
        int: Number of pages, or None if all pages
    """
    pages = parse_page_range(page_range_str)
    return len(pages) if pages is not None else None
