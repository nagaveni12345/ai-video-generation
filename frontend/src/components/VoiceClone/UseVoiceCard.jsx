import React from 'react';
import { Mic } from 'lucide-react';

const UseVoiceCard = () => {
  return (
    <div 
      className="rounded-[16px] p-[24px] border border-[#F97316]/30"
      style={{
        background: 'linear-gradient(180deg, #1C0803 0%, #150501 100%)',
      }}
    >
      <div className="flex items-center gap-[10px] mb-[20px]">
        <Mic className="w-[18px] h-[18px] text-[#F97316]" strokeWidth={2} />
        <h2 className="text-white text-[16px] font-semibold tracking-wide">Use Your Cloned Voice</h2>
      </div>

      <div className="flex flex-col gap-[12px]">
        {/* Row 1 */}
        <div className="flex items-center gap-[16px] bg-black/30 rounded-[12px] p-[16px]">
          <img src="https://unpkg.com/emoji-datasource-apple@14.0.0/img/apple/64/1f3ac.png" alt="Video Narration" className="w-[20px] h-[20px] shrink-0 drop-shadow-md" />
          <div>
            <h3 className="text-white text-[14px] font-semibold leading-tight mb-[4px]">Video Narration</h3>
            <p className="text-[#9CA3AF] text-[13px] leading-tight font-medium">Add voiceovers to videos</p>
          </div>
        </div>

        {/* Row 2 */}
        <div className="flex items-center gap-[16px] bg-black/30 rounded-[12px] p-[16px]">
          <img src="https://unpkg.com/emoji-datasource-apple@14.0.0/img/apple/64/1f464.png" alt="Avatar Speech" className="w-[20px] h-[20px] shrink-0 drop-shadow-md" />
          <div>
            <h3 className="text-white text-[14px] font-semibold leading-tight mb-[4px]">Avatar Speech</h3>
            <p className="text-[#9CA3AF] text-[13px] leading-tight font-medium">Sync with AI avatars</p>
          </div>
        </div>

        {/* Row 3 */}
        <div className="flex items-center gap-[16px] bg-black/30 rounded-[12px] p-[16px]">
          <img src="https://unpkg.com/emoji-datasource-apple@14.0.0/img/apple/64/1f30d.png" alt="Multi-Language" className="w-[20px] h-[20px] shrink-0 drop-shadow-md" />
          <div>
            <h3 className="text-white text-[14px] font-semibold leading-tight mb-[4px]">Multi-Language</h3>
            <p className="text-[#9CA3AF] text-[13px] leading-tight font-medium">Speak in any language</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UseVoiceCard;
