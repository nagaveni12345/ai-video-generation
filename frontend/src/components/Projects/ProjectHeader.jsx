import React from 'react';
import { Folder } from 'lucide-react';

const ProjectHeader = () => {
  return (
    <div className="flex flex-col md:flex-row md:items-start justify-between gap-6 mb-[28px]">
      <div className="flex flex-col">
        <h1 className="text-[32px] font-[600] leading-[40px] text-[#FFFFFF]">My Projects</h1>
        <p className="text-[#6B7280] text-[14px] font-[400] mt-[6px]">Manage all your AI video creations</p>
      </div>
      
      <button 
        className="flex items-center justify-center gap-[6px] h-[36px] px-[14px] rounded-[8px] bg-gradient-to-r from-[#9333EA] to-[#EC4899] hover:opacity-90 transition-all shadow-[0_6px_20px_rgba(147,51,234,0.3)] shrink-0"
      >
        <Folder className="w-[14px] h-[14px] text-white" />
        <span className="text-white font-[500] text-[13px]">New Project</span>
      </button>
    </div>
  );
};

export default ProjectHeader;
