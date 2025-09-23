import React from 'react';
import './Layout.css';

const Footer = () => {
  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-content">
          <div className="footer-left">
            <p>&copy; 2024 Splitwise Clone. Built with React & Flask.</p>
          </div>
          <div className="footer-right">
            <p>Made with ❤️ for splitting bills</p>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;