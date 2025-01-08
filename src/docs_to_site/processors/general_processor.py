"""
General post-processing functionality that applies to all document types.
"""

from typing import Optional, Dict, Any
import re
from pathlib import Path
from . import BaseProcessor

class GeneralProcessor(BaseProcessor):
    """Handles common post-processing tasks for all document types."""
    
    def __init__(self) -> None:
        """Initialize the general processor."""
        super().__init__()
    
    def process(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Apply general markdown formatting improvements.
        
        Args:
            content: The content to process
            metadata: Optional metadata from the document
            
        Returns:
            Properly formatted markdown content
        """
        content = self._clean_whitespace(content)
        content = self._format_links(content)
        content = self._format_images(content)
        content = self._format_lists(content)
        content = self._format_code_blocks(content)
        
        return content
    
    def _clean_whitespace(self, content: str) -> str:
        """Clean up problematic whitespace."""
        # Remove problematic whitespace characters
        content = content.replace("\v", " ")
        content = re.sub(r"[\f\r]", "", content)
        
        # Normalize line endings
        content = re.sub(r"\n{3,}", "\n\n", content)
        
        return content
    
    def _format_links(self, content: str) -> str:
        """Format and validate markdown links."""
        # Convert URLs to markdown links if not already
        url_pattern = r"(?<![\[\(])(https?://[^\s\)\]]+)"
        content = re.sub(
            url_pattern,
            lambda m: f"[{m.group(0)}]({m.group(0)})",
            content
        )
        return content
    
    def _format_images(self, content: str) -> str:
        """Format and validate image references."""
        # Fix newlines in image alt text
        content = re.sub(
            r"!\[(.*?)\n+(.*?)\]\((.*?)\)",
            lambda m: f"![{m.group(1)} {m.group(2)}]({m.group(3)})",
            content
        )
        return content
    
    def _format_lists(self, content: str) -> str:
        """Format markdown lists for consistency."""
        # Add proper spacing around bullet points
        content = re.sub(
            r"(\n[*-] .+?)(\n[^*\n-])",
            r"\1\n\2",
            content
        )
        return content
    
    def _format_code_blocks(self, content: str) -> str:
        """Format code blocks and inline code."""
        # TODO: Implement code block formatting
        return content 