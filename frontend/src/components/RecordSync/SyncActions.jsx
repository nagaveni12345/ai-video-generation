import React from 'react';
import { motion } from 'framer-motion';

const SyncActions = ({ syncSettings, toggleSetting }) => {
  return (
    <div className="bg-[#0B0B0B] border border-[#1F1F1F] rounded-[16px] p-5">
      <h3 className="text-[14px] text-[#E5E7EB] mb-1 font-medium">Sync Actions</h3>
      <p className="text-[12px] text-[#6B7280] mb-5">Configure synchronization parameters</p>
      
      <div className="flex flex-col">
        {syncSettings.map((item, idx) => (
          <div key={item.name} className={`flex items-center justify-between py-[10px] ${idx !== syncSettings.length - 1 ? 'border-b border-white/[0.03]' : ''}`}>
            <span className="text-[13px] text-[#D1D5DB]">{item.name}</span>
            <div 
              onClick={() => toggleSetting(idx)}
              className={`w-[40px] h-[20px] rounded-full relative flex items-center px-0.5 transition-colors duration-300 cursor-pointer ${item.active ? 'bg-[#2563EB]' : 'bg-[#1F2937]'}`}
            >
              <motion.div 
                animate={{ x: item.active ? 20 : 0 }}
                transition={{ type: "spring", stiffness: 500, damping: 30 }}
                className="w-3.5 h-3.5 bg-white rounded-full shadow-sm" 
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SyncActions;
