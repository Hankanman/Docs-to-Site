![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/Hankanman/Docs-to-Site/test.yml)
[![codecov](https://codecov.io/github/Hankanman/Docs-to-Site/graph/badge.svg?token=8L0V5NJFLN)](https://codecov.io/github/Hankanman/Docs-to-Site)

# Docs-to-Site

A Python-based tool that converts various document formats into a hosted MkDocs site using GitHub Pages. The tool utilizes the markitdown library for document conversion and MkDocs for static site generation.

## Features

- Convert various document formats to Markdown:
  - Documents: PDF, DOC, DOCX, RTF, ODT, TXT
  - Presentations: PPT, PPTX (with image extraction)
  - Spreadsheets: XLS, XLSX, CSV
  - Images: JPG, JPEG, PNG, GIF, BMP, WEBP
  - Audio: MP3, WAV, M4A, OGG, FLAC
  - Web: HTML, HTM
  - Data formats: JSON, XML
  - Archives: ZIP
- Extract and organize images from PowerPoint presentations
- Generate MkDocs site configuration with:
  - Automatic navigation structure
  - Material theme with modern features
  - Proper image handling and paths
- Create organized documentation structure
- GitHub Pages integration

## Installation

### From PyPI (not yet available)
```bash
pip install docs-to-site
```

### From Source
```bash
# Clone the repository
git clone https://github.com/yourusername/Docs-to-Site.git
cd Docs-to-Site

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

### Dependencies Only
```bash
# Production dependencies
pip install -r requirements.txt

# Development dependencies
pip install -r requirements-dev.txt
```

## Usage

Basic conversion:
```bash
Docs-to-Site convert /path/to/input/folder /path/to/output/folder
```

With custom MkDocs configuration:
```bash
Docs-to-Site convert /path/to/input/folder /path/to/output/folder --config /path/to/mkdocs.yml
```

For more detailed options:
```bash
Docs-to-Site --help
```

### Output Structure

The converter creates the following structure in your output directory:
```
output/
├── docs/
│   ├── images/
│   │   └── [document-name]/
│   │       └── image_1.png
│   └── converted_doc.md
└── mkdocs.yml
```

## Development

1. Install development dependencies:
```bash
pip install -e ".[dev]"
```

2. Run tests:
```bash
pytest
```

3. Run code quality checks:
```bash
black .
isort .
flake8
mypy src tests
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 