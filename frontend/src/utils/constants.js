// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

// API endpoints
export const API_ENDPOINTS = {
  // User endpoints
  REGISTER: '/register',
  LOGIN: '/login',
  LOGOUT: '/logout',
  REFRESH: '/refresh',
  
  // Group endpoints
  GROUPS: '/group',
  GROUP_BY_ID: (id) => `/group/${id}`,
  JOIN_GROUP: (id) => `/group/${id}/add-user`,
  LEAVE_GROUP: (id) => `/group/${id}/remove-user`,
  
  // Expense endpoints
  EXPENSES: '/expense',
  EXPENSE_BY_ID: (id) => `/expense/${id}`,
  GROUP_EXPENSES: (groupId) => `/group/${groupId}/expenses`,
  
  // Settlement endpoints
  SETTLEMENTS: '/settlement',
  SETTLEMENT_BY_ID: (id) => `/settlement/${id}`,
  GROUP_SETTLEMENTS: (groupId) => `/group/${groupId}/settlements`,
  GROUP_BALANCES: (groupId) => `/group/${groupId}/balances`,
  
  // History endpoints
  USER_HISTORY: '/history',
  GROUP_HISTORY: (groupId) => `/group/${groupId}/history`
};

// HTTP methods
export const HTTP_METHODS = {
  GET: 'GET',
  POST: 'POST',
  PUT: 'PUT',
  DELETE: 'DELETE'
};

// Storage keys
export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'splitfree_access_token',
  REFRESH_TOKEN: 'splitfree_refresh_token',
  USER_DATA: 'splitfree_user_data'
};

export default API_BASE_URL;