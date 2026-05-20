import React from 'react';
import { 
  Sparkles, 
  Video, 
  UserCircle2, 
  Mic, 
  Languages, 
  ArrowRight,
  Cpu
} from 'lucide-react';
import { motion } from 'framer-motion';
import chipIcon from '../../assets/Icons/Chip Icon.png';
import sparkleIcon from '../../assets/Icons/White Sparkle.png';
import rightArrowIcon from '../../assets/Icons/Right arrow icon.png';
import videoIconAsset from '../../assets/Icons/video Icon.png';
import avatarIcon from '../../assets/Icons/Avatar Icon.png';
import voiceIcon from '../../assets/Icons/Voice Icon.png';
import languageIcon from '../../assets/Icons/Multi language Icon.png';
import thunderIcon from '../../assets/Icons/Thunder Icon.png';

const features = [
  {
    title: "Text to Video",
    desc: "Transform any script into stunning professional videos with photorealistic AI avatars in seconds.",
    icon: sparkleIcon,
    badge: "2x faster"
  },
  {
    title: "Record & Sync",
    desc: "Record yourself or upload footage and let AI automatically sync it with your text and narration.",
    icon: videoIconAsset,
    badge: "Frame-perfect"
  },
  {
    title: "Avatar Creator",
    desc: "Create hyper-realistic male and female AI avatars with custom appearance, clothes and expressions.",
    icon: avatarIcon,
    badge: "500+ styles"
  },
  {
    title: "Voice Cloning",
    desc: "Upload a 30-second voice sample and clone it perfectly. Your AI avatar speaks exactly like you.",
    icon: voiceIcon,
    badge: "99% accuracy"
  },
  {
    title: "Multi-Language",
    desc: "Auto-translate and dub your videos into 50+ languages while preserving your original voice tone.",
    icon: languageIcon,
    badge: "50+ languages"
  },
  {
    title: "Action Sync",
    desc: "Synchronize hand gestures, body movements and facial expressions perfectly with your content.",
    icon: thunderIcon,
    badge: "Real-time"
  }
];

const FeatureCard = ({ title, desc, icon, badge }) => (
  <div 
    style={{
      width: '389px',
      height: '247.5px',
      background: 'rgba(255, 255, 255, 0.04)',
      border: '1px solid rgba(255, 255, 255, 0.08)',
      borderRadius: '16px',
      padding: '24px 29px',
      display: 'flex',
      flexDirection: 'column',
      position: 'relative',
      transition: 'all 0.3s ease',
      flexShrink: 0
    }}
    className="group hover:bg-white/[0.06] hover:border-white/[0.12]"
  >
    {/* Top Row */}
    <div className="flex justify-between items-start mb-6">
      {/* Icon Container */}
      <div 
        style={{
          width: '48px',
          height: '48px',
          background: 'rgba(255, 255, 255, 0.1)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: '14px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}
      >
        <img src={icon} alt="" style={{ width: '24px', height: '24px' }} />
      </div>

      {/* Badge */}
      {badge && (
        <div 
          style={{
            height: '26px',
            background: 'rgba(255, 255, 255, 0.05)',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            borderRadius: '33554400px',
            padding: '4px 10px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
        >
          <span
            style={{
              fontFamily: 'Inter',
              fontWeight: 400,
              fontSize: '12px',
              lineHeight: '16px',
              color: 'rgba(106, 114, 130, 1)'
            }}
          >
            {badge}
          </span>
        </div>
      )}
    </div>

    {/* Heading */}
    <h3 
      style={{
        width: '331px',
        height: '28px',
        fontFamily: 'Inter',
        fontWeight: 600,
        fontSize: '20px',
        lineHeight: '28px',
        color: 'rgba(255, 255, 255, 1)',
        marginBottom: '12px'
      }}
    >
      {title}
    </h3>

    {/* Paragraph */}
    <p 
      style={{
        width: '100%',
        minHeight: '68.25px', // Consistent height for 3 lines to align links
        fontFamily: 'Inter, system-ui, sans-serif',
        fontWeight: 400,
        fontSize: '14px',
        lineHeight: '22.75px',
        color: 'rgba(153, 161, 175, 1)',
        marginBottom: '16px',
        letterSpacing: '-0.01em'
      }}
    >
      {desc}
    </p>

    {/* Explore Feature Link */}
    <div 
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '4px',
        cursor: 'pointer',
        marginTop: 'auto'
      }}
    >
      <span 
        style={{
          fontFamily: 'Inter',
          fontWeight: 400,
          fontSize: '14px',
          lineHeight: '20px',
          color: 'rgba(255, 255, 255, 0.5)'
        }}
      >
        Explore feature
      </span>
      <img src={rightArrowIcon} alt="" style={{ width: '14px', height: '14px', opacity: 0.5 }} />
    </div>
  </div>
);

const Features = () => {
  return (
    <section 
      style={{
        width: '100%',
        minHeight: '894px',
        padding: '60px 80px',
        background: 'rgba(0, 0, 0, 1)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center'
      }}
    >
      <div 
        style={{
          width: '1280px',
          height: '801px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center'
        }}
      >
        {/* Header Container */}
        <div 
          style={{
            width: '1216px',
            height: '190px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            marginBottom: '64px'
          }}
        >

          {/* Powered By Badge */}
          <div 
            style={{
              width: '207.81px',
              height: '34px',
              background: 'rgba(255, 255, 255, 0.06)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '33554400px',
              display: 'flex',
              alignItems: 'center',
              padding: '0 17px',
              gap: '8px',
              marginBottom: '20px'
            }}
          >
            <img 
              src={chipIcon} 
              alt="Chip Icon" 
              style={{ 
                width: '14px', 
                height: '14px',
                flexShrink: 0
              }} 
            />
            <span
              style={{
                width: '165px',
                height: '20px',
                fontFamily: 'Inter',
                fontSize: '13.7px',
                color: 'rgba(153, 161, 175, 1)',
                fontWeight: 500,
                lineHeight: '20px',
                whiteSpace: 'nowrap',
                display: 'flex',
                alignItems: 'center'
              }}
            >
              Powered by advanced AI
            </span>
          </div>

          {/* Main Heading */}
          <h2
            style={{
              width: '1207px',
              height: '60px',
              fontFamily: 'Inter',
              fontWeight: 700,
              fontSize: '60px',
              lineHeight: '60px',
              color: 'rgba(255, 255, 255, 1)',
              textAlign: 'center',
              marginBottom: '20px'
            }}
          >
            Everything You Need
          </h2>

          {/* Paragraph */}
          <p
            style={{
              width: '672px',
              height: '56px',
              fontFamily: 'Inter',
              fontWeight: 400,
              fontSize: '20px',
              lineHeight: '28px',
              color: 'rgba(153, 161, 175, 1)',
              textAlign: 'center'
            }}
          >
            One platform. Every tool you need to create, translate, and scale your video content globally.
          </p>
        </div>

        {/* Grid */}
        <div className="flex flex-wrap justify-center gap-6 max-w-[1240px]">
          {features.map((feature, idx) => (
            <FeatureCard 
              key={idx}
              title={feature.title}
              desc={feature.desc}
              icon={feature.icon}
              badge={feature.badge}
            />
          ))}
        </div>

        {/* CTA */}
        <div className="mt-16 flex justify-center pb-12">
          <button className="bg-white text-black px-8 py-3.5 rounded-full text-[15px] font-bold flex items-center gap-2 hover:bg-gray-100 transition-all active:scale-95 group">
            Start Creating Now <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
          </button>
        </div>
      </div>
    </section>
  );
};

export default Features;
