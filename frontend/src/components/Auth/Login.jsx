import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { isValidEmail, validateRequired } from '../../utils/helpers';
import Button from '../UI/Button';
import FormInput from '../UI/FormInput';
import './Auth.css';

const Login = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [validationErrors, setValidationErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { login, error, clearError } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
    
    // Clear validation error when user starts typing
    if (validationErrors[name]) {
      setValidationErrors(prev => ({
        ...prev,
        [name]: '',
      }));
    }
    
    // Clear API error
    if (error) {
      clearError();
    }
  };

  const validateForm = () => {
    const errors = {};

    // Email validation
    const emailError = validateRequired(formData.email, 'Email');
    if (emailError) {
      errors.email = emailError;
    } else if (!isValidEmail(formData.email)) {
      errors.email = 'Please enter a valid email address';
    }

    // Password validation
    const passwordError = validateRequired(formData.password, 'Password');
    if (passwordError) {
      errors.password = passwordError;
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    try {
      await login(formData);
      navigate('/dashboard');
    } catch (err) {
      // Error is handled by AuthContext
      console.error('Login error:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <Link to="/" className="home-link">← Back to Home</Link>
          <h1>Welcome Back</h1>
          <p>Sign in to your SplitFree account</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <FormInput
            label="Email"
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            placeholder="Enter your email"
            autoComplete="email"
            error={validationErrors.email}
            required
          />

          <FormInput
            label="Password"
            type="password"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            placeholder="Enter your password"
            autoComplete="current-password"
            error={validationErrors.password}
            required
          />

          {error && (
            <div className="error-message auth-error">{error}</div>
          )}

          <Button
            type="submit"
            variant="primary"
            size="large"
            disabled={isSubmitting}
            loading={isSubmitting}
          >
            {isSubmitting ? 'Signing In...' : 'Login'}
          </Button>
        </form>

        <div className="auth-footer">
          <p>
            Don't have an account?{' '}
            <Link to="/register" className="auth-link">
              Sign up here
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;