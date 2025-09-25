import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './Homepage.css';

const Homepage = () => {
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const navigate = useNavigate();
  const { login, register } = useAuth();

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (isLogin) {
        // Login with email and password (backend expects email)
        await login({ email: formData.email, password: formData.password });
      } else {
        // Signup with username, email, and password
        await register({ username: formData.username, email: formData.email, password: formData.password });
      }
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.message || err.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  const openAuthModal = (type) => {
    setIsLogin(type === 'login');
    setShowAuthModal(true);
    setError('');
    setFormData({ username: '', email: '', password: '' });
  };

  const closeAuthModal = () => {
    setShowAuthModal(false);
    setError('');
    setFormData({ username: '', email: '', password: '' });
  };

  const switchAuthMode = () => {
    setIsLogin(!isLogin);
    setError('');
    setFormData({ username: '', email: '', password: '' });
  };

  return (
    <div className="homepage">
      {/* Header */}
      <header className="homepage-header">
        <div className="container">
          <div className="header-content">
            <div className="logo">
              <span className="logo-icon">💰</span>
              <span className="logo-text">SplitFree</span>
            </div>
            <nav className="header-nav">
              <button 
                className="btn btn-outline"
                onClick={() => openAuthModal('login')}
              >
                Login
              </button>
              <button 
                className="btn btn-primary"
                onClick={() => openAuthModal('signup')}
              >
                Sign Up
              </button>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="hero-section">
        <div className="container">
          <div className="hero-content">
            <div className="hero-text">
              <h1 className="hero-title">
                Split expenses with friends, 
                <span className="highlight"> effortlessly</span>
              </h1>
              <p className="hero-description">
                Track shared expenses, split bills fairly, and settle up with ease. 
                SplitFree makes group expense management simple and transparent.
              </p>
              <div className="hero-actions">
                <button 
                  className="btn btn-primary btn-large"
                  onClick={() => openAuthModal('signup')}
                >
                  Start Splitting for Free
                </button>
                <button 
                  className="btn btn-outline btn-large"
                  onClick={() => openAuthModal('login')}
                >
                  Already have an account?
                </button>
              </div>
            </div>
            <div className="hero-image">
              <div className="hero-illustration">
                <div className="expense-card">
                  <div className="expense-header">
                    <span className="expense-icon">🍕</span>
                    <span className="expense-title">Pizza Night</span>
                  </div>
                  <div className="expense-amount">$48.00</div>
                  <div className="expense-split">Split between 4 friends</div>
                </div>
                <div className="expense-card">
                  <div className="expense-header">
                    <span className="expense-icon">🏠</span>
                    <span className="expense-title">Rent</span>
                  </div>
                  <div className="expense-amount">$1,200.00</div>
                  <div className="expense-split">Split between 3 roommates</div>
                </div>
                <div className="expense-card">
                  <div className="expense-header">
                    <span className="expense-icon">✈️</span>
                    <span className="expense-title">Trip to Paris</span>
                  </div>
                  <div className="expense-amount">$2,400.00</div>
                  <div className="expense-split">Split between 6 friends</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <div className="container">
          <div className="section-header">
            <h2>Why Choose SplitFree?</h2>
            <p>Everything you need to manage group expenses seamlessly</p>
          </div>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">📊</div>
              <h3>Smart Expense Tracking</h3>
              <p>Add expenses quickly and split them fairly between group members with our intelligent splitting system.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">👥</div>
              <h3>Group Management</h3>
              <p>Create groups for different occasions - trips, roommates, dinners. Keep everything organized and separate.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">💳</div>
              <h3>Easy Settlements</h3>
              <p>Track who owes what and settle up with a single click. No more awkward money conversations.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📱</div>
              <h3>Real-time Updates</h3>
              <p>Everyone in your group sees expense updates instantly. Stay synchronized with your friends.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🔒</div>
              <h3>Secure & Private</h3>
              <p>Your financial data is encrypted and secure. Only group members can see shared expenses.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📈</div>
              <h3>Detailed History</h3>
              <p>View complete expense history with detailed breakdowns and settlement records for all your groups.</p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="how-it-works-section">
        <div className="container">
          <div className="section-header">
            <h2>How SplitFree Works</h2>
            <p>Get started in 3 simple steps</p>
          </div>
          <div className="steps-grid">
            <div className="step-card">
              <div className="step-number">1</div>
              <div className="step-content">
                <h3>Create a Group</h3>
                <p>Start by creating a group and inviting your friends, roommates, or travel companions.</p>
              </div>
            </div>
            <div className="step-card">
              <div className="step-number">2</div>
              <div className="step-content">
                <h3>Add Expenses</h3>
                <p>Add shared expenses like meals, rent, utilities, or trip costs. Choose how to split them.</p>
              </div>
            </div>
            <div className="step-card">
              <div className="step-number">3</div>
              <div className="step-content">
                <h3>Settle Up</h3>
                <p>See who owes what and settle up easily. Keep track of all payments and balances.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="container">
          <div className="cta-content">
            <h2>Ready to Start Splitting?</h2>
            <p>Join thousands of users who are already managing their group expenses with SplitFree</p>
            <button 
              className="btn btn-primary btn-large"
              onClick={() => openAuthModal('signup')}
            >
              Sign Up Now - It's Free!
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="homepage-footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-logo">
              <span className="logo-icon">💰</span>
              <span className="logo-text">SplitFree</span>
            </div>
            <div className="footer-text">
              <p>&copy; 2025 SplitFree. Making expense splitting effortless.</p>
            </div>
          </div>
        </div>
      </footer>

      {/* Authentication Modal */}
      {showAuthModal && (
        <div className="modal-overlay" onClick={closeAuthModal}>
          <div className="auth-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{isLogin ? 'Welcome Back' : 'Join SplitFree'}</h2>
              <button className="close-btn" onClick={closeAuthModal}>×</button>
            </div>
            
            <form onSubmit={handleSubmit} className="auth-form">
              {error && <div className="error-message">{error}</div>}
              
              {!isLogin && (
                <div className="form-group">
                  <label htmlFor="username">Username</label>
                  <input
                    type="text"
                    id="username"
                    name="username"
                    value={formData.username}
                    onChange={handleInputChange}
                    required
                    placeholder="Enter your username"
                  />
                </div>
              )}

              <div className="form-group">
                <label htmlFor="email">Email</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  required
                  placeholder="Enter your email"
                />
              </div>

              <div className="form-group">
                <label htmlFor="password">Password</label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  required
                  placeholder="Enter your password"
                />
              </div>

              <button 
                type="submit" 
                className="btn btn-primary btn-full"
                disabled={loading}
              >
                {loading ? 'Please wait...' : (isLogin ? 'Login' : 'Sign Up')}
              </button>
            </form>

            <div className="auth-switch">
              <p>
                {isLogin ? "Don't have an account? " : "Already have an account? "}
                <button 
                  type="button" 
                  className="link-btn"
                  onClick={switchAuthMode}
                >
                  {isLogin ? 'Sign up here' : 'Login here'}
                </button>
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Homepage;