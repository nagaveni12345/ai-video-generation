import React from 'react';
import { Sparkles } from 'lucide-react';

const Preview = () => {
  return (
    <div 
      className="border border-[#1F1F1F] rounded-[16px] p-[20px] w-full flex flex-col"
      style={{ background: 'linear-gradient(180deg, #0B0B0B 0%, #050505 100%)' }}
    >
      <h3 className="text-[14px] text-[#E5E7EB] mb-[12px] font-medium leading-none">Preview</h3>
      
      <div 
        className="h-[220px] bg-[#030303] border border-[#111111] rounded-[12px] flex flex-col items-center justify-center relative"
        style={{ boxShadow: 'inset 0 0 30px rgba(0,0,0,0.6)' }}
      >
        <Sparkles className="w-[22px] h-[22px] text-[#6B7280]" />
        <p className="text-[13px] text-[#6B7280] font-normal mt-[6px]">
          Your video will appear here
        </p>
      </div>
    </div>
  );
};

export default Preview;
