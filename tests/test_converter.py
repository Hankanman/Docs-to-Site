"""
Tests for the document converter functionality.
"""
import pytest
from pathlib import Path
from markdown_converter.converter import DocumentConverter, SUPPORTED_FORMATS


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
    assert converter.mkdocs_config == output_dir / 'mkdocs.yml'


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