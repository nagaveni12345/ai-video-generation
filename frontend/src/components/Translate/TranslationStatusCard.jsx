import React from 'react';
import { Languages } from 'lucide-react';

const TranslationStatusCard = () => {
  return (
    <div
      style={{
        background: '#0D0D0D',
        border: '1px solid #1C1C1C',
        borderRadius: '16px',
        padding: '20px',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <p
        style={{
          margin: 0,
          marginBottom: '16px',
          fontSize: '15px',
          fontWeight: '600',
          color: '#FFFFFF',
          letterSpacing: '-0.01em',
        }}
      >
        Translation Status
      </p>

      <div
        style={{
          height: '190px',
          background: '#030303',
          borderRadius: '12px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '12px',
        }}
      >
        <Languages size={40} color="#4B5563" strokeWidth={1.5} />
        <span
          style={{
            color: '#6B7280',
            fontSize: '13px',
            fontWeight: '400',
          }}
        >
          Select languages to translate
        </span>
      </div>
    </div>
  );
};

export default TranslationStatusCard;
