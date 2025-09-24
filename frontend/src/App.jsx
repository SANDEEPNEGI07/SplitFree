import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { useGroups } from './hooks/useApi';
import { getGroupHistory } from './services/history';
import Header from './components/Layout/Header';
import Footer from './components/Layout/Footer';
import LoadingSpinner from './components/UI/LoadingSpinner';

// Auth Components
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';

// Pages
import Dashboard from './pages/Dashboard';
import GroupDetails from './pages/GroupDetails';

import './App.css';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingSpinner message="Loading..." />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="protected-layout">
      <Header />
      <main className="main-content">
        {children}
      </main>
      <Footer />
    </div>
  );
};

// Public Route Component (redirects to dashboard if authenticated)
const PublicRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingSpinner message="Loading..." />;
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};

// Temporary placeholder components
const Groups = () => {
  const navigate = useNavigate();
  const { groups, loading, createGroup } = useGroups();
  const [showCreateForm, setShowCreateForm] = React.useState(false);
  const [formData, setFormData] = React.useState({ name: '', description: '' });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await createGroup(formData);
      setFormData({ name: '', description: '' });
      setShowCreateForm(false);
    } catch (error) {
      console.error('Error creating group:', error);
    }
  };

  if (loading) {
    return <LoadingSpinner message="Loading groups..." />;
  }

  return (
    <div className="container">
      <div className="page-header">
        <h1>Your Groups</h1>
        <button 
          className="btn btn-primary"
          onClick={() => setShowCreateForm(true)}
        >
          Create New Group
        </button>
      </div>

      {showCreateForm && (
        <div className="modal-overlay" onClick={() => setShowCreateForm(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Create New Group</h2>
              <button onClick={() => setShowCreateForm(false)}>×</button>
            </div>
            <form onSubmit={handleSubmit} className="modal-body">
              <div className="form-group">
                <label>Group Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  className="form-input"
                  required
                />
              </div>
              <div className="form-group">
                <label>Description</label>
                <input
                  type="text"
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  className="form-input"
                  required
                />
              </div>
              <button type="submit" className="btn btn-primary">Create Group</button>
            </form>
          </div>
        </div>
      )}

      <div className="groups-grid">
        {groups && groups.length > 0 ? (
          groups.map(group => (
            <div key={group.id} className="group-card">
              <div className="group-avatar-large">
                {group.name.charAt(0).toUpperCase()}
              </div>
              <h3>{group.name}</h3>
              <p>{group.description}</p>
              <div className="group-stats">
                <span>👥 {group.users?.length || 0} members</span>
                <span>💳 {group.expense_count || 0} expenses</span>
                <span>💰 ${(group.total_amount || 0).toFixed(2)}</span>
              </div>
              <div className="group-actions">
                <button 
                  className="btn btn-outline"
                  onClick={() => navigate(`/group/${group.id}`)}
                >
                  View Details
                </button>
                <button 
                  className="btn btn-primary"
                  onClick={() => navigate(`/group/${group.id}`)}
                >
                  Add Expense
                </button>
              </div>
            </div>
          ))
        ) : (
          <div className="empty-state">
            <h2>No Groups Yet</h2>
            <p>Create your first group to start splitting expenses with friends!</p>
            <button 
              className="btn btn-primary"
              onClick={() => setShowCreateForm(true)}
            >
              Create Your First Group
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

const History = () => {
  const navigate = useNavigate();
  const { groups, loading: groupsLoading } = useGroups();
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState('all'); // 'all', 'expenses', 'settlements'

  // Load history when group is selected
  useEffect(() => {
    if (selectedGroup) {
      loadGroupHistory(selectedGroup.id);
    }
  }, [selectedGroup]);

  const loadGroupHistory = async (groupId) => {
    setLoading(true);
    try {
      console.log(`Loading history for group ${groupId}`);
      const data = await getGroupHistory(groupId);
      console.log('History data received:', data);
      
      // Check if data.items exists and is an array
      if (data && data.items && Array.isArray(data.items)) {
        // Sort by date, with expenses first (they have dates), then settlements
        const sortedItems = data.items.sort((a, b) => {
          if (!a.date && !b.date) return b.id - a.id; // Both are settlements, sort by ID desc
          if (!a.date) return 1; // a is settlement, b is expense
          if (!b.date) return -1; // a is expense, b is settlement
          return new Date(b.date) - new Date(a.date); // Both have dates, sort desc
        });
        console.log('Sorted history items:', sortedItems);
        setHistory(sortedItems);
      } else {
        console.log('No items in response or invalid format');
        setHistory([]);
      }
    } catch (error) {
      console.error('Error loading history:', error);
      setHistory([]);
    } finally {
      setLoading(false);
    }
  };

  const getUserName = (userId) => {
    if (!selectedGroup) return 'Unknown';
    const user = selectedGroup.users.find(u => u.id === userId);
    return user ? user.username : 'Unknown';
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'No date';
    return new Date(dateString).toLocaleDateString();
  };

  const filteredHistory = history.filter(item => {
    if (filter === 'all') return true;
    if (filter === 'expenses') return item.type === 'expense';
    if (filter === 'settlements') return item.type === 'settlement';
    return true;
  });

  if (groupsLoading) {
    return <LoadingSpinner message="Loading your groups..." />;
  }

  return (
    <div className="container">
      <div className="page-header">
        <h1>History</h1>
        {selectedGroup && (
          <div className="history-filters">
            <button
              className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
              onClick={() => setFilter('all')}
            >
              All Activity
            </button>
            <button
              className={`filter-btn ${filter === 'expenses' ? 'active' : ''}`}
              onClick={() => setFilter('expenses')}
            >
              Expenses
            </button>
            <button
              className={`filter-btn ${filter === 'settlements' ? 'active' : ''}`}
              onClick={() => setFilter('settlements')}
            >
              Settlements
            </button>
          </div>
        )}
      </div>

      {/* Group Selection */}
      {!selectedGroup ? (
        <div className="group-selection">
          <h2>Select a Group</h2>
          <p>Choose a group to view its complete history of expenses and settlements</p>
          <div className="groups-grid">
            {groups && groups.length > 0 ? (
              groups.map(group => (
                <div 
                  key={group.id} 
                  className="group-card clickable"
                  onClick={() => setSelectedGroup(group)}
                >
                  <div className="group-avatar-large">
                    {group.name.charAt(0).toUpperCase()}
                  </div>
                  <h3>{group.name}</h3>
                  <p>{group.description}</p>
                  <div className="group-stats">
                    <span>👥 {group.users?.length || 0} members</span>
                    <span>📜 View history</span>
                  </div>
                </div>
              ))
            ) : (
              <div className="empty-state">
                <h3>No Groups Found</h3>
                <p>You need to be part of a group to view history</p>
                <button 
                  className="btn btn-primary"
                  onClick={() => navigate('/groups')}
                >
                  Browse Groups
                </button>
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="history-section">
          {/* Selected Group Header */}
          <div className="selected-group-header">
            <div className="group-info">
              <div className="group-avatar-small">
                {selectedGroup.name.charAt(0).toUpperCase()}
              </div>
              <div>
                <h3>{selectedGroup.name}</h3>
                <p>{selectedGroup.users?.length || 0} members</p>
              </div>
            </div>
            <button 
              className="btn btn-outline"
              onClick={() => setSelectedGroup(null)}
            >
              Change Group
            </button>
          </div>

          {/* History Timeline */}
          <div className="history-timeline">
            {loading ? (
              <LoadingSpinner message="Loading history..." />
            ) : filteredHistory.length > 0 ? (
              <div className="timeline-items">
                {filteredHistory.map(item => (
                  <div key={`${item.type}-${item.id}`} className={`timeline-item ${item.type}`}>
                    <div className="timeline-marker">
                      {item.type === 'expense' ? '💳' : '💰'}
                    </div>
                    <div className="timeline-content">
                      <div className="timeline-header">
                        <h4>
                          {item.type === 'expense' 
                            ? item.description 
                            : `Settlement: ${getUserName(item.paid_by)} → ${getUserName(item.paid_to)}`
                          }
                        </h4>
                        <div className="timeline-meta">
                          <span className="timeline-amount">${item.amount}</span>
                          <span className="timeline-date">{formatDate(item.date)}</span>
                        </div>
                      </div>
                      
                      {item.type === 'expense' ? (
                        <div className="expense-details">
                          <p className="payer-info">
                            Paid by <strong>{getUserName(item.paid_by)}</strong>
                          </p>
                          {item.splits && item.splits.length > 0 && (
                            <div className="splits-info">
                              <h5>Split Details:</h5>
                              <div className="splits-grid">
                                {item.splits.map(split => (
                                  <div key={split.user_id} className="split-item">
                                    <span className="split-user">{getUserName(split.user_id)}</span>
                                    <div className="split-amounts">
                                      <span className="split-owed">Owes: ${split.owed.toFixed(2)}</span>
                                      {split.paid > 0 && (
                                        <span className="split-paid">Paid: ${split.paid.toFixed(2)}</span>
                                      )}
                                      {split.remaining !== 0 && (
                                        <span className={`split-remaining ${split.remaining > 0 ? 'debt' : 'credit'}`}>
                                          {split.remaining > 0 ? 'Owes' : 'Credit'}: ${Math.abs(split.remaining).toFixed(2)}
                                        </span>
                                      )}
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      ) : (
                        <div className="settlement-details">
                          <p className="settlement-info">
                            <strong>{getUserName(item.paid_by)}</strong> paid <strong>{getUserName(item.paid_to)}</strong>
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <div className="empty-icon">📜</div>
                <h3>No {filter === 'all' ? 'activity' : filter} yet</h3>
                <p>
                  {filter === 'all' 
                    ? `No expenses or settlements recorded for ${selectedGroup.name}` 
                    : `No ${filter} found for ${selectedGroup.name}`
                  }
                </p>
                <button 
                  className="btn btn-primary"
                  onClick={() => navigate(`/group/${selectedGroup.id}`)}
                >
                  Add Activity
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Routes>
            {/* Public Routes */}
            <Route 
              path="/login" 
              element={
                <PublicRoute>
                  <Login />
                </PublicRoute>
              } 
            />
            <Route 
              path="/register" 
              element={
                <PublicRoute>
                  <Register />
                </PublicRoute>
              } 
            />

            {/* Protected Routes */}
            <Route 
              path="/dashboard" 
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/groups" 
              element={
                <ProtectedRoute>
                  <Groups />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/group/:groupId" 
              element={
                <ProtectedRoute>
                  <GroupDetails />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/history" 
              element={
                <ProtectedRoute>
                  <History />
                </ProtectedRoute>
              } 
            />

            {/* Default Route */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            
            {/* Catch all route */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;