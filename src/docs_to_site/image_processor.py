"""
Image processing functionality for document conversion.
"""
import logging
import os
import shutil
from pathlib import Path
from typing import Dict, Optional

from pptx import Presentation
from pptx.shapes.picture import Picture

from .utils import sanitize_filename, IMAGE_FORMATS

logger = logging.getLogger(__name__)

def normalize_image_name(name: str) -> str:
    """Normalize image name to handle variations in spacing and extensions."""
    # Remove extension
    base = str(Path(name).stem)
    # Remove spaces, underscores, and dots
    base = base.replace(' ', '').replace('_', '').replace('.', '')
    # Convert to lowercase for case-insensitive matching
    return base.lower()

def extract_pptx_images(document: Path, doc_images_dir: Path) -> Dict[str, str]:
    """
    Extract images from a PowerPoint file.
    
    Args:
        document: Path to the PowerPoint file
        doc_images_dir: Directory to save images in
    
    Returns:
        Dictionary mapping original image filenames to new image paths
    """
    image_map = {}
    try:
        prs = Presentation(document)
        image_count = 0

        for slide in prs.slides:
            for shape in slide.shapes:
                if isinstance(shape, Picture):
                    try:
                        # Get image data and format
                        image = shape.image
                        image_bytes = image.blob
                        image_ext = image.ext.lower()
                        if not image_ext.startswith('.'):
                            image_ext = '.' + image_ext

                        # Generate unique filename
                        image_count += 1
                        image_name = f"image_{image_count}{image_ext}"
                        image_path = doc_images_dir / image_name

                        # Save image
                        with open(image_path, 'wb') as f:
                            f.write(image_bytes)
                        logger.info(f"Extracted image: {image_path}")

                        # Map all possible variations of the image name
                        possible_names = []
                        if hasattr(shape, 'name'):
                            possible_names.append(shape.name)
                        if hasattr(shape, 'image_filename'):
                            possible_names.append(shape.image_filename)
                        
                        # Add common PowerPoint image naming patterns
                        for name in possible_names:
                            # Store the full name
                            image_map[name] = image_name
                            # Store just the filename
                            image_map[Path(name).name] = image_name
                            # Store normalized name for matching
                            norm_name = normalize_image_name(name)
                            image_map[norm_name] = image_name
                            # Add common extensions
                            for ext in ['.jpg', '.jpeg', '.png', '.gif']:
                                image_map[f"{norm_name}{ext}"] = image_name
                            
                        logger.debug(f"Image mappings for {image_name}: {[k for k in image_map.keys() if image_map[k] == image_name]}")

                    except Exception as e:
                        logger.warning(f"Failed to extract image from shape in {document}: {str(e)}")
                        logger.debug(f"Shape details - name: {getattr(shape, 'name', 'N/A')}, type: {type(shape)}")

    except Exception as e:
        logger.warning(f"Failed to extract images from {document}: {str(e)}")

    logger.info(f"Total images extracted: {image_count}")
    logger.info(f"Image mappings: {image_map}")
    return image_map

def copy_embedded_images(document: Path, doc_images_dir: Path) -> Dict[str, str]:
    """
    Copy embedded images from the document's directory to the output images directory.
    
    Args:
        document: Path to the document being converted
        doc_images_dir: Directory to copy images to
        
    Returns:
        Dictionary mapping original image filenames to new paths
    """
    image_map = {}
    # Look for images in the same directory as the document
    doc_dir = document.parent
    for img_ext in IMAGE_FORMATS:
        for img_file in doc_dir.glob(f"*{img_ext}"):
            try:
                # Generate a sanitized name for the image
                sanitized_name = sanitize_filename(img_file.name)
                new_path = doc_images_dir / sanitized_name
                
                # Copy the image
                shutil.copy2(img_file, new_path)
                logger.info(f"Copied embedded image: {img_file} -> {new_path}")
                
                # Store both the original name and sanitized name in the map
                image_map[img_file.name] = sanitized_name
                image_map[sanitized_name] = sanitized_name
            except Exception as e:
                logger.warning(f"Failed to copy embedded image {img_file}: {str(e)}")
    
    return image_map 