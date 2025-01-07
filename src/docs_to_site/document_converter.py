"""
Core document conversion functionality.
"""
import logging
import re
from pathlib import Path
from typing import Dict, List, Tuple

from markitdown import MarkItDown, UnsupportedFormatException, FileConversionException

from .image_processor import extract_pptx_images, copy_embedded_images
from .utils import sanitize_filename, sanitize_title, SUPPORTED_FORMATS

logger = logging.getLogger(__name__)

def format_markdown(content: str, document: Path, image_map: Dict[str, str] | None = None) -> str:
    """
    Format the Markdown content for better readability.
    
    Args:
        content: Original Markdown content
        document: Path to the source document
        image_map: Optional mapping of original image names to new paths
    
    Returns:
        Formatted Markdown content
    """
    # Clean up vertical tabs and other problematic whitespace
    content = content.replace('\v', ' ')  # Replace vertical tabs with newlines
    content = re.sub(r'[\f\r]', '', content)  # Remove form feeds and carriage returns
    
    # Fix newlines in image alt text
    content = re.sub(r'!\[(.*?)\n+(.*?)\]\((.*?)\)', lambda m: f'![{m.group(1)} {m.group(2)}]({m.group(3)})', content)
    
    # Ensure tables have newlines after them (only after the last row)
    content = re.sub(r'(\|[^\n]*\|)\s*\n(?!\|)', r'\1\n\n', content)
    
    # Format slide markers
    content = re.sub(r'<!-- Slide number: (\d+) -->', r'\n---\n### Slide \1\n', content)
    
    # Add proper spacing around headings
    content = re.sub(r'(#{1,6} .+?)(\n(?!#))', r'\1\n\2', content)
    
    # Add proper spacing around images
    content = re.sub(r'(!\[.*?\]\(.*?\))(\n[^!\n])', r'\1\n\2', content)
    
    # Add proper spacing around bullet points
    content = re.sub(r'(\n[*-] .+?)(\n[^*\n-])', r'\1\n\2', content)
    
    # Add proper spacing around sections
    content = re.sub(r'(\n\n[^#\n-].*?)(\n[^#\n-])', r'\1\n\2', content)
    
    # Update image paths if we have a mapping
    if image_map:
        # Log all image references in the markdown
        image_refs = re.findall(r'!\[(.*?)\]\((.*?)\)', content)
        logger.info(f"Found image references in markdown: {image_refs}")
        
        # First try to match exact filenames
        for old_name, new_path in image_map.items():
            pattern = rf'!\[(.*?)\]\({re.escape(old_name)}\)'
            if re.search(pattern, content):
                logger.debug(f"Found match for {old_name} -> {new_path}")
            content = re.sub(
                pattern,
                rf'![\1](images/{sanitize_filename(document.stem)}/{new_path})',
                content
            )

        # Then try to match using normalized names and handle extensions
        for match in re.finditer(r'!\[(.*?)\]\((.*?)\)', content):
            alt_text = match.group(1)
            img_name = match.group(2)
            base_name = Path(img_name).stem
            
            # Try different variations of the image name
            variations = [
                img_name,  # Original name
                Path(img_name).name,  # Just the filename
                base_name,  # Just the name without extension
                f"{base_name}.jpg",  # Common PowerPoint export extensions
                f"{base_name}.jpeg",
                f"{base_name}.png",
                f"{base_name}.gif",
            ]
            
            # Try to find a match using any of the variations
            found_match = False
            for var in variations:
                # Try exact match
                if var in image_map:
                    new_path = image_map[var]
                    logger.debug(f"Found variation match: {var} -> {new_path}")
                    content = content.replace(
                        match.group(0),
                        f'![{alt_text}](images/{sanitize_filename(document.stem)}/{new_path})'
                    )
                    found_match = True
                    break
                
                # Try normalized version
                norm_var = var.lower().replace(' ', '').replace('_', '').replace('.', '')
                if norm_var in image_map:
                    new_path = image_map[norm_var]
                    logger.debug(f"Found normalized match: {norm_var} -> {new_path}")
                    content = content.replace(
                        match.group(0),
                        f'![{alt_text}](images/{sanitize_filename(document.stem)}/{new_path})'
                    )
                    found_match = True
                    break
                
                # Try just the normalized base name
                norm_base = base_name.lower().replace(' ', '').replace('_', '')
                for mapped_name, mapped_path in image_map.items():
                    mapped_base = Path(mapped_name).stem.lower().replace(' ', '').replace('_', '')
                    if norm_base == mapped_base:
                        logger.debug(f"Found base name match: {norm_base} -> {mapped_path}")
                        content = content.replace(
                            match.group(0),
                            f'![{alt_text}](images/{sanitize_filename(document.stem)}/{mapped_path})'
                        )
                        found_match = True
                        break
                
                if found_match:
                    break
            
            if not found_match:
                logger.warning(f"No mapping found for image: {img_name}")
    
    # Fix any remaining absolute image paths
    content = re.sub(
        r'!\[(.*?)\]\(/images/',
        r'![\1](images/',
        content
    )
    
    # Remove any duplicate image paths
    content = re.sub(
        r'images/[^/]+/images/[^/]+/',
        lambda m: m.group(0).split('/', 1)[1],
        content
    )
    
    # Log any remaining unmatched image references
    remaining_refs = re.findall(r'!\[(.*?)\]\((.*?)\)', content)
    logger.info(f"Remaining image references after processing: {remaining_refs}")
    
    # Detect and format URLs that aren't already markdown links
    # First, exclude URLs that are already part of markdown links or images
    def is_in_markdown_link(match, text):
        # Check if the URL is already part of a markdown link
        start = max(0, match.start() - 50)  # Look at the 50 chars before the match
        end = min(len(text), match.end() + 50)  # Look at the 50 chars after the match
        context = text[start:end]
        
        # If there's a closing bracket before the URL and an opening bracket after,
        # it's likely already in a markdown link
        before = context[:match.start()-start]
        after = context[match.end()-start:]
        return '](' in before and ')' in after

    # URL regex pattern
    url_pattern = r'(?<![\[\(])(https?://[^\s\)\]]+)'
    
    # Find all URLs and replace them with markdown links if they're not already links
    content = re.sub(
        url_pattern,
        lambda m: m.group(0) if is_in_markdown_link(m, content) else f'[{m.group(0)}]({m.group(0)})',
        content
    )
    
    # Remove extra blank lines
    content = re.sub(r'\n{3,}', r'\n\n', content)
    
    return content

class DocumentConverter:
    """Handles the conversion of documents to Markdown and MkDocs site generation."""

    def __init__(self, input_dir: Path, output_dir: Path) -> None:
        """
        Initialize the document converter.

        Args:
            input_dir: Directory containing input documents
            output_dir: Directory where the MkDocs site will be generated
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.docs_dir = output_dir / 'docs'
        self.converter = MarkItDown()
        self.converted_files: Dict[Path, str] = {}  # Maps output paths to titles
        self.images_dir = self.docs_dir / 'images'

    def is_supported_format(self, file_path: Path) -> bool:
        """Check if a file has a supported format."""
        return file_path.suffix.lower() in SUPPORTED_FORMATS

    def get_documents(self) -> List[Tuple[Path, bool]]:
        """
        Find all supported documents in the input directory.
        
        Returns:
            List of tuples containing (file_path, is_accessible)
        """
        documents = []
        for file in self.input_dir.rglob('*'):
            if file.is_file() and self.is_supported_format(file):
                # Check if file is accessible
                try:
                    with open(file, 'rb') as f:
                        f.read(1)
                    documents.append((file, True))
                    logger.info(f"Found supported document: {file}")
                except (PermissionError, OSError):
                    logger.warning(f"File {file} exists but cannot be accessed. It may be open in another program.")
                    documents.append((file, False))

        logger.info(f"Found {len(documents)} supported documents")
        if not documents:
            logger.warning(f"No supported documents found. Supported formats are: {', '.join(sorted(SUPPORTED_FORMATS))}")
        return documents

    def convert_document(self, document: Path) -> Path:
        """
        Convert a single document to Markdown.

        Args:
            document: Path to the document to convert

        Returns:
            Path to the converted Markdown file

        Raises:
            FileConversionException: If the file cannot be converted
            PermissionError: If the file cannot be accessed
            OSError: If there are file system related errors
        """
        relative_path = document.relative_to(self.input_dir)
        # Sanitize the filename part while keeping the directory structure
        sanitized_name = sanitize_filename(relative_path.stem) + '.md'
        sanitized_path = relative_path.parent / sanitized_name
        output_path = self.docs_dir / sanitized_path
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Converting {document} to {output_path}")
        try:
            # First check if we can access the file
            with open(document, 'rb') as f:
                f.read(1)
            
            # Create document-specific images directory in the same directory as the markdown file
            doc_images_dir = output_path.parent / 'images' / sanitize_filename(document.stem)
            doc_images_dir.mkdir(parents=True, exist_ok=True)
            
            # Initialize image map
            image_map = {}
            
            # Copy any embedded images from the document's directory
            embedded_images = copy_embedded_images(document, doc_images_dir)
            if embedded_images:
                image_map.update(embedded_images)
            
            # Extract images if it's a PowerPoint file
            if document.suffix.lower() in {'.ppt', '.pptx'}:
                pptx_images = extract_pptx_images(document, doc_images_dir)
                if pptx_images:
                    image_map.update(pptx_images)
            
            # Convert document to Markdown
            result = self.converter.convert_local(str(document))
            
            # Get the title and content
            title = getattr(result, 'title', None)
            if not title:
                # Use the filename without extension as title if no title is found
                title = document.stem
            title = sanitize_title(title)
            
            content = result.text_content
            
            # If we have a title, add it as a header
            markdown_content = f"# {title}\n\n" if title else ""
            markdown_content += content
            
            # Format the content
            markdown_content = format_markdown(markdown_content, document, image_map)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            # Store the title for navigation
            relative_output = output_path.relative_to(self.docs_dir)
            self.converted_files[relative_output] = title
            
            return output_path
        except (PermissionError, OSError) as e:
            logger.error(f"Cannot access file {document}. The file may be open in another program or you may not have permission to access it.")
            raise
        except UnsupportedFormatException as e:
            logger.error(f"Unsupported format for file: {document}")
            raise
        except FileConversionException as e:
            logger.error(f"Error converting {document}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error converting {document}: {str(e)}")
            raise 