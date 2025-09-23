import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './Pages.css';
import { useGroups } from '../hooks/useApi';
import { getGroupExpenses, createExpense, deleteExpense } from '../services/expenses';
import { addUserToGroup, removeUserFromGroup, getUserById } from '../services/groups';
import LoadingSpinner from '../components/UI/LoadingSpinner';
import Modal from '../components/UI/Modal';
import Button from '../components/UI/Button';
import UserSearch from '../components/UI/UserSearch';

const GroupDetails = () => {
  const { groupId } = useParams();
  const navigate = useNavigate();
  const { groups, loading: groupsLoading, refetch } = useGroups();
  const [expenses, setExpenses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddExpenseModal, setShowAddExpenseModal] = useState(false);
  const [showAddMemberModal, setShowAddMemberModal] = useState(false);
  const [expenseForm, setExpenseForm] = useState({
    amount: '',
    description: '',
    paid_by: ''
  });

  // Debug logging for modal state changes
  useEffect(() => {
    console.log('showAddExpenseModal changed to:', showAddExpenseModal);
  }, [showAddExpenseModal]);

  useEffect(() => {
    console.log('showAddMemberModal changed to:', showAddMemberModal);
  }, [showAddMemberModal]);

  const currentGroup = groups.find(g => g.id === parseInt(groupId));

  useEffect(() => {
    if (groupId) {
      loadGroupData();
    }
  }, [groupId]);

  const loadGroupData = async () => {
    setLoading(true);
    try {
      const expensesData = await getGroupExpenses(groupId);
      setExpenses(expensesData);
    } catch (error) {
      console.error('Error loading group data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddExpense = async (e) => {
    e.preventDefault();
    
    console.log('Creating expense with data:', {
      groupId,
      expenseForm,
      currentGroup
    });
    
    try {
      const expenseData = {
        ...expenseForm,
        amount: parseFloat(expenseForm.amount),
        paid_by: parseInt(expenseForm.paid_by)
      };
      
      console.log('Sending expense data to API:', expenseData);
      
      const result = await createExpense(groupId, expenseData);
      console.log('Expense creation result:', result);
      
      setShowAddExpenseModal(false);
      setExpenseForm({ amount: '', description: '', paid_by: '' });
      loadGroupData(); // Refresh expenses
      
      alert('Expense created successfully!');
    } catch (error) {
      console.error('Error creating expense:', error);
      console.error('Error response:', error.response?.data);
      alert('Error creating expense: ' + (error.response?.data?.message || error.message));
    }
  };

  const handleAddMember = async (user) => {
    console.log('Adding member:', user, 'to group:', groupId);
    
    try {
      const result = await addUserToGroup(groupId, user.id);
      console.log('Add member result:', result);
      
      setShowAddMemberModal(false);
      refetch(); // Refresh group data to get updated members
      
      alert(`${user.username} added to group successfully!`);
    } catch (error) {
      console.error('Error adding member:', error);
      console.error('Error response:', error.response?.data);
      alert('Error adding member: ' + (error.response?.data?.message || error.message));
    }
  };

  const handleRemoveMember = async (userId) => {
    if (window.confirm('Are you sure you want to remove this member?')) {
      try {
        await removeUserFromGroup(groupId, userId);
        refetch(); // Refresh group data
      } catch (error) {
        console.error('Error removing member:', error);
        alert('Error removing member: ' + (error.response?.data?.message || error.message));
      }
    }
  };

  const handleDeleteExpense = async (expenseId) => {
    if (window.confirm('Are you sure you want to delete this expense?')) {
      try {
        await deleteExpense(groupId, expenseId);
        loadGroupData(); // Refresh expenses
      } catch (error) {
        console.error('Error deleting expense:', error);
        alert('Error deleting expense: ' + (error.response?.data?.message || error.message));
      }
    }
  };

  const calculateUserBalance = (userId) => {
    let balance = 0;
    expenses.forEach(expense => {
      if (expense.paid_by === userId) {
        balance += expense.amount;
      }
      const userSplit = expense.splits?.find(split => split.user_id === userId);
      if (userSplit) {
        balance -= userSplit.amount;
      }
    });
    return balance;
  };

  if (groupsLoading || loading) {
    return <LoadingSpinner />;
  }

  if (!currentGroup) {
    return (
      <div className="page-container">
        <div className="error-message">
          <h2>Group not found</h2>
          <Button onClick={() => navigate('/dashboard')}>
            Back to Dashboard
          </Button>
        </div>
      </div>
    );
  }

  const totalExpenses = expenses.reduce((sum, expense) => sum + expense.amount, 0);

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="header-content">
          <Button 
            variant="secondary" 
            onClick={() => navigate('/dashboard')}
            className="back-button"
          >
            ← Back
          </Button>
          <div>
            <h1>{currentGroup.name}</h1>
            <p className="group-description">{currentGroup.description}</p>
          </div>
        </div>
        <div className="header-actions">
          <Button 
            onClick={() => {
              console.log('Add Member button clicked!');
              setShowAddMemberModal(true);
            }}
            variant="secondary"
          >
            Add Member
          </Button>
          <Button onClick={() => {
            console.log('Add Expense button clicked!');
            setShowAddExpenseModal(true);
          }}>
            Add Expense
          </Button>
        </div>
      </div>

      <div className="group-stats">
        <div className="stat-card">
          <h3>Total Expenses</h3>
          <p className="stat-value">${totalExpenses.toFixed(2)}</p>
        </div>
        <div className="stat-card">
          <h3>Members</h3>
          <p className="stat-value">{currentGroup.users?.length || 0}</p>
        </div>
        <div className="stat-card">
          <h3>Transactions</h3>
          <p className="stat-value">{expenses.length}</p>
        </div>
      </div>

      <div className="content-grid">
        <div className="members-section">
          <h2>Members</h2>
          {currentGroup.users && currentGroup.users.length > 0 ? (
            <div className="members-list">
              {currentGroup.users.map(user => {
                const balance = calculateUserBalance(user.id);
                return (
                  <div key={user.id} className="member-card">
                    <div className="member-info">
                      <h4>{user.username}</h4>
                      <p>{user.email}</p>
                      <p className={`balance ${balance > 0 ? 'positive' : balance < 0 ? 'negative' : 'neutral'}`}>
                        Balance: ${balance.toFixed(2)}
                      </p>
                    </div>
                    <Button 
                      variant="danger" 
                      size="small"
                      onClick={() => handleRemoveMember(user.id)}
                    >
                      Remove
                    </Button>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="empty-state">No members in this group yet.</p>
          )}
        </div>

        <div className="expenses-section">
          <h2>Recent Expenses</h2>
          {expenses.length > 0 ? (
            <div className="expenses-list">
              {expenses.map(expense => {
                const payer = currentGroup.users?.find(u => u.id === expense.paid_by);
                return (
                  <div key={expense.id} className="expense-card">
                    <div className="expense-header">
                      <h4>{expense.description}</h4>
                      <div className="expense-actions">
                        <Button 
                          variant="danger" 
                          size="small"
                          onClick={() => handleDeleteExpense(expense.id)}
                        >
                          Delete
                        </Button>
                      </div>
                    </div>
                    <div className="expense-details">
                      <p><strong>Amount:</strong> ${expense.amount.toFixed(2)}</p>
                      <p><strong>Paid by:</strong> {payer?.username || 'Unknown'}</p>
                      <p><strong>Date:</strong> {new Date(expense.date).toLocaleDateString()}</p>
                      {expense.splits && expense.splits.length > 0 && (
                        <div className="expense-splits">
                          <p><strong>Split:</strong></p>
                          <ul>
                            {expense.splits.map((split, index) => {
                              const splitUser = currentGroup.users?.find(u => u.id === split.user_id);
                              return (
                                <li key={index}>
                                  {splitUser?.username || 'Unknown'}: ${split.amount.toFixed(2)}
                                </li>
                              );
                            })}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="empty-state">No expenses recorded yet.</p>
          )}
        </div>
      </div>

      {/* Add Expense Modal */}
      <Modal 
        isOpen={showAddExpenseModal} 
        onClose={() => {
          console.log('Closing Add Expense Modal');
          setShowAddExpenseModal(false);
        }}
        title="Add New Expense"
      >
        {console.log('Rendering Add Expense Modal, isOpen:', showAddExpenseModal)}
        <form onSubmit={handleAddExpense} className="modal-form">
          <div className="form-group">
            <label>Description</label>
            <input
              type="text"
              value={expenseForm.description}
              onChange={(e) => setExpenseForm({...expenseForm, description: e.target.value})}
              required
              placeholder="What was this expense for?"
            />
          </div>
          <div className="form-group">
            <label>Amount ($)</label>
            <input
              type="number"
              step="0.01"
              value={expenseForm.amount}
              onChange={(e) => setExpenseForm({...expenseForm, amount: e.target.value})}
              required
              placeholder="0.00"
            />
          </div>
          <div className="form-group">
            <label>Paid by</label>
            <select
              value={expenseForm.paid_by}
              onChange={(e) => setExpenseForm({...expenseForm, paid_by: e.target.value})}
              required
            >
              <option value="">Select who paid</option>
              {currentGroup.users?.map(user => (
                <option key={user.id} value={user.id}>
                  {user.username}
                </option>
              ))}
            </select>
          </div>
          <div className="modal-actions">
            <Button 
              type="button" 
              variant="secondary" 
              onClick={() => setShowAddExpenseModal(false)}
            >
              Cancel
            </Button>
            <Button type="submit">Add Expense</Button>
          </div>
        </form>
      </Modal>

      {/* Add Member Modal */}
      <Modal 
        isOpen={showAddMemberModal} 
        onClose={() => {
          console.log('Closing Add Member Modal');
          setShowAddMemberModal(false);
        }}
        title="Add Member to Group"
      >
        {console.log('Rendering Add Member Modal, isOpen:', showAddMemberModal)}
        <UserSearch 
          onUserSelect={handleAddMember}
          excludeUserIds={currentGroup.users?.map(u => u.id) || []}
        />
      </Modal>
    </div>
  );
};

export default GroupDetails;