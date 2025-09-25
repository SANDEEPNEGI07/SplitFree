import React from 'react';
import './UI.css';

const FormInput = ({ 
  label,
  error,
  required = false,
  className = '',
  containerClassName = '',
  ...props 
}) => {
  const inputClass = `form-input ${error ? 'form-input-error' : ''} ${className}`.trim();
  const containerClass = `form-group ${containerClassName}`.trim();

  return (
    <div className={containerClass}>
      {label && (
        <label className="form-label">
          {label}
          {required && <span className="form-required">*</span>}
        </label>
      )}
      <input className={inputClass} {...props} />
      {error && <span className="form-error">{error}</span>}
    </div>
  );
};

export default FormInput;