import React from 'react';
import { Sparkles } from 'lucide-react';

const ProTips = () => {
  const tips = [
    "Be specific with details like lighting, camera angles, and mood",
    "Include action verbs for more dynamic videos",
    "Mention color palettes to get the perfect aesthetic"
  ];

  return (
    <div 
      className="border border-[rgba(168,85,247,0.3)] rounded-[16px] p-[16px]"
      style={{ background: 'linear-gradient(135deg, #1E0B2E 0%, #3B0A2A 100%)' }}
    >
      <div className="flex items-center gap-[8px] mb-[12px]">
        <Sparkles className="w-4 h-4 text-[#A855F7]" />
        <h3 className="text-[14px] font-medium text-white leading-none">Pro Tips</h3>
      </div>
      <ul className="flex flex-col gap-[10px]">
        {tips.map((tip, idx) => (
          <li key={idx} className="flex items-start gap-3">
            <div className="w-[4px] h-[4px] bg-[#A855F7] rounded-full mt-[8px] shrink-0" />
            <p className="text-[13px] text-[#D1D5DB] leading-[20px] font-normal">
              {tip}
            </p>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ProTips;
