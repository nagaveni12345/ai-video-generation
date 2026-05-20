import React from 'react';
import { 
  MoreVertical, 
  Video, 
  RefreshCcw, 
  UserCircle2, 
  Mic, 
  Globe, 
  Clock, 
  Trash2
} from 'lucide-react';

const ProjectCard = ({ project }) => {
  const getIcon = (type) => {
    switch (type) {
      case 'Text to Video': return <Video className="w-[12px] h-[12px]" />;
      case 'Record & Sync': return <RefreshCcw className="w-[12px] h-[12px]" />;
      case 'Avatar': return <UserCircle2 className="w-[12px] h-[12px]" />;
      case 'Voice Clone': return <Mic className="w-[12px] h-[12px]" />;
      case 'Translation': return <Globe className="w-[12px] h-[12px]" />;
      default: return <Video className="w-[12px] h-[12px]" />;
    }
  };

  return (
    <div className="bg-[#0B0B0B] rounded-[16px] border border-[#1F1F1F] overflow-hidden flex flex-col group hover:border-[#2F2F2F] transition-all">
      {/* Preview Section */}
      <div className={`relative aspect-video w-full bg-gradient-to-br ${project.gradient}`}>
        {/* Status Badge */}
        <div className="absolute top-[12px] right-[12px]">
          <div className="px-3 py-1 rounded-full text-[10px] font-medium leading-none bg-black/20 text-white/80 border border-white/10 backdrop-blur-sm">
            {project.status}
          </div>
        </div>
        
        {/* Duration Badge */}
        {project.duration && (
          <div className="absolute bottom-[10px] right-[10px] bg-black/60 text-white text-[10px] px-[6px] py-[3px] rounded-[4px] font-bold">
            {project.duration}
          </div>
        )}
      </div>

      {/* Content Section */}
      <div className="p-[16px] flex flex-col flex-1">
        <div className="flex justify-between items-start mb-[4px]">
          <h3 className="text-[14px] font-[600] text-[#FFFFFF] truncate max-w-[85%] leading-tight">{project.title}</h3>
          <button className="text-[#6B7280] hover:text-white transition-colors">
            <MoreVertical className="w-[14px] h-[14px]" />
          </button>
        </div>

        <div className="flex items-center gap-[6px] text-[#6B7280] text-[12px] mt-[6px]">
          {getIcon(project.type)}
          <span className="leading-none">{project.type}</span>
        </div>

        <div className="flex items-center gap-[6px] text-[#6B7280] text-[12px] mt-[4px]">
          <Clock className="w-[12px] h-[12px]" />
          <span className="leading-none">{project.date}</span>
        </div>

        {/* Action Buttons Row - Exactly as screenshot */}
        <div className="flex items-center gap-[8px] mt-[16px]">
          <button className="flex-[4] h-[32px] bg-white rounded-[6px] hover:opacity-90 transition-all shadow-sm" />
          <button className="w-[32px] h-[32px] bg-white rounded-[6px] flex items-center justify-center hover:opacity-90 transition-all shadow-sm" />
          <button className="w-[32px] h-[32px] bg-white rounded-[6px] flex items-center justify-center hover:opacity-90 transition-all shadow-sm">
             <Trash2 className="w-[14px] h-[14px] text-[#EF4444]" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProjectCard;
