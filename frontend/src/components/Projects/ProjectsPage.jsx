import React from 'react';
import Navbar from '../Home/Navbar';
import ProjectHeader from './ProjectHeader';
import StatsCardsRow from './StatsCardsRow';
import ProjectToolbar from './ProjectToolbar';
import ProjectGrid from './ProjectGrid';

const ProjectsPage = ({ active, setActive }) => {
  return (
    <div className="min-h-screen bg-[#000000] text-white font-inter">
      <Navbar active={active} setActive={setActive} />
      
      <main className="max-w-[1200px] mx-auto px-10 pt-[32px] pb-[40px]">
        <ProjectHeader />
        <StatsCardsRow />
        <ProjectToolbar />
        <ProjectGrid />
      </main>
    </div>
  );
};

export default ProjectsPage;
