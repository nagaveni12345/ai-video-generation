import React, { useState, useRef, useEffect } from 'react';
import ReactCountryFlag from 'react-country-flag';

const LANGUAGES = [
  { label: 'Spanish',    code: 'ES' },
  { label: 'French',     code: 'FR' },
  { label: 'German',     code: 'DE' },
  { label: 'Italian',    code: 'IT' },
  { label: 'Portuguese', code: 'BR' },
  { label: 'Hindi',      code: 'IN' },
  { label: 'Arabic',     code: 'SA' },
  { label: 'Chinese',    code: 'CN' },
  { label: 'Japanese',   code: 'JP' },
  { label: 'Korean',     code: 'KR' },
  { label: 'Russian',    code: 'RU' },
  { label: 'Dutch',      code: 'NL' },
  { label: 'Turkish',    code: 'TR' },
  { label: 'Polish',     code: 'PL' },
  { label: 'English',    code: 'US' },
];

const ChevronDown = ({ open }) => (
  <svg
    width="16" height="16" viewBox="0 0 16 16" fill="none"
    xmlns="http://www.w3.org/2000/svg"
    style={{
      transition: 'transform 0.2s ease',
      transform: open ? 'rotate(180deg)' : 'rotate(0deg)',
      flexShrink: 0,
    }}
  >
    <path d="M4 6L8 10L12 6" stroke="#6B7280" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

const TargetLanguageDropdown = () => {
  const [selected, setSelected] = useState(LANGUAGES[0]);
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    const handler = (e) => {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  return (
    <div
      style={{
        background: '#0D0D0D',
        border: '1px solid #1C1C1C',
        borderRadius: '16px',
        padding: '20px',
        display: 'flex',
        flexDirection: 'column',
        gap: '14px',
      }}
    >
      <p style={{ margin: 0, fontSize: '15px', fontWeight: '600', color: '#FFFFFF', letterSpacing: '-0.01em' }}>
        Target Language
      </p>

      <div ref={ref} style={{ position: 'relative' }}>
        <button
          onClick={() => setOpen((v) => !v)}
          style={{
            width: '100%',
            height: '40px',
            background: '#050505',
            border: '1px solid #1F1F1F',
            borderRadius: '8px',
            padding: '0 12px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            cursor: 'pointer',
            outline: 'none',
            boxSizing: 'border-box',
          }}
        >
          <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <ReactCountryFlag
              countryCode={selected.code}
              svg
              style={{ width: '20px', height: '14px', borderRadius: '2px', objectFit: 'cover' }}
            />
            <span style={{ fontSize: '14px', color: '#E5E7EB', fontWeight: '400' }}>{selected.label}</span>
          </span>
          <ChevronDown open={open} />
        </button>

        {open && (
          <div
            style={{
              position: 'absolute',
              top: 'calc(100% + 4px)',
              left: 0, right: 0,
              background: '#0D0D0D',
              border: '1px solid #1F1F1F',
              borderRadius: '8px',
              overflow: 'hidden',
              zIndex: 100,
              boxShadow: '0 8px 24px rgba(0,0,0,0.6)',
              maxHeight: '200px',
              overflowY: 'auto',
            }}
          >
            {LANGUAGES.map((lang) => {
              const isActive = lang.label === selected.label;
              return (
                <div
                  key={lang.label}
                  onClick={() => { setSelected(lang); setOpen(false); }}
                  style={{
                    padding: '9px 12px',
                    display: 'flex', alignItems: 'center', gap: '8px',
                    fontSize: '13px',
                    color: isActive ? '#FFFFFF' : '#9CA3AF',
                    background: isActive ? '#1A1A1A' : 'transparent',
                    cursor: 'pointer',
                    transition: 'background 0.15s ease',
                  }}
                  onMouseEnter={(e) => { if (!isActive) e.currentTarget.style.background = '#141414'; }}
                  onMouseLeave={(e) => { if (!isActive) e.currentTarget.style.background = 'transparent'; }}
                >
                  <ReactCountryFlag
                    countryCode={lang.code}
                    svg
                    style={{ width: '18px', height: '13px', borderRadius: '2px', objectFit: 'cover' }}
                  />
                  <span>{lang.label}</span>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default TargetLanguageDropdown;
