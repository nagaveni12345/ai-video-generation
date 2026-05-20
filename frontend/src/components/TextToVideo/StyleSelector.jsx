import React from 'react';

const styles = [
  { 
    name: 'Cinematic', 
    gradient: 'linear-gradient(135deg, #A855F7 0%, #EC4899 100%)' 
  },
  { 
    name: 'Animated', 
    gradient: 'linear-gradient(135deg, #3B82F6 0%, #06B6D4 100%)' 
  },
  { 
    name: 'Realistic', 
    gradient: 'linear-gradient(135deg, #22C55E 0%, #10B981 100%)' 
  },
  { 
    name: 'Artistic', 
    gradient: 'linear-gradient(135deg, #F97316 0%, #EF4444 100%)' 
  }
];

const StyleSelector = ({ selected, onSelect }) => {
  return (
    <div className="bg-[#0B0B0B] border border-[#1F1F1F] rounded-[16px] p-[20px]">
      <h3 className="text-[14px] text-[#E5E7EB] mb-[12px] font-medium">Video Style</h3>
      <div className="grid grid-cols-2 gap-[16px]">
        {styles.map((style) => (
          <button
            key={style.name}
            onClick={() => onSelect(style.name)}
            style={{
              background: selected === style.name 
                ? 'rgba(168, 85, 247, 0.08)' 
                : 'linear-gradient(180deg, #0A0A0A 0%, #050505 100%)'
            }}
            className={`group relative h-[110px] rounded-[14px] border px-[12px] flex flex-col items-center justify-center gap-[10px] transition-all duration-200 ease-out hover:-translate-y-[2px] ${
              selected === style.name 
                ? 'border-[#A855F7] border-[2px] shadow-[0_0_0_1px_rgba(168,85,247,0.3),0_8px_20px_rgba(168,85,247,0.25)]' 
                : 'border-[#1F1F1F] hover:border-[#374151]'
            }`}
          >
            {/* Inner Gradient Box */}
            <div 
              className="w-full h-[56px] rounded-[10px]"
              style={{ background: style.gradient }}
            />
            
            <span className={`text-[13px] font-medium transition-colors ${selected === style.name ? 'text-white' : 'text-[#D1D5DB]'}`}>
              {style.name}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
};

export default StyleSelector;
