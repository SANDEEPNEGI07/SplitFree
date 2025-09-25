import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useGroups } from '../hooks/useApi';
import { getGroupBalances } from '../services/settlements';
import { getRecentActivity } from '../services/history';
import { formatCurrency } from '../utils/helpers';
import LoadingSpinner from '../components/UI/LoadingSpinner';
import Button from '../components/UI/Button';
import './Pages.css';

const Dashboard = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { groups, loading: groupsLoading } = useGroups();
  const [balanceStats, setBalanceStats] = useState({
    totalOwed: 0,
    totalOwe: 0,
    recentExpenses: 0
  });
  const [balancesLoading, setBalancesLoading] = useState(true);
  const [recentActivity, setRecentActivity] = useState([]);
  const [activityLoading, setActivityLoading] = useState(true);

  // Fetch balance data for all groups
  useEffect(() => {
    const fetchBalances = async () => {
      console.log('Dashboard: Starting fetchBalances');
      console.log('Dashboard: Groups:', groups);
      console.log('Dashboard: User:', user);
      
      if (!groups || !user || !user.id) {
        console.log('Dashboard: Missing groups or user, stopping');
        setBalancesLoading(false);
        return;
      }

      setBalancesLoading(true);
      try {
        let totalOwed = 0;
        let totalOwe = 0;
        let recentExpenses = 0;

        // Fetch balances for each group
        for (const group of groups) {
          try {
            console.log('Dashboard: Fetching balances for group', group.id);
            const balances = await getGroupBalances(group.id);
            console.log('Dashboard: Received balances:', balances);
            console.log('Dashboard: Current user:', user);
            
            // Find user balance with flexible comparison (handles string/number type differences)
            const userBalance = balances.find(b => 
              b.user_id === user.id || 
              b.user_id === parseInt(user.id) || 
              parseInt(b.user_id) === parseInt(user.id)
            );
            console.log('Dashboard: Found user balance:', userBalance);
            
            if (userBalance && userBalance.balance !== undefined) {
              const balance = parseFloat(userBalance.balance);
              console.log('Dashboard: Processing balance:', balance);
              if (balance > 0) {
                totalOwed += balance;
                console.log('Dashboard: Added to totalOwed:', balance, 'New total:', totalOwed);
              } else if (balance < 0) {
                totalOwe += Math.abs(balance);
                console.log('Dashboard: Added to totalOwe:', Math.abs(balance), 'New total:', totalOwe);
              }
            } else {
              console.log('Dashboard: No balance found for user');
            }
            
            recentExpenses += group.expense_count || 0;
          } catch (error) {
            console.error(`Error fetching balances for group ${group.id}:`, error);
          }
        }

        setBalanceStats({
          totalOwed: totalOwed,
          totalOwe: totalOwe,
          recentExpenses: recentExpenses
        });
      } catch (error) {
        console.error('Error fetching balance stats:', error);
      } finally {
        setBalancesLoading(false);
      }
    };

    fetchBalances();
  }, [groups, user]);

  // Fetch recent activity across all groups
  useEffect(() => {
    const fetchRecentActivity = async () => {
      if (!groups || groups.length === 0) {
        setActivityLoading(false);
        return;
      }

      setActivityLoading(true);
      try {
        console.log('Dashboard: Fetching recent activity for groups:', groups);
        const activity = await getRecentActivity(groups, 5); // Get 5 most recent items
        console.log('Dashboard: Recent activity received:', activity);
        setRecentActivity(activity);
      } catch (error) {
        console.error('Error fetching recent activity:', error);
        setRecentActivity([]);
      } finally {
        setActivityLoading(false);
      }
    };

    fetchRecentActivity();
  }, [groups]);

  if (groupsLoading || balancesLoading) {
    return <LoadingSpinner message="Loading dashboard..." />;
  }

  const totalGroups = groups?.length || 0;

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
              <p className="stat-amount positive">{formatCurrency(balanceStats.totalOwed)}</p>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon negative">💸</div>
            <div className="stat-content">
              <h3>You owe</h3>
              <p className="stat-amount negative">{formatCurrency(balanceStats.totalOwe)}</p>
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
              <p className="stat-amount">{balanceStats.recentExpenses}</p>
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
              {activityLoading ? (
                <div className="activity-loading">
                  <p>Loading recent activity...</p>
                </div>
              ) : recentActivity.length > 0 ? (
                recentActivity.map((activity, index) => (
                  <div key={`${activity.type}-${activity.id}-${index}`} className="activity-item">
                    <div className="activity-icon">
                      {activity.type === 'expense' ? '💳' : '💰'}
                    </div>
                    <div className="activity-content">
                      <h4>
                        {activity.type === 'expense' 
                          ? activity.description 
                          : `Settlement in ${activity.groupName}`}
                      </h4>
                      <p>{activity.groupName} • {activity.date ? new Date(activity.date).toLocaleDateString() : 'Recent'}</p>
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
                        <span className="group-expenses">
                          💳 {group.expense_count || 0} expenses
                        </span>
                      </div>
                    </div>
                    <div className="group-actions">
                      <Button 
                        size="small"
                        variant="outline"
                        onClick={() => navigate(`/group/${group.id}`)}
                      >
                        View
                      </Button>
                    </div>
                  </div>
                ))
              ) : (
                <div className="empty-state">
                  <p>No groups yet. Create your first group to start splitting expenses!</p>
                  <Button 
                    variant="primary"
                    onClick={() => navigate('/groups')}
                  >
                    Create Group
                  </Button>
                </div>
              )}
              
              {groups && groups.length > 5 && (
                <div className="show-more">
                  <Button 
                    variant="outline"
                    onClick={() => navigate('/groups')}
                  >
                    View All {groups.length} Groups
                  </Button>
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