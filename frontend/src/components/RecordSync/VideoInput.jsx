import React from 'react';
import { Video, Mic, Upload } from 'lucide-react';

const VideoInput = () => {
  return (
    <div className="bg-[#0B0B0B] border border-[#1F1F1F] rounded-[16px] p-5 flex flex-col">
      <h3 className="text-[14px] text-[#E5E7EB] mb-3 font-medium">Video Input</h3>
      <div className="h-[220px] bg-[#050505] rounded-[12px] flex items-center justify-center text-[#6B7280] text-[13px] mb-4">
        <div className="flex flex-col items-center gap-2">
          <Video className="w-8 h-8 opacity-20" />
          <span className="text-center">No video recorded yet</span>
        </div>
      </div>
      <div className="flex gap-3">
        <button className="flex-1 h-10 bg-gradient-to-r from-[#3B82F6] to-[#06B6D4] rounded-[8px] text-white text-[14px] font-medium flex items-center justify-center gap-2 hover:opacity-90 transition-all active:scale-[0.98]">
          <Mic className="w-4 h-4" /> Start Recording
        </button>
        <button className="flex-1 h-10 bg-white rounded-[8px] text-black text-[14px] font-medium flex items-center justify-center gap-2 hover:bg-gray-100 transition-all active:scale-[0.98]">
          <Upload className="w-4 h-4" /> Upload File
        </button>
      </div>
    </div>
  );
};

export default VideoInput;
