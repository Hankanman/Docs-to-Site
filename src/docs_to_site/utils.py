"""
Common utility functions for document conversion.
"""

import logging
import re
from pathlib import Path
from slugify import slugify

logger = logging.getLogger(__name__)

# Document formats supported by the converter
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
    Sanitize a document title for use in navigation.

    Args:
        title: The title to sanitize

    Returns:
        A sanitized title
    """
    # Remove any file extensions
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


def format_markdown(content: str) -> str:
    """
    Format the Markdown content for better readability.

    Args:
        content: Original Markdown content

    Returns:
        Formatted Markdown content
    """
    # Clean up vertical tabs and other problematic whitespace
    content = content.replace("\v", " ")  # Replace vertical tabs with newlines
    content = re.sub(r"[\f\r]", "", content)  # Remove form feeds and carriage returns

    # Fix newlines in image alt text
    content = re.sub(
        r"!\[(.*?)\n+(.*?)\]\((.*?)\)",
        lambda m: f"![{m.group(1)} {m.group(2)}]({m.group(3)})",
        content,
    )

    # Ensure tables have newlines after them (only after the last row)
    content = re.sub(r"(\|[^\n]*\|)\s*\n(?!\|)", r"\1\n\n", content)

    # Format slide markers
    content = re.sub(r"<!-- Slide number: (\d+) -->", r"\n---\n### Slide \1\n", content)

    # Add proper spacing around headings
    content = re.sub(r"(#{1,6} .+?)(\n(?!#))", r"\1\n\2", content)

    # Add proper spacing around bullet points
    content = re.sub(r"(\n[*-] .+?)(\n[^*\n-])", r"\1\n\2", content)

    # Add proper spacing around sections
    content = re.sub(r"(\n\n[^#\n-].*?)(\n[^#\n-])", r"\1\n\2", content)

    # Detect and format URLs that aren't already markdown links
    # First, exclude URLs that are already part of markdown links or images
    def is_in_markdown_link(match, text):
        # Check if the URL is already part of a markdown link
        start = max(0, match.start() - 50)  # Look at the 50 chars before the match
        end = min(len(text), match.end() + 50)  # Look at the 50 chars after the match
        context = text[start:end]

        # If there's a closing bracket before the URL and an opening bracket after,
        # it's likely already in a markdown link
        before = context[: match.start() - start]
        after = context[match.end() - start :]
        return "](" in before and ")" in after

    # URL regex pattern
    url_pattern = r"(?<![\[\(])(https?://[^\s\)\]]+)"

    # Find all URLs and replace them with markdown links if they're not already links
    content = re.sub(
        url_pattern,
        lambda m: (
            m.group(0)
            if is_in_markdown_link(m, content)
            else f"[{m.group(0)}]({m.group(0)})"
        ),
        content,
    )

    # Remove extra blank lines
    content = re.sub(r"\n{3,}", r"\n\n", content)

    return content
