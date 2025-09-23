import api from './api';

// Get all expenses for a specific group
export const getGroupExpenses = async (groupId) => {
  try {
    const response = await api.get(`/group/${groupId}/expense`);
    return response.data;
  } catch (error) {
    console.error('Error fetching group expenses:', error);
    throw error;
  }
};

// Create a new expense in a group
export const createExpense = async (groupId, expenseData) => {
  try {
    console.log('Expenses service - Creating expense:', {
      groupId,
      expenseData,
      url: `/group/${groupId}/expense`
    });
    
    const response = await api.post(`/group/${groupId}/expense`, expenseData);
    console.log('Expenses service - Create expense response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Expenses service - Error creating expense:', error);
    console.error('Expenses service - Error response:', error.response?.data);
    throw error;
  }
};

// Get details of a specific expense
export const getExpenseDetails = async (groupId, expenseId) => {
  try {
    const response = await api.get(`/group/${groupId}/expense/${expenseId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching expense details:', error);
    throw error;
  }
};

// Delete an expense
export const deleteExpense = async (groupId, expenseId) => {
  try {
    const response = await api.delete(`/group/${groupId}/expense/${expenseId}`);
    return response.data;
  } catch (error) {
    console.error('Error deleting expense:', error);
    throw error;
  }
};