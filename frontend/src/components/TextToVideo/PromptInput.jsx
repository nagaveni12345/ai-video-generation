import React from 'react';

const PromptInput = ({ value, onChange }) => {
  return (
    <div className="bg-[#0B0B0B] border border-[#1F1F1F] rounded-[16px] p-[20px] flex flex-col">
      <h3 className="text-[14px] text-[#E5E7EB] mb-[12px] font-medium">Describe Your Video</h3>
      <div className="relative bg-[#050505] border border-[#1F1F1F] rounded-[12px] p-[12px] flex flex-col h-[130px]">
        <textarea 
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="w-full flex-1 bg-transparent border-none outline-none text-[#D1D5DB] placeholder:text-[#4B5563] text-[13px] leading-relaxed resize-none scrollbar-hide"
          placeholder="Example: A serene sunset over a mountain lake with birds flying across the sky, golden hour lighting, cinematic 4K..."
          maxLength={1000}
        />
      </div>
      <div className="mt-[8px] text-[12px] text-[#6B7280]">
        {value.length} / 1000 characters
      </div>
    </div>
  );
};

export default PromptInput;
