"""
Command-line interface for the Markdown Document Converter.
"""
import click
from pathlib import Path
from .converter import DocumentConverter
from .ui import ConverterUI


@click.group()
def cli():
    """Convert various document formats to a MkDocs site."""
    pass


@cli.command()
@click.argument('input_dir', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.argument('output_dir', type=click.Path(file_okay=False, dir_okay=True))
@click.option('--config', '-c', type=click.Path(exists=True, dir_okay=False), help='Custom MkDocs configuration file')
def convert(input_dir: str, output_dir: str, config: str | None = None):
    """Convert documents from INPUT_DIR to OUTPUT_DIR."""
    converter = DocumentConverter(
        Path(input_dir), 
        Path(output_dir),
        Path(config) if config else None
    )
    converter.convert()


@cli.command()
def gui():
    """Launch the graphical user interface."""
    app = ConverterUI()
    app.run()


def main():
    cli()


if __name__ == "__main__":
    main() 