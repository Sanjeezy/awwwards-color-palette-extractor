# Awwwards Color Palette Extractor

A web application that scrapes award-winning websites from Awwwards.com and automatically extracts their color palettes. This tool helps designers and developers discover and get inspired by color schemes from cutting-edge website designs.

## Features

- **Web Scraping**: Extract website information from Awwwards
- **Color Extraction**: Analyze website thumbnails to identify dominant color palettes
- **Interactive UI**: Browse, search, and filter websites by title, tags, or colors
- **Save Favorites**: Create a collection of your favorite color schemes
- **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

### Backend
- **Python (Flask)**: Web framework for the API
- **BeautifulSoup**: HTML parsing and web scraping
- **Scikit-learn**: Color extraction algorithms using K-means clustering
- **Pillow (PIL)**: Image processing

### Frontend
- **React**: UI components and state management
- **React Router**: Navigation and routing
- **Framer Motion**: Animations and transitions
- **Axios**: API requests
- **React Colorful**: Color picker component

## Project Structure

The project is organized into two main directories:

```
/
├── backend/            # Flask API
│   ├── app.py          # Main application
│   ├── scraper.py      # Awwwards scraping
│   ├── color_extractor.py  # Color extraction
│   └── ...
│
├── frontend/           # React frontend
│   ├── src/
│   │   ├── components/ # React components
│   │   ├── pages/      # Page components
│   │   ├── styles/     # CSS styles
│   │   └── ...
│   └── ...
│
├── data/               # Stored data
│   ├── websites.json   # Scraped websites
│   └── images/         # Website thumbnails
│
└── ...
```

## Getting Started

### Prerequisites

- Docker and Docker Compose (recommended)
- Alternatively: Node.js 16+ and Python 3.9+

### Using Docker (Recommended)

1. Clone the repository:
   ```
   git clone https://github.com/Sanjeezy/awwwards-color-palette-extractor.git
   cd awwwards-color-palette-extractor
   ```

2. Start the application with Docker Compose:
   ```
   docker-compose up
   ```

3. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000

### Manual Setup

#### Backend

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create the data directories:
   ```
   mkdir -p data/images
   ```

5. Run the Flask application:
   ```
   flask run
   ```

#### Frontend

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Run the React development server:
   ```
   npm start
   ```

## API Endpoints

- `GET /api/websites`: Get all websites with pagination
- `GET /api/websites/<id>`: Get a specific website
- `GET /api/palettes`: Get all color palettes
- `GET /api/search`: Search websites by query, tag, or color
- `POST /api/trigger-scrape`: Manually trigger web scraping (protected by API key)

## Environment Variables

### Backend

- `FLASK_APP`: Flask application entry point (default: app.py)
- `FLASK_DEBUG`: Enable debug mode (default: false)
- `DATA_DIR`: Directory for storing data (default: data/)
- `API_KEY`: API key for protected endpoints
- `ENABLE_SCHEDULED_SCRAPING`: Enable automatic scraping (default: true)
- `SCRAPE_PAGES`: Number of pages to scrape (default: 5)

### Frontend

- `REACT_APP_API_URL`: Backend API URL (default: http://localhost:5000)

## Deployment

### Production Build

1. Build the Docker image:
   ```
   docker build -t awwwards-color-extractor .
   ```

2. Run the container:
   ```
   docker run -p 5000:5000 -e API_KEY=your_secret_key awwwards-color-extractor
   ```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Disclaimer

This project is for educational and inspirational purposes only. We respect the intellectual property of all websites featured in this tool and encourage users to use the extracted color palettes as inspiration rather than direct copying. All website information and images are credited to their original creators.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
