import { Play, Sparkles, Check, Users, Video, Globe, Star, ChevronDown } from 'lucide-react';
import { motion } from 'framer-motion';
import aiBackground from '../../assets/Images/AI Video Background.jpg';
import rightArrowIcon from '../../assets/Icons/Right arrow icon.png';
import videoPreviewAsset from '../../assets/Images/AI Video Background.jpg';

const Hero = () => {
  const stats = [
    { icon: <Users size={20} />, value: '1M+', label: 'Active Creators' },
    { icon: <Video size={20} />, value: '10M+', label: 'Videos Generated' },
    { icon: <Globe size={20} />, value: '50+', label: 'Languages' },
    { icon: <Star size={20} className="fill-white" />, value: '4.9★', label: 'User Rating' }
  ];

  return (
    <section
      className="relative overflow-hidden flex flex-col items-center"
      style={{
        width: '100%',
        minHeight: '1130px',
        background: 'linear-gradient(135deg, #000000 0%, #101828 50%, #000000 100%)',
        opacity: 1,
        margin: '0 auto',
        overflowX: 'hidden'
      }}
    >
      {/* 🔹 Background Image Layer */}
      <div
        className="absolute pointer-events-none flex items-center justify-center overflow-hidden"
        style={{
          width: '1512px',
          height: '1157px',
          top: '0px',
          left: '50%',
          transform: 'translateX(-50%)',
          opacity: 0.1,
          zIndex: 1
        }}
      >
        <img
          src={aiBackground}
          alt=""
          className="w-full h-full object-cover grayscale brightness-110"
        />
      </div>

      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background: 'radial-gradient(circle at center, rgba(37, 99, 235, 0.15) 0%, rgba(37, 99, 235, 0.05) 40%, transparent 70%)',
          zIndex: 2
        }}
      />

      {/* 🔹 Top Black Fade Overlay */}
      <div
        className="absolute top-0 left-0 w-full h-[300px] pointer-events-none"
        style={{
          background: 'linear-gradient(to bottom, #000000 0%, rgba(0,0,0,0.8) 20%, transparent 60%)',
          zIndex: 3
        }}
      />

      {/* 🔹 Bottom Black Fade Overlay */}
      <div
        className="absolute bottom-0 left-0 w-full h-[300px] pointer-events-none"
        style={{
          background: 'linear-gradient(to top, #000000 0%, rgba(0,0,0,0.8) 20%, transparent 100%)',
          zIndex: 3
        }}
      />

      {/* 🔹 Bottom Left Corner Overlay+Blur */}
      <div
        className="absolute pointer-events-none"
        style={{
          width: '473.95px',
          height: '473.95px',
          top: '621.02px',
          left: '35.02px',
          opacity: 0.09,
          borderRadius: '16777200px',
          background: 'rgba(255, 255, 255, 0.05)',
          backdropFilter: 'blur(64px)',
          zIndex: 2
        }}
      />

      {/* 🔹 Top Right Corner Overlay+Blur */}
      <div
        className="absolute pointer-events-none"
        style={{
          width: '409.25px',
          height: '409.25px',
          top: '67.38px',
          left: '963.38px',
          opacity: 0.06,
          borderRadius: '16777200px',
          background: 'rgba(255, 255, 255, 0.05)',
          backdropFilter: 'blur(64px)',
          zIndex: 2
        }}
      />

      <div className="relative z-10 max-w-[1200px] mx-auto px-6 pt-5 flex flex-col items-center text-center">
        {/* Main Heading */}
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="flex flex-col items-center select-none"
          style={{
            width: '1024px',
            height: '248px',
            paddingTop: '8px',
            opacity: 1
          }}
        >
          <div
            style={{
              width: '726px',
              height: '240px',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              alignItems: 'center'
            }}
          >
            <span
              className="text-white"
              style={{
                fontFamily: 'Inter',
                fontWeight: 700,
                fontSize: '88.3px',
                lineHeight: '120px',
                textAlign: 'center'
              }}
            >
              Create AI Videos
            </span>
            <span
              className="bg-clip-text text-transparent"
              style={{
                fontFamily: 'Inter',
                fontWeight: 700,
                fontSize: '88.3px',
                lineHeight: '120px',
                textAlign: 'center',
                background: 'linear-gradient(180deg, #E5E7EB 0%, #9CA3AF 100%)',
                WebkitBackgroundClip: 'text'
              }}
            >
              In Minutes
            </span>
          </div>
        </motion.h1>

        {/* Subtext */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="flex flex-col items-center select-none mb-8"
          style={{
            width: '768px',
            height: '78px',
            maxWidth: '768px',
            opacity: 1
          }}
        >
          <span
            style={{
              width: '730px',
              height: '78px',
              fontFamily: 'Inter',
              fontWeight: 400,
              fontSize: '21.2px',
              lineHeight: '39px',
              textAlign: 'center',
              color: 'rgba(153, 161, 175, 1)'
            }}
          >
            Transform text into professional videos with AI avatars, clone voices, and translate to 50+ languages. All in one powerful platform.
          </span>
        </motion.p>

        {/* Buttons Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="flex flex-col items-center select-none"
          style={{
            width: '1024px',
            height: '82px',
            paddingTop: '24px',
            opacity: 1
          }}
        >
          <div className="flex items-center" style={{ gap: '16px' }}>
            <button
              className="flex items-center justify-center bg-white hover:bg-neutral-100 transition-colors active:scale-95"
              style={{
                width: '191px',
                height: '56px',
                borderRadius: '14px',
                boxShadow: '0px 8px 10px -6px rgba(0, 0, 0, 0.1), 0px 20px 25px -5px rgba(0, 0, 0, 0.1)',
                gap: '16px',
                border: 'none',
                cursor: 'pointer'
              }}
            >
              <span
                style={{
                  fontFamily: 'Inter',
                  fontWeight: 500,
                  fontSize: '17px',
                  lineHeight: '28px',
                  color: 'rgba(0, 0, 0, 1)',
                  textAlign: 'center',
                  display: 'inline-block'
                }}
              >
                Get Started Free
              </span>
              <div style={{ width: '16px', height: '16px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <img
                  src={rightArrowIcon}
                  alt=""
                  style={{
                    width: '16px',
                    height: '16px',
                    opacity: 1,
                    objectFit: 'contain',
                    filter: 'invert(1)' // Arrow asset is white, need it black for white button
                  }}
                />
              </div>
            </button>

            <button
              className="flex items-center justify-center bg-white/[0.05] hover:bg-white/[0.08] transition-all active:scale-95"
              style={{
                width: '163px',
                height: '58px',
                borderRadius: '14px',
                border: '1px solid rgba(255, 255, 255, 0.3)',
                backdropFilter: 'blur(8px)',
                gap: '16px',
                cursor: 'pointer',
                padding: '0 12px'
              }}
            >
              <div style={{ width: '16px', height: '16px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Play className="w-4 h-4 fill-white text-white" />
              </div>
              <span
                style={{
                  width: '105px',
                  height: '28px',
                  fontFamily: 'Inter',
                  fontSize: '17.2px',
                  fontWeight: 500,
                  lineHeight: '28px',
                  color: 'rgba(255, 255, 255, 1)',
                  textAlign: 'center',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                Watch Demo
              </span>
            </button>
          </div>
        </motion.div>

        {/* Video Preview Section */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="relative flex flex-col items-center select-none"
          style={{
            width: '896px',
            height: '544px',
            maxWidth: '896px',
            paddingTop: '40px',
            opacity: 1
          }}
        >


          {/* Background+Border+Shadow (The Card) */}
          <div
            className="relative overflow-hidden group cursor-pointer"
            style={{
              width: '896px',
              height: '504px',
              borderRadius: '16px',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              background: 'linear-gradient(135deg, #111111 0%, #000000 100%)',
              boxShadow: '0px 25px 50px -12px rgba(0, 0, 0, 0.5)',
              zIndex: 1
            }}
          >
            {/* AI video demo image layer */}
            <div
              className="absolute inset-0 overflow-hidden"
              style={{
                width: '894px',
                height: '502px',
                margin: 'auto',
                opacity: 1,
                zIndex: 1
              }}
            >
              <img
                src={videoPreviewAsset}
                alt=""
                className="w-full h-full object-cover grayscale"
              />
            </div>

            {/* Bottom Gradient Overlay */}
            <div
              className="absolute inset-0"
              style={{
                width: '894px',
                height: '502px',
                margin: 'auto',
                opacity: 1,
                background: 'linear-gradient(0deg, rgba(0, 0, 0, 0.8) 0%, rgba(0, 0, 0, 0.2) 50%, rgba(0, 0, 0, 0) 100%)'
              }}
            />

            {/* Overlay Tags */}
            <div 
              className="absolute top-6 left-6 flex items-center z-20"
              style={{
                width: '119px',
                height: '38px',
                gap: '8px',
                padding: '8px 16px',
                borderRadius: '14px',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                background: 'rgba(28, 28, 30, 0.8)',
                backdropFilter: 'blur(12px)'
              }}
            >
              <div 
                style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '16777200px',
                  background: 'rgba(251, 44, 54, 1)'
                }}
              />
              <span
                style={{
                  width: '69px',
                  height: '20px',
                  fontFamily: 'Inter',
                  fontWeight: 500,
                  fontSize: '13.7px',
                  lineHeight: '20px',
                  color: 'rgba(255, 255, 255, 1)',
                  textAlign: 'center',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                Live Demo
              </span>
            </div>

            <div 
              className="absolute top-6 right-6 flex items-center justify-center z-20"
              style={{
                width: '103px',
                height: '42px',
                paddingTop: '10.75px',
                paddingRight: '16px',
                paddingBottom: '9.25px',
                paddingLeft: '16px',
                borderRadius: '14px',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                background: 'rgba(255, 255, 255, 0.1)',
                backdropFilter: 'blur(12px)'
              }}
            >
              <span
                style={{
                  width: '69px',
                  height: '20px',
                  fontFamily: 'Inter',
                  fontWeight: 500,
                  fontSize: '13.8px',
                  lineHeight: '20px',
                  color: 'rgba(255, 255, 255, 1)',
                  textAlign: 'center',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                4K Quality
              </span>
            </div>

            {/* Play Button Overlay */}
            <div className="absolute inset-0 flex items-center justify-center z-20">
              <div
                className="transition-all duration-300 group-hover:scale-110 flex items-center justify-center"
                style={{
                  width: '80px',
                  height: '80px',
                  background: 'rgba(255, 255, 255, 0.2)',
                  borderRadius: '16777200px',
                  border: '2px solid rgba(255, 255, 255, 0.4)',
                  backdropFilter: 'blur(12px)',
                  paddingLeft: '24px',
                  paddingRight: '20px'
                }}
              >
                <Play className="w-8 h-8 fill-white text-white" />
              </div>
            </div>

            {/* AI Generated Tag */}
            <div 
              className="absolute bottom-6 left-6 flex items-center z-20"
              style={{
                width: '145px',
                height: '38px',
                gap: '8px',
                padding: '8px 16px',
                borderRadius: '14px',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                background: 'rgba(255, 255, 255, 0.1)',
                backdropFilter: 'blur(12px)'
              }}
            >
              <div 
                className="flex items-center justify-center"
                style={{
                  width: '16px',
                  height: '16px',
                  borderRadius: '50%',
                  border: '1.5px solid #10b981'
                }}
              >
                <Check className="w-2.5 h-2.5 text-[#10b981] stroke-[4px]" />
              </div>
              <span
                style={{
                  width: '87px',
                  height: '20px',
                  fontFamily: 'Inter',
                  fontWeight: 500,
                  fontSize: '13.7px',
                  lineHeight: '20px',
                  color: 'rgba(255, 255, 255, 1)',
                  textAlign: 'center',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                AI Generated
              </span>
            </div>
          </div>

          {/* Scroll Indicator */}
          <div className="mt-12 flex flex-col items-center gap-2">
            <span 
              style={{
                width: '107.13px',
                height: '20px',
                fontFamily: 'Inter',
                fontWeight: 500,
                fontSize: '13.8px',
                lineHeight: '20px',
                color: 'rgba(153, 161, 175, 1)',
                textAlign: 'center'
              }}
            >
              Scroll to explore
            </span>
            <ChevronDown 
              className="animate-bounce" 
              style={{ 
                width: '24px', 
                height: '24px', 
                color: 'rgba(153, 161, 175, 1)' 
              }} 
            />
          </div>
        </motion.div>

      </div>

      {/* Stats Section */}
      <div
        style={{
          width: '100%',
          height: '226px',
          padding: '48px 96px',
          background: 'rgba(0, 0, 0, 1)',
          borderTop: '1px solid rgba(255, 255, 255, 0.1)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          marginTop: '80px',
          position: 'relative',
          zIndex: 20
        }}
      >
        <div
          style={{
            width: '1248px',
            height: '128px',
            padding: '0 32px',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center'
          }}
        >
          <div
            style={{
              width: '1184px',
              height: '128px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}
          >
            {stats.map((stat, idx) => (
              <div
                key={idx}
                style={{
                  width: '277.75px',
                  height: '128px',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '16px'
                }}
              >
                {/* Icon Container */}
                <div
                  style={{
                    width: '48px',
                    height: '48px',
                    background: 'rgba(255, 255, 255, 0.08)',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    borderRadius: '16px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'rgba(255, 255, 255, 1)'
                  }}
                >
                  {/* Icon Layout */}
                  <div style={{ width: '20px', height: '20px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    {stat.icon}
                  </div>
                </div>

                {/* Text Content */}
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px' }}>
                  <span
                    style={{
                      height: '40px',
                      fontFamily: 'Inter',
                      fontWeight: 700,
                      fontSize: '36px',
                      lineHeight: '40px',
                      color: 'rgba(255, 255, 255, 1)',
                      textAlign: 'center'
                    }}
                  >
                    {stat.value}
                  </span>
                  <span
                    style={{
                      height: '20px',
                      fontFamily: 'Inter',
                      fontWeight: 400,
                      fontSize: '14px',
                      lineHeight: '20px',
                      color: 'rgba(106, 114, 130, 1)',
                      textAlign: 'center'
                    }}
                  >
                    {stat.label}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;
