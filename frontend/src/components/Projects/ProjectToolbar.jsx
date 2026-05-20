import React from 'react';

const ProjectToolbar = () => {
  const [activeCategory, setActiveCategory] = React.useState('All');

  return (
    <div className="flex items-center gap-[12px] mt-[16px] mb-[20px]">
      {/* Active "All" Tab */}
      <button
        onClick={() => setActiveCategory('All')}
        className="h-[36px] px-6 rounded-[10px] text-[14px] font-semibold transition-all bg-[#A855F7] text-white shadow-lg shadow-purple-500/10"
      >
        All
      </button>
      
      {/* Inactive Tabs (White Rectangles) as shown in reference */}
      {[1, 2, 3, 4].map((i) => (
        <button
          key={i}
          className="h-[36px] w-[90px] bg-white rounded-[10px] border border-transparent transition-all hover:bg-white/90"
        />
      ))}
    </div>
  );
};

export default ProjectToolbar;
