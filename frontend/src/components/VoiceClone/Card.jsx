import React from 'react';

const Card = ({ children, className = '' }) => {
  return (
    <div 
      className={`bg-gradient-to-b from-[#0B0B0B] to-[#050505] border border-[#1F1F1F] rounded-[16px] p-[20px] ${className}`}
    >
      {children}
    </div>
  );
};

export default Card;
