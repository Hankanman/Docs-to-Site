"""
Command-line interface for the Markdown Document Converter.
"""
import logging
import sys
from pathlib import Path

import click

from .converter import DocumentConverter
from .cli import main

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

@click.group()
@click.version_option()
def cli():
    """Convert various document formats to a hosted MkDocs site."""
    pass

@cli.command()
@click.argument('input_dir', type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path))
@click.argument('output_dir', type=click.Path(file_okay=False, dir_okay=True, path_type=Path))
@click.option('--config', '-c', type=click.Path(exists=True, dir_okay=False, path_type=Path),
              help='Path to custom MkDocs configuration file.')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def convert(input_dir: Path, output_dir: Path, config: Path | None = None, verbose: bool = False):
    """
    Convert documents from INPUT_DIR and generate a MkDocs site in OUTPUT_DIR.
    
    The converter will:
    1. Find all supported documents in INPUT_DIR
    2. Convert them to Markdown
    3. Generate a MkDocs site configuration
    4. Save everything in OUTPUT_DIR
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        
    try:
        converter = DocumentConverter(input_dir, output_dir, config)
        converter.convert()
    except Exception as e:
        logging.error(str(e))
        sys.exit(1)

if __name__ == '__main__':
    main() 