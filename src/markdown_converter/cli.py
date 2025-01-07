"""
Command-line interface for the Markdown Document Converter.
"""
import click
from pathlib import Path
from typing import Optional

from . import __version__
from .converter import DocumentConverter


@click.group()
@click.version_option(version=__version__)
def cli() -> None:
    """Convert various document formats to a hosted MkDocs site."""
    pass


@cli.command()
@click.argument('input_dir', type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path))
@click.argument('output_dir', type=click.Path(file_okay=False, dir_okay=True, path_type=Path))
@click.option('--config', '-c', type=click.Path(exists=True, dir_okay=False, path_type=Path),
              help='Path to custom MkDocs configuration file.')
def convert(input_dir: Path, output_dir: Path, config: Optional[Path] = None) -> None:
    """
    Convert documents from INPUT_DIR and create a MkDocs site in OUTPUT_DIR.
    """
    converter = DocumentConverter(input_dir, output_dir, config)
    converter.convert()


def main() -> None:
    """Main entry point for the CLI."""
    cli() 