import React from 'react';
import { Globe } from 'lucide-react';

const TranslateButton = ({ selectedCount = 0 }) => {
  return (
    <button
      style={{
        width: '100%',
        height: '60px',
        borderRadius: '16px',
        background: 'linear-gradient(90deg, #2E3192 0%, #8B20B3 100%)',
        color: '#9CA3AF',
        fontSize: '17px',
        fontWeight: '500',
        border: 'none',
        cursor: 'pointer',
        boxShadow: '0 10px 40px rgba(46, 49, 146, 0.4), 0 10px 40px rgba(139, 32, 179, 0.4)',
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '12px',
        marginTop: '12px',
        letterSpacing: '0.01em'
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateY(-2px) scale(1.005)';
        e.currentTarget.style.color = '#FFFFFF';
        e.currentTarget.style.boxShadow = '0 15px 50px rgba(46, 49, 146, 0.5), 0 15px 50px rgba(139, 32, 179, 0.5)';
        e.currentTarget.style.filter = 'brightness(1.1)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0) scale(1)';
        e.currentTarget.style.color = '#9CA3AF';
        e.currentTarget.style.boxShadow = '0 10px 40px rgba(46, 49, 146, 0.4), 0 10px 40px rgba(139, 32, 179, 0.4)';
        e.currentTarget.style.filter = 'brightness(1)';
      }}
      className="group"
    >
      <Globe 
        size={20} 
        style={{ 
          opacity: 0.7,
          strokeWidth: 1.5
        }} 
      />
      <span>
        Translate to {selectedCount} Language{selectedCount !== 1 ? 's' : ''}
      </span>
    </button>
  );
};

export default TranslateButton;
