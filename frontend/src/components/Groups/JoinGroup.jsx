import React, { useState } from 'react';
import { joinGroupByCode, getGroupByCode } from '../../services/groups';
import './JoinGroup.css';

const JoinGroup = ({ onClose, onGroupJoined }) => {
  const [inviteCode, setInviteCode] = useState('');
  const [groupPreview, setGroupPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [joining, setJoining] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handlePreview = async () => {
    if (!inviteCode.trim()) {
      setError('Please enter an invite code');
      return;
    }

    setLoading(true);
    setError('');
    try {
      const group = await getGroupByCode(inviteCode.trim());
      setGroupPreview(group);
    } catch (error) {
      console.error('Error previewing group:', error);
      setError('Invalid invite code or group not found');
      setGroupPreview(null);
    } finally {
      setLoading(false);
    }
  };

  const handleJoinGroup = async () => {
    if (!groupPreview) return;

    setJoining(true);
    setError('');
    try {
      await joinGroupByCode(inviteCode.trim());
      setSuccess(true);
      setTimeout(() => {
        onGroupJoined();
        onClose();
      }, 1500);
    } catch (error) {
      console.error('Error joining group:', error);
      setError(error.response?.data?.message || 'Failed to join group');
    } finally {
      setJoining(false);
    }
  };

  const handleCodeChange = (e) => {
    const code = e.target.value.toUpperCase();
    setInviteCode(code);
    setGroupPreview(null);
    setError('');
  };

  if (success) {
    return (
      <div className="join-modal-overlay" onClick={onClose}>
        <div className="join-modal" onClick={(e) => e.stopPropagation()}>
          <div className="join-success">
            <div className="success-icon">🎉</div>
            <h3>Successfully Joined!</h3>
            <p>Welcome to {groupPreview?.name}!</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="join-modal-overlay" onClick={onClose}>
      <div className="join-modal" onClick={(e) => e.stopPropagation()}>
        <div className="join-header">
          <h2>Join a Group</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <div className="join-content">
          <div className="join-section">
            <h3>Enter Group Code</h3>
            <p>Enter the SPLIT-ABC123 format code to join a group</p>
            
            <div className="code-input-section">
              <div className="form-group">
                <input
                  type="text"
                  value={inviteCode}
                  onChange={handleCodeChange}
                  placeholder="SPLIT-ABC123"
                  className="code-input"
                  maxLength={12}
                />
                <button 
                  onClick={handlePreview}
                  disabled={loading || !inviteCode.trim()}
                  className="btn btn-secondary"
                >
                  {loading ? 'Checking...' : 'Preview Group'}
                </button>
              </div>

              {error && (
                <div className="error-message">{error}</div>
              )}

              {groupPreview && (
                <div className="group-preview">
                  <div className="preview-header">
                    <h4>Group Preview</h4>
                    <span className={`group-badge ${groupPreview.is_public ? 'public' : 'private'}`}>
                      {groupPreview.is_public ? '🌍 Public' : '🔒 Private'}
                    </span>
                  </div>
                  
                  <div className="preview-details">
                    <h5>{groupPreview.name}</h5>
                    <p>{groupPreview.description}</p>
                    <div className="preview-stats">
                      <span>👥 {groupPreview.users?.length || 0} members</span>
                    </div>
                  </div>

                  <div className="preview-actions">
                    <button 
                      onClick={handleJoinGroup}
                      disabled={joining}
                      className="btn btn-primary"
                    >
                      {joining ? 'Joining...' : `Join ${groupPreview.name}`}
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="join-divider">
            <span>or</span>
          </div>

          <div className="join-section">
            <h3>Email Invitation</h3>
            <p>If you received an email invitation, click the link in the email to join directly.</p>
            <div className="email-help">
              <div className="help-icon">📧</div>
              <div className="help-text">
                <strong>Check your email</strong>
                <br />Look for an invitation email and click the "Join Group" button
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default JoinGroup;