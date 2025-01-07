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
  - Supports all common image formats
  - Automatically converts WMF images to PNG (requires ImageMagick)
- Generate MkDocs site configuration with:
  - Automatic navigation structure
  - Material theme with modern features
  - Proper image handling and paths
- Create organized documentation structure
- GitHub Pages integration

## Requirements

### Python Dependencies
- Python 3.9 or higher
- Dependencies listed in `requirements.txt`

### System Dependencies
- ImageMagick (required for WMF image conversion)
  - Ubuntu/Debian: `sudo apt-get install imagemagick libmagickwand-dev`
  - macOS: `brew install imagemagick`
  - Windows: Install from [ImageMagick website](https://imagemagick.org/script/download.php) or via Chocolatey: `choco install imagemagick.app`

## Installation

1. Install system dependencies:
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install -y imagemagick libmagickwand-dev

   # macOS
   brew install imagemagick

   # Windows (using Chocolatey)
   choco install imagemagick.app
   ```

2. Install Python package:
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

## Notes

- If ImageMagick is not installed, WMF images from PowerPoint files will be skipped
- The tool will automatically detect ImageMagick availability and provide appropriate warnings
- For best results with PowerPoint presentations, ensure ImageMagick is properly installed

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 