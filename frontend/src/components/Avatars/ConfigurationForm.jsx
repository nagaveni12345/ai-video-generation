import React, { useState } from 'react';
import { Sparkles } from 'lucide-react';

const ConfigurationForm = () => {
  const [gender, setGender] = useState('Male');
  const [age, setAge] = useState(30);
  const [ethnicity, setEthnicity] = useState('Diverse');
  const [hairStyle, setHairStyle] = useState('Short');

  return (
    <div className="flex flex-col gap-[20px]">
      {/* Avatar Name */}
      <div className="bg-gradient-to-b from-[#0B0B0B] to-[#050505] p-[20px] rounded-[16px] border border-[#1F1F1F]">
        <label className="block text-[13px] font-medium text-[#E5E7EB] mb-[8px]">Avatar Name</label>
        <input 
          type="text" 
          placeholder="Enter avatar name..." 
          className="w-full h-[40px] bg-[#050505] border border-[#1F1F1F] rounded-[8px] px-[12px] text-[13px] text-white placeholder-[#6B7280] focus:outline-none transition-colors"
        />
      </div>

      {/* Gender */}
      <div className="bg-gradient-to-b from-[#0B0B0B] to-[#050505] p-[20px] rounded-[16px] border border-[#1F1F1F]">
        <label className="block text-[14px] font-medium text-[#E5E7EB] mb-[16px]">Gender</label>
        <div className="flex flex-row gap-[16px] w-full">
          <div 
            onClick={() => setGender('Male')}
            className={`flex-1 flex flex-col items-center justify-center h-[100px] rounded-[14px] cursor-pointer transition-all duration-200 ease-out border group ${
              gender === 'Male' 
                ? 'border-[#22C55E] border-2 bg-[rgba(34,197,94,0.12)] shadow-[0_0_0_1px_rgba(34,197,94,0.4),0_6px_20px_rgba(34,197,94,0.25)]' 
                : 'bg-[#050505] border-[#1F1F1F] hover:border-[#374151] hover:-translate-y-[2px]'
            }`}
          >
            <span className="text-[32px] leading-none mb-[8px]">👨</span>
            <span className={`text-[14px] font-medium transition-colors ${gender === 'Male' ? 'text-white' : 'text-[#D1D5DB] group-hover:text-white'}`}>Male</span>
          </div>
          <div 
            onClick={() => setGender('Female')}
            className={`flex-1 flex flex-col items-center justify-center h-[100px] rounded-[14px] cursor-pointer transition-all duration-200 ease-out border group ${
              gender === 'Female' 
                ? 'border-[#22C55E] border-2 bg-[rgba(34,197,94,0.12)] shadow-[0_0_0_1px_rgba(34,197,94,0.4),0_6px_20px_rgba(34,197,94,0.25)]' 
                : 'bg-[#050505] border-[#1F1F1F] hover:border-[#374151] hover:-translate-y-[2px]'
            }`}
          >
            <span className="text-[32px] leading-none mb-[8px]">👱‍♀️</span>
            <span className={`text-[14px] font-medium transition-colors ${gender === 'Female' ? 'text-white' : 'text-[#D1D5DB] group-hover:text-white'}`}>Female</span>
          </div>
        </div>
      </div>

      {/* Age */}
      <div className="bg-gradient-to-b from-[#0B0B0B] to-[#050505] p-[20px] rounded-[18px] border border-[#1F1F1F]">
        <label className="block text-[14px] font-semibold text-white mb-[12px]">Age: {age} years</label>
        <div className="relative w-full h-[14px] flex items-center group">
          {/* Track (Inactive/Right) */}
          <div className="absolute w-full h-full bg-[#EAEAF0] rounded-full" />
          {/* Active Progress (Left) */}
          <div 
            className="absolute h-full bg-[#05050C] rounded-l-full transition-all duration-150" 
            style={{ width: `${(age - 18) / (70 - 18) * 100}%` }} 
          />
          {/* Input Range (Invisible) */}
          <input 
            type="range" 
            min="18" 
            max="70" 
            value={age}
            onChange={(e) => setAge(parseInt(e.target.value))}
            className="absolute w-full h-full opacity-0 cursor-pointer z-10"
          />
          {/* Custom Thumb */}
          <div 
            className="absolute h-[14px] w-[14px] bg-white rounded-full border-[1.5px] border-[#0A0A10] pointer-events-none transition-all duration-150 shadow-sm box-border"
            style={{ left: `calc(${(age - 18) / (70 - 18) * 100}% - 7px)` }}
          />
        </div>
        <div className="flex justify-between mt-[10px] px-[1px]">
          <span className="text-[12px] text-[#9CA3AF]">18</span>
          <span className="text-[12px] text-[#9CA3AF]">70</span>
        </div>
      </div>

      {/* Ethnicity */}
      <div className="bg-gradient-to-b from-[#0B0B0B] to-[#050505] p-[20px] rounded-[18px] border border-[#1F1F1F]">
        <label className="block text-[16px] font-medium text-[#E5E7EB] mb-[16px]">Ethnicity</label>
        <div className="grid grid-cols-3 gap-[12px]">
          {['Diverse', 'Asian', 'Caucasian', 'African', 'Hispanic', 'Middle Eastern'].map(eth => (
            <div 
              key={eth}
              onClick={() => setEthnicity(eth)}
              className={`flex items-center justify-center h-[40px] rounded-[10px] text-[13px] font-medium cursor-pointer transition-all duration-200 border group ${
                ethnicity === eth 
                  ? 'border-[#22C55E] border-2 bg-[rgba(34,197,94,0.12)] shadow-[0_0_0_1px_rgba(34,197,94,0.4),0_6px_20px_rgba(34,197,94,0.25)] text-white' 
                  : 'bg-[#050505] border-[#1F1F1F] text-[#9CA3AF] hover:border-[#374151] hover:-translate-y-[2px] hover:text-white'
              }`}
            >
              {eth}
            </div>
          ))}
        </div>
      </div>

      {/* Hair Style */}
      <div className="bg-gradient-to-b from-[#0B0B0B] to-[#050505] p-[20px] rounded-[18px] border border-[#1F1F1F]">
        <div className="bg-[#050505] rounded-full h-[36px] flex items-center px-1 border border-white/5">
           <div className="bg-[#E5E7EB] rounded-full h-[28px] px-[20px] flex items-center justify-center text-[13px] font-medium text-[#111111]">
             Hair Style
           </div>
        </div>
        <div className="grid grid-cols-4 gap-[12px] mt-[16px]">
          {[
            { id: 'Short', icon: '💇‍♂️' },
            { id: 'Long', icon: '💇‍♀️' },
            { id: 'Curly', icon: '👱' },
            { id: 'Bald', icon: '👨‍🦲' }
          ].map(style => (
            <div 
              key={style.id}
              onClick={() => setHairStyle(style.id)}
              className={`flex flex-col items-center justify-center h-[80px] rounded-[12px] cursor-pointer transition-all border group ${
                hairStyle === style.id 
                  ? 'border-[#22C55E] border-2 bg-[rgba(34,197,94,0.1)] text-white' 
                  : 'bg-[#050505] border-[#1F1F1F] text-[#9CA3AF] hover:border-[#374151]'
              }`}
            >
              <span className="text-[28px] mb-[6px]">{style.icon}</span>
              <span className={`text-[12px] font-medium transition-colors ${hairStyle === style.id ? 'text-white' : 'text-[#9CA3AF] group-hover:text-white'}`}>
                {style.id}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center gap-[10px] mt-[16px]">
        <button className="flex-1 h-[48px] rounded-[14px] text-[15px] font-medium text-[rgba(255,255,255,0.95)] flex items-center justify-center gap-[8px] transition-all duration-300 ease-in-out shadow-[0_6px_16px_rgba(16,185,129,0.30)] bg-gradient-to-r from-[#064E3B] via-[#047857] to-[#10B981] hover:brightness-110 active:scale-[0.98] border border-white/5 shadow-[inset_0_1px_0_rgba(255,255,255,0.08)]">
          <Sparkles className="w-[16px] h-[16px] opacity-95 text-inherit" />
          Create Avatar
        </button>
        <button className="w-[40px] h-[40px] bg-white rounded-[12px] flex items-center justify-center transition-colors hover:bg-gray-100 active:scale-95 flex-shrink-0">
           <div className="w-[18px] h-[18px] bg-transparent" />
        </button>
      </div>
    </div>
  );
};

export default ConfigurationForm;
