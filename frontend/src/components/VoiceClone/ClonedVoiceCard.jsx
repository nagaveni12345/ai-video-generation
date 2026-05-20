import React from 'react';
import { AudioLines } from 'lucide-react';
import Card from './Card';

const ClonedVoiceCard = () => {
  return (
    <Card>
      <h2 className="text-white text-[16px] font-medium mb-[12px]">
        Cloned Voice
      </h2>
      
      <div className="flex flex-col items-center justify-center h-[256px] bg-[#030303] rounded-[12px] gap-[12px]">
        <AudioLines className="text-[#4B5563] w-[40px] h-[40px]" strokeWidth={1.5} />
        <span className="text-[#6B7280] text-[14px]">
          Cloned voice will appear here
        </span>
      </div>
    </Card>
  );
};

export default ClonedVoiceCard;
