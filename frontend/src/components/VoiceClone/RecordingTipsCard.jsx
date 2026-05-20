import React from 'react';

const RecordingTipsCard = () => {
  return (
    <div 
      className="rounded-[16px] p-[24px] border border-[#F97316]/30"
      style={{
        background: 'linear-gradient(180deg, #1C0803 0%, #150501 100%)',
      }}
    >
      <h2 className="text-white text-[16px] font-semibold mb-[16px]">
        Recording Tips
      </h2>
      
      <ul className="space-y-[12px] pl-[4px]">
        <li className="flex items-start gap-[12px]">
          <span className="w-[4px] h-[4px] bg-[#F97316] rounded-full mt-[7px] shrink-0"></span>
          <p className="text-[#D1D5DB] text-[13px] leading-relaxed">
            Record in a quiet environment without background noise
          </p>
        </li>
        <li className="flex items-start gap-[12px]">
          <span className="w-[4px] h-[4px] bg-[#F97316] rounded-full mt-[7px] shrink-0"></span>
          <p className="text-[#D1D5DB] text-[13px] leading-relaxed">
            Speak naturally with varied emotions and tones
          </p>
        </li>
        <li className="flex items-start gap-[12px]">
          <span className="w-[4px] h-[4px] bg-[#F97316] rounded-full mt-[7px] shrink-0"></span>
          <p className="text-[#D1D5DB] text-[13px] leading-relaxed">
            Record at least 2-3 minutes for best cloning results
          </p>
        </li>
      </ul>
    </div>
  );
};

export default RecordingTipsCard;
