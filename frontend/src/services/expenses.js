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
    const response = await api.post(`/group/${groupId}/expense`, expenseData);
    return response.data;
  } catch (error) {
    console.error('Error creating expense:', error);
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