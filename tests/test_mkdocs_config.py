"""
Tests for MkDocs configuration generation.
"""
import pytest
from pathlib import Path
import yaml
from docs_to_site.mkdocs_config import MkDocsConfig


@pytest.fixture
def temp_dirs(tmp_path):
    """Create temporary input and output directories."""
    output_dir = tmp_path / "output"
    docs_dir = output_dir / "docs"
    docs_dir.mkdir(parents=True)
    return output_dir, docs_dir


def test_mkdocs_config_generation(temp_dirs):
    """Test MkDocs configuration generation."""
    output_dir, docs_dir = temp_dirs
    
    # Add some mock converted files
    converted_files = {
        Path("doc1.md"): "Document 1",
        Path("section/doc2.md"): "Section - Document 2",
        Path("section/doc3.md"): "Section - Document 3",
    }
    
    config = MkDocsConfig(output_dir, docs_dir)
    config.generate(converted_files)
    
    # Check if config file was created
    config_path = output_dir / 'mkdocs.yml'
    assert config_path.exists()
    
    # Verify config contents
    with open(config_path) as f:
        config_data = yaml.safe_load(f)
    
    assert config_data["site_name"] == "Documentation"
    assert config_data["theme"]["name"] == "material"
    assert "nav" in config_data


@pytest.mark.parametrize("config_content", [
    {"site_name": "Custom Site", "theme": "readthedocs"},
    {"site_name": "Test Site", "theme": {"name": "material", "custom_option": True}},
])
def test_custom_mkdocs_config(temp_dirs, config_content):
    """Test using custom MkDocs configuration."""
    output_dir, docs_dir = temp_dirs
    
    # Create custom config file
    config_file = output_dir / "custom_mkdocs.yml"
    with open(config_file, 'w') as f:
        yaml.dump(config_content, f)
    
    # Add some mock converted files
    converted_files = {
        Path("doc1.md"): "Document 1",
    }
    
    config = MkDocsConfig(output_dir, docs_dir, config_file)
    config.generate(converted_files)
    
    # Verify config was used
    with open(output_dir / 'mkdocs.yml') as f:
        final_config = yaml.safe_load(f)
    
    assert final_config["site_name"] == config_content["site_name"]


def test_nav_structure_with_special_characters(temp_dirs):
    """Test navigation structure with special characters."""
    output_dir, docs_dir = temp_dirs
    
    # Add some mock converted files with special characters
    converted_files = {
        Path("doc1.md"): "Client - Guide™",
        Path("section/doc2.md"): "Client - Presentation",
        Path("section/doc3.md"): "Client - Notes [1.2]",
    }
    
    config = MkDocsConfig(output_dir, docs_dir)
    config.generate(converted_files)
    
    with open(output_dir / 'mkdocs.yml') as f:
        config_data = yaml.safe_load(f)
    
    # Check that navigation was created without special characters
    nav = config_data["nav"]
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