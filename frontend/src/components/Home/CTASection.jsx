import React from 'react';
import { ArrowRight, Check } from 'lucide-react';

const CTASection = () => {
  const features = [
    "No credit card required",
    "Free 14-day trial",
    "Cancel anytime"
  ];

  return (
    <section className="bg-gradient-to-b from-black to-[#0B1220] py-[120px]">
      <div className="max-w-[900px] mx-auto text-center px-4">
        {/* Title */}
        <h2 className="text-[32px] sm:text-[40px] lg:text-[48px] leading-[40px] sm:leading-[48px] lg:leading-[56px] font-semibold tracking-[-0.02em] text-white mb-4">
          Ready to Get Started?
        </h2>

        {/* Subtitle */}
        <p className="text-[16px] leading-[24px] text-gray-400 mb-8 whitespace-nowrap sm:whitespace-normal lg:whitespace-nowrap">
          Join millions of creators using AI to transform their video content. Start your free trial today.
        </p>

        {/* Button Group */}
        <div className="flex flex-col sm:flex-row justify-center gap-4 mb-10">
          <button className="h-[52px] px-8 bg-white text-black text-[15px] font-semibold rounded-2xl hover:bg-gray-100 transition-all duration-200 flex items-center justify-center w-full sm:w-auto shadow-[0_4px_14px_rgba(255,255,255,0.1)] active:scale-95 group">
            Start Free Trial
            <ArrowRight className="w-4 h-4 ml-2 transition-transform group-hover:translate-x-1" />
          </button>
          <button className="h-[52px] px-8 bg-white/5 border border-white/10 text-white text-[15px] font-semibold rounded-2xl hover:bg-white/10 transition-all duration-200 flex items-center justify-center w-full sm:w-auto active:scale-95">
            View Examples
          </button>
        </div>

        {/* Bottom Info Row */}
        <div className="flex flex-row flex-wrap justify-center items-center gap-x-12 gap-y-6 mt-16">
          {features.map((feature, index) => (
            <div key={index} className="flex items-center gap-2.5">
              <svg 
                className="w-5 h-5" 
                viewBox="0 0 24 24" 
                fill="none" 
                xmlns="http://www.w3.org/2000/svg"
              >
                <circle cx="12" cy="12" r="10" stroke="#00C875" strokeWidth="2.2" />
                <path 
                  d="M8.5 12.5L11 15L15.5 9" 
                  stroke="#00C875" 
                  strokeWidth="2.5" 
                  strokeLinecap="round" 
                  strokeLinejoin="round"
                />
              </svg>
              <span className="text-[15px] text-[#A1A1AA] font-medium tracking-tight">
                {feature}
              </span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default CTASection;
