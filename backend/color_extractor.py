from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
import logging
import os
import colorsys

logger = logging.getLogger(__name__)

def extract_colors_from_image(image_path, num_colors=5, resize_width=200):
    """
    Extract dominant colors from an image using K-means clustering
    
    Args:
        image_path: Path to the image file
        num_colors: Number of colors to extract
        resize_width: Width to resize the image to before processing
    
    Returns:
        List of hex color codes
    """
    try:
        # Check if the file exists
        if not os.path.exists(image_path):
            logger.error(f"Image file not found: {image_path}")
            return []
        
        # Open the image
        img = Image.open(image_path)
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize to speed up processing
        width, height = img.size
        new_height = int(height * resize_width / width)
        img = img.resize((resize_width, new_height), Image.LANCZOS)
        
        # Convert to numpy array
        img_array = np.array(img)
        
        # Reshape to a list of RGB pixels
        pixels = img_array.reshape(-1, 3)
        
        # Remove white, black, and near-white/black pixels
        filtered_pixels = []
        for pixel in pixels:
            r, g, b = pixel
            # Skip near-white pixels
            if r > 240 and g > 240 and b > 240:
                continue
            # Skip near-black pixels
            if r < 15 and g < 15 and b < 15:
                continue
            filtered_pixels.append(pixel)
        
        if len(filtered_pixels) < 100:
            # Not enough pixels after filtering, use original pixels
            filtered_pixels = pixels
        else:
            filtered_pixels = np.array(filtered_pixels)
        
        # Apply K-means clustering
        kmeans = KMeans(n_clusters=num_colors, random_state=42, n_init=10)
        kmeans.fit(filtered_pixels)
        
        # Get the RGB values of the cluster centers
        colors = kmeans.cluster_centers_.astype(int)
        
        # Convert to hex color codes
        hex_colors = []
        for color in colors:
            r, g, b = color
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            hex_colors.append(hex_color)
        
        # Order colors by visual appeal
        ordered_colors = order_colors_by_appeal(colors)
        
        logger.info(f"Extracted {len(ordered_colors)} colors from {image_path}")
        return ordered_colors
    
    except Exception as e:
        logger.exception(f"Error extracting colors from {image_path}: {e}")
        return []

def order_colors_by_appeal(colors):
    """
    Order colors by visual appeal
    
    Strategy:
    1. Convert to HSV
    2. Order by saturation (more saturated is more visually appealing)
    3. For similar saturation, order by value (brightness)
    """
    color_features = []
    
    for color in colors:
        r, g, b = color
        # Convert to HSV
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        
        # Create a score prioritizing saturation and value
        # Saturation is weighted more (0.7) than value (0.3)
        appeal_score = 0.7 * s + 0.3 * v
        
        # Add to list with original RGB
        color_features.append({
            'rgb': (r, g, b),
            'hsv': (h, s, v),
            'appeal_score': appeal_score
        })
    
    # Sort by appeal score, descending
    sorted_colors = sorted(color_features, key=lambda x: x['appeal_score'], reverse=True)
    
    # Convert back to hex
    ordered_hex_colors = []
    for color in sorted_colors:
        r, g, b = color['rgb']
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        ordered_hex_colors.append(hex_color)
    
    return ordered_hex_colors

def calculate_color_contrast(color1, color2):
    """
    Calculate contrast ratio between two colors as per WCAG 2.0
    
    This is useful for ensuring text is readable against backgrounds
    """
    # Convert hex to RGB
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    # Calculate luminance
    def luminance(rgb):
        rgb_srgb = [c / 255.0 for c in rgb]
        rgb_linear = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb_srgb]
        return 0.2126 * rgb_linear[0] + 0.7152 * rgb_linear[1] + 0.0722 * rgb_linear[2]
    
    # Calculate contrast ratio
    l1 = luminance(hex_to_rgb(color1))
    l2 = luminance(hex_to_rgb(color2))
    
    if l1 > l2:
        return (l1 + 0.05) / (l2 + 0.05)
    else:
        return (l2 + 0.05) / (l1 + 0.05)

def generate_accessible_text_color(background_color):
    """
    Generate an accessible text color (black or white) based on the background color
    """
    # Convert hex to RGB
    bg_hex = background_color.lstrip('#')
    r, g, b = tuple(int(bg_hex[i:i+2], 16) for i in (0, 2, 4))
    
    # Calculate perceived brightness
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    
    # Use white text on dark backgrounds, black text on light backgrounds
    if brightness < 128:
        return "#ffffff"  # White text
    else:
        return "#000000"  # Black text

if __name__ == "__main__":
    # For testing the color extractor directly
    logging.basicConfig(level=logging.INFO)
    
    # Test with a sample image
    test_image = "test.jpg"
    if os.path.exists(test_image):
        colors = extract_colors_from_image(test_image)
        print(f"Extracted colors: {colors}")
