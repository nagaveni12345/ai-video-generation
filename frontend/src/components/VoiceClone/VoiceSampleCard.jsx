import React from 'react';
import { Mic, Lightbulb } from 'lucide-react';
import Card from './Card';

const VoiceSampleCard = () => {
  return (
    <Card>
      {/* Title */}
      <h2 className="text-white text-[16px] font-medium mb-[12px]">
        Voice Sample
      </h2>

      {/* Input Box state */}
      <div className="flex flex-col items-center justify-center h-[120px] bg-[#030303] rounded-[12px] gap-2 mb-[12px]">
        <Mic className="text-[#6B7280] w-[24px] h-[24px]" strokeWidth={1.5} />
        <span className="text-[#6B7280] text-[14px]">No voice sample yet</span>
      </div>

      {/* Primary Button */}
      <button className="w-full h-[40px] rounded-[8px] bg-gradient-to-r from-[#F97316] to-[#EF4444] text-white text-[14px] font-medium flex items-center justify-center gap-2 transition-all duration-200 hover:brightness-110 active:scale-[0.98]">
        <Mic className="w-4 h-4" />
        Record Voice Sample
      </button>

      {/* Secondary Bar (Disabled) */}
      <div className="w-full h-[40px] bg-white rounded-[8px] mt-[12px]"></div>

      {/* Tip Text */}
      <div className="mt-[16px] flex items-center gap-[6px]">
        <span className="text-[14px]">💡</span>
        <p className="text-[12px] text-[#9CA3AF]">
          Tip: Record at least 30 seconds of clear speech for best results
        </p>
      </div>
    </Card>
  );
};

export default VoiceSampleCard;
