import React, { useState } from 'react';
import Card from './Card';

const profiles = [
  { id: 'natural', label: 'Natural Voice', icon: '1f3a4' },
  { id: 'professional', label: 'Professional', icon: '1f4bc' },
  { id: 'energetic', label: 'Energetic', icon: '26a1' },
  { id: 'calm', label: 'Calm', icon: '1f9d8' }
];

const VoiceProfilesCard = () => {
  const [selected, setSelected] = useState('natural');

  return (
    <Card>
      <h2 className="text-white text-[16px] font-semibold mb-[20px]">
        Voice Profiles
      </h2>
      
      <div className="grid grid-cols-2 gap-[16px]">
        {profiles.map((profile) => {
          const isSelected = selected === profile.id;
          return (
            <button
              key={profile.id}
              onClick={() => setSelected(profile.id)}
              className={`h-[88px] flex flex-col justify-between items-start p-[16px] rounded-[12px] transition-all duration-200 text-left box-border ${
                isSelected 
                  ? 'bg-[#050505] border-[2px] border-[#F97316] shadow-[0_0_15px_rgba(249,115,22,0.2)]' 
                  : 'bg-[#050505] border-[1px] border-[#2A2A2A] hover:border-[#404040]'
              }`}
            >
              <img 
                src={`https://unpkg.com/emoji-datasource-apple@14.0.0/img/apple/64/${profile.icon}.png`} 
                alt={profile.label} 
                className="w-[22px] h-[22px] block drop-shadow-md" 
              />
              <span className="text-[13px] font-semibold text-white leading-none block">
                {profile.label}
              </span>
            </button>
          );
        })}
      </div>
    </Card>
  );
};

export default VoiceProfilesCard;
