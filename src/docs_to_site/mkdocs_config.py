"""
MkDocs configuration and navigation structure generation.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from .utils import sanitize_title

logger = logging.getLogger(__name__)

class MkDocsConfig:
    """Handles MkDocs configuration generation and management."""
    
    def __init__(self, output_dir: Path, docs_dir: Path, custom_config: Optional[Path] = None):
        """
        Initialize the MkDocs configuration generator.
        
        Args:
            output_dir: Directory where the MkDocs site will be generated
            docs_dir: Directory containing the Markdown files
            custom_config: Optional path to custom MkDocs configuration
        """
        self.output_dir = output_dir
        self.docs_dir = docs_dir
        self.custom_config = custom_config
        self.config_data: Dict[str, Any] = {}
        
    def _load_custom_config(self) -> None:
        """Load configuration from a custom config file."""
        if not self.custom_config:
            return
            
        try:
            with open(self.custom_config, 'r', encoding='utf-8') as f:
                self.config_data = yaml.safe_load(f)
            logger.info(f"Loaded custom configuration from {self.custom_config}")
        except Exception as e:
            logger.warning(f"Failed to load custom config {self.custom_config}: {str(e)}")
            self._generate_default_config()
    
    def _generate_default_config(self) -> None:
        """Generate default MkDocs configuration."""
        self.config_data = {
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
    
    def _build_nav_structure(self, converted_files: Dict[Path, str]) -> List[Any]:
        """
        Build navigation structure from converted files.
        
        Args:
            converted_files: Dictionary mapping file paths to their titles
            
        Returns:
            List of navigation items in MkDocs format
        """
        # Create a nested dictionary for the navigation
        nav_structure: Dict[str, Any] = {}
        
        for file_path, title in converted_files.items():
            current = nav_structure
            # Handle nested paths
            parts = list(file_path.parts)
            
            # Process all parts except the last one (which is the file)
            for part in parts[:-1]:
                clean_part = sanitize_title(part)
                if clean_part not in current:
                    current[clean_part] = {}
                current = current[clean_part]
            
            # Add the file at the end
            file_path_str = str(file_path).replace('\\', '/')
            current[title] = file_path_str
        
        # Convert the nested dictionary to MkDocs nav format
        def dict_to_nav(d: Dict[str, Any]) -> List[Any]:
            nav = []
            # Sort items to ensure consistent ordering
            for k, v in sorted(d.items()):
                if isinstance(v, str):
                    nav.append({k: v})
                else:
                    # Handle nested sections
                    subnav = dict_to_nav(v)
                    if subnav:  # Only add non-empty sections
                        nav.append({k: subnav})
            return nav
        
        return dict_to_nav(nav_structure)
    
    def generate(self, converted_files: Dict[Path, str]) -> None:
        """
        Generate the MkDocs configuration file.
        
        Args:
            converted_files: Dictionary mapping file paths to their titles
        """
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or generate config
        if self.custom_config:
            self._load_custom_config()
        else:
            self._generate_default_config()
        
        # Add navigation structure if we have files
        if converted_files:
            self.config_data['nav'] = self._build_nav_structure(converted_files)
        
        # Write config file
        config_path = self.output_dir / 'mkdocs.yml'
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(
                    self.config_data,
                    f,
                    default_flow_style=False,
                    sort_keys=False,
                    allow_unicode=True,
                    encoding='utf-8'
                )
            logger.info(f"Generated MkDocs configuration at {config_path}")
        except Exception as e:
            logger.error(f"Failed to write MkDocs configuration: {str(e)}")
            raise
