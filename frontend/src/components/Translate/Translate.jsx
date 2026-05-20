import React, { useState } from 'react';
import { Languages, Globe } from 'lucide-react';
import Navbar from '../Home/Navbar';
import VideoUploadCard from './VideoUploadCard';
import SourceLanguageDropdown from './SourceLanguageDropdown';
import PopularLanguagesCard from './PopularLanguagesCard';
import AllLanguagesCard from './AllLanguagesCard';
import TranslationStatusCard from './TranslationStatusCard';
import TranslationFeaturesCard from './TranslationFeaturesCard';
import StatsCardGroup from './StatsCardGroup';
import TranslateButton from './TranslateButton';

const Translate = ({ active, setActive }) => {
  const [selectedLanguages, setSelectedLanguages] = useState([]);

  const toggleLanguage = (lang) => {
    setSelectedLanguages((prev) => {
      const exists = prev.find((l) => l.code === lang.code);
      return exists
        ? prev.filter((l) => l.code !== lang.code)
        : [...prev, lang];
    });
  };

  const handleTranslate = () => {
    console.log('Translating to:', selectedLanguages);
    // Add translation logic here
  };

  return (
    <div className="min-h-screen bg-[#000000] text-white font-inter">
      <Navbar active={active} setActive={setActive} />

      <main className="max-w-[1100px] mx-auto px-6 pt-[48px] pb-[100px]">

        {/* Header Section — Center aligned as per Figma */}
        <div className="flex flex-col items-center mb-[40px]">
          <div 
            style={{ 
              display: 'inline-flex', 
              alignItems: 'center', 
              gap: '6px', 
              padding: '4px 12px', 
              borderRadius: '100px', 
              background: '#111111', 
              border: '1px solid #1F1F1F',
              marginBottom: '16px'
            }}
          >
            <span style={{ fontSize: '11px', fontWeight: '500', color: '#9CA3AF' }}>
              Multi-Language Translation
            </span>
          </div>
          
          <h1 
            style={{ 
              fontSize: '48px', 
              fontWeight: '700', 
              color: '#FFFFFF', 
              marginBottom: '12px', 
              textAlign: 'center',
              letterSpacing: '-0.02em',
              lineHeight: '1.1'
            }}
          >
            Translate to 50+ Languages
          </h1>
          <p 
            style={{ 
              fontSize: '15px', 
              color: '#9CA3AF', 
              textAlign: 'center', 
              fontWeight: '400',
              maxWidth: '600px'
            }}
          >
            Automatically translate your videos with voice cloning in any language
          </p>
        </div>

        {/* Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-[24px]">
          {/* Left Column */}
          <div className="flex flex-col gap-[24px]">
            <VideoUploadCard />
            <SourceLanguageDropdown />
            <PopularLanguagesCard 
              selected={selectedLanguages} 
              onToggle={toggleLanguage} 
            />
            <AllLanguagesCard 
              selected={selectedLanguages} 
              onToggle={toggleLanguage} 
            />
            <TranslateButton selectedCount={selectedLanguages.length} />
          </div>

          {/* Right Column */}
          <div className="flex flex-col gap-[24px]">
            <TranslationStatusCard />
            <TranslationFeaturesCard />
            <StatsCardGroup selectedCount={selectedLanguages.length} />
          </div>
        </div>

      </main>
    </div>
  );
};

export default Translate;
