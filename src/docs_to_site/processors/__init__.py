"""
Base classes for document post-processors.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any

class BaseProcessor(ABC):
    """Base class for all document processors."""
    
    def __init__(self) -> None:
        """Initialize the processor."""
        pass
    
    @abstractmethod
    def process(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Process the content and return the processed result.
        
        Args:
            content: The content to process
            metadata: Optional metadata from the original document
            
        Returns:
            The processed content
        """
        pass
    
    def cleanup(self) -> None:
        """Cleanup any resources used by the processor."""
        pass 