"""
Document to Site Converter
"""

from pathlib import Path
from typing import Optional

from .converter import Converter

__version__ = "0.1.0"


def convert(
    input_dir: str | Path, output_dir: str | Path, config: Optional[str | Path] = None
) -> None:
    """
    Convert documents to a MkDocs site.

    Args:
        input_dir: Directory containing input documents
        output_dir: Directory where the MkDocs site will be generated
        config: Optional path to custom MkDocs configuration
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    config_path = Path(config) if config else None

    converter = Converter(input_path, output_path, config_path)
    converter.convert()
