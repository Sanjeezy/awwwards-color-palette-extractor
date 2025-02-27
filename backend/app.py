from flask import Flask, jsonify
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
import os
import logging
from datetime import datetime

from api import setup_routes
from scraper import scrape_awwwards
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable CORS
    CORS(app)
    
    # Setup API routes
    setup_routes(app)
    
    # Register error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Resource not found"}), 404
    
    @app.errorhandler(500)
    def server_error(error):
        logger.error(f"Server error: {error}")
        return jsonify({"error": "Internal server error"}), 500
    
    return app

def schedule_scraping():
    """Schedule periodic scraping of Awwwards websites"""
    logger.info("Setting up scheduled scraping")
    scheduler = BackgroundScheduler()
    # Run scraping job once a day at midnight
    scheduler.add_job(func=scrape_awwwards, trigger="cron", hour=0)
    scheduler.start()
    logger.info("Scheduled scraping initialized")

if __name__ == "__main__":
    app = create_app()
    
    # Run initial scraping if database is empty
    # This could be checked against a database condition
    if os.environ.get("RUN_INITIAL_SCRAPE", "false").lower() == "true":
        logger.info("Running initial scrape")
        scrape_awwwards()
    
    # Set up scheduled scraping
    if os.environ.get("ENABLE_SCHEDULED_SCRAPING", "true").lower() == "true":
        schedule_scraping()
    
    # Run the Flask app
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG", "false").lower() == "true")
