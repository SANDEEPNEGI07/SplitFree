import React, { useState } from 'react';
import api from '../../services/api';
import Button from './Button';

const UserSearch = ({ onUserSelect, excludeUserIds = [] }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Note: Since the backend doesn't have a user search endpoint,
  // we'll implement a simple user ID lookup for now
  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setError('Please enter a user ID');
      return;
    }

    setLoading(true);
    setError('');
    setSearchResults([]);

    try {
      // Try to get user by ID
      const userId = parseInt(searchQuery.trim());
      if (isNaN(userId)) {
        setError('Please enter a valid user ID');
        setLoading(false);
        return;
      }

      // Check if user is already excluded (already in group)
      if (excludeUserIds.includes(userId)) {
        setError('This user is already in the group');
        setLoading(false);
        return;
      }

      const response = await api.get(`/user/${userId}`);
      setSearchResults([response.data]);
    } catch (error) {
      if (error.response?.status === 404) {
        setError('User not found');
      } else {
        setError('Error searching for user');
      }
      console.error('Error searching for user:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="user-search">
      <div className="search-input-group">
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Enter user ID to search..."
          className="search-input"
        />
        <Button 
          onClick={handleSearch} 
          disabled={loading}
          variant="secondary"
        >
          {loading ? 'Searching...' : 'Search'}
        </Button>
      </div>

      {error && (
        <div className="search-error">
          {error}
        </div>
      )}

      {searchResults.length > 0 && (
        <div className="search-results">
          <h4>Search Results:</h4>
          {searchResults.map(user => (
            <div key={user.id} className="search-result-item">
              <div className="user-info">
                <strong>{user.username}</strong>
                <span className="user-email">{user.email}</span>
              </div>
              <Button 
                onClick={() => onUserSelect(user)}
                size="small"
              >
                Add to Group
              </Button>
            </div>
          ))}
        </div>
      )}

      <div className="search-help">
        <p><strong>Note:</strong> Currently you need to know the user's ID to add them to the group.</p>
        <p>In a real application, this would search by username or email address.</p>
      </div>
    </div>
  );
};

export default UserSearch;