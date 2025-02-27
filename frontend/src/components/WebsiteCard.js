import React from 'react';
import ColorPalette from './ColorPalette';
import '../styles/WebsiteCard.css';

/**
 * WebsiteCard component displays a website with its thumbnail and color palette
 * 
 * @param {Object} props
 * @param {Object} props.website - Website data
 */
const WebsiteCard = ({ website }) => {
  if (!website) return null;
  
  // Extract website data
  const {
    id,
    title,
    url,
    local_image,
    palette = [],
    tags = []
  } = website;
  
  // Format URL for display
  const displayUrl = url ? url.replace(/https?:\/\/(www\.)?/, '').split('/')[0] : '';
  const displayTitle = title || displayUrl;
  
  // Handle click on the "Visit Website" button
  const handleVisitClick = (e) => {
    e.stopPropagation();
    window.open(url, '_blank', 'noopener,noreferrer');
  };
  
  return (
    <div className="website-card">
      <div className="card-header">
        {local_image ? (
          <img 
            src={`/api/images/${local_image}`}
            alt={displayTitle}
            className="website-image"
            onError={(e) => {
              e.target.onerror = null;
              e.target.src = `https://via.placeholder.com/300x200?text=${displayTitle.charAt(0)}`;
            }}
          />
        ) : (
          <div className="website-image placeholder-image">
            <span>{displayTitle.charAt(0)}</span>
          </div>
        )}
      </div>
      
      <div className="card-body">
        <h3 className="website-title">{displayTitle}</h3>
        <p className="website-url">{displayUrl}</p>
        
        {tags && tags.length > 0 && (
          <div className="website-tags">
            {tags.slice(0, 3).map((tag, index) => (
              <span key={`${tag}-${index}`} className="tag">{tag}</span>
            ))}
            {tags.length > 3 && <span className="tag more-tag">+{tags.length - 3}</span>}
          </div>
        )}
        
        <div className="website-palette">
          <ColorPalette colors={palette} small={true} />
        </div>
        
        <button className="visit-button" onClick={handleVisitClick}>
          Visit Website
        </button>
      </div>
    </div>
  );
};

export default WebsiteCard;
