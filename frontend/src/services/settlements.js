import api from './api';

// Get all settlements for a specific group
export const getGroupSettlements = async (groupId) => {
  try {
    const response = await api.get(`/group/${groupId}/settlement`);
    return response.data;
  } catch (error) {
    console.error('Error fetching group settlements:', error);
    throw error;
  }
};

// Create a new settlement in a group
export const createSettlement = async (groupId, settlementData) => {
  try {
    console.log('Settlements service - Creating settlement:', {
      groupId,
      settlementData,
      url: `/group/${groupId}/settlement`
    });
    
    const response = await api.post(`/group/${groupId}/settlement`, settlementData);
    console.log('Settlements service - Create settlement response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Settlements service - Error creating settlement:', error);
    console.error('Settlements service - Error response:', error.response?.data);
    throw error;
  }
};

// Get balances for all members in a group
export const getGroupBalances = async (groupId) => {
  try {
    const response = await api.get(`/group/${groupId}/balances`);
    return response.data;
  } catch (error) {
    console.error('Error fetching group balances:', error);
    throw error;
  }
};

// Clean up invalid settlements
export const cleanupSettlements = async (groupId) => {
  try {
    const response = await api.delete(`/group/${groupId}/settlement/cleanup`);
    return response.data;
  } catch (error) {
    console.error('Error cleaning up settlements:', error);
    throw error;
  }
};