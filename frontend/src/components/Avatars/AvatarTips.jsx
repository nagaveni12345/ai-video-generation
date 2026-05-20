import { Sliders } from 'lucide-react';

const AvatarTips = () => {
  return (
    <div className="w-full max-w-[538px] bg-gradient-to-br from-[#011A14] to-[#000000] p-[20px] rounded-[18px] border border-[#22C55E]/40 shadow-[0_0_20px_rgba(34,197,94,0.15)]">
      <div className="flex items-center gap-[10px] mb-[14px]">
        <Sliders className="w-[18px] h-[18px] text-[#22C55E]" />
        <h3 className="text-[16px] font-medium text-[#E5E7EB]">Avatar Tips</h3>
      </div>
      <ul className="flex flex-col gap-[12px]">
        {[
          'Avatars can be used in all your video projects',
          'Customize facial features for unique characters',
          'Export avatars in multiple formats and resolutions'
        ].map((tip, i) => (
          <li key={i} className="flex items-center gap-[10px] text-[14px] text-[#D1D5DB] font-normal leading-[22px]">
            <div className="w-[6px] h-[6px] rounded-full bg-[#22C55E] flex-shrink-0" />
            <span>{tip}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default AvatarTips;
