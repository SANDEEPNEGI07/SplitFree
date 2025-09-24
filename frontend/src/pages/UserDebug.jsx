import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useGroups } from '../hooks/useApi';
import { getGroupBalances } from '../services/settlements';
import { authService } from '../services/auth';

const UserDebug = () => {
  const { user, isAuthenticated } = useAuth();
  const { groups } = useGroups();
  const [debugInfo, setDebugInfo] = useState({});
  const [testResults, setTestResults] = useState([]);

  const addTestResult = (test, result) => {
    setTestResults(prev => [...prev, { test, result, time: new Date().toLocaleTimeString() }]);
  };

  const testCurrentUser = async () => {
    try {
      const currentUser = await authService.getCurrentUser();
      addTestResult('getCurrentUser()', { success: true, data: currentUser });
    } catch (error) {
      addTestResult('getCurrentUser()', { success: false, error: error.message });
    }
  };

  const testBalance = async () => {
    if (groups && groups.length > 0 && user) {
      try {
        const firstGroup = groups[0];
        const balances = await getGroupBalances(firstGroup.id);
        const userBalance = balances.find(b => b.user_id == user.id || b.user_id === parseInt(user.id));
        addTestResult(`getGroupBalances(${firstGroup.id})`, { 
          success: true, 
          balances, 
          userBalance,
          userId: user.id 
        });
      } catch (error) {
        addTestResult('getGroupBalances', { success: false, error: error.message });
      }
    } else {
      addTestResult('getGroupBalances', { success: false, error: 'No groups or user available' });
    }
  };

  useEffect(() => {
    const gatherDebugInfo = async () => {
      const info = {
        isAuthenticated,
        user,
        userType: typeof user,
        userKeys: user ? Object.keys(user) : [],
        hasUserId: user?.id !== undefined,
        hasUsername: user?.username !== undefined,
        groups: groups ? groups.length : 0,
        groupsData: groups?.map(g => ({ id: g.id, name: g.name, expense_count: g.expense_count })),
        timestamp: new Date().toISOString(),
        localStorage: {
          hasAccessToken: !!localStorage.getItem('splitwise_access_token'),
          hasRefreshToken: !!localStorage.getItem('splitwise_refresh_token')
        }
      };

      setDebugInfo(info);
    };

    gatherDebugInfo();
  }, [user, groups, isAuthenticated]);

  return (
    <div style={{ padding: '20px' }}>
      <h1>User Debug Information</h1>
      
      <div style={{ marginBottom: '20px' }}>
        <button onClick={testCurrentUser} style={{ margin: '5px', padding: '10px' }}>
          Test getCurrentUser()
        </button>
        <button onClick={testBalance} style={{ margin: '5px', padding: '10px' }}>
          Test Balance Calculation
        </button>
        <button onClick={() => setTestResults([])} style={{ margin: '5px', padding: '10px' }}>
          Clear Tests
        </button>
      </div>

      <div style={{ display: 'flex', gap: '20px' }}>
        <div style={{ flex: 1 }}>
          <h2>Current State</h2>
          <pre style={{ background: '#f5f5f5', padding: '10px', overflow: 'auto', whiteSpace: 'pre-wrap', fontSize: '12px' }}>
            {JSON.stringify(debugInfo, null, 2)}
          </pre>
        </div>
        
        <div style={{ flex: 1 }}>
          <h2>Test Results</h2>
          <div style={{ background: '#f0f0f0', padding: '10px', maxHeight: '500px', overflow: 'auto' }}>
            {testResults.length === 0 ? (
              <p>No tests run yet</p>
            ) : (
              testResults.map((result, index) => (
                <div key={index} style={{ marginBottom: '10px', padding: '8px', background: 'white', borderRadius: '3px' }}>
                  <strong>{result.time} - {result.test}</strong>
                  <pre style={{ fontSize: '11px', margin: '5px 0' }}>
                    {JSON.stringify(result.result, null, 2)}
                  </pre>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserDebug;