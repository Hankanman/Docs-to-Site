"""
Command-line interface for the Markdown Document Converter.
"""
import click
from pathlib import Path
from . import convert as convert_docs
from .ui import ConverterUI
import logging


@click.group()
def cli():
    """Convert various document formats to a MkDocs site."""
    pass


@cli.command()
@click.argument('input_dir', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.argument('output_dir', type=click.Path(file_okay=False, dir_okay=True))
@click.option('--config', '-c', type=click.Path(exists=True, dir_okay=False), help='Custom MkDocs configuration file')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def convert(input_dir: str, output_dir: str, config: str | None = None, verbose: bool = False):
    """Convert documents from INPUT_DIR to OUTPUT_DIR."""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    convert_docs(input_dir, output_dir, config)


@cli.command()
def gui():
    """Launch the graphical user interface."""
    app = ConverterUI()
    app.run()


def main():
    cli()


if __name__ == "__main__":
    main() 