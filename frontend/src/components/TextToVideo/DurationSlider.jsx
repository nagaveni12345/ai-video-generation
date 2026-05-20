import React from 'react';

const DurationSlider = ({ value, onChange }) => {
  return (
    <div 
      className="border border-[#1F1F1F] rounded-[18px] px-[24px] py-[20px] w-full"
      style={{ background: 'linear-gradient(180deg, #0B0B0B 0%, #050505 100%)' }}
    >
      <div className="flex justify-between items-center mb-[18px]">
        <h3 className="text-[18px] text-[#E5E7EB] font-medium leading-none">Duration: {value} seconds</h3>
      </div>
      <div className="relative w-full h-[14px] flex items-center group mb-[12px]">
        {/* Track (Inactive/Right) */}
        <div className="absolute w-full h-full bg-[#EAEAF0] rounded-full" />
        {/* Active Progress (Left) */}
        <div 
          className="absolute h-full bg-[#05050C] rounded-l-full transition-all duration-150" 
          style={{ width: `${((value - 5) / (60 - 5)) * 100}%` }} 
        />
        {/* Input Range (Invisible) */}
        <input 
          type="range" 
          min="5" 
          max="60" 
          value={value}
          onChange={(e) => onChange(parseInt(e.target.value))}
          className="absolute w-full h-full opacity-0 cursor-pointer z-10"
        />
        {/* Custom Thumb */}
        <div 
          className="absolute h-[14px] w-[14px] bg-white rounded-full border-[1.5px] border-[#0A0A10] pointer-events-none transition-all duration-150 shadow-sm box-border"
          style={{ left: `calc(${((value - 5) / (60 - 5)) * 100}% - 7px)` }}
        />
      </div>
      <div className="flex justify-between mt-[8px] px-[1px]">
        <span className="text-[13px] text-[#6B7280]">5s</span>
        <span className="text-[13px] text-[#6B7280]">60s</span>
      </div>
    </div>
  );
};

export default DurationSlider;
