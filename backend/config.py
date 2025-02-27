import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration"""
    # API Key for protected endpoints
    API_KEY = os.environ.get('API_KEY', 'default-dev-key-change-in-prod')
    
    # Data storage
    DATA_DIR = os.environ.get('DATA_DIR', 'data')
    
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(24).hex())
    DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    
    # Scraping settings
    SCRAPE_PAGES = int(os.environ.get('SCRAPE_PAGES', 5))
    SCRAPE_SECTION = os.environ.get('SCRAPE_SECTION', 'websites')
    
    # Color extraction settings
    NUM_COLORS = int(os.environ.get('NUM_COLORS', 5))
    
    # Cache settings (in seconds)
    CACHE_TIMEOUT = int(os.environ.get('CACHE_TIMEOUT', 3600))  # 1 hour
    
    # Rate limiting (requests per minute)
    RATE_LIMIT = int(os.environ.get('RATE_LIMIT', 10))

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    
    # Make sure these are set in production
    def __init__(self):
        required_vars = ['API_KEY', 'SECRET_KEY']
        missing = [var for var in required_vars if not os.environ.get(var)]
        if missing:
            raise Exception(f"Missing required environment variables: {', '.join(missing)}")

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    DATA_DIR = 'test_data'
