import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useGroups } from '../hooks/useApi';
import { formatCurrency } from '../utils/helpers';
import LoadingSpinner from '../components/UI/LoadingSpinner';
import './Pages.css';

const Dashboard = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { groups, loading: groupsLoading } = useGroups();

  if (groupsLoading) {
    return <LoadingSpinner message="Loading dashboard..." />;
  }

  const totalGroups = groups?.length || 0;
  
  // TODO: Replace with real API data when endpoints are ready
  const mockStats = {
    totalOwed: 0, // Will come from backend balance calculation
    totalOwe: 0,  // Will come from backend balance calculation
    recentExpenses: 0 // Will come from backend expense count
  };

  // TODO: Replace with real activity data from backend
  const recentActivity = []; // Will be populated from /history endpoint

  return (
    <div className="container">
      <div className="dashboard">
        <div className="dashboard-header">
          <h1>Welcome back, {user?.username}!</h1>
          <p>Here's your expense summary</p>
        </div>

        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon positive">💰</div>
            <div className="stat-content">
              <h3>You are owed</h3>
              <p className="stat-amount positive">{formatCurrency(mockStats.totalOwed)}</p>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon negative">💸</div>
            <div className="stat-content">
              <h3>You owe</h3>
              <p className="stat-amount negative">{formatCurrency(mockStats.totalOwe)}</p>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon neutral">👥</div>
            <div className="stat-content">
              <h3>Active Groups</h3>
              <p className="stat-amount">{totalGroups}</p>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon neutral">📋</div>
            <div className="stat-content">
              <h3>Recent Expenses</h3>
              <p className="stat-amount">{mockStats.recentExpenses}</p>
            </div>
          </div>
        </div>

        <div className="dashboard-sections">
          <div className="section">
            <div className="section-header">
              <h2>Recent Activity</h2>
              <a href="/history" className="section-link">View all</a>
            </div>
            <div className="activity-list">
              {recentActivity.length > 0 ? (
                recentActivity.map(activity => (
                  <div key={activity.id} className="activity-item">
                    <div className="activity-icon">
                      {activity.type === 'expense' ? '🧾' : '💰'}
                    </div>
                    <div className="activity-content">
                      <h4>{activity.description}</h4>
                      <p>{activity.group} • {activity.date}</p>
                    </div>
                    <div className="activity-amount">
                      {formatCurrency(activity.amount)}
                    </div>
                  </div>
                ))
              ) : (
                <div className="empty-state">
                  <p>No recent activity. Start by adding expenses to your groups!</p>
                </div>
              )}
            </div>
          </div>

          <div className="section">
            <div className="section-header">
              <h2>Your Groups ({totalGroups})</h2>
              <a href="/groups" className="section-link">Manage groups</a>
            </div>
            <div className="groups-list">
              {groups && groups.length > 0 ? (
                groups.slice(0, 5).map(group => (
                  <div key={group.id} className="group-item">
                    <div className="group-avatar">
                      {group.name.charAt(0).toUpperCase()}
                    </div>
                    <div className="group-content">
                      <h4>{group.name}</h4>
                      <p>{group.description}</p>
                      <div className="group-meta">
                        <span className="group-members">
                          👥 {group.users?.length || 0} members
                        </span>
                        {/* TODO: Add expense count when backend provides it */}
                        <span className="group-expenses">
                          💳 0 expenses
                        </span>
                      </div>
                    </div>
                    <div className="group-actions">
                      <button 
                        className="btn-small btn-outline"
                        onClick={() => navigate(`/group/${group.id}`)}
                      >
                        View
                      </button>
                    </div>
                  </div>
                ))
              ) : (
                <div className="empty-state">
                  <p>No groups yet. Create your first group to start splitting expenses!</p>
                  <a href="/groups" className="btn btn-primary">Create Group</a>
                </div>
              )}
              
              {groups && groups.length > 5 && (
                <div className="show-more">
                  <a href="/groups" className="btn btn-outline">
                    View All {totalGroups} Groups
                  </a>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="quick-actions">
          <h2>Quick Actions</h2>
          <div className="actions-grid">
            <a href="/groups" className="action-card">
              <div className="action-icon">👥</div>
              <h3>Create Group</h3>
              <p>Start a new group to split expenses</p>
            </a>
            <a href="/expenses" className="action-card">
              <div className="action-icon">💳</div>
              <h3>Add Expense</h3>
              <p>Record a new expense to split</p>
            </a>
            <a href="/history" className="action-card">
              <div className="action-icon">📊</div>
              <h3>View History</h3>
              <p>Check your expense history</p>
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;