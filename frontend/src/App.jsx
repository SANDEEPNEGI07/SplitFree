import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { useGroups } from './hooks/useApi';
import Header from './components/Layout/Header';
import Footer from './components/Layout/Footer';
import LoadingSpinner from './components/UI/LoadingSpinner';

// Auth Components
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';

// Pages
import Dashboard from './pages/Dashboard';
import Debug from './pages/Debug';
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
                <span>💳 0 expenses</span>
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

const Expenses = () => (
  <div className="container">
    <div className="page-header">
      <h1>Expenses</h1>
      <p>Track and manage your expenses here.</p>
    </div>
    <div className="coming-soon">
      <h2>🚧 Coming Soon!</h2>
      <p>Expenses functionality is being developed.</p>
    </div>
  </div>
);

const History = () => (
  <div className="container">
    <div className="page-header">
      <h1>History</h1>
      <p>View your expense history and activity.</p>
    </div>
    <div className="coming-soon">
      <h2>🚧 Coming Soon!</h2>
      <p>History functionality is being developed.</p>
    </div>
  </div>
);

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
              path="/expenses" 
              element={
                <ProtectedRoute>
                  <Expenses />
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

            {/* Debug Route - Remove in production */}
            <Route 
              path="/debug" 
              element={<Debug />} 
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