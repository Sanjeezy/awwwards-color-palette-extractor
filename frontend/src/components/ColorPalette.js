import React from 'react';
import '../styles/ColorPalette.css';

/**
 * ColorPalette component displays a set of colors
 * 
 * @param {Object} props
 * @param {Array} props.colors - Array of hex color codes
 * @param {boolean} props.small - Use small size for the swatches
 */
const ColorPalette = ({ colors = [], small = false }) => {
  // If no colors are provided, return empty
  if (!colors || colors.length === 0) {
    return <div className="empty-palette">No colors available</div>;
  }

  // Handle click to copy color code
  const handleColorClick = (color) => {
    navigator.clipboard.writeText(color)
      .then(() => {
        alert(`Copied ${color} to clipboard!`);
      })
      .catch(err => {
        console.error('Failed to copy color:', err);
      });
  };
  
  return (
    <div className={`color-palette ${small ? 'color-palette-small' : ''}`}>
      {colors.map((color, index) => (
        <div 
          key={`${color}-${index}`}
          className="color-swatch"
          style={{ backgroundColor: color }}
          onClick={() => handleColorClick(color)}
          title={`Click to copy: ${color}`}
        >
          {!small && <span className="color-code">{color}</span>}
        </div>
      ))}
    </div>
  );
};

export default ColorPalette;
