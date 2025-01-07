"""
Main document conversion orchestration.
"""
import logging
from pathlib import Path
from typing import Optional

from .document_converter import DocumentConverter
from .mkdocs_config import generate_mkdocs_config

logger = logging.getLogger(__name__)

def convert_documents(input_dir: Path, output_dir: Path, config: Optional[Path] = None) -> None:
    """
    Convert all documents in the input directory to a MkDocs site.
    
    Args:
        input_dir: Directory containing input documents
        output_dir: Directory where the MkDocs site will be generated
        config: Optional path to custom MkDocs configuration
    """
    logger.info(f"Starting document conversion from {input_dir} to {output_dir}")

    # Initialize converter
    converter = DocumentConverter(input_dir, output_dir)

    # Get all documents
    documents = converter.get_documents()
    if not documents:
        raise ValueError(f"No supported documents found in {input_dir}")

    # Convert documents
    conversion_errors = []
    inaccessible_files = []

    for doc, is_accessible in documents:
        if not is_accessible:
            inaccessible_files.append(doc)
            continue

        try:
            converter.convert_document(doc)
        except (PermissionError, OSError):
            inaccessible_files.append(doc)
        except Exception as e:
            logger.error(f"Failed to convert {doc}: {str(e)}")
            conversion_errors.append((doc, str(e)))

    # Generate MkDocs configuration
    generate_mkdocs_config(
        output_dir=output_dir,
        docs_dir=converter.docs_dir,
        converted_files=converter.converted_files,
        custom_config=config
    )

    # Report conversion summary
    total = len(documents)
    inaccessible = len(inaccessible_files)
    failed = len(conversion_errors)
    succeeded = total - failed - inaccessible

    logger.info(f"Document conversion complete:")
    logger.info(f"- Successfully converted: {succeeded}/{total} documents")
    if inaccessible_files:
        logger.warning("The following files could not be accessed (they may be open in another program):")
        for doc in inaccessible_files:
            logger.warning(f"- {doc}")
    if conversion_errors:
        logger.warning("The following documents failed to convert:")
        for doc, error in conversion_errors:
            logger.warning(f"- {doc}: {error}") 