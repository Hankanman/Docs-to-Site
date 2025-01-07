"""
Tests for utility functions.
"""
import pytest
from docs_to_site.utils import sanitize_title, sanitize_filename, SUPPORTED_FORMATS


def test_supported_formats():
    """Test that supported formats are properly defined."""
    expected_formats = {
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
    assert SUPPORTED_FORMATS == expected_formats


@pytest.mark.parametrize("input_title,expected", [
    ("Title with  character", "Title with character"),
    ("Product™", "Product"),
    ("Chapter [1.2]", "Chapter (1.2)"),
    ("Title – with em dash", "Title - with em dash"),
    ("Multiple   spaces", "Multiple spaces"),
    ("Title with © and ®", "Title with and"),
    ("Client Flyer – Build watsonx.ai", "Client Flyer - Build watsonx.ai"),
    ("Title with control chars\x00\x1F", "Title with control chars"),
    ("Unicode: 你好", "Unicode 你好"),
    ("Brackets: [Test]", "Brackets (Test)"),
])
def test_title_sanitization(input_title, expected):
    """Test that titles are properly sanitized."""
    assert sanitize_title(input_title) == expected


@pytest.mark.parametrize("input_filename,expected", [
    ("file with spaces.txt", "file-with-spaces"),
    ("file_with_symbols_#@!.doc", "file-with-symbols"),
    ("résumé.pdf", "resume"),
    ("file/with\\invalid:chars.txt", "file-with-invalid-chars"),
    ("Test.File.With.Dots.txt", "Test.File.With.Dots"),
    ("UPPERCASE_file.txt", "UPPERCASE-file"),
])
def test_filename_sanitization(input_filename, expected):
    """Test that filenames are properly sanitized."""
    assert sanitize_filename(input_filename).startswith(expected)


def test_windows_1252_encoding():
    """Test handling of Windows-1252 encoded text."""
    # This is a Windows-1252 encoded string with special characters
    win1252_text = b'Client Flyer \x96 Build watsonx.ai'.decode('cp1252')
    sanitized = sanitize_title(win1252_text)
    assert sanitized == "Client Flyer - Build watsonx.ai" 