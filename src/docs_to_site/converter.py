"""
Main document conversion orchestration.
"""
import logging
from pathlib import Path
from typing import Optional, List, Tuple, Dict

from .document_converter import DocumentConverter
from .mkdocs_config import MkDocsConfig

logger = logging.getLogger(__name__)

class Converter:
    """Main converter class that orchestrates the document conversion process."""
    
    def __init__(self, input_dir: Path, output_dir: Path, config: Optional[Path] = None):
        """
        Initialize the converter.
        
        Args:
            input_dir: Directory containing input documents
            output_dir: Directory where the MkDocs site will be generated
            config: Optional path to custom MkDocs configuration
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.config = config
        
        # Initialize components
        self.document_converter = DocumentConverter(input_dir, output_dir)
        self.mkdocs = MkDocsConfig(output_dir, self.document_converter.docs_dir, config)
        
        # Track conversion results
        self.conversion_errors: List[Tuple[Path, str]] = []
        self.inaccessible_files: List[Path] = []
        self.succeeded = 0
        self.total = 0
    
    def convert(self) -> None:
        """
        Convert all documents in the input directory to a MkDocs site.
        
        Raises:
            ValueError: If no supported documents are found
            OSError: If there are file system related errors
        """
        logger.info(f"Starting document conversion from {self.input_dir} to {self.output_dir}")
        
        try:
            # Get all documents
            documents = self.document_converter.get_documents()
            if not documents:
                raise ValueError(f"No supported documents found in {self.input_dir}")
            
            self.total = len(documents)
            
            # Convert documents
            for doc, is_accessible in documents:
                if not is_accessible:
                    self.inaccessible_files.append(doc)
                    continue
                
                try:
                    self.document_converter.convert_document(doc)
                    self.succeeded += 1
                except (PermissionError, OSError):
                    self.inaccessible_files.append(doc)
                except Exception as e:
                    logger.error(f"Failed to convert {doc}: {str(e)}")
                    self.conversion_errors.append((doc, str(e)))
            
            # Generate MkDocs configuration
            self.mkdocs.generate(self.document_converter.converted_files)
            
            # Report conversion summary
            self._report_summary()
            
        finally:
            # Ensure cleanup is called even if conversion fails
            self.cleanup()
    
    def _report_summary(self) -> None:
        """Report the conversion summary to the logger."""
        failed = len(self.conversion_errors)
        inaccessible = len(self.inaccessible_files)
        
        logger.info("Document conversion complete:")
        logger.info(f"- Successfully converted: {self.succeeded}/{self.total} documents")
        
        if self.inaccessible_files:
            logger.warning(
                "The following files could not be accessed (they may be open in another program):"
            )
            for doc in self.inaccessible_files:
                logger.warning(f"- {doc}")
                
        if self.conversion_errors:
            logger.warning("The following documents failed to convert:")
            for doc, error in self.conversion_errors:
                logger.warning(f"- {doc}: {error}")
    
    def cleanup(self) -> None:
        """Clean up resources used by the converter."""
        self.document_converter.cleanup()
    
    @property
    def failed_count(self) -> int:
        """Get the number of failed conversions."""
        return len(self.conversion_errors)
    
    @property
    def inaccessible_count(self) -> int:
        """Get the number of inaccessible files."""
        return len(self.inaccessible_files)
    
    @property
    def success_rate(self) -> float:
        """Get the conversion success rate as a percentage."""
        if self.total == 0:
            return 0.0
        return (self.succeeded / self.total) * 100
