import { useState, useEffect } from 'react';
import { 
  getAllGroups as fetchAllGroups, 
  createGroup as createGroupAPI, 
  deleteGroup as deleteGroupAPI, 
  getGroupById as fetchGroupById 
} from '../services/groups';
import { 
  getGroupExpenses as fetchGroupExpenses, 
  createExpense as createExpenseAPI, 
  deleteExpense as deleteExpenseAPI, 
  getExpenseDetails as fetchExpenseDetails 
} from '../services/expenses';

// Custom hook for API calls with loading and error states
export const useApi = (apiFunction, dependencies = []) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async (...args) => {
    try {
      setLoading(true);
      setError(null);
      const result = await apiFunction(...args);
      setData(result);
      return result;
    } catch (err) {
      setError(err.message || 'An error occurred');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (dependencies.length === 0 || dependencies.every(dep => dep !== null && dep !== undefined)) {
      fetchData(...dependencies);
    }
  }, dependencies);

  return { data, loading, error, refetch: fetchData };
};

// Custom hook for groups
export const useGroups = () => {
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchGroups = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchAllGroups();
      setGroups(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const createGroup = async (groupData) => {
    try {
      const newGroup = await createGroupAPI(groupData);
      setGroups(prev => [...prev, newGroup]);
      return newGroup;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const updateGroup = async (groupId, groupData) => {
    try {
      // Note: updateGroup is not implemented in backend, removing this function
      throw new Error('Update group functionality not implemented');
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const deleteGroup = async (groupId) => {
    try {
      await deleteGroupAPI(groupId);
      setGroups(prev => prev.filter(group => group.id !== groupId));
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  useEffect(() => {
    fetchGroups();
  }, []);

  return {
    groups,
    loading,
    error,
    refetch: fetchGroups,
    createGroup,
    updateGroup,
    deleteGroup,
  };
};

// Custom hook for expenses
export const useExpenses = () => {
  const [expenses, setExpenses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchExpenses = async () => {
    try {
      setLoading(true);
      setError(null);
      // Note: Since expenses are group-specific, this function needs a groupId
      throw new Error('fetchExpenses requires groupId - use getGroupExpenses instead');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const createExpense = async (expenseData) => {
    try {
      const newExpense = await createExpenseAPI(expenseData);
      setExpenses(prev => [...prev, newExpense]);
      return newExpense;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const updateExpense = async (expenseId, expenseData) => {
    try {
      // Note: updateExpense is not implemented in backend
      throw new Error('Update expense functionality not implemented');
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const deleteExpense = async (expenseId) => {
    try {
      await deleteExpenseAPI(expenseId);
      setExpenses(prev => prev.filter(expense => expense.id !== expenseId));
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  useEffect(() => {
    fetchExpenses();
  }, []);

  return {
    expenses,
    loading,
    error,
    refetch: fetchExpenses,
    createExpense,
    updateExpense,
    deleteExpense,
  };
};