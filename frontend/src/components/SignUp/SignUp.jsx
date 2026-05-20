import React, { useState } from 'react';
import videoFile from '../../assets/sign in video.mp4';

import chromeImage from '../../assets/Icons/Chrome icon.png';
import appleImage from '../../assets/Icons/Apple icon.png';
import rightArrowIcon from '../../assets/Icons/Right arrow icon.png';
import mailImage from '../../assets/Icons/Mail icon.png';
import lockImage from '../../assets/Icons/Lock icon.png';
import eyeImage from '../../assets/Icons/Eye icon.png';
import alertImage from '../../assets/Icons/Alert icon.png';

const GoogleIcon = () => (
  <img src={chromeImage} alt="Google" className="w-full h-full object-contain" />
);

const AppleIcon = () => (
  <img src={appleImage} alt="Apple" className="w-full h-full object-contain" />
);

const MailIcon = () => (
  <img src={mailImage} alt="Mail" className="w-full h-full object-contain" />
);

const LockIcon = () => (
  <img src={lockImage} alt="Lock" className="w-full h-full object-contain" />
);

const EyeIcon = () => (
  <img src={eyeImage} alt="Eye" className="w-full h-full object-contain" />
);

const ArrowRightIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M5 12H19M19 12L12 5M19 12L12 19" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

const UserIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M12 12C14.7614 12 17 9.76142 17 7C17 4.23858 14.7614 2 12 2C9.23858 2 7 4.23858 7 7C7 9.76142 9.23858 12 12 12Z" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M20.59 22C20.59 18.13 16.74 15 12 15C7.26003 15 3.41003 18.13 3.41003 22" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

const AuthErrorIcon = () => (
  <img src={alertImage} alt="Alert" className="w-full h-full object-contain" />
);

const SignUp = ({ setActive }) => {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState({
    fullName: false,
    email: false,
    password: false
  });
  const [showPassword, setShowPassword] = useState(false);

  const handleSignUp = (e) => {
    e.preventDefault();
    
    const newErrors = {
      fullName: fullName === '',
      email: email === '',
      password: password === ''
    };

    setErrors(newErrors);

    // If no errors, proceed to Home
    if (!newErrors.fullName && !newErrors.email && !newErrors.password) {
      if (setActive) setActive('Home');
    }
  };

  return (
    <div className="relative flex w-full min-h-screen bg-black overflow-y-auto overflow-x-hidden font-sans">
      {/* Left side - Video */}
      <div className="w-1/2 relative overflow-hidden flex items-center justify-center bg-black">
        <video
          autoPlay
          loop
          muted
          playsInline
          style={{
            width: '711.4375px',
            height: '1264.77783203125px',
            position: 'absolute',
            left: '-0.44px',
            top: '50%',
            marginTop: '-632.3889px', /* Half of height to center vertically */
            transform: 'rotate(-180deg)',
            opacity: 1,
            objectFit: 'cover'
          }}
        >
          <source src={videoFile} type="video/mp4" />
        </video>
        {/* Optional overlay to darken/blend the video slightly */}
        <div className="absolute inset-0 bg-black/20 z-10 pointer-events-none"></div>
      </div>

      {/* Right side - Form */}
      <div className="w-1/2 min-h-full flex items-center justify-center py-10 z-20">
        <div
          className="bg-[#FFFFFF] flex flex-col items-center justify-between w-full max-w-[551px]"
          style={{
            height: '900px',
            padding: '40px 29px 40px 28px',
            borderRadius: '40px',
            boxShadow: '0px 4px 4px 0px rgba(0, 0, 0, 0.2)',
            opacity: 1
          }}
        >

          <div className="flex flex-col items-center mb-[32px] w-full">
            <h1
              className="text-[#000000] flex items-center justify-center whitespace-nowrap"
              style={{
                width: '190px',
                height: '40px',
                opacity: 1,
                fontFamily: 'Inter, sans-serif',
                fontSize: '30px',
                fontWeight: 900,
                lineHeight: '40px',
                letterSpacing: '0px',
                textAlign: 'center',
                marginTop: '9px', // Using margin to reflect 'top' in flex context
                marginLeft: '32px' // Using margin to reflect 'left' in flex context
              }}
            >
              VidAI Studio
            </h1>
          </div>
          <div
            className="relative mb-[40px]"
            style={{
              width: '448px',
              height: '92px',
              opacity: 1
            }}
          >
            {/* Create account heading container */}
            <div
              className="absolute"
              style={{
                width: '448px',
                height: '40px',
                top: '20px',
                left: '0'
              }}
            >
              <h2
                className="text-[#000000] whitespace-nowrap"
                style={{
                  width: '278px',
                  height: '40px',
                  marginTop: '-2px', // Reflecting top: -2px
                  fontFamily: 'Inter, sans-serif',
                  fontSize: '36px',
                  fontWeight: 900,
                  lineHeight: '40px',
                  letterSpacing: '0px'
                }}
              >
                Create account
              </h2>
            </div>

            {/* Already have one? para container */}
            <div
              className="absolute flex flex-row items-center justify-start gap-[4px]"
              style={{
                width: '448px',
                height: '24px',
                top: '68px',
                left: '0'
              }}
            >
              <div
                className="flex flex-row items-center gap-[4px]"
                style={{
                  width: '195px',
                  height: '24px',
                  marginTop: '-2px' // Reflecting top: -2px
                }}
              >
                <span
                  style={{
                    fontFamily: 'Inter, sans-serif',
                    fontSize: '16px',
                    fontWeight: 400,
                    lineHeight: '24px',
                    color: '#6B7280',
                    letterSpacing: '0px'
                  }}
                >
                  Already have one?
                </span>
                <button
                  onClick={() => setActive && setActive('SignIn')}
                  className="hover:text-gray-700 transition-colors"
                  style={{
                    fontFamily: 'Inter, sans-serif',
                    fontSize: '16px',
                    fontWeight: 400,
                    lineHeight: '24px',
                    color: '#111111',
                    textDecoration: 'underline',
                    letterSpacing: '0px'
                  }}
                >
                  Sign in
                </button>
              </div>
            </div>
          </div>

          <div
            className="relative mb-[16px]"
            style={{
              width: '448px',
              height: '46px',
              opacity: 1
            }}
          >
            {/* Google Button */}
            <button
              className="absolute transition-colors flex items-center justify-center"
              style={{
                width: '218px',
                height: '46px',
                left: '0',
                borderRadius: '14px',
                border: '1px solid rgba(0, 0, 0, 0.1)', // Default border
                background: 'rgba(255, 255, 255, 0.06)',
                opacity: 1
              }}
            >
              <span
                className="absolute"
                style={{
                  width: '16px',
                  height: '16px',
                  top: '15px',
                  left: '72.98px'
                }}
              >
                <GoogleIcon />
              </span>
              <span
                className="absolute flex items-center justify-center whitespace-nowrap text-[#000000]"
                style={{
                  width: '48px',
                  height: '20px',
                  top: '12px',
                  left: '97.98px',
                  fontFamily: 'Inter, sans-serif',
                  fontSize: '14px',
                  fontWeight: 500,
                  lineHeight: '20px',
                  letterSpacing: '0px'
                }}
              >
                Google
              </span>
            </button>

            {/* Apple Button */}
            <button
              className="absolute transition-colors flex items-center justify-center"
              style={{
                width: '218px',
                height: '46px',
                left: '230px',
                borderRadius: '14px',
                border: '1px solid rgba(0, 0, 0, 0.1)', // Default border
                background: 'rgba(255, 255, 255, 0.06)',
                opacity: 1
              }}
            >
              <span
                className="absolute"
                style={{
                  width: '16px',
                  height: '16px',
                  top: '15px',
                  left: '73.3px'
                }}
              >
                <AppleIcon />
              </span>
              <span
                className="absolute flex items-center justify-center whitespace-nowrap text-[#000000]"
                style={{
                  width: '39px',
                  height: '20px',
                  top: '12px',
                  left: '103.3px',
                  fontFamily: 'Inter, sans-serif',
                  fontSize: '14px',
                  fontWeight: 500,
                  lineHeight: '20px',
                  letterSpacing: '0px'
                }}
              >
                Apple
              </span>
            </button>
          </div>

          <div
            className="flex items-center justify-center mb-[32px]"
            style={{
              width: '448px',
              height: '16px',
              gap: '16px',
              opacity: 1
            }}
          >
            <div style={{ width: '173.625px', height: '1px', background: 'rgba(0, 0, 0, 0.3)', opacity: 1 }}></div>
            <span
              className="flex items-center justify-center whitespace-nowrap"
              style={{
                width: '73px',
                height: '16px',
                opacity: 1,
                fontFamily: 'Inter, sans-serif',
                fontWeight: 400,
                fontSize: '12px',
                lineHeight: '16px',
                color: 'rgba(74, 85, 101, 1)',
                letterSpacing: '0px'
              }}
            >
              or with email
            </span>
            <div style={{ width: '173.625px', height: '1px', background: 'rgba(0, 0, 0, 0.3)', opacity: 1 }}></div>
          </div>

          <form
            className="w-full flex flex-col"
            onSubmit={handleSignUp}
            style={{
              width: '448px',
              gap: '24px',
              opacity: 1
            }}
          >
            <div
              className="flex flex-col"
              style={{
                width: '448px',
                gap: '6px',
                opacity: 1
              }}
            >
              <label
                style={{
                  width: '448px',
                  height: '20px',
                  fontFamily: 'Inter, sans-serif',
                  fontWeight: 500,
                  fontSize: '14px',
                  lineHeight: '20px',
                  color: 'rgba(153, 161, 175, 1)',
                  letterSpacing: '0px'
                }}
              >
                Full name
              </label>
              <div
                className="relative flex items-center"
                style={{
                  width: '448px',
                  height: '50px',
                  borderRadius: '14px',
                  border: `1px solid ${errors.fullName ? '#EF4444' : 'rgba(0, 0, 0, 0.15)'}`,
                  background: 'rgba(255, 255, 255, 0.05)',
                  opacity: 1
                }}
              >
                <div
                  className="absolute pointer-events-none flex items-center justify-center transition-colors"
                  style={{
                    width: '16px',
                    height: '16px',
                    top: '17px',
                    left: '17px',
                    color: '#9CA3AF',
                    opacity: 1,
                    zIndex: 10
                  }}
                >
                  <UserIcon />
                </div>
                <input
                  type="text"
                  placeholder="Enter your full name"
                  value={fullName}
                  onChange={(e) => {
                    setFullName(e.target.value);
                    if (errors.fullName) setErrors({ ...errors, fullName: false });
                  }}
                  className="bg-transparent border-none focus:outline-none transition-colors placeholder:text-[#4a5565]"
                  style={{
                    position: 'absolute',
                    width: '446px',
                    height: '48px',
                    top: '1px',
                    left: '1px',
                    padding: '14px 16px 14px 44px',
                    fontFamily: 'Inter, sans-serif',
                    fontWeight: 400,
                    fontSize: '14px',
                    lineHeight: '100%',
                    color: '#111827',
                    opacity: 1
                  }}
                />
              </div>
              {errors.fullName && (
                <div 
                  className="flex items-center" 
                  style={{ width: '195px', height: '17px', gap: '12px', marginTop: '8px', opacity: 1 }}
                >
                  <div style={{ width: '17px', height: '17px', opacity: 1 }}>
                    <AuthErrorIcon />
                  </div>
                  <span 
                    style={{ 
                      width: '166px', 
                      height: '17px', 
                      fontFamily: 'Inter', 
                      fontWeight: 400, 
                      fontSize: '12px', 
                      lineHeight: '100%', 
                      color: 'rgba(247, 0, 39, 1)',
                      display: 'flex',
                      alignItems: 'center'
                    }}
                  >
                    The name already exists
                  </span>
                </div>
              )}
            </div>

            <div
              className="flex flex-col"
              style={{
                width: '448px',
                gap: '6px',
                opacity: 1
              }}
            >
              <label
                style={{
                  width: '448px',
                  height: '20px',
                  fontFamily: 'Inter, sans-serif',
                  fontWeight: 500,
                  fontSize: '14px',
                  lineHeight: '20px',
                  color: 'rgba(153, 161, 175, 1)',
                  letterSpacing: '0px'
                }}
              >
                Email address
              </label>
              <div
                className="relative flex items-center"
                style={{
                  width: '448px',
                  height: '50px',
                  borderRadius: '14px',
                  border: `1px solid ${errors.email ? '#EF4444' : 'rgba(0, 0, 0, 0.15)'}`,
                  background: 'rgba(255, 255, 255, 0.05)',
                  opacity: 1
                }}
              >
                <div
                  className="absolute pointer-events-none flex items-center justify-center transition-colors"
                  style={{
                    width: '16px',
                    height: '16px',
                    top: '17px',
                    left: '17px',
                    color: '#9CA3AF',
                    opacity: 1,
                    zIndex: 10
                  }}
                >
                  <MailIcon />
                </div>
                <input
                  type="email"
                  placeholder="Enter your email address"
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value);
                    if (errors.email) setErrors({ ...errors, email: false });
                  }}
                  className="bg-transparent border-none focus:outline-none transition-colors placeholder:text-[#4a5565]"
                  style={{
                    position: 'absolute',
                    width: '446px',
                    height: '48px',
                    top: '1px',
                    left: '1px',
                    padding: '14px 16px 14px 44px',
                    fontFamily: 'Inter, sans-serif',
                    fontWeight: 400,
                    fontSize: '14px',
                    lineHeight: '100%',
                    color: '#111827',
                    opacity: 1
                  }}
                />
              </div>
              {errors.email && (
                <div 
                  className="flex items-center" 
                  style={{ width: '195px', height: '17px', gap: '12px', marginTop: '8px', opacity: 1 }}
                >
                  <div style={{ width: '17px', height: '17px', opacity: 1 }}>
                    <AuthErrorIcon />
                  </div>
                  <span 
                    style={{ 
                      width: '166px', 
                      height: '17px', 
                      fontFamily: 'Inter', 
                      fontWeight: 400, 
                      fontSize: '12px', 
                      lineHeight: '100%', 
                      color: 'rgba(247, 0, 39, 1)',
                      display: 'flex',
                      alignItems: 'center'
                    }}
                  >
                    The email already exists
                  </span>
                </div>
              )}
            </div>

            <div
              className="flex flex-col"
              style={{
                width: '448px',
                gap: '6px',
                opacity: 1
              }}
            >
              <label
                style={{
                  width: '448px',
                  height: '20px',
                  fontFamily: 'Inter, sans-serif',
                  fontWeight: 500,
                  fontSize: '14px',
                  lineHeight: '20px',
                  color: 'rgba(153, 161, 175, 1)',
                  letterSpacing: '0px'
                }}
              >
                Password
              </label>
              <div
                className="relative flex items-center"
                style={{
                  width: '448px',
                  height: '50px',
                  borderRadius: '14px',
                  border: `1px solid ${errors.password ? '#EF4444' : 'rgba(0, 0, 0, 0.15)'}`,
                  background: 'rgba(255, 255, 255, 0.05)',
                  opacity: 1
                }}
              >
                <div
                  className="absolute pointer-events-none flex items-center justify-center transition-colors"
                  style={{
                    width: '16px',
                    height: '16px',
                    top: '17px',
                    left: '17px',
                    color: '#9CA3AF',
                    opacity: 1,
                    zIndex: 10
                  }}
                >
                  <LockIcon />
                </div>
                <input
                  type={showPassword ? "text" : "password"}
                  placeholder="At least 8 characters"
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value);
                    if (errors.password) setErrors({ ...errors, password: false });
                  }}
                  className="bg-transparent border-none focus:outline-none transition-colors placeholder:text-[#4a5565]"
                  style={{
                    position: 'absolute',
                    width: '446px',
                    height: '48px',
                    top: '1px',
                    left: '1px',
                    padding: '14px 48px 14px 44px',
                    fontFamily: 'Inter, sans-serif',
                    fontWeight: 400,
                    fontSize: '14px',
                    lineHeight: '100%',
                    color: '#111827',
                    opacity: 1
                  }}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute text-[#6B7280] hover:text-[#000000] transition-colors flex items-center justify-center"
                  style={{
                    width: '16px',
                    height: '16px',
                    top: '17px',
                    left: '415px',
                    zIndex: 10,
                    opacity: showPassword ? 1 : 0.6
                  }}
                >
                  <EyeIcon />
                </button>
              </div>
              
              {/* Password Strength Indicator */}
              {password.length > 0 && !errors.password && (
                <div className="flex flex-col gap-[8px] mt-[12px] w-full">
                  <div className="flex gap-[8px] w-full">
                    <div 
                      className="h-[4px] rounded-full transition-all duration-300"
                      style={{ 
                        width: '106px', 
                        backgroundColor: password.length > 0 ? (password.length < 5 ? '#EF4444' : (password.length < 8 ? '#F59E0B' : (password.length < 11 ? '#10B981' : '#10B981'))) : '#E5E7EB' 
                      }}
                    />
                    <div 
                      className="h-[4px] rounded-full transition-all duration-300"
                      style={{ 
                        width: '106px', 
                        backgroundColor: password.length >= 5 ? (password.length < 8 ? '#F59E0B' : (password.length < 11 ? '#10B981' : '#10B981')) : '#E5E7EB' 
                      }}
                    />
                    <div 
                      className="h-[4px] rounded-full transition-all duration-300"
                      style={{ 
                        width: '106px', 
                        backgroundColor: password.length >= 8 ? (password.length < 11 ? '#10B981' : '#10B981') : '#E5E7EB' 
                      }}
                    />
                    <div 
                      className="h-[4px] rounded-full transition-all duration-300"
                      style={{ 
                        width: '106px', 
                        backgroundColor: password.length >= 11 ? '#10B981' : '#E5E7EB' 
                      }}
                    />
                  </div>
                  <span 
                    className="text-[12px] font-medium font-inter transition-colors duration-300"
                    style={{ 
                      color: password.length < 5 ? '#EF4444' : (password.length < 8 ? '#F59E0B' : (password.length < 11 ? '#10B981' : '#10B981')) 
                    }}
                  >
                    {password.length < 5 ? 'Weak' : (password.length < 8 ? 'Fair' : (password.length < 11 ? 'Good' : 'Strong'))}
                  </span>
                </div>
              )}

              {errors.password && (
                <div 
                  className="flex items-center" 
                  style={{ width: '195px', height: '17px', gap: '12px', marginTop: '8px', opacity: 1 }}
                >
                  <div style={{ width: '17px', height: '17px', opacity: 1 }}>
                    <AuthErrorIcon />
                  </div>
                  <span 
                    style={{ 
                      width: '166px', 
                      height: '17px', 
                      fontFamily: 'Inter', 
                      fontWeight: 400, 
                      fontSize: '12px', 
                      lineHeight: '100%', 
                      color: 'rgba(247, 0, 39, 1)',
                      display: 'flex',
                      alignItems: 'center'
                    }}
                  >
                    The password already exists
                  </span>
                </div>
              )}
            </div>

            <div 
              className="flex items-start mb-[10px] relative" 
              style={{ 
                width: '448px', 
                height: '22.75px', 
                opacity: 1 
              }}
            >
              <div 
                className="relative flex items-center justify-center"
                style={{ 
                  width: '16px', 
                  height: '16px', 
                  top: '2px',
                  opacity: 1
                }}
              >
                <input 
                  id="terms" 
                  type="checkbox" 
                  className="peer appearance-none w-[16px] h-[16px] rounded-[3px] border border-solid bg-white checked:bg-[#000000] checked:border-[#000000] focus:ring-1 focus:ring-[#000000] focus:outline-none cursor-pointer transition-colors"
                  style={{
                    borderColor: 'rgba(0, 0, 0, 0.3)'
                  }}
                  required
                />
                <svg 
                  className="absolute w-[10px] h-[10px] text-white opacity-0 peer-checked:opacity-100 pointer-events-none transition-opacity" 
                  viewBox="0 0 24 24" 
                  fill="none" 
                  stroke="currentColor" 
                  strokeWidth="4" 
                  strokeLinecap="round" 
                  strokeLinejoin="round"
                >
                  <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
              </div>
              <label 
                htmlFor="terms" 
                className="cursor-pointer select-none absolute whitespace-nowrap"
                style={{ 
                  width: '356px', 
                  height: '23px',
                  left: '26px',
                  fontFamily: 'Inter, sans-serif',
                  fontWeight: 500,
                  fontSize: '14px',
                  lineHeight: '22.75px',
                  color: 'rgba(153, 161, 175, 1)',
                  top: '-1px'
                }}
              >
                I agree to VidAI's <span className="font-medium" style={{ color: 'rgba(148, 163, 184, 1)', lineHeight: '22.75px' }}>Terms of Service</span> and <span className="font-medium" style={{ color: 'rgba(148, 163, 184, 1)', lineHeight: '22.75px' }}>Privacy Policy</span>
              </label>
            </div>

            <button
              type="submit"
              className="flex items-center justify-center bg-[#000000] hover:bg-gray-800 text-[#FFFFFF] rounded-full transition-all duration-200"
              style={{
                width: '448px',
                height: '56px',
                borderRadius: '14px',
                opacity: 1,
                boxShadow: '0px 0px 40px 0px rgba(255, 255, 255, 0.15)'
              }}
            >
              <div className="flex items-center justify-center gap-[8px]">
                <span
                  style={{
                    fontFamily: 'Inter, sans-serif',
                    fontWeight: 700,
                    fontSize: '16px',
                    lineHeight: '24px',
                    color: 'rgba(255, 255, 255, 1)',
                    textAlign: 'center',
                    letterSpacing: '0px'
                  }}
                >
                  Create account
                </span>
                <span className="flex items-center justify-center">
                  <ArrowRightIcon />
                </span>
              </div>
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default SignUp;
