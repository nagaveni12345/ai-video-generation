import React from 'react';

const ScriptInput = ({ scriptText, setScriptText }) => {
  return (
    <div className="bg-[#0B0B0B] border border-[#1F1F1F] rounded-[16px] p-5 flex flex-col">
      <div className="flex justify-between items-center mb-3">
        <h3 className="text-[14px] text-[#E5E7EB] font-medium">Script</h3>
        <div className="w-6 h-6 flex flex-col justify-center items-end gap-1 cursor-pointer group">
          <div className="w-4 h-[1.5px] bg-[#9CA3AF] group-hover:bg-white transition-colors" />
          <div className="w-3 h-[1.5px] bg-[#9CA3AF] group-hover:bg-white transition-colors" />
          <div className="w-4 h-[1.5px] bg-[#9CA3AF] group-hover:bg-white transition-colors" />
        </div>
      </div>
      <div className="relative h-[220px] bg-[#050505] border border-[#1F1F1F] rounded-[12px] p-3 flex flex-col">
        <textarea 
          value={scriptText}
          onChange={(e) => setScriptText(e.target.value)}
          className="w-full flex-1 bg-transparent border-none outline-none text-[#D1D5DB] placeholder:text-[#4B5563] text-[13px] leading-relaxed resize-none scrollbar-hide"
          placeholder="Enter your script here... The AI will automatically sync your video with the text timing."
        />
        <div className="mt-2 text-[12px] text-[#6B7280]">
          {scriptText.length} characters
        </div>
      </div>
    </div>
  );
};

export default ScriptInput;
