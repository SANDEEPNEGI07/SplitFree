import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { acceptInvitation } from '../services/groups';
import LoadingSpinner from '../components/UI/LoadingSpinner';
import Button from '../components/UI/Button';

const AcceptInvitation = () => {
  const { token } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [invitation, setInvitation] = useState(null);
  const [error, setError] = useState('');
  const [accepting, setAccepting] = useState(false);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    if (token) {
      loadInvitation();
    } else {
      setError('Invalid invitation link');
      setLoading(false);
    }
  }, [token]);

  const loadInvitation = async () => {
    try {
      setLoading(true);
      const invitationData = await acceptInvitation(token);
      setInvitation(invitationData);
    } catch (error) {
      console.error('Error loading invitation:', error);
      setError(error.response?.data?.message || 'Invalid or expired invitation');
    } finally {
      setLoading(false);
    }
  };

  const handleAcceptInvitation = async () => {
    try {
      setAccepting(true);
      await acceptInvitation(token);
      setSuccess(true);
      setTimeout(() => {
        navigate('/groups');
      }, 2000);
    } catch (error) {
      console.error('Error accepting invitation:', error);
      setError(error.response?.data?.message || 'Failed to accept invitation');
    } finally {
      setAccepting(false);
    }
  };

  if (loading) {
    return (
      <div className="container">
        <div className="invitation-container">
          <LoadingSpinner message="Loading invitation..." />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container">
        <div className="invitation-container">
          <div className="invitation-error">
            <div className="error-icon">❌</div>
            <h2>Invalid Invitation</h2>
            <p>{error}</p>
            <Button onClick={() => navigate('/groups')}>
              Go to Groups
            </Button>
          </div>
        </div>
      </div>
    );
  }

  if (success) {
    return (
      <div className="container">
        <div className="invitation-container">
          <div className="invitation-success">
            <div className="success-icon">🎉</div>
            <h2>Welcome to {invitation?.group?.name}!</h2>
            <p>You have successfully joined the group.</p>
            <p>Redirecting to your groups...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="invitation-container">
        <div className="invitation-card">
          <div className="invitation-header">
            <h2>Group Invitation</h2>
            <p>You've been invited to join a group!</p>
          </div>

          {invitation && (
            <div className="invitation-details">
              <div className="group-info">
                <h3>{invitation.group?.name}</h3>
                <p>{invitation.group?.description}</p>
                <div className="group-stats">
                  <span>👥 {invitation.group?.users?.length || 0} members</span>
                  <span className={`group-badge ${invitation.group?.is_public ? 'public' : 'private'}`}>
                    {invitation.group?.is_public ? '🌍 Public' : '🔒 Private'}
                  </span>
                </div>
              </div>

              <div className="invitation-actions">
                <Button 
                  onClick={handleAcceptInvitation}
                  disabled={accepting}
                  variant="primary"
                >
                  {accepting ? 'Joining...' : 'Accept Invitation'}
                </Button>
                <Button 
                  onClick={() => navigate('/groups')}
                  variant="secondary"
                >
                  Maybe Later
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AcceptInvitation;