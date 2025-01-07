"""
Tests for image processing functionality.
"""
import pytest
from pathlib import Path
import shutil
from docs_to_site.image_processor import (
    normalize_image_name,
    extract_pptx_images,
    copy_embedded_images
)


@pytest.fixture
def temp_dirs(tmp_path):
    """Create temporary input and output directories."""
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()
    return input_dir, output_dir


def test_normalize_image_name():
    """Test image name normalization."""
    assert normalize_image_name("Picture 1.jpg") == "picture1"
    assert normalize_image_name("image_file.PNG") == "imagefile"
    assert normalize_image_name("test/path/image.gif") == "image"
    assert normalize_image_name("Picture.With.Dots.jpg") == "picturewithdots"
    assert normalize_image_name("UPPERCASE_FILE.png") == "uppercasefile"


def test_copy_embedded_images(temp_dirs):
    """Test copying embedded images."""
    input_dir, output_dir = temp_dirs
    
    # Create some test images
    test_images = [
        "test1.jpg",
        "test2.png",
        "test3.gif"
    ]
    
    for img in test_images:
        (input_dir / img).touch()
    
    image_map = copy_embedded_images(input_dir / "test.docx", output_dir)
    
    # Check that all images were mapped
    assert len(image_map) == len(test_images)  # Each image maps to itself since no sanitization needed
    
    # Check that images were copied
    for img in test_images:
        assert (output_dir / img).exists()
        # Check that the map contains both original and sanitized names
        assert image_map[img] == img 