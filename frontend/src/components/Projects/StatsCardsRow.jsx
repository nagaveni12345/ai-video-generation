import React from 'react';

const StatCard = ({ number, label, color }) => {
  return (
    <div className="bg-[#0B0B0B] border border-[#1F1F1F] rounded-[14px] p-[18px]">
      <div 
        className="text-[22px] font-[600]"
        style={{ color: color }}
      >
        {number}
      </div>
      <div className="text-[13px] text-[#6B7280] mt-[6px]">
        {label}
      </div>
    </div>
  );
};

const StatsCardsRow = () => {
  const stats = [
    { number: 24, label: 'Total Projects', color: '#A855F7' },
    { number: 18, label: 'Videos Created', color: '#3B82F6' },
    { number: 4, label: 'Avatars', color: '#22C55E' },
    { number: 12, label: 'Translations', color: '#6366F1' }
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-[16px] mb-[28px] w-full">
      {stats.map((stat, index) => (
        <StatCard 
          key={index} 
          number={stat.number} 
          label={stat.label} 
          color={stat.color} 
        />
      ))}
    </div>
  );
};

export default StatsCardsRow;
