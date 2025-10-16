import React, { useState } from 'react';
import { sendGroupInvitation } from '../../services/groups';
import './GroupInvite.css';

const GroupInvite = ({ group, onClose, onInviteSent }) => {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email.trim()) {
      setError('Email is required');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await sendGroupInvitation(group.id, email.trim(), message.trim());
      setSuccess(true);
      setEmail('');
      setMessage('');
      
      // Call parent callback if provided
      if (onInviteSent) {
        onInviteSent(email.trim());
      }
      
      // Auto close after 2 seconds
      setTimeout(() => {
        setSuccess(false);
        onClose();
      }, 2000);
      
    } catch (error) {
      setError(error.response?.data?.message || 'Failed to send invitation');
    } finally {
      setLoading(false);
    }
  };

  const copyGroupCode = () => {
    navigator.clipboard.writeText(group.invite_code);
    // You could add a toast notification here
  };

  const shareGroupCode = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: `Join ${group.name} on SplitFree`,
          text: `Use code: ${group.invite_code}`,
          url: `${window.location.origin}/join/${group.invite_code}`
        });
      } catch (error) {
        console.log('Error sharing:', error);
      }
    } else {
      copyGroupCode();
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content invite-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Invite People to {group.name}</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <div className="modal-body">
          {success ? (
            <div className="success-message">
              <div className="success-icon">✅</div>
              <h3>Invitation Sent!</h3>
              <p>An invitation email has been sent to {email}</p>
            </div>
          ) : (
            <>
              {/* Email Invitation Section */}
              <div className="invite-section">
                <h3>📧 Send Email Invitation</h3>
                <form onSubmit={handleSubmit}>
                  <div className="form-group">
                    <label>Email Address</label>
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="friend@example.com"
                      className="form-input"
                      required
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Personal Message (Optional)</label>
                    <textarea
                      value={message}
                      onChange={(e) => setMessage(e.target.value)}
                      placeholder="Hey! Join our group to split expenses..."
                      className="form-input"
                      rows="3"
                    />
                  </div>

                  {error && <div className="error-message">{error}</div>}

                  <button 
                    type="submit" 
                    className="btn btn-primary"
                    disabled={loading}
                  >
                    {loading ? 'Sending...' : 'Send Invitation'}
                  </button>
                </form>
              </div>

              {/* Divider */}
              <div className="invite-divider">
                <span>OR</span>
              </div>

              {/* Group Code Section */}
              <div className="invite-section">
                <h3>🔑 Share Group Code</h3>
                <p>Anyone with this code can join the group</p>
                
                <div className="group-code-container">
                  <div className="group-code">{group.invite_code}</div>
                  <div className="code-actions">
                    <button 
                      onClick={copyGroupCode}
                      className="btn btn-secondary"
                    >
                      📋 Copy Code
                    </button>
                    <button 
                      onClick={shareGroupCode}
                      className="btn btn-secondary"
                    >
                      📤 Share
                    </button>
                  </div>
                </div>
                
                <div className="share-help">
                  <small>Share via WhatsApp, SMS, or any messaging app!</small>
                </div>
              </div>

              {/* Group Settings Info */}
              <div className="group-info">
                <div className={`group-status ${group.is_public ? 'public' : 'private'}`}>
                  <span className="status-icon">
                    {group.is_public ? '🌍' : '🔒'}
                  </span>
                  <span className="status-text">
                    {group.is_public 
                      ? 'Public Group - Anyone with the code can join'
                      : 'Private Group - Requires email invitation'
                    }
                  </span>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default GroupInvite;