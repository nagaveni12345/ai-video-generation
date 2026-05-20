import React from 'react';
import Navbar from '../Home/Navbar';
import SectionHeader from './SectionHeader';
import VoiceSampleCard from './VoiceSampleCard';
import ClonedVoiceCard from './ClonedVoiceCard';
import VoiceSettingsCard from './VoiceSettingsCard';
import VoiceProfilesCard from './VoiceProfilesCard';
import UseVoiceCard from './UseVoiceCard';
import RecordingTipsCard from './RecordingTipsCard';

const VoiceClone = ({ active, setActive }) => {
  return (
    <div className="min-h-screen bg-[#000000] text-white font-inter">
      <Navbar active={active} setActive={setActive} />
      
      <main className="max-w-[1100px] mx-auto px-6 pt-[32px] pb-[40px]">
        <SectionHeader 
          tag="Voice Cloning" 
          title="Clone Your Voice" 
          subtitle="Upload a voice sample and create AI-generated speech in your voice" 
        />
        
        {/* Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-[24px]">
          {/* Left Column */}
          <div className="flex flex-col gap-[24px]">
            <VoiceSampleCard />
            <VoiceSettingsCard />
            <VoiceProfilesCard />
            
            {/* Clone Voice Action Button */}
            <button 
              className="w-full h-[48px] rounded-[12px] text-[14px] font-medium text-[#E5E7EB] flex items-center justify-center gap-[8px] transition-all duration-200 ease-out hover:brightness-110 active:scale-[0.98]"
              style={{ 
                background: 'linear-gradient(90deg, #F97316 0%, #EF4444 100%)',
                boxShadow: '0 10px 30px rgba(239, 68, 68, 0.2)'
              }}
            >
              <span className="text-[#E5E7EB] w-[16px] h-[16px] flex items-center justify-center">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M2 10v3"></path>
                  <path d="M6 6v11"></path>
                  <path d="M10 3v18"></path>
                  <path d="M14 8v7"></path>
                  <path d="M18 5v13"></path>
                  <path d="M22 10v3"></path>
                </svg>
              </span>
              Clone Voice
            </button>
          </div>

          {/* Right Column */}
          <div className="flex flex-col gap-[24px]">
            <ClonedVoiceCard />
            <UseVoiceCard />
            <RecordingTipsCard />
          </div>
        </div>
      </main>
    </div>
  );
};

export default VoiceClone;
