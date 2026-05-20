import React from 'react';
import avatarIcon from '../../assets/Icons/Avatar Icon.png';
import shieldIcon from '../../assets/Icons/Shield Icon.png';
import worldIcon from '../../assets/Icons/world Icon.png';
import cameraIcon from '../../assets/Icons/Camera Icon.png';
import thunderIcon from '../../assets/Icons/Thunder Icon.png';
import rightArrowIcon from '../../assets/Icons/Right arrow icon.png';
import dummyImage from '../../assets/Images/Dummy image.jpg';

const AvatarShowcase = () => {
  const points = [
    { icon: shieldIcon, text: "Commercially licensed for any use" },
    { icon: worldIcon, text: "Culturally diverse representation" },
    { icon: cameraIcon, text: "Custom avatar creation from your photo" },
    { icon: thunderIcon, text: "Real-time emotion and expression control" }
  ];

  const avatars = [
    { name: "Alex", type: "Male • Business", color: "linear-gradient(135deg, #364153 0%, #101828 100%)" },
    { name: "Sofia", type: "Female • Casual", color: "linear-gradient(135deg, #4A5565 0%, #1E2939 100%)" },
    { name: "James", type: "Male • Academic", color: "linear-gradient(135deg, #1E2939 0%, #000000 100%)" },
    { name: "Mia", type: "Female • Creative", color: "linear-gradient(135deg, #6A7282 0%, #1E2939 100%)" }
  ];

  return (
    <section 
      style={{
        width: '100%',
        minHeight: '877px',
        background: 'rgba(0, 0, 0, 1)',
        paddingTop: '50px',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        overflow: 'hidden'
      }}
    >
      <div 
        style={{
          width: '1276px',
          height: '757px',
          display: 'flex',
          alignItems: 'center',
          position: 'relative'
        }}
      >
        <div 
          style={{
            width: '1212px',
            height: '756.65px',
            marginLeft: '32px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}
        >
          {/* Left Content */}
          <div 
            style={{
              width: '571.5px',
              height: '547.75px',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center'
            }}
          >
            {/* Badge */}
            <div 
              style={{
                width: '223.45px',
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
                src={avatarIcon} 
                alt="" 
                style={{ 
                  width: '14px', 
                  height: '14px',
                  filter: 'brightness(0) invert(1)' 
                }} 
              />
              <span 
                style={{
                  fontFamily: 'Inter',
                  fontSize: '14px',
                  color: 'rgba(153, 161, 175, 1)',
                  fontWeight: 400,
                  whiteSpace: 'nowrap'
                }}
              >
                500+ photorealistic avatars
              </span>
            </div>

            {/* Heading */}
            <h2 
              style={{
                width: '571.5px',
                height: '96px',
                fontFamily: 'Inter',
                fontWeight: 700,
                fontSize: '48px',
                lineHeight: '48px',
                color: '#FFFFFF',
                marginBottom: '20px',
                display: 'flex',
                flexDirection: 'column'
              }}
            >
              <span>Lifelike AI Avatars</span>
              <span style={{ color: 'rgba(153, 161, 175, 1)' }}>That Speak For You</span>
            </h2>

            {/* Paragraph */}
            <p 
              style={{
                width: '571.5px',
                fontFamily: 'Inter',
                fontWeight: 400,
                fontSize: '18px',
                lineHeight: '29.25px',
                color: 'rgba(153, 161, 175, 1)',
                marginBottom: '32px'
              }}
            >
              Choose from hundreds of diverse, photorealistic male and female avatars. Each one moves naturally, speaks with emotion, and perfectly lip-syncs to your voice.
            </p>

            {/* Points */}
            <div 
              style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '16px',
                marginBottom: '40px'
              }}
            >
              {points.map((point, idx) => (
                <div 
                  key={idx}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px'
                  }}
                >
                  <div 
                    style={{
                      width: '32px',
                      height: '32px',
                      background: 'rgba(255, 255, 255, 0.08)',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      borderRadius: '10px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}
                  >
                    <img src={point.icon} alt="" style={{ width: '16px', height: '16px', filter: 'brightness(0) invert(1)' }} />
                  </div>
                  <span 
                    style={{
                      fontFamily: 'Inter',
                      fontSize: '14px',
                      color: 'rgba(209, 213, 220, 1)',
                      fontWeight: 400
                    }}
                  >
                    {point.text}
                  </span>
                </div>
              ))}
            </div>

            {/* Button */}
            <button 
              style={{
                width: '207px',
                height: '50px',
                background: 'rgba(255, 255, 255, 0.06)',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                borderRadius: '14px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '12px',
                cursor: 'pointer',
                transition: 'all 0.3s ease'
              }}
              className="hover:bg-white/[0.1] hover:border-white/[0.3]"
            >
              <span 
                style={{
                  fontFamily: 'Inter',
                  fontWeight: 500,
                  fontSize: '16px',
                  color: '#FFFFFF'
                }}
              >
                Create your avatar
              </span>
              <img src={rightArrowIcon} alt="" style={{ width: '16px', height: '16px' }} />
            </button>
          </div>

          {/* Right Cards Grid */}
          <div 
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(2, 277.75px)',
              gap: '24px'
            }}
          >
            {avatars.map((avatar, idx) => (
              <div 
                key={idx}
                style={{
                  width: '277.75px',
                  height: '370.32px',
                  borderRadius: '16px',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  background: avatar.color,
                  position: 'relative',
                  overflow: 'hidden'
                }}
              >
                {/* Image Overlay */}
                <img 
                  src={dummyImage} 
                  alt="" 
                  style={{
                    width: '100%',
                    height: '100%',
                    objectFit: 'cover',
                    opacity: 0.4,
                    position: 'absolute',
                    top: 0,
                    left: 0
                  }}
                />
                <div 
                  style={{
                    width: '100%',
                    height: '100%',
                    background: 'linear-gradient(to bottom, transparent 0%, rgba(0,0,0,0.8) 100%)',
                    position: 'absolute',
                    top: 0,
                    left: 0
                  }}
                />

                {/* Content Overlay */}
                <div 
                  style={{
                    position: 'absolute',
                    bottom: '13px',
                    left: '13px',
                    width: 'calc(100% - 26px)'
                  }}
                >
                  <h4 
                    style={{
                      fontFamily: 'Inter',
                      fontWeight: 600,
                      fontSize: '14px',
                      color: '#FFFFFF',
                      marginBottom: '4px'
                    }}
                  >
                    {avatar.name}
                  </h4>
                  <p 
                    style={{
                      fontFamily: 'Inter',
                      fontWeight: 400,
                      fontSize: '12px',
                      color: 'rgba(153, 161, 175, 1)'
                    }}
                  >
                    {avatar.type}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default AvatarShowcase;
