"""
Common utility functions for document conversion.
"""
import re
from pathlib import Path
from slugify import slugify

def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to be safe for all operating systems.
    
    Args:
        filename: The filename to sanitize
    
    Returns:
        A sanitized filename
    """
    # Get the stem and extension separately
    path = Path(filename)
    # Handle paths with multiple segments
    if len(path.parts) > 1:
        # Join all parts except the last with hyphens
        stem = '-'.join(part for part in path.parts[:-1])
        stem += f"-{path.parts[-1]}"
    else:
        stem = path.stem
    suffix = path.suffix
    
    # Slugify the stem only
    clean_stem = slugify(stem,
                        lowercase=False,
                        separator='-',
                        regex_pattern=r'[^-a-zA-Z0-9.]+',  # Allow dots
                        replacements=[
                            ('_', '-'),    # Convert underscores to hyphens
                            ('/', '-'),    # Convert slashes to hyphens
                            ('\\', '-'),   # Convert backslashes to hyphens
                        ])
    
    # Recombine with the extension
    return f"{clean_stem}{suffix}"

def sanitize_title(title: str) -> str:
    """
    Sanitize a title for use in MkDocs navigation.
    
    Args:
        title: The title to sanitize
    
    Returns:
        A sanitized title
    """
    # First handle special characters and spacing
    replacements = {
        '–': '-',  # en dash
        '—': '-',  # em dash
        '™': '',   # trademark
        '®': '',   # registered trademark
        '©': '',   # copyright
        '[': '(',  # brackets to parentheses
        ']': ')',
    }
    
    # Apply replacements
    clean_title = title
    for old, new in replacements.items():
        clean_title = clean_title.replace(old, new)
    
    # Remove other special characters but keep unicode letters/numbers
    clean_title = ''.join(c for c in clean_title if c.isalnum() or c.isspace() or c in '()-.,')
    
    # Normalize spaces
    clean_title = ' '.join(clean_title.split())
    
    return clean_title.strip()

# Constants
SUPPORTED_FORMATS = {
    # Documents
    '.pdf', '.doc', '.docx', '.rtf', '.odt', '.txt',
    # Presentations
    '.ppt', '.pptx',
    # Spreadsheets
    '.xls', '.xlsx', '.csv',
    # Images
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp',
    # Audio
    '.mp3', '.wav', '.m4a', '.ogg', '.flac',
    # Web
    '.html', '.htm',
    # Data formats
    '.json', '.xml',
    # Archives
    '.zip'
}

IMAGE_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'} 