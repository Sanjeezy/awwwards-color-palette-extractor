import os
import json
import logging
import shutil
from typing import List, Dict, Any
import requests
from PIL import Image
from io import BytesIO
import re
import time
from functools import wraps
import threading

logger = logging.getLogger(__name__)

def rate_limited(max_per_minute):
    """
    Decorator to rate limit function calls
    
    Args:
        max_per_minute: Maximum number of calls per minute
    """
    lock = threading.Lock()
    min_interval = 60.0 / max_per_minute
    last_time_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with lock:
                elapsed = time.time() - last_time_called[0]
                left_to_wait = min_interval - elapsed
                
                if left_to_wait > 0:
                    time.sleep(left_to_wait)
                
                last_time_called[0] = time.time()
            
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator

def ensure_directory(path):
    """
    Ensure a directory exists
    
    Args:
        path: Directory path
    """
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        logger.info(f"Created directory: {path}")

def save_json(data, file_path):
    """
    Save data to a JSON file
    
    Args:
        data: Data to save
        file_path: File path
    """
    # Ensure directory exists
    directory = os.path.dirname(file_path)
    ensure_directory(directory)
    
    # Create a temporary file to avoid corruption if the process is interrupted
    temp_file = f"{file_path}.tmp"
    
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Rename the temporary file to the target file
    os.replace(temp_file, file_path)
    
    logger.info(f"Saved data to {file_path}")

def load_json(file_path, default=None):
    """
    Load data from a JSON file
    
    Args:
        file_path: File path
        default: Default value if file doesn't exist
    
    Returns:
        Loaded data or default value
    """
    if not os.path.exists(file_path):
        return default
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def download_image_from_url(url, save_path=None):
    """
    Download image from URL
    
    Args:
        url: Image URL
        save_path: Path to save the image
    
    Returns:
        PIL Image object and saved path if successful, None otherwise
    """
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        
        img = Image.open(BytesIO(response.content))
        
        if save_path:
            directory = os.path.dirname(save_path)
            ensure_directory(directory)
            img.save(save_path)
            return img, save_path
        
        return img, None
    
    except Exception as e:
        logger.error(f"Failed to download image from {url}: {str(e)}")
        return None, None

def sanitize_filename(filename):
    """
    Sanitize a filename by removing invalid characters
    
    Args:
        filename: Filename to sanitize
    
    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    sanitized = re.sub(r'[^\w\-.]', '_', filename)
    
    # Ensure filename is not empty
    if not sanitized:
        sanitized = 'file'
    
    return sanitized

def generate_thumbnail(image_path, thumbnail_path, size=(200, 200)):
    """
    Generate a thumbnail from an image
    
    Args:
        image_path: Path to the original image
        thumbnail_path: Path to save the thumbnail
        size: Thumbnail size (width, height)
    
    Returns:
        Path to the thumbnail if successful, None otherwise
    """
    try:
        img = Image.open(image_path)
        img.thumbnail(size)
        
        # Ensure directory exists
        directory = os.path.dirname(thumbnail_path)
        ensure_directory(directory)
        
        img.save(thumbnail_path)
        return thumbnail_path
    
    except Exception as e:
        logger.error(f"Failed to generate thumbnail for {image_path}: {str(e)}")
        return None

def clean_url(url):
    """
    Clean a URL by removing trailing slashes and query parameters
    
    Args:
        url: URL to clean
    
    Returns:
        Cleaned URL
    """
    # Remove query parameters
    url = url.split('?')[0]
    
    # Remove trailing slash
    if url.endswith('/'):
        url = url[:-1]
    
    return url

def extract_domain(url):
    """
    Extract domain from URL
    
    Args:
        url: URL
    
    Returns:
        Domain
    """
    # Remove protocol
    domain = url.split('://')[-1]
    
    # Remove path
    domain = domain.split('/')[0]
    
    # Remove www
    if domain.startswith('www.'):
        domain = domain[4:]
    
    return domain

def calculate_file_hash(file_path):
    """
    Calculate file hash for caching purposes
    
    Args:
        file_path: Path to the file
    
    Returns:
        File hash
    """
    import hashlib
    
    hasher = hashlib.md5()
    
    with open(file_path, 'rb') as f:
        buf = f.read(65536)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(65536)
    
    return hasher.hexdigest()

def compare_colors(color1, color2, threshold=30):
    """
    Compare two colors and return True if they are similar
    
    Args:
        color1: First color in hex format
        color2: Second color in hex format
        threshold: Similarity threshold (0-255)
    
    Returns:
        True if colors are similar, False otherwise
    """
    # Convert hex to RGB
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    # Calculate Euclidean distance
    def color_distance(rgb1, rgb2):
        r1, g1, b1 = rgb1
        r2, g2, b2 = rgb2
        return ((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) ** 0.5
    
    rgb1 = hex_to_rgb(color1)
    rgb2 = hex_to_rgb(color2)
    
    return color_distance(rgb1, rgb2) <= threshold
