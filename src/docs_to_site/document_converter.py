"""
Core document conversion functionality.
"""

import logging
from pathlib import Path
from typing import Dict, List, Tuple

from markitdown import MarkItDown, UnsupportedFormatException, FileConversionException

from .utils import sanitize_filename, sanitize_title, SUPPORTED_FORMATS
from .processors.factory import ProcessorFactory

logger = logging.getLogger(__name__)


class DocumentConverter:
    """Handles the conversion of documents to Markdown and MkDocs site generation."""

    def __init__(self, input_dir: Path, output_dir: Path) -> None:
        """
        Initialize the document converter.

        Args:
            input_dir: Directory containing input documents
            output_dir: Directory where the MkDocs site will be generated
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.docs_dir = output_dir / "docs"
        self.images_dir = self.docs_dir / "images"
        self.converter = MarkItDown()
        self.processor_factory = ProcessorFactory()
        self.converted_files: Dict[Path, str] = {}  # Maps output paths to titles

    def is_supported_format(self, file_path: Path) -> bool:
        """Check if a file has a supported format."""
        return file_path.suffix.lower() in SUPPORTED_FORMATS

    def get_documents(self) -> List[Tuple[Path, bool]]:
        """
        Find all supported documents in the input directory.

        Returns:
            List of tuples containing (file_path, is_accessible)
        """
        documents = []
        for file in self.input_dir.rglob("*"):
            if file.is_file() and self.is_supported_format(file):
                # Check if file is accessible
                try:
                    with open(file, "rb") as f:
                        f.read(1)
                    documents.append((file, True))
                    logger.info(f"Found supported document: {file}")
                except (PermissionError, OSError):
                    logger.warning(
                        f"File {file} exists but cannot be accessed. It may be open in another program."
                    )
                    documents.append((file, False))

        logger.info(f"Found {len(documents)} supported documents")
        if not documents:
            logger.warning(
                f"No supported documents found. Supported formats are: {', '.join(sorted(SUPPORTED_FORMATS))}"
            )
        return documents

    def convert_document(self, document: Path) -> Path:
        """
        Convert a single document to Markdown.

        Args:
            document: Path to the document to convert

        Returns:
            Path to the converted Markdown file

        Raises:
            FileConversionException: If the file cannot be converted
            PermissionError: If the file cannot be accessed
            OSError: If there are file system related errors
        """
        relative_path = document.relative_to(self.input_dir)
        # Sanitize the filename part while keeping the directory structure
        sanitized_name = sanitize_filename(relative_path.stem) + ".md"
        sanitized_path = relative_path.parent / sanitized_name
        output_path = self.docs_dir / sanitized_path

        output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Converting {document} to {output_path}")
        try:
            # First check if we can access the file
            with open(document, "rb") as f:
                f.read(1)

            # Convert document to Markdown using MarkItDown
            result = self.converter.convert_local(str(document))

            # Get the title and content
            title = getattr(result, "title", None)
            if not title:
                # Use the filename without extension as title if no title is found
                title = document.stem
            title = sanitize_title(title)

            content = result.text_content

            # If we have a title, add it as a header
            markdown_content = f"# {title}\n\n" if title else ""
            markdown_content += content

            # Apply post-processing
            processors = self.processor_factory.get_processors(document)
            for processor in processors:
                markdown_content = processor.process(
                    markdown_content, metadata=getattr(result, "metadata", None)
                )

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)

            # Store the title for navigation
            relative_output = output_path.relative_to(self.docs_dir)
            self.converted_files[relative_output] = title

            return output_path

        except (UnsupportedFormatException, FileConversionException) as e:
            logger.error(f"Failed to convert {document}: {str(e)}")
            raise

    def cleanup(self) -> None:
        """Cleanup resources used by the converter."""
        self.processor_factory.cleanup()
