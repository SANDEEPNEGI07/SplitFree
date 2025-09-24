import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { getInitials } from '../../utils/helpers';
import './Layout.css';

const Header = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const isActive = (path) => {
    return location.pathname === path ? 'active' : '';
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <header className="header">
      <div className="container">
        <div className="header-content">
          <div className="header-left">
            <Link to="/dashboard" className="logo">
              <span className="logo-icon">💰</span>
              <span className="logo-text">Splitwise</span>
            </Link>
          </div>

          <nav className="header-nav">
            <Link 
              to="/dashboard" 
              className={`nav-link ${isActive('/dashboard')}`}
            >
              Dashboard
            </Link>
            <Link 
              to="/groups" 
              className={`nav-link ${isActive('/groups')}`}
            >
              Groups
            </Link>
            <Link 
              to="/expenses" 
              className={`nav-link ${isActive('/expenses')}`}
            >
              Expenses
            </Link>
            <Link 
              to="/history" 
              className={`nav-link ${isActive('/history')}`}
            >
              History
            </Link>
          </nav>

          <div className="header-right">
            <div className="user-menu">
              <div className="user-avatar">
                {getInitials(user?.username || user?.email || 'U')}
              </div>
              <div className="user-info">
                <span className="user-name">
                  {user?.username}
                </span>
                <span className="user-email">{user?.email}</span>
              </div>
              <button 
                onClick={handleLogout}
                className="logout-btn"
                title="Logout"
              >
                🚪
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;