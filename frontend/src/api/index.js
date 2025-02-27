// API client for interacting with the backend

/**
 * Fetch all websites with pagination
 * @param {Object} options
 * @param {number} options.page - Page number
 * @param {number} options.perPage - Items per page
 * @returns {Promise<Object>} - Websites data
 */
export const fetchWebsites = async ({ page = 1, perPage = 12 } = {}) => {
  try {
    const response = await fetch(`/api/websites?page=${page}&per_page=${perPage}`);
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    return response.json();
  } catch (error) {
    console.error("Error fetching websites:", error);
    throw error;
  }
};

/**
 * Fetch a single website by ID
 * @param {string} id - Website ID
 * @returns {Promise<Object>} - Website data
 */
export const fetchWebsite = async (id) => {
  try {
    const response = await fetch(`/api/websites/${id}`);
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    return response.json();
  } catch (error) {
    console.error(`Error fetching website ${id}:`, error);
    throw error;
  }
};

/**
 * Search websites by query, tag, or color
 * @param {Object} options
 * @param {string} options.q - Search query
 * @param {string} options.tag - Tag to filter by
 * @param {string} options.color - Color to filter by
 * @param {number} options.page - Page number
 * @param {number} options.perPage - Items per page
 * @returns {Promise<Object>} - Search results
 */
export const searchWebsites = async ({ q = '', tag = '', color = '', page = 1, perPage = 12 } = {}) => {
  try {
    const params = new URLSearchParams();
    if (q) params.append('q', q);
    if (tag) params.append('tag', tag);
    if (color) params.append('color', color);
    params.append('page', page);
    params.append('per_page', perPage);
    
    const response = await fetch(`/api/search?${params.toString()}`);
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    return response.json();
  } catch (error) {
    console.error("Error searching websites:", error);
    throw error;
  }
};
