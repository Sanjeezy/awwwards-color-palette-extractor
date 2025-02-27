import React, { useState, useEffect } from 'react';
import WebsiteGrid from './components/WebsiteGrid';
import { fetchWebsites } from './api';
import './styles/App.css';

function App() {
  const [websites, setWebsites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Fetch websites on component mount
  useEffect(() => {
    const getWebsites = async () => {
      try {
        setLoading(true);
        const data = await fetchWebsites();
        setWebsites(data.websites || []);
      } catch (err) {
        console.error('Error fetching websites:', err);
        setError('Failed to load websites. Please make sure the backend is running and you have scraped some websites.');
      } finally {
        setLoading(false);
      }
    };
    
    getWebsites();
  }, []);
  
  return (
    <div className="App">
      <header className="App-header">
        <h1>Awwwards Color Palette Extractor</h1>
        <p>
          Discover color palettes from award-winning websites on Awwwards.com
        </p>
      </header>
      
      <main>
        {error ? (
          <div className="error-message">
            <p>{error}</p>
            <p>
              Try running:
              <pre>
                curl -X POST http://localhost:5001/api/trigger-scrape \<br/>
                &nbsp;&nbsp;-H "X-API-Key: default-dev-key-change-in-prod" \<br/>
                &nbsp;&nbsp;-H "Content-Type: application/json" \<br/>
                &nbsp;&nbsp;-d '{"pages": 1}'
              </pre>
            </p>
          </div>
        ) : (
          <WebsiteGrid websites={websites} loading={loading} />
        )}
      </main>
    </div>
  );
}

export default App;
