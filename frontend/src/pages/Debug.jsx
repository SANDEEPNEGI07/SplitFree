import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useGroups } from '../hooks/useApi';
import { getGroupBalances } from '../services/settlements';

const Debug = () => {
  const { user, isAuthenticated } = useAuth();
  const { groups } = useGroups();
  const [debugInfo, setDebugInfo] = useState({});

  const addResult = (test, result, error = null) => {
    // Legacy function for compatibility
  };

  const testBackendConnection = async () => {
    try {
      const response = await fetch('http://localhost:5000/swagger-ui');
      addResult('Backend Connection', response.ok ? 'SUCCESS' : 'FAILED');
    } catch (error) {
      addResult('Backend Connection', 'FAILED', error.message);
    }
  };

  const testRegistration = async () => {
    try {
      const userData = {
        username: 'debuguser',
        email: 'debug@test.com',
        password: 'testpass123'
      };

      const response = await fetch('/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      const data = await response.json();
      addResult('Registration Test', response.ok ? 'SUCCESS' : 'FAILED', JSON.stringify(data));
    } catch (error) {
      addResult('Registration Test', 'FAILED', error.message);
    }
  };

  const testLogin = async () => {
    try {
      const credentials = {
        email: 'debug@test.com',
        password: 'testpass123'
      };

      const response = await fetch('/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      const data = await response.json();
      addResult('Login Test', response.ok ? 'SUCCESS' : 'FAILED', JSON.stringify(data));

      if (data.access_token) {
        // Test token decoding
        try {
          const payload = JSON.parse(atob(data.access_token.split('.')[1]));
          addResult('Token Decode', 'SUCCESS', JSON.stringify(payload));
        } catch (error) {
          addResult('Token Decode', 'FAILED', error.message);
        }
      }
    } catch (error) {
      addResult('Login Test', 'FAILED', error.message);
    }
  };

  const clearResults = () => {
    setTestResults([]);
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'monospace' }}>
      <h1>Debug Page</h1>
      
      <div style={{ marginBottom: '20px' }}>
        <button onClick={testBackendConnection} style={{ margin: '5px', padding: '10px' }}>
          Test Backend Connection
        </button>
        <button onClick={testRegistration} style={{ margin: '5px', padding: '10px' }}>
          Test Registration
        </button>
        <button onClick={testLogin} style={{ margin: '5px', padding: '10px' }}>
          Test Login
        </button>
        <button onClick={clearResults} style={{ margin: '5px', padding: '10px' }}>
          Clear Results
        </button>
      </div>

      <div style={{ background: '#f5f5f5', padding: '20px', borderRadius: '5px' }}>
        <h3>Test Results:</h3>
        {testResults.length === 0 ? (
          <p>No tests run yet.</p>
        ) : (
          testResults.map((result, index) => (
            <div key={index} style={{ marginBottom: '10px', padding: '10px', background: 'white', borderRadius: '3px' }}>
              <strong>{result.time} - {result.test}:</strong> 
              <span style={{ color: result.result === 'SUCCESS' ? 'green' : 'red', marginLeft: '10px' }}>
                {result.result}
              </span>
              {result.error && (
                <div style={{ marginTop: '5px', fontSize: '12px', color: '#666' }}>
                  {result.error}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Debug;