import { Palette } from 'lucide-react';

const RecentAvatars = () => {
  return (
    <div className="w-full max-w-[538px] bg-gradient-to-br from-[#011A14] to-[#000000] p-[20px] rounded-[18px] border border-[#22C55E]/40 shadow-[0_0_20px_rgba(34,197,94,0.15)]">
      <div className="flex items-center gap-[8px] mb-[16px]">
        <Palette className="w-[18px] h-[18px] text-[#22C55E]" />
        <h3 className="text-[16px] font-medium text-[#E5E7EB]">Recent Avatars</h3>
      </div>
      <div className="grid grid-cols-4 gap-[14px]">
        {['👱‍♀️', '👦', '👱‍♀️', '👦'].map((avatar, idx) => (
          <div key={idx} className="w-full h-[90px] bg-[#021A14] border border-[rgba(255,255,255,0.06)] rounded-[12px] flex items-center justify-center text-[28px] cursor-pointer hover:border-[#22C55E]/50 transition-all">
            {avatar}
          </div>
        ))}
      </div>
    </div>
  );
};

export default RecentAvatars;
