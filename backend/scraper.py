import requests
from bs4 import BeautifulSoup
import json
import os
import time
import random
import logging
import uuid
from datetime import datetime
from urllib.parse import urljoin
import io
from PIL import Image
import threading
from color_extractor import extract_colors_from_image
from config import Config

logger = logging.getLogger(__name__)

# Headers to mimic a real browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'DNT': '1',
}

# Base URL for Awwwards
BASE_URL = 'https://www.awwwards.com/'

# Lock for thread-safe file operations
file_lock = threading.Lock()

def scrape_awwwards(pages=5, section='websites'):
    """
    Scrape Awwwards websites
    
    Args:
        pages: Number of pages to scrape
        section: Section to scrape (websites, nominees, etc.)
    """
    logger.info(f"Starting scraping of {pages} pages from {section} section")
    
    # Create data directory if it doesn't exist
    os.makedirs(Config.DATA_DIR, exist_ok=True)
    os.makedirs(os.path.join(Config.DATA_DIR, 'images'), exist_ok=True)
    
    # Check if websites.json exists
    json_file = os.path.join(Config.DATA_DIR, 'websites.json')
    websites = []
    
    if os.path.exists(json_file):
        with open(json_file, 'r') as f:
            websites = json.load(f)
            logger.info(f"Loaded {len(websites)} existing websites from JSON")
    
    # Track URLs to avoid duplicates
    existing_urls = {website['url'] for website in websites}
    
    # Process each page
    for page in range(1, pages + 1):
        logger.info(f"Scraping page {page} of {pages}")
        
        try:
            # Construct the page URL
            if page == 1:
                url = urljoin(BASE_URL, section)
            else:
                url = urljoin(BASE_URL, f"{section}/page-{page}")
            
            # Make the request with a random delay to be respectful
            time.sleep(random.uniform(1, 3))
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find website entries
            website_items = soup.select('.grid-item')
            
            if not website_items:
                logger.warning(f"No website items found on page {page}")
                continue
            
            logger.info(f"Found {len(website_items)} website items on page {page}")
            
            # Process each website entry
            for item in website_items:
                try:
                    # Extract website data
                    website_data = extract_website_data(item)
                    
                    if not website_data or website_data['url'] in existing_urls:
                        continue
                    
                    # Download and process image
                    if 'image_url' in website_data:
                        image_filename = download_image(website_data['image_url'], website_data['id'])
                        
                        if image_filename:
                            website_data['local_image'] = image_filename
                            
                            # Extract color palette
                            image_path = os.path.join(Config.DATA_DIR, 'images', image_filename)
                            palette = extract_colors_from_image(image_path)
                            
                            if palette:
                                website_data['palette'] = palette
                    
                    # Add to our list and update existing_urls
                    websites.append(website_data)
                    existing_urls.add(website_data['url'])
                    
                    # Save periodically to avoid losing data if the process crashes
                    if len(websites) % 10 == 0:
                        with file_lock:
                            with open(json_file, 'w') as f:
                                json.dump(websites, f, indent=2)
                
                except Exception as e:
                    logger.exception(f"Error processing website item: {e}")
        
        except Exception as e:
            logger.exception(f"Error scraping page {page}: {e}")
    
    # Final save
    with file_lock:
        with open(json_file, 'w') as f:
            json.dump(websites, f, indent=2)
    
    logger.info(f"Scraping complete. {len(websites)} websites in the database.")
    return len(websites)

def extract_website_data(item):
    """Extract website data from a HTML item"""
    try:
        # Main website data
        website = {
            'id': str(uuid.uuid4()),
            'scraped_at': datetime.now().isoformat()
        }
        
        # Title
        title_element = item.select_one('.title')
        if title_element:
            website['title'] = title_element.get_text(strip=True)
        
        # URL
        url_element = item.select_one('a.js-visit-item')
        if url_element:
            website['url'] = url_element.get('href')
        else:
            # Skip items without URLs
            return None
        
        # Image URL
        image_element = item.select_one('figure img')
        if image_element:
            image_url = image_element.get('data-src') or image_element.get('src')
            if image_url:
                website['image_url'] = urljoin(BASE_URL, image_url)
        
        # Description
        desc_element = item.select_one('.description')
        if desc_element:
            website['description'] = desc_element.get_text(strip=True)
        
        # Tags
        tags = []
        tag_elements = item.select('.tags a')
        for tag_el in tag_elements:
            tag = tag_el.get_text(strip=True)
            if tag:
                tags.append(tag)
        
        if tags:
            website['tags'] = tags
        
        # Award status
        award_element = item.select_one('.box-award')
        if award_element:
            award_text = award_element.get_text(strip=True)
            website['award'] = award_text
        
        return website
    
    except Exception as e:
        logger.exception(f"Error extracting website data: {e}")
        return None

def download_image(url, website_id):
    """Download an image from a URL and save it locally"""
    try:
        # Generate a filename based on the website ID
        ext = os.path.splitext(url)[1] or '.jpg'
        filename = f"{website_id}{ext}"
        local_path = os.path.join(Config.DATA_DIR, 'images', filename)
        
        # Don't re-download if file exists
        if os.path.exists(local_path):
            return filename
        
        # Download the image
        time.sleep(random.uniform(0.5, 1.5))
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        
        # Open and save the image using PIL
        img = Image.open(io.BytesIO(response.content))
        img.save(local_path)
        
        logger.info(f"Downloaded image: {filename}")
        return filename
    
    except Exception as e:
        logger.exception(f"Error downloading image {url}: {e}")
        return None

if __name__ == "__main__":
    # For testing the scraper directly
    logging.basicConfig(level=logging.INFO)
    scrape_awwwards(pages=1)
