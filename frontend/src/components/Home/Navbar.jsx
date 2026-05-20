import React from 'react';
import { 
  Sparkles, 
  Video, 
  UserCircle2, 
  Mic, 
  Languages, 
  Folder,
  Menu,
  X
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const Navbar = ({ active, setActive }) => {
  const [isOpen, setIsOpen] = React.useState(false);

  const navItems = [
    { name: 'Text to Video', icon: Sparkles },
    { name: 'Record & Sync', icon: Video },
    { name: 'Avatars', icon: UserCircle2 },
    { name: 'Voice Clone', icon: Mic },
    { name: 'Translate', icon: Languages },
    { name: 'Projects', icon: Folder }
  ];

  return (
    <nav className="sticky top-0 z-50 h-[64px] w-full px-4 sm:px-12 lg:px-20 bg-[#000000] border-b border-white/5 flex items-center justify-between font-inter">
      {/* Left Section: Logo + Brand */}
      <div className="flex items-center gap-[10px] cursor-pointer shrink-0" onClick={() => setActive('Home')}>
        <div className="w-[32px] h-[32px] bg-white rounded-[10px] flex items-center justify-center">
          <Sparkles className="w-[18px] h-[18px] text-black" fill="white" strokeWidth={2.5} />
        </div>
        <span className="text-[20px] font-bold text-white tracking-[-0.01em] leading-none">
          VidAI Studio
        </span>
      </div>

        {/* Center Section: Desktop Navigation */}
        <div className="hidden lg:flex items-center gap-1">
          {navItems.map((item) => (
            <button
              key={item.name}
              onClick={() => setActive(item.name)}
              className={`group flex items-center gap-2 px-4 py-2 rounded-full text-[14px] font-medium transition-all ${
                active === item.name 
                  ? 'text-white bg-[#1A1A1A] border border-[#262626]' 
                  : 'text-[#9CA3AF] hover:text-white border border-transparent'
              }`}
            >
              <item.icon 
                className={`w-[14px] h-[14px] stroke-[2] transition-colors ${
                  active === item.name ? 'text-white' : 'text-[#9CA3AF] group-hover:text-white'
                }`} 
              />
              <span className="leading-none">{item.name}</span>
            </button>
          ))}
        </div>

      {/* Mobile Actions */}
      <div className="md:hidden flex items-center">
        <button 
          onClick={() => setIsOpen(!isOpen)}
          className="text-[#9CA3AF] hover:text-white p-2"
        >
          {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Mobile Menu Dropdown */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.2 }}
            className="absolute top-[64px] left-0 w-full bg-[#000000] border-b border-white/5 py-4 px-12 md:hidden shadow-2xl"
          >
            <div className="flex flex-col gap-4">
              {navItems.map((item) => (
                <button
                  key={item.name}
                  onClick={() => {
                    setActive(item.name);
                    setIsOpen(false);
                  }}
                  className={`flex items-center gap-2 py-3 text-[14px] font-normal transition text-[#9CA3AF] ${
                    active === item.name ? 'text-white' : 'hover:text-white'
                  }`}
                >
                  <item.icon className="w-[14px] h-[14px] stroke-[1.5]" />
                  <span>{item.name}</span>
                </button>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
};

export default Navbar;
