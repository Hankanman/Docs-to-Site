"""
Tests for the document converter functionality.
"""
import pytest
from pathlib import Path
import yaml
from docs_to_site.converter import (
    DocumentConverter, 
    SUPPORTED_FORMATS,
    sanitize_title,
    sanitize_filename
)


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


def test_is_supported_format(temp_dirs):
    """Test file format support checking."""
    input_dir, output_dir = temp_dirs
    converter = DocumentConverter(input_dir, output_dir)
    
    assert converter.is_supported_format(Path("test.docx"))
    assert converter.is_supported_format(Path("test.PDF"))  # Test case insensitivity
    assert not converter.is_supported_format(Path("test.unsupported"))


def test_is_image_format(temp_dirs):
    """Test image format checking."""
    input_dir, output_dir = temp_dirs
    converter = DocumentConverter(input_dir, output_dir)
    
    assert converter.is_image_format(Path("test.jpg"))
    assert converter.is_image_format(Path("test.PNG"))  # Test case insensitivity
    assert not converter.is_image_format(Path("test.docx"))


def test_convert_empty_directory(temp_dirs):
    """Test conversion with empty directory."""
    input_dir, output_dir = temp_dirs
    converter = DocumentConverter(input_dir, output_dir)
    
    with pytest.raises(ValueError, match="No supported documents found"):
        converter.convert()


def test_generate_mkdocs_config(temp_dirs):
    """Test MkDocs configuration generation."""
    input_dir, output_dir = temp_dirs
    # Create output directory
    output_dir.mkdir(exist_ok=True)
    converter = DocumentConverter(input_dir, output_dir)
    
    # Add some mock converted files
    converter.converted_files = {
        Path("doc1.md"): "Document 1",
        Path("section/doc2.md"): "Section - Document 2",
        Path("section/doc3.md"): "Section - Document 3",
    }
    
    converter.generate_mkdocs_config()
    
    # Check if config file was created
    assert converter.mkdocs_config.exists()
    
    # Verify config contents
    with open(converter.mkdocs_config) as f:
        config = yaml.safe_load(f)
    
    assert config["site_name"] == "Documentation"
    assert config["theme"]["name"] == "material"
    assert "nav" in config


def test_format_markdown(temp_dirs):
    """Test Markdown content formatting."""
    input_dir, output_dir = temp_dirs
    converter = DocumentConverter(input_dir, output_dir)
    
    content = """<!-- Slide number: 1 -->
Some content
<!-- Slide number: 2 -->
More content"""
    
    formatted = converter.format_markdown(content, Path("test.pptx"))
    
    assert "### Slide 1" in formatted
    assert "### Slide 2" in formatted


def test_format_markdown_with_images(temp_dirs):
    """Test Markdown formatting with image path updates."""
    input_dir, output_dir = temp_dirs
    converter = DocumentConverter(input_dir, output_dir)
    
    content = '![Alt text](Picture1.jpg)\n![Another](image.png)'
    image_map = {
        'Picture1.jpg': '/images/test/image_1.jpg',
        'image.png': '/images/test/image_2.png'
    }
    
    formatted = converter.format_markdown(content, Path("test.pptx"), image_map)
    
    assert '/images/test/image_1.jpg' in formatted
    assert '/images/test/image_2.png' in formatted


@pytest.mark.parametrize("config_content", [
    {"site_name": "Custom Site", "theme": "readthedocs"},
    {"site_name": "Test Site", "theme": {"name": "material", "custom_option": True}},
])
def test_custom_mkdocs_config(temp_dirs, config_content):
    """Test using custom MkDocs configuration."""
    input_dir, output_dir = temp_dirs
    # Create output directory
    output_dir.mkdir(exist_ok=True)
    config_file = input_dir / "mkdocs.yml"
    
    # Create custom config file
    with open(config_file, 'w') as f:
        yaml.dump(config_content, f)
    
    converter = DocumentConverter(input_dir, output_dir, config=config_file)
    converter.generate_mkdocs_config()
    
    # Verify config was used
    with open(converter.mkdocs_config) as f:
        final_config = yaml.safe_load(f)
    
    assert final_config["site_name"] == config_content["site_name"] 


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


def test_nav_structure_with_special_characters(temp_dirs):
    """Test navigation structure with special characters."""
    input_dir, output_dir = temp_dirs
    output_dir.mkdir(exist_ok=True)
    converter = DocumentConverter(input_dir, output_dir)
    
    # Add some mock converted files with special characters
    converter.converted_files = {
        Path("doc1.md"): "Client - Guide™",
        Path("section/doc2.md"): "Client - Presentation",
        Path("section/doc3.md"): "Client - Notes [1.2]",
    }
    
    converter.generate_mkdocs_config()
    
    with open(converter.mkdocs_config) as f:
        config = yaml.safe_load(f)
    
    # Check that navigation was created without special characters
    nav = config["nav"]
    # Find the Client section
    client_section = next(item for item in nav if "Client" in item)
    assert "Client" in client_section
    
    # Get the items in the Client section
    client_items = client_section["Client"]
    titles = [list(item.keys())[0] for item in client_items]
    
    # Check sanitized titles
    assert "Guide" in titles
    assert "Presentation" in titles
    assert "Notes (1.2)" in titles 


def test_windows_1252_encoding():
    """Test handling of Windows-1252 encoded text."""
    # This is a Windows-1252 encoded string with special characters
    win1252_text = b'Client Flyer \x96 Build watsonx.ai'.decode('cp1252')
    sanitized = sanitize_title(win1252_text)
    assert sanitized == "Client Flyer - Build watsonx.ai" 