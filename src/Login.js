import React, { useState } from 'react';
import logo from './assets/logos/logo.png';
import facebookLogo from './assets/logos/facebook.png';
import appleLogo from './assets/logos/apple.png';
import googleLogo from './assets/logos/google.png';
import './App.css';

function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [stayLoggedIn, setStayLoggedIn] = useState(false);
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const [forgotPasswordEmail, setForgotPasswordEmail] = useState('');
  const [forgotPasswordMessage, setForgotPasswordMessage] = useState('');
  const [forgotPasswordError, setForgotPasswordError] = useState('');
  const [isSubmittingReset, setIsSubmittingReset] = useState(false);

  const isFormValid = email.trim() !== '' && password.trim() !== '';
  const isForgotPasswordValid = forgotPasswordEmail.trim() !== '';

  const handleSubmit = (e) => {
    e.preventDefault();
    if (isFormValid) {
      console.log('Sign in attempted with:', { email, password, stayLoggedIn });
    }
  };

  const handleForgotPasswordSubmit = async (e) => {
    e.preventDefault();
    if (!isForgotPasswordValid) return;

    setIsSubmittingReset(true);
    setForgotPasswordError('');
    setForgotPasswordMessage('');

    try {
      const response = await fetch('http://localhost:8000/auth/forgot-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: forgotPasswordEmail }),
      });

      const data = await response.json();
      
      if (response.ok) {
        setForgotPasswordMessage(data.message);
      } else {
        setForgotPasswordError(data.detail || 'An error occurred');
      }
    } catch (error) {
      setForgotPasswordError('Network error. Please try again.');
    } finally {
      setIsSubmittingReset(false);
    }
  };

  const handleReturnToSignIn = () => {
    setShowForgotPassword(false);
    setForgotPasswordEmail('');
    setForgotPasswordMessage('');
    setForgotPasswordError('');
  };

  return (
    <div className="App">
      <div className="login-container">
        <div className="logo-container">
          <img src={logo} alt="StubHub" className="logo" />
        </div>
        
        {!showForgotPassword ? (
          <>
            <h1 className="login-title">Sign in to StubHub</h1>
            
            <form onSubmit={handleSubmit} className="login-form">
              <div className="input-group">
                <input
                  type="email"
                  placeholder="Email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="input-field"
                />
              </div>
              
              <div className="input-group">
                <input
                  type="password"
                  placeholder="Password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="input-field"
                />
              </div>
              
              <div className="checkbox-row">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={stayLoggedIn}
                    onChange={(e) => setStayLoggedIn(e.target.checked)}
                    className="checkbox"
                  />
                  Stay logged in
                </label>
                <button type="button" className="forgot-password" onClick={() => setShowForgotPassword(true)}>Forgot Password</button>
              </div>
              
              <button
                type="submit"
                className={`sign-in-btn ${!isFormValid ? 'disabled' : ''}`}
                disabled={!isFormValid}
              >
                Sign in
              </button>
            </form>
            
            <button className="email-code-btn">
              Sign in with Email Code
            </button>
            
            <div className="social-login">
              <button className="facebook-btn">
                <img src={facebookLogo} alt="Facebook" className="social-icon" />
                Log in with Facebook
              </button>
              
              <button className="apple-btn">
                <img src={appleLogo} alt="Apple" className="social-icon" />
                Sign in with Apple
              </button>
              
              <button className="google-btn">
                <img src={googleLogo} alt="Google" className="social-icon" />
                Sign in with Google
              </button>
            </div>
            
            <div className="create-account">
              <span>New to StubHub? </span>
              <button type="button" className="create-account-link" onClick={() => console.log('Create account clicked')}>Create account</button>
            </div>
          </>
        ) : (
          <>
            <h1 className="login-title">Forgot Password</h1>
            
            <form onSubmit={handleForgotPasswordSubmit} className="login-form">
              <div className="input-group">
                <input
                  type="email"
                  placeholder="Email"
                  value={forgotPasswordEmail}
                  onChange={(e) => setForgotPasswordEmail(e.target.value)}
                  className="input-field"
                />
              </div>
              
              {forgotPasswordError && (
                <div className="error-message">{forgotPasswordError}</div>
              )}
              
              {forgotPasswordMessage && (
                <div className="success-message">{forgotPasswordMessage}</div>
              )}
              
              <button
                type="submit"
                className={`sign-in-btn ${!isForgotPasswordValid || isSubmittingReset ? 'disabled' : ''}`}
                disabled={!isForgotPasswordValid || isSubmittingReset}
              >
                {isSubmittingReset ? 'Sending...' : 'Send Reset Link'}
              </button>
            </form>
            
            <button type="button" className="return-to-signin" onClick={handleReturnToSignIn}>
              Return to sign in
            </button>
          </>
        )}
      </div>
    </div>
  );
}

export default Login;
