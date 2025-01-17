"""
Tests for the document converter functionality.
"""
import pytest
from pathlib import Path
import yaml
from docs_to_site.document_converter import DocumentConverter
from docs_to_site.utils import SUPPORTED_FORMATS, sanitize_title, sanitize_filename


@pytest.fixture
def temp_dirs(tmp_path):
    """Create temporary input and output directories."""
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    return input_dir, output_dir


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


def test_converter_initialization(temp_dirs):
    """Test that the converter is properly initialized."""
    input_dir, output_dir = temp_dirs
    converter = DocumentConverter(input_dir, output_dir)
    
    assert converter.input_dir == input_dir
    assert converter.output_dir == output_dir
    assert converter.docs_dir == output_dir / 'docs'
    assert converter.images_dir == output_dir / 'docs' / 'images'


def test_get_documents_empty_directory(temp_dirs):
    """Test that an empty directory returns no documents."""
    input_dir, output_dir = temp_dirs
    converter = DocumentConverter(input_dir, output_dir)
    
    documents = converter.get_documents()
    assert len(documents) == 0


def test_get_documents_with_files(temp_dirs):
    """Test that supported documents are found."""
    input_dir, output_dir = temp_dirs
    
    # Create test files
    (input_dir / "test.docx").touch()
    (input_dir / "test.txt").touch()
    (input_dir / "test.unsupported").touch()
    (input_dir / "test.pptx").touch()
    (input_dir / "test.jpg").touch()
    
    converter = DocumentConverter(input_dir, output_dir)
    documents = converter.get_documents()
    
    # We expect 4 supported files (docx, txt, pptx, jpg)
    assert len(documents) == 4
    # Each document should be a tuple of (Path, bool)
    for doc, is_accessible in documents:
        assert isinstance(doc, Path)
        assert isinstance(is_accessible, bool)
        assert doc.suffix.lower() in SUPPORTED_FORMATS


def test_is_supported_format(temp_dirs):
    """Test file format support checking."""
    input_dir, output_dir = temp_dirs
    converter = DocumentConverter(input_dir, output_dir)
    
    assert converter.is_supported_format(Path("test.docx"))
    assert converter.is_supported_format(Path("test.PDF"))  # Test case insensitivity
    assert not converter.is_supported_format(Path("test.unsupported"))


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