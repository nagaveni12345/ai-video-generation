import React from 'react';

const StatsCardGroup = ({ selectedCount = 0 }) => {
  const stats = [
    { value: '50+', label: 'Languages' },
    { value: selectedCount, label: 'Selected' },
    { value: '0', label: 'Completed' },
  ];

  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(3, 1fr)',
        gap: '12px',
      }}
    >
      {stats.map((stat, idx) => (
        <div
          key={idx}
          style={{
            background: '#0B0B0B',
            border: '1px solid #1F1F1F',
            borderRadius: '12px',
            padding: '12px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            textAlign: 'center',
            gap: '4px',
          }}
        >
          <span
            style={{
              fontSize: '18px',
              fontWeight: '600',
              color: '#FFFFFF',
            }}
          >
            {stat.value}
          </span>
          <span
            style={{
              fontSize: '12px',
              color: '#6B7280',
              fontWeight: '400',
            }}
          >
            {stat.label}
          </span>
        </div>
      ))}
    </div>
  );
};

export default StatsCardGroup;
