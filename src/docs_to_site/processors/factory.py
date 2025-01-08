"""
Factory for creating and managing document processors.
"""

from pathlib import Path
from typing import List, Type

from . import BaseProcessor
from .general_processor import GeneralProcessor
from .pdf_processor import PDFProcessor
from .presentation_processor import PresentationProcessor

class ProcessorFactory:
    """Factory for creating document processors."""
    
    def __init__(self) -> None:
        """Initialize the processor factory."""
        self._general_processor = GeneralProcessor()
        self._processors = {
            '.pdf': PDFProcessor(),
            '.pptx': PresentationProcessor(),
            '.ppt': PresentationProcessor(),
        }
    
    def get_processors(self, file_path: Path) -> List[BaseProcessor]:
        """
        Get the appropriate processors for a given file.
        
        Args:
            file_path: Path to the file being processed
            
        Returns:
            List of processors to apply in order
        """
        processors = [self._general_processor]  # Always apply general processor
        
        # Add format-specific processor if available
        suffix = file_path.suffix.lower()
        if suffix in self._processors:
            processors.append(self._processors[suffix])
            
        return processors
    
    def cleanup(self) -> None:
        """Cleanup all processors."""
        self._general_processor.cleanup()
        for processor in self._processors.values():
            processor.cleanup() 