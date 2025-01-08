"""
Command-line interface for the Markdown Document Converter.
"""

import logging

from .cli import main

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

if __name__ == "__main__":
    main()
