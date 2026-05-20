import React from 'react';
import ConfigurationForm from './ConfigurationForm.jsx';
import AvatarPreview from './AvatarPreview';
import RecentAvatars from './RecentAvatars';
import AvatarTips from './AvatarTips';
import { Sparkles, UserCircle2 } from 'lucide-react';
import Navbar from '../Home/Navbar';

const AvatarCreator = ({ active, setActive }) => {
  return (
    <div className="min-h-screen bg-[#000000] text-white font-inter">
      <Navbar active={active} setActive={setActive} />
      
      <main className="w-[1100px] mx-auto px-0 pt-[32px] pb-[40px]">
        {/* Section Header */}
        <div className="flex flex-col items-center text-center mb-[32px]">
          <div className="inline-flex items-center gap-2 px-[12px] py-[6px] rounded-full bg-[#111] border border-[#1F1F1F] text-[#9CA3AF] text-[12px] font-medium mb-[16px]">
             <UserCircle2 className="w-3.5 h-3.5" />
             <span>Avatar Creator</span>
          </div>
          <h1 className="text-[40px] font-semibold text-white mb-[10px] tracking-[-0.02em] leading-[48px]">
            Create AI Avatars
          </h1>
          <p className="text-[14px] text-[#6B7280]">
            Design realistic male and female avatars for your videos
          </p>
        </div>

        {/* Main Grid Layout */}
        <div className="grid grid-cols-[538px_538px] gap-[24px] items-start">
          {/* Left Column → Form controls */}
          <div className="flex flex-col gap-[20px]">
             <ConfigurationForm />
          </div>

          {/* Right Column → Preview + info */}
          <div className="flex flex-col gap-[20px]">
            <AvatarPreview />
            <RecentAvatars />
            <AvatarTips />
          </div>
        </div>
      </main>
    </div>
  );
};

export default AvatarCreator;
