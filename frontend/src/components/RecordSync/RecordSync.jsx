import React from 'react';
import { Video } from 'lucide-react';
import Navbar from '../Home/Navbar';
import VideoInput from './VideoInput';
import ScriptInput from './ScriptInput';
import SyncActions from './SyncActions';

const RecordSyncHero = ({ active, setActive }) => {
  const [syncSettings, setSyncSettings] = React.useState(() => {
    const saved = localStorage.getItem('syncSettings');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {
        console.error("Error parsing syncSettings from localStorage", e);
      }
    }
    return [
      { name: 'Hand Gestures', active: true },
      { name: 'Head Movement', active: true },
      { name: 'Facial Expressions', active: true }
    ];
  });

  const [isSyncing, setIsSyncing] = React.useState(false);
  const [isSynced, setIsSynced] = React.useState(false);
  const [scriptText, setScriptText] = React.useState('');

  React.useEffect(() => {
    localStorage.setItem('syncSettings', JSON.stringify(syncSettings));
  }, [syncSettings]);

  const toggleSetting = (index) => {
    const newSettings = [...syncSettings];
    newSettings[index].active = !newSettings[index].active;
    setSyncSettings(newSettings);
  };

  const handleSync = () => {
    if (isSyncing) return;
    setIsSyncing(true);
    setIsSynced(false);
    
    // Simulate sync process
    setTimeout(() => {
      setIsSyncing(false);
      setIsSynced(true);
    }, 2000);
  };

  return (
    <>
      <Navbar active={active} setActive={setActive} />
      <section className="bg-[#000000] min-h-screen w-full flex flex-col items-center pt-[32px] pb-[32px] px-6 font-inter">
      <div className="w-full max-w-[1100px] mx-auto flex flex-col items-center">
        {/* Tag Button / Pill */}
        <button className="flex items-center gap-2 text-[12px] px-4 py-2 rounded-full bg-[#111111] border border-[#222222] text-[#D1D5DB] mb-4 hover:bg-[#1A1A1A] transition-colors">
          <Video className="w-4 h-4 text-[#9CA3AF]" />
          Record & Sync
        </button>

        {/* Heading */}
        <h1 
          className="text-[44px] font-bold text-white mb-3 text-center leading-[52px] tracking-tight bg-clip-text text-transparent"
          style={{ background: 'linear-gradient(180deg, #FFFFFF 0%, #9CA3AF 100%)', WebkitBackgroundClip: 'text' }}
        >
          Record & Sync to Text
        </h1>

        {/* Subtitle */}
        <p className="text-[14px] text-[#9CA3AF] text-center mb-10">
          Record your video and automatically sync it with your script
        </p>

        {/* Main Grid Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 w-full mb-5">
          <VideoInput />
          <ScriptInput scriptText={scriptText} setScriptText={setScriptText} />
        </div>

        {/* Bottom Row Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 w-full">
          <SyncActions syncSettings={syncSettings} toggleSetting={toggleSetting} />

          {/* Bottom Right — CTA Button Container */}
          <div className="flex flex-col items-center">
           <button 
             onClick={handleSync}
             disabled={isSyncing}
             className={`h-[48px] w-full rounded-[12px] bg-gradient-to-r from-[#2563EB] to-[#06B6D4] text-white text-[14px] font-medium shadow-[0_10px_30px_rgba(37,99,235,0.3)] transition-all ${isSyncing ? 'opacity-50 cursor-not-allowed' : 'hover:scale-[1.02] active:scale-[0.98]'}`}
           >
            {isSyncing ? 'Syncing...' : isSynced ? 'Sync Again' : 'Sync Video with Text'}
           </button>
          </div>
        </div>
      </div>
    </section>
    </>
  );
};

export default RecordSyncHero;
