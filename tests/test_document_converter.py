"""
Tests for document conversion functionality.
"""
import pytest
from pathlib import Path
from docs_to_site.document_converter import DocumentConverter, format_markdown
from docs_to_site.utils import SUPPORTED_FORMATS


@pytest.fixture
def temp_dirs(tmp_path):
    """Create temporary input and output directories."""
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    return input_dir, output_dir


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


def test_format_markdown():
    """Test Markdown content formatting."""
    content = """<!-- Slide number: 1 -->
Some content
<!-- Slide number: 2 -->
More content"""
    
    formatted = format_markdown(content, Path("test.pptx"))
    
    assert "### Slide 1" in formatted
    assert "### Slide 2" in formatted


def test_format_markdown_with_images():
    """Test Markdown formatting with image path updates."""
    content = '![Alt text](Picture1.jpg)\n![Another](image.png)'
    image_map = {
        'Picture1.jpg': 'image_1.jpg',
        'image.png': 'image_2.png'
    }
    
    formatted = format_markdown(content, Path("test.pptx"), image_map)
    
    assert 'images/test/image_1.jpg' in formatted
    assert 'images/test/image_2.png' in formatted 