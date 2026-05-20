import React, { useState } from 'react';
import Card from './Card';

const VoiceSettingsCard = () => {
  const [pitch, setPitch] = useState(50);
  const [speed, setSpeed] = useState(50);

  // Derive text labels based on value
  const getPitchLabel = () => pitch === 50 ? 'Natural' : (pitch < 50 ? 'Lower' : 'Higher');
  const getSpeedLabel = () => speed === 50 ? 'Normal' : (speed < 50 ? 'Slower' : 'Faster');

  return (
    <Card>
      <h2 className="text-white text-[16px] font-semibold mb-[20px]">
        Voice Settings
      </h2>
      
      <div className="mb-[24px]">
        <h3 className="text-white text-[14px] font-semibold mb-[12px]">Pitch: {getPitchLabel()}</h3>
        <div className="relative w-full h-[14px] flex items-center group">
          {/* Track (Inactive/Right) */}
          <div className="absolute w-full h-full bg-[#EAEAF0] rounded-full" />
          {/* Active Progress (Left) */}
          <div 
            className="absolute h-full bg-[#05050C] rounded-l-full transition-all duration-150" 
            style={{ width: `${pitch}%` }} 
          />
          {/* Input Range (Invisible) */}
          <input 
            type="range" 
            min="0" 
            max="100" 
            value={pitch}
            onChange={(e) => setPitch(parseInt(e.target.value))}
            className="absolute w-full h-full opacity-0 cursor-pointer z-10"
          />
          {/* Custom Thumb */}
          <div 
            className="absolute h-[14px] w-[14px] bg-white rounded-full border-[1.5px] border-[#0A0A10] pointer-events-none transition-all duration-150 shadow-sm box-border"
            style={{ left: `calc(${pitch}% - 7px)` }}
          />
        </div>
        <div className="flex justify-between mt-[10px] px-[1px]">
          <span className="text-[12px] text-[#9CA3AF]">Lower</span>
          <span className="text-[12px] text-[#9CA3AF]">Higher</span>
        </div>
      </div>

      <div>
        <h3 className="text-white text-[14px] font-semibold mb-[12px]">Speed: {getSpeedLabel()}</h3>
        <div className="relative w-full h-[14px] flex items-center group">
          {/* Track (Inactive/Right) */}
          <div className="absolute w-full h-full bg-[#EAEAF0] rounded-full" />
          {/* Active Progress (Left) */}
          <div 
            className="absolute h-full bg-[#05050C] rounded-l-full transition-all duration-150" 
            style={{ width: `${speed}%` }} 
          />
          {/* Input Range (Invisible) */}
          <input 
            type="range" 
            min="0" 
            max="100" 
            value={speed}
            onChange={(e) => setSpeed(parseInt(e.target.value))}
            className="absolute w-full h-full opacity-0 cursor-pointer z-10"
          />
          {/* Custom Thumb */}
          <div 
            className="absolute h-[14px] w-[14px] bg-white rounded-full border-[1.5px] border-[#0A0A10] pointer-events-none transition-all duration-150 shadow-sm box-border"
            style={{ left: `calc(${speed}% - 7px)` }}
          />
        </div>
        <div className="flex justify-between mt-[10px] px-[1px]">
          <span className="text-[12px] text-[#9CA3AF]">Slower</span>
          <span className="text-[12px] text-[#9CA3AF]">Faster</span>
        </div>
      </div>
    </Card>
  );
};

export default VoiceSettingsCard;
