import React, { useState } from 'react';
import ReactCountryFlag from 'react-country-flag';
import { Sparkles } from 'lucide-react';

const POPULAR_LANGUAGES = [
  { label: 'English',    code: 'US' },
  { label: 'Spanish',    code: 'ES' },
  { label: 'French',     code: 'FR' },
  { label: 'German',     code: 'DE' },
  { label: 'Chinese',    code: 'CN' },
  { label: 'Japanese',   code: 'JP' },
  { label: 'Arabic',     code: 'SA' },
  { label: 'Portuguese', code: 'BR' },
];

  

const PopularLanguagesCard = ({ selected, onToggle }) => {
  return (
    <div
      style={{
        background: '#0D0D0D',
        border: '1px solid #1C1C1C',
        borderRadius: '16px',
        padding: '20px',
        display: 'flex',
        flexDirection: 'column',
        gap: '16px',
      }}
    >
      {/* Title row */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <Sparkles size={16} color="#A5B4FC" />
        <p
          style={{
            margin: 0,
            fontSize: '15px',
            fontWeight: '600',
            color: '#FFFFFF',
            letterSpacing: '-0.01em',
          }}
        >
          Popular Languages
        </p>
      </div>

      {/* 2-col grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '10px',
        }}
      >
        {POPULAR_LANGUAGES.map((lang) => {
          const isSelected = selected.some((l) => l.code === lang.code);

          return (
            <button
              key={lang.code}
              onClick={() => onToggle(lang)}
              style={{
                height: '52px',
                background: isSelected ? '#18181F' : '#050505',
                border: isSelected ? '1px solid #4F46E5' : '1px solid #1F1F1F',
                borderRadius: '10px',
                padding: '0 16px',
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                cursor: 'pointer',
                outline: 'none',
                transition: 'border 0.15s ease, background 0.15s ease',
                boxSizing: 'border-box',
              }}
              onMouseEnter={(e) => {
                if (!isSelected) {
                  e.currentTarget.style.border = '1px solid #2A2A2A';
                  e.currentTarget.style.background = '#0A0A0A';
                }
              }}
              onMouseLeave={(e) => {
                if (!isSelected) {
                  e.currentTarget.style.border = '1px solid #1F1F1F';
                  e.currentTarget.style.background = '#050505';
                }
              }}
            >
              <ReactCountryFlag
                countryCode={lang.code}
                svg
                style={{
                  width: '24px',
                  height: '17px',
                  borderRadius: '3px',
                  objectFit: 'cover',
                  flexShrink: 0,
                }}
              />
              <span
                style={{
                  fontSize: '15px',
                  color: isSelected ? '#FFFFFF' : '#D1D5DB',
                  fontWeight: isSelected ? '500' : '400',
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                }}
              >
                {lang.label}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default PopularLanguagesCard;
