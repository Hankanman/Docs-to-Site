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
from wand.color import Color

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

def convert_wmf_to_png(image_bytes: bytes, output_path: Path, is_icon: bool = True) -> Optional[Path]:
    """
    Convert WMF image to PNG or SVG format using ImageMagick.
    Attempts to preserve vector content by using direct ImageMagick commands.
    
    Args:
        image_bytes: The WMF image data
        output_path: The desired output path for the converted file
        is_icon: Whether the WMF is being used as an icon (affects size/density settings)
        
    Returns:
        Path to the converted file or None if conversion fails
    """
    # Check ImageMagick availability first
    is_available, message = check_imagemagick()
    if not is_available:
        logger.warning(f"Cannot convert WMF: {message}")
        return None

    try:
        # Create a temporary WMF file
        temp_wmf = output_path.with_suffix('.tmp.wmf')
        temp_wmf.write_bytes(image_bytes)
        
        try:
            # Try vector conversion first using direct ImageMagick command
            svg_path = output_path.with_suffix('.svg')
            
            # Adjust settings based on whether it's an icon
            density = '72' if is_icon else '300'
            size_param = ['-resize', '64x64>'] if is_icon else []  # Resize if larger than 64x64
            
            convert_cmd = [
                'magick',
                'convert',
                '-density', density,
                '-background', 'transparent',
                '-define', 'wmf:vector',
                '-define', 'wmf:preserve-vector',
                '-define', 'svg:include-xml',
                str(temp_wmf),
            ]
            
            # Add size parameter for icons
            if size_param:
                convert_cmd.extend(size_param)
                
            convert_cmd.append('SVG:' + str(svg_path))
            
            result = subprocess.run(convert_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                # Verify the SVG is not just a base64 wrapper
                svg_content = svg_path.read_text()
                if 'base64' not in svg_content and ('<path' in svg_content or '<polygon' in svg_content or '<rect' in svg_content):
                    logger.info(f"Successfully converted WMF to SVG: {svg_path}")
                    return svg_path
                else:
                    logger.warning("SVG conversion resulted in base64 encoding, falling back to PNG")
                    svg_path.unlink(missing_ok=True)
            
            # Fallback to PNG conversion
            png_path = output_path.with_suffix('.png')
            convert_cmd = [
                'magick',
                'convert',
                '-density', density,
                '-background', 'white',
                '-alpha', 'remove',
                str(temp_wmf),
            ]
            
            # Add size parameter for icons
            if size_param:
                convert_cmd.extend(size_param)
                
            convert_cmd.append(str(png_path))
            
            result = subprocess.run(convert_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"Successfully converted WMF to PNG: {png_path}")
                return png_path
            else:
                logger.warning(f"PNG conversion failed: {result.stderr}")
                return None
                
        finally:
            # Clean up temporary file
            temp_wmf.unlink(missing_ok=True)
                
    except Exception as e:
        logger.warning(f"Failed to convert WMF: {str(e)}")
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
    gif_map = {}  # Separate map for GIFs to ensure they take precedence
    try:
        prs = Presentation(document)
        image_count = 0
        
        for slide_num, slide in enumerate(prs.slides, 1):
            logger.debug(f"Processing slide {slide_num}")
            for shape in slide.shapes:
                if isinstance(shape, Picture):
                    try:
                        # Get image data and format
                        image = shape.image
                        image_bytes = image.blob
                        image_ext = image.ext.lower()
                        if not image_ext.startswith('.'):
                            image_ext = '.' + image_ext
                            
                        logger.debug(f"Found image in slide {slide_num}: format={image_ext}, shape_name={getattr(shape, 'name', 'N/A')}")

                        # Generate unique filename
                        image_count += 1
                        image_name = f"image_{image_count}{image_ext}"
                        image_path = doc_images_dir / image_name
                        
                        # Handle WMF files
                        if image_ext.lower() == '.wmf':
                            if is_available:
                                # Detect if it's being used as an icon based on size or placement
                                is_icon = True  # We're assuming all WMFs are icons as per requirement
                                png_path = convert_wmf_to_png(image_bytes, image_path, is_icon=is_icon)
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
                            logger.debug(f"Adding shape name to mapping: {shape.name}")
                        if hasattr(shape, 'image_filename'):
                            possible_names.append(shape.image_filename)
                            logger.debug(f"Adding image filename to mapping: {shape.image_filename}")
                        
                        # Add mappings for all possible names
                        for name in possible_names:
                            # Store the full name
                            if image_ext == '.gif':
                                gif_map[name] = image_name
                                gif_map[Path(name).name] = image_name
                                gif_map[normalize_image_name(name)] = image_name
                                gif_map[f"{normalize_image_name(name)}.gif"] = image_name
                                gif_map[f"{Path(name).stem}.gif"] = image_name
                            else:
                                image_map[name] = image_name
                                image_map[Path(name).name] = image_name
                                image_map[normalize_image_name(name)] = image_name
                                # Add common extensions for non-GIF images
                                for ext in ['.jpg', '.jpeg', '.png']:
                                    image_map[f"{normalize_image_name(name)}{ext}"] = image_name
                                    image_map[f"{Path(name).stem}{ext}"] = image_name
                        
                        logger.debug(f"Image mappings for {image_name}: {[k for k in image_map.keys() if image_map[k] == image_name]}")

                    except Exception as e:
                        logger.warning(f"Failed to extract image from shape in {document}: {str(e)}")
                        logger.debug(f"Shape details - name: {getattr(shape, 'name', 'N/A')}, type: {type(shape)}")

    except Exception as e:
        logger.warning(f"Failed to extract images from {document}: {str(e)}")
    
    # Merge GIF mappings into the main map, ensuring they take precedence
    image_map.update(gif_map)
    
    logger.info(f"Total images extracted: {image_count}")
    logger.debug(f"Final image mappings: {image_map}")
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