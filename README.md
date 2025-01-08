![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/Hankanman/Docs-to-Site/test.yml)
[![codecov](https://codecov.io/github/Hankanman/Docs-to-Site/graph/badge.svg?token=8L0V5NJFLN)](https://codecov.io/github/Hankanman/Docs-to-Site)

# Docs-to-Site

A Python-based tool that converts various document formats into a hosted MkDocs site using GitHub Pages. The tool utilizes the markitdown library for document conversion and MkDocs for static site generation.

## Features

- Convert various document formats to Markdown:
  - Documents: DOCX, DOC, RTF, ODT, TXT
  - Presentations: PPT, PPTX
  - Markdown: MD
- Generate MkDocs site configuration with:
  - Automatic navigation structure
  - Material theme with modern features
- Create organized documentation structure
- GitHub Pages integration

## Requirements

### Python Dependencies
- Python 3.9 or higher
- Dependencies listed in `requirements.txt`

## Installation

1. Install Python package:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Basic usage:
   ```bash
   python -m docs_to_site convert input_folder output_folder
   ```

2. With custom MkDocs config:
   ```bash
   python -m docs_to_site convert input_folder output_folder --config custom_mkdocs.yml
   ```

3. Using the GUI:
   ```bash
   python -m docs_to_site gui
   ```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 