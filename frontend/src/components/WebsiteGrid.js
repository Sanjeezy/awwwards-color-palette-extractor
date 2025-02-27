import React from 'react';
import WebsiteCard from './WebsiteCard';
import '../styles/WebsiteGrid.css';

/**
 * WebsiteGrid component displays a grid of websites
 * 
 * @param {Object} props
 * @param {Array} props.websites - Array of website data
 * @param {boolean} props.loading - Loading state
 */
const WebsiteGrid = ({ websites = [], loading = false }) => {
  // If loading and no websites, show loading state
  if (loading && websites.length === 0) {
    return (
      <div className="website-grid-loading">
        <div className="loader"></div>
        <p>Loading websites...</p>
      </div>
    );
  }
  
  // If no websites and not loading, show empty state
  if (websites.length === 0) {
    return (
      <div className="website-grid-empty">
        <p>No websites found. Try triggering a scrape first.</p>
      </div>
    );
  }
  
  return (
    <div className="website-grid">
      {websites.map((website) => (
        <WebsiteCard key={website.id} website={website} />
      ))}
    </div>
  );
};

export default WebsiteGrid;
