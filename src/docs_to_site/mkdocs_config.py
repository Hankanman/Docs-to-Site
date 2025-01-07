"""
MkDocs configuration and navigation structure generation.
"""
import logging
from pathlib import Path
from typing import Any, Dict, List

import yaml

from .utils import sanitize_title

logger = logging.getLogger(__name__)

def build_nav_structure(converted_files: Dict[Path, str]) -> List[Any]:
    """
    Build the navigation structure for MkDocs.
    
    Args:
        converted_files: Dictionary mapping file paths to their titles
        
    Returns:
        List of navigation items in MkDocs format
    """
    nav_structure: Dict[str, Any] = {}

    # Sort files by path for consistent ordering
    sorted_files = sorted(converted_files.items(), key=lambda x: str(x[0]))

    # Group files by prefix (e.g., "Client -" or "watsonx")
    groups: Dict[str, List[tuple[Path, str]]] = {}
    for file_path, title in sorted_files:
        # Extract prefix from title
        prefix = title.split(' - ')[0] if ' - ' in title else 'Other'
        # Sanitize the prefix
        prefix = sanitize_title(prefix)
        if prefix not in groups:
            groups[prefix] = []
        groups[prefix].append((file_path, title))

    # Build navigation structure with groups
    for prefix, files in groups.items():
        if len(files) > 1:
            # Create a group for multiple files with the same prefix
            nav_structure[prefix] = {
                sanitize_title(title.replace(prefix + ' - ', '')): str(file_path)
                for file_path, title in files
            }
        else:
            # Single file goes directly in the root
            file_path, title = files[0]
            nav_structure[sanitize_title(title)] = str(file_path)

    # Convert the nested dictionary to MkDocs nav format
    def dict_to_nav(d: Dict[str, Any]) -> List[Any]:
        nav = []
        for k, v in d.items():
            if isinstance(v, str):
                nav.append({k: v})
            else:
                # Handle groups
                subnav = []
                for sub_k, sub_v in v.items():
                    subnav.append({sub_k: sub_v})
                nav.append({k: subnav})
        return nav

    return dict_to_nav(nav_structure)

def generate_mkdocs_config(output_dir: Path, docs_dir: Path, converted_files: Dict[Path, str], custom_config: Path | None = None) -> None:
    """
    Generate the MkDocs configuration file with navigation structure.
    
    Args:
        output_dir: Directory where the MkDocs site will be generated
        docs_dir: Directory containing the Markdown files
        converted_files: Dictionary mapping file paths to their titles
        custom_config: Optional path to custom MkDocs configuration
    """
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if custom_config:
        # Use custom config if provided
        with open(custom_config, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
    else:
        # Generate default config
        config_data = {
            'site_name': 'Documentation',
            'theme': {
                'name': 'material',
                'features': [
                    'navigation.instant',
                    'navigation.tracking',
                    'navigation.sections',
                    'navigation.expand',
                    'toc.integrate'
                ],
                'palette': {
                    'primary': 'blue',
                    'accent': 'blue'
                }
            },
            'docs_dir': 'docs',
            'use_directory_urls': False,  # This helps with relative image paths
            'markdown_extensions': [
                'attr_list',
                'md_in_html',
                'tables',
                'fenced_code',
                'footnotes',
                'admonition',
                'toc',
                'pymdownx.highlight',
                'pymdownx.superfences'
            ]
        }

    # Add navigation structure
    if converted_files:
        config_data['nav'] = build_nav_structure(converted_files)

    # Write config file
    config_path = output_dir / 'mkdocs.yml'
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(
            config_data, 
            f, 
            default_flow_style=False, 
            sort_keys=False, 
            allow_unicode=True,
            encoding='utf-8'
        ) 