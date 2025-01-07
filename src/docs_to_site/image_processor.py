"""
Image processing functionality for document conversion.
"""
import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Optional, Tuple
import io

from pptx import Presentation
from pptx.shapes.picture import Picture
from PIL import Image
from wand.image import Image as WandImage
from wand.exceptions import WandError

from .utils import sanitize_filename, IMAGE_FORMATS

logger = logging.getLogger(__name__)

def check_imagemagick() -> Tuple[bool, str]:
    """
    Check if ImageMagick is available in the system.
    
    Returns:
        Tuple of (is_available: bool, message: str)
    """
    try:
        with WandImage() as img:
            return True, "ImageMagick is available"
    except WandError as e:
        if "delegate" in str(e).lower() and "wmf" in str(e).lower():
            return False, "ImageMagick WMF delegate library is missing"
        return False, f"ImageMagick is not properly installed: {str(e)}"
    except Exception as e:
        return False, f"Failed to check ImageMagick: {str(e)}"

def normalize_image_name(name: str) -> str:
    """Normalize image name to handle variations in spacing and extensions."""
    # Remove extension
    base = str(Path(name).stem)
    # Remove spaces, underscores, and dots
    base = base.replace(' ', '').replace('_', '').replace('.', '')
    # Convert to lowercase for case-insensitive matching
    return base.lower()

def convert_wmf_to_png(image_bytes: bytes, output_path: Path) -> Optional[Path]:
    """
    Convert WMF image to PNG format using Wand (ImageMagick).
    
    Args:
        image_bytes: The WMF image data
        output_path: The desired output path for the PNG file
        
    Returns:
        Path to the converted PNG file or None if conversion fails
    """
    # Check ImageMagick availability first
    is_available, message = check_imagemagick()
    if not is_available:
        logger.warning(f"Cannot convert WMF: {message}")
        return None

    try:
        # Convert WMF to PNG using Wand
        png_path = output_path.with_suffix('.png')
        
        with WandImage(blob=image_bytes, format='wmf') as img:
            # Set resolution to ensure good quality
            img.resolution = (300, 300)
            # Convert to PNG
            img.format = 'png'
            img.save(filename=str(png_path))
            logger.info(f"Successfully converted WMF to PNG: {png_path}")
            return png_path
    except Exception as e:
        logger.warning(f"Failed to convert WMF to PNG using Wand: {str(e)}")
        return None

def extract_pptx_images(document: Path, doc_images_dir: Path) -> Dict[str, str]:
    """
    Extract images from a PowerPoint file.
    
    Args:
        document: Path to the PowerPoint file
        doc_images_dir: Directory to save images in
    
    Returns:
        Dictionary mapping original image filenames to new image paths
    """
    # Check ImageMagick at the start
    is_available, message = check_imagemagick()
    if not is_available:
        logger.warning(f"ImageMagick is not available: {message}. WMF images will be skipped.")

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

                        # Handle WMF files
                        if image_ext.lower() == '.wmf':
                            if is_available:
                                png_path = convert_wmf_to_png(image_bytes, image_path)
                                if png_path:
                                    image_name = png_path.name
                                    image_path = png_path
                                else:
                                    logger.warning(f"Skipping WMF image that couldn't be converted: {image_name}")
                                    continue
                            else:
                                logger.warning(f"Skipping WMF image due to missing ImageMagick: {image_name}")
                                continue
                        else:
                            # Save non-WMF image
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