import api from './api';

// Get all groups
export const getAllGroups = async () => {
  try {
    const response = await api.get('/group');
    return response.data;
  } catch (error) {
    console.error('Error fetching groups:', error);
    throw error;
  }
};

// Get group by ID
export const getGroupById = async (groupId) => {
  try {
    const response = await api.get(`/group/${groupId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching group:', error);
    throw error;
  }
};

// Create new group
export const createGroup = async (groupData) => {
  try {
    const response = await api.post('/group', groupData);
    return response.data;
  } catch (error) {
    console.error('Error creating group:', error);
    throw error;
  }
};

// Delete group
export const deleteGroup = async (groupId) => {
  try {
    const response = await api.delete(`/group/${groupId}`);
    return response.data;
  } catch (error) {
    console.error('Error deleting group:', error);
    throw error;
  }
};

// Add user to group
export const addUserToGroup = async (groupId, userId) => {
  try {
    const response = await api.post(`/group/${groupId}/user`, {
      user_id: userId
    });
    return response.data;
  } catch (error) {
    console.error('Error adding user to group:', error);
    throw error;
  }
};

// Remove user from group
export const removeUserFromGroup = async (groupId, userId) => {
  try {
    const response = await api.delete(`/group/${groupId}/user/${userId}`);
    return response.data;
  } catch (error) {
    console.error('Error removing user from group:', error);
    throw error;
  }
};

// Get user by ID (for adding members)
export const getUserById = async (userId) => {
  try {
    const response = await api.get(`/user/${userId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching user:', error);
    throw error;
  }
};
