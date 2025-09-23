import { apiRequest } from './api';
import { API_ENDPOINTS, HTTP_METHODS, STORAGE_KEYS } from '../utils/constants';

// Authentication service
export const authService = {
  // Register new user
  register: async (userData) => {
    const response = await apiRequest(HTTP_METHODS.POST, API_ENDPOINTS.REGISTER, userData);
    return response;
  },

  // Login user
  login: async (credentials) => {
    console.log('Auth service login called with:', credentials);
    const response = await apiRequest(HTTP_METHODS.POST, API_ENDPOINTS.LOGIN, credentials);
    console.log('API login response:', response);
    
    // Store tokens and user data
    if (response.access_token) {
      localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, response.access_token);
      console.log('Stored access token');
    }
    if (response.refresh_token) {
      localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, response.refresh_token);
      console.log('Stored refresh token');
    }
    
    return response;
  },

  // Logout user
  logout: async () => {
    try {
      await apiRequest(HTTP_METHODS.POST, API_ENDPOINTS.LOGOUT);
    } catch (error) {
      // Even if logout fails on server, clear local storage
      console.error('Logout error:', error);
    } finally {
      // Clear local storage
      localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
      localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
      localStorage.removeItem(STORAGE_KEYS.USER_DATA);
    }
  },

  // Refresh access token
  refreshToken: async () => {
    const refreshToken = localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await apiRequest(HTTP_METHODS.POST, API_ENDPOINTS.REFRESH, {}, {
      headers: {
        Authorization: `Bearer ${refreshToken}`,
      },
    });

    if (response.access_token) {
      localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, response.access_token);
    }

    return response;
  },

  // Check if user is authenticated
  isAuthenticated: () => {
    return !!localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
  },

  // Get current user data from token
  getCurrentUser: () => {
    const token = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
    if (!token) return null;

    try {
      // Decode JWT token to get user info
      const payload = JSON.parse(atob(token.split('.')[1]));
      return {
        id: payload.sub,
        email: payload.email,
        // Add other user fields as needed
      };
    } catch (error) {
      console.error('Error decoding token:', error);
      return null;
    }
  },
};