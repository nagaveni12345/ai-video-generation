import React from 'react';
import { Sparkles, Check } from 'lucide-react';

const TranslationFeaturesCard = () => {
  const features = [
    { 
      title: 'Voice Cloning', 
      subtitle: 'Maintains your voice in all languages' 
    },
    { 
      title: 'Lip Sync', 
      subtitle: 'Automatically syncs lip movements' 
    },
    { 
      title: 'Subtitles', 
      subtitle: 'Auto-generated in each language' 
    },
  ];

  return (
    <div
      style={{
        background: '#0A0A14',
        border: '1px solid rgba(168, 85, 247, 0.25)',
        borderRadius: '16px',
        padding: '24px',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* Title */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '24px' }}>
        <Sparkles size={18} color="#A5B4FC" />
        <h3
          style={{
            margin: 0,
            fontSize: '15px',
            fontWeight: '600',
            color: '#FFFFFF',
            letterSpacing: '-0.01em',
          }}
        >
          Translation Features
        </h3>
      </div>

      {/* List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        {features.map((feature, idx) => (
          <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '14px' }}>
            {/* Checkbox Icon */}
            <div
              style={{
                width: '38px',
                height: '38px',
                background: '#16162A',
                borderRadius: '12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#6366F1',
                flexShrink: 0,
              }}
            >
              <Check size={18} strokeWidth={2.5} />
            </div>

            {/* Content */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
              <span
                style={{
                  fontSize: '15px',
                  fontWeight: '600',
                  color: '#FFFFFF',
                }}
              >
                {feature.title}
              </span>
              <span
                style={{
                  fontSize: '13px',
                  color: '#8E8EA0',
                  fontWeight: '400',
                }}
              >
                {feature.subtitle}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TranslationFeaturesCard;
