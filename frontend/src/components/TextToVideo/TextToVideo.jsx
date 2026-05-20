import React from 'react';
import { Wand2, Sparkles } from 'lucide-react';
import Navbar from '../Home/Navbar';
import PromptInput from './PromptInput';
import StyleSelector from './StyleSelector';
import DurationSlider from './DurationSlider';
import Preview from './Preview';
import ProTips from './ProTips';

const TextToVideo = ({ active, setActive }) => {
  const [prompt, setPrompt] = React.useState('');
  const [style, setStyle] = React.useState('Artistic');
  const [duration, setDuration] = React.useState(30);

  return (
    <div className="min-h-screen bg-[#000000] text-white font-inter">
      <Navbar active={active} setActive={setActive} />
      
      <main className="max-w-[1100px] mx-auto px-6 pt-[32px] pb-[40px]">
        {/* Header Section */}
        <div className="flex flex-col items-center mb-[32px]">
          <div className="flex items-center gap-2 px-[12px] py-[6px] rounded-full bg-[#111111] border border-[#1F1F1F] text-[#9CA3AF] text-[12px] font-medium mb-[16px]">
            <Sparkles className="w-3.5 h-3.5" />
            Text to Video Generator
          </div>
          <h1 
            className="text-[40px] font-semibold text-white mb-[12px] tracking-[-0.02em] text-center leading-[48px]"
          >
            Transform Words into Videos
          </h1>
          <p className="text-[14px] text-[#9CA3AF] text-center">Describe your vision and watch AI bring it to life</p>
        </div>

        {/* Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-[24px]">
          {/* Left Column */}
          <div className="flex flex-col gap-[24px]">
            <PromptInput value={prompt} onChange={setPrompt} />
            <StyleSelector selected={style} onSelect={setStyle} />
            <DurationSlider value={duration} onChange={setDuration} />
            
            <div className="mt-2"> {/* Additional spacing to reach 24px total if needed */}
              <button 
                className="group w-full h-[48px] rounded-[12px] text-[14px] font-medium text-[#E5E7EB] flex items-center justify-center gap-[8px] transition-all duration-200 ease-out hover:brightness-110 active:scale-[0.98]"
                style={{ 
                  background: 'linear-gradient(90deg, #6D28D9 0%, #DB2777 100%)',
                  boxShadow: '0 10px 30px rgba(168, 85, 247, 0.4)'
                }}
              >
                <Wand2 className="w-[16px] h-[16px] transition-transform group-hover:rotate-12" />
                Generate Video
              </button>
            </div>
          </div>

          {/* Right Column */}
          <div className="flex flex-col gap-[24px]">
            <Preview />
            <ProTips />
          </div>
        </div>
      </main>
    </div>
  );
};

export default TextToVideo;
