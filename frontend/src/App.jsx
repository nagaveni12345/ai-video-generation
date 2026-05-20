import React from 'react';
import Home from './components/Home/Home';
import RecordSyncHero from './components/RecordSync/RecordSync';
import TextToVideo from './components/TextToVideo/TextToVideo';
import VoiceClone from './components/VoiceClone/VoiceClone';
import Translate from './components/Translate/Translate';

import ProjectsPage from './components/Projects/ProjectsPage';
import AvatarCreator from './components/Avatars/AvatarCreator';
import SignIn from './components/SignIn/SignIn';
import SignUp from './components/SignUp/SignUp';

const App = () => {
  const [activeTab, setActiveTab] = React.useState('SignIn');

  const renderContent = () => {
    switch (activeTab) {
      case 'SignIn':
        return <SignIn active={activeTab} setActive={setActiveTab} />;
      case 'SignUp':
        return <SignUp setActive={setActiveTab} />;
      case 'Record & Sync':
        return <RecordSyncHero active={activeTab} setActive={setActiveTab} />;
      case 'Text to Video':
        return <TextToVideo active={activeTab} setActive={setActiveTab} />;
      case 'Voice Clone':
        return <VoiceClone active={activeTab} setActive={setActiveTab} />;
      case 'Translate':
        return <Translate active={activeTab} setActive={setActiveTab} />;
      case 'Projects':
        return <ProjectsPage active={activeTab} setActive={setActiveTab} />;
      case 'Avatars':
        return <AvatarCreator active={activeTab} setActive={setActiveTab} />;
      default:
        return <Home active={activeTab} setActive={setActiveTab} />;
    }
  };

  return (
    <div className="min-h-screen bg-black text-white selection:bg-white/10 font-inter">
      {renderContent()}
    </div>
  );
};

export default App;
