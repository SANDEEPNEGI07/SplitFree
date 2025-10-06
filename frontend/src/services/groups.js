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
    console.log('Groups service - Adding user to group:', {
      groupId,
      userId,
      url: `/group/${groupId}/user`,
      data: { user_id: userId }
    });
    
    const response = await api.post(`/group/${groupId}/user`, {
      user_id: userId
    });
    console.log('Groups service - Add user response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Groups service - Error adding user to group:', error);
    console.error('Groups service - Error response:', error.response?.data);
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

// Send email invitation to join group
export const sendGroupInvitation = async (groupId, email, message = '') => {
  try {
    const response = await api.post(`/group/${groupId}/invite-email`, {
      email,
      message
    });
    return response.data;
  } catch (error) {
    console.error('Error sending group invitation:', error);
    throw error;
  }
};

// Join group using invite code
export const joinGroupByCode = async (inviteCode) => {
  try {
    const response = await api.post('/group/join-by-code', {
      invite_code: inviteCode
    });
    return response.data;
  } catch (error) {
    console.error('Error joining group by code:', error);
    throw error;
  }
};

// Get group info by invite code (public endpoint)
export const getGroupByCode = async (inviteCode) => {
  try {
    const response = await api.get(`/group/code/${inviteCode}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching group by code:', error);
    throw error;
  }
};

// Accept email invitation
export const acceptInvitation = async (inviteToken) => {
  try {
    const response = await api.get(`/invite/${inviteToken}`);
    return response.data;
  } catch (error) {
    console.error('Error accepting invitation:', error);
    throw error;
  }
};
