import React from 'react';
import ReactCountryFlag from 'react-country-flag';

const ALL_LANGUAGES = [
  { label: 'English',    code: 'US' },
  { label: 'Spanish',    code: 'ES' },
  { label: 'French',     code: 'FR' },
  { label: 'German',     code: 'DE' },
  { label: 'Chinese',    code: 'CN' },
  { label: 'Japanese',   code: 'JP' },
  { label: 'Korean',     code: 'KR' },
  { label: 'Arabic',     code: 'SA' },
  { label: 'Hindi',      code: 'IN' },
  { label: 'Portuguese', code: 'BR' },
  { label: 'Russian',    code: 'RU' },
  { label: 'Italian',    code: 'IT' },
];

const AllLanguagesCard = ({ selected, onToggle }) => {
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
      <p
        style={{
          margin: 0,
          fontSize: '15px',
          fontWeight: '600',
          color: '#FFFFFF',
          letterSpacing: '-0.01em',
        }}
      >
        All Languages
      </p>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '10px',
        }}
      >
        {ALL_LANGUAGES.map((lang) => {
          const isSelected = selected.some((l) => l.code === lang.code);
          return (
            <button
              key={lang.code}
              onClick={() => onToggle(lang)}
              style={{
                height: '44px',
                width: '100%',
                background: isSelected ? '#18181F' : '#050505',
                border: isSelected ? '1px solid #4F46E5' : '1px solid #1F1F1F',
                borderRadius: '10px',
                padding: '0 12px',
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                cursor: 'pointer',
                transition: 'all 0.15s ease',
              }}
            >
              <ReactCountryFlag
                countryCode={lang.code}
                svg
                style={{
                  width: '20px',
                  height: '14px',
                  borderRadius: '2px',
                  objectFit: 'cover',
                  flexShrink: 0,
                }}
              />
              <span
                style={{
                  fontSize: '14px',
                  color: isSelected ? '#FFFFFF' : '#D1D5DB',
                  fontWeight: isSelected ? '500' : '400',
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

export default AllLanguagesCard;
