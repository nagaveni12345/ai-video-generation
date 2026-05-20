import React from 'react';
import ProjectCard from './ProjectCard';

const projects = [
  {
    id: 1,
    title: "Product Launch Video",
    type: "Text to Video",
    status: "Completed",
    duration: "2:45",
    date: "2 days ago",
    gradient: "from-[#9333EA] to-[#EC4899]"
  },
  {
    id: 2,
    title: "CEO Interview",
    type: "Record & Sync",
    status: "Completed",
    duration: "5:20",
    date: "1 week ago",
    gradient: "from-[#3B82F6] to-[#06B6D4]"
  },
  {
    id: 3,
    title: "Female Avatar - Sarah",
    type: "Avatar",
    status: "Completed",
    duration: null,
    date: "3 days ago",
    gradient: "from-[#22C55E] to-[#16A34A]"
  },
  {
    id: 4,
    title: "Marketing Campaign Voice",
    type: "Voice Clone",
    status: "Completed",
    duration: "1:30",
    date: "5 days ago",
    gradient: "from-[#F97316] to-[#EF4444]"
  },
  {
    id: 5,
    title: "Tutorial in Spanish",
    type: "Translation",
    status: "Processing",
    duration: "4:15",
    date: "1 day ago",
    gradient: "from-[#8B5CF6] to-[#4F46E5]"
  },
  {
    id: 6,
    title: "Company Overview",
    type: "Text to Video",
    status: "Completed",
    duration: "3:00",
    date: "1 week ago",
    gradient: "from-[#F59E0B] to-[#F97316]"
  }
];

const ProjectGrid = () => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-[20px] w-full">
      {projects.map((project) => (
        <ProjectCard key={project.id} project={project} />
      ))}
    </div>
  );
};

export default ProjectGrid;
