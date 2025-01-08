"""
Common utility functions for document conversion.
"""

import logging
from pathlib import Path
from slugify import slugify
from typing import Tuple
from wand.image import Image as WandImage
from wand.exceptions import WandError

logger = logging.getLogger(__name__)


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
        stem = "-".join(part for part in path.parts[:-1])
        stem += f"-{path.parts[-1]}"
    else:
        stem = path.stem
    suffix = path.suffix

    # Slugify the stem only
    clean_stem = slugify(
        stem,
        lowercase=False,
        separator="-",
        regex_pattern=r"[^-a-zA-Z0-9.]+",  # Allow dots
        replacements=[
            ("_", "-"),  # Convert underscores to hyphens
            ("/", "-"),  # Convert slashes to hyphens
            ("\\", "-"),  # Convert backslashes to hyphens
        ],
    )

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
        "–": "-",  # en dash
        "—": "-",  # em dash
        "™": "",  # trademark
        "®": "",  # registered trademark
        "©": "",  # copyright
        "[": "(",  # brackets to parentheses
        "]": ")",
    }

    # Apply replacements
    clean_title = title
    for old, new in replacements.items():
        clean_title = clean_title.replace(old, new)

    # Remove other special characters but keep unicode letters/numbers
    clean_title = "".join(
        c for c in clean_title if c.isalnum() or c.isspace() or c in "()-.,"
    )

    # Normalize spaces
    clean_title = " ".join(clean_title.split())

    return clean_title.strip()


# Constants
SUPPORTED_FORMATS = {
    # Documents
    ".pdf",
    ".doc",
    ".docx",
    ".rtf",
    ".odt",
    ".txt",
    # Presentations
    ".ppt",
    ".pptx",
    # Spreadsheets
    ".xls",
    ".xlsx",
    ".csv",
    # Images
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".bmp",
    ".webp",
    # Audio
    ".mp3",
    ".wav",
    ".m4a",
    ".ogg",
    ".flac",
    # Web
    ".html",
    ".htm",
    # Data formats
    ".json",
    ".xml",
    # Archives
    ".zip",
}

IMAGE_FORMATS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg"}


def normalize_image_name(name: str) -> str:
    """Normalize image name to handle variations in spacing and extensions."""
    # Remove extension
    base = str(Path(name).stem)
    # Remove spaces, underscores, and dots
    base = base.replace(" ", "").replace("_", "").replace(".", "")
    # Convert to lowercase for case-insensitive matching
    return base.lower()


def check_imagemagick() -> Tuple[bool, str]:
    """
    Check if ImageMagick is available in the system.

    Returns:
        Tuple of (is_available: bool, message: str)
    """
    try:
        with WandImage() as img:
            return True, "ImageMagick is available"
    except WandError as e:
        if "delegate" in str(e).lower() and "wmf" in str(e).lower():
            return False, "ImageMagick WMF delegate library is missing"
        return False, f"ImageMagick is not properly installed: {str(e)}"
    except Exception as e:
        return False, f"Failed to check ImageMagick: {str(e)}"
