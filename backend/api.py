from flask import Blueprint, jsonify, request, current_app
import logging
from scraper import scrape_awwwards
from models import Website, ColorPalette
import json
import os

logger = logging.getLogger(__name__)

# Create API blueprint
api = Blueprint('api', __name__)

@api.route('/websites', methods=['GET'])
def get_websites():
    """Get all websites with their color palettes"""
    try:
        # In a real application, this would query a database
        # For now, we'll read from a JSON file
        data_file = os.path.join(current_app.config['DATA_DIR'], 'websites.json')
        
        if not os.path.exists(data_file):
            return jsonify([]), 200
        
        with open(data_file, 'r') as f:
            websites = json.load(f)
        
        # Add pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        start = (page - 1) * per_page
        end = start + per_page
        
        return jsonify({
            'websites': websites[start:end],
            'total': len(websites),
            'page': page,
            'per_page': per_page,
            'total_pages': (len(websites) + per_page - 1) // per_page
        }), 200
    
    except Exception as e:
        logger.exception("Error retrieving websites")
        return jsonify({"error": str(e)}), 500

@api.route('/websites/<website_id>', methods=['GET'])
def get_website(website_id):
    """Get a specific website by ID"""
    try:
        data_file = os.path.join(current_app.config['DATA_DIR'], 'websites.json')
        
        if not os.path.exists(data_file):
            return jsonify({"error": "Website not found"}), 404
        
        with open(data_file, 'r') as f:
            websites = json.load(f)
        
        # Find website by ID
        website = next((w for w in websites if w['id'] == website_id), None)
        
        if not website:
            return jsonify({"error": "Website not found"}), 404
        
        return jsonify(website), 200
    
    except Exception as e:
        logger.exception(f"Error retrieving website {website_id}")
        return jsonify({"error": str(e)}), 500

@api.route('/palettes', methods=['GET'])
def get_palettes():
    """Get all color palettes"""
    try:
        # In a real application, this would query a database
        # For now, we'll extract palettes from the websites data
        data_file = os.path.join(current_app.config['DATA_DIR'], 'websites.json')
        
        if not os.path.exists(data_file):
            return jsonify([]), 200
        
        with open(data_file, 'r') as f:
            websites = json.load(f)
        
        # Extract only the palettes
        palettes = [{'id': w['id'], 'url': w['url'], 'colors': w['palette']} for w in websites if 'palette' in w]
        
        # Add pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        start = (page - 1) * per_page
        end = start + per_page
        
        return jsonify({
            'palettes': palettes[start:end],
            'total': len(palettes),
            'page': page,
            'per_page': per_page,
            'total_pages': (len(palettes) + per_page - 1) // per_page
        }), 200
    
    except Exception as e:
        logger.exception("Error retrieving palettes")
        return jsonify({"error": str(e)}), 500

@api.route('/trigger-scrape', methods=['POST'])
def trigger_scrape():
    """Manually trigger scraping (protected by API key)"""
    try:
        # Check for API key in headers
        api_key = request.headers.get('X-API-Key')
        if api_key != current_app.config['API_KEY']:
            return jsonify({"error": "Unauthorized"}), 401
        
        # Get optional parameters
        pages = request.json.get('pages', 1)
        section = request.json.get('section', 'websites')
        
        # Trigger scraping in a background thread to not block the response
        import threading
        thread = threading.Thread(target=scrape_awwwards, kwargs={
            'pages': pages,
            'section': section
        })
        thread.daemon = True
        thread.start()
        
        return jsonify({"message": "Scraping initiated"}), 202
    
    except Exception as e:
        logger.exception("Error triggering scrape")
        return jsonify({"error": str(e)}), 500

@api.route('/search', methods=['GET'])
def search():
    """Search websites by tags, title, or colors"""
    try:
        # Get search parameters
        query = request.args.get('q', '').lower()
        tag = request.args.get('tag', '').lower()
        color = request.args.get('color', '').lower().lstrip('#')
        
        data_file = os.path.join(current_app.config['DATA_DIR'], 'websites.json')
        
        if not os.path.exists(data_file):
            return jsonify([]), 200
        
        with open(data_file, 'r') as f:
            websites = json.load(f)
        
        # Filter websites
        results = websites
        
        if query:
            results = [w for w in results if query in w.get('title', '').lower() or 
                      any(query in tag.lower() for tag in w.get('tags', []))]
        
        if tag:
            results = [w for w in results if tag in [t.lower() for t in w.get('tags', [])]]
        
        if color:
            # Match websites with a color similar to the search color
            def is_color_similar(hex_color1, hex_color2, threshold=30):
                # Convert hex to RGB
                r1, g1, b1 = int(hex_color1[0:2], 16), int(hex_color1[2:4], 16), int(hex_color1[4:6], 16)
                r2, g2, b2 = int(hex_color2[0:2], 16), int(hex_color2[2:4], 16), int(hex_color2[4:6], 16)
                
                # Calculate Euclidean distance
                distance = ((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) ** 0.5
                return distance <= threshold
            
            results = [w for w in results if any(is_color_similar(color, c.lstrip('#').lower()) 
                                               for c in w.get('palette', []))]
        
        # Add pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        start = (page - 1) * per_page
        end = start + per_page
        
        return jsonify({
            'websites': results[start:end],
            'total': len(results),
            'page': page,
            'per_page': per_page,
            'total_pages': (len(results) + per_page - 1) // per_page
        }), 200
    
    except Exception as e:
        logger.exception("Error searching websites")
        return jsonify({"error": str(e)}), 500

def setup_routes(app):
    """Register API blueprint with the app"""
    app.register_blueprint(api, url_prefix='/api')
