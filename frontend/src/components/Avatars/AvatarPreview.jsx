import { UserCircle2 } from 'lucide-react';

const AvatarPreview = () => {
  return (
    <div className="w-full max-w-[538px] bg-gradient-to-b from-[#0B0B0B] to-[#050505] p-[20px] rounded-[16px] border border-[#1F1F1F] shadow-[0_0_0_1px_rgba(255,255,255,0.02)]">
      <h3 className="text-[14px] font-medium text-[#E5E7EB] mb-[12px]">Preview</h3>
      <div className="w-full h-[600px] bg-[#020202] rounded-[12px] border border-[#111111] shadow-[inset_0_0_40px_rgba(0,0,0,0.7)] flex flex-col items-center justify-center relative">
        <UserCircle2 className="w-[56px] h-[56px] text-[#2a2a2a] mb-4" strokeWidth={1.5} />
        <p className="text-[13px] text-[#6B7280] font-normal text-center">Your avatar will appear here</p>
      </div>
    </div>
  );
};

export default AvatarPreview;
