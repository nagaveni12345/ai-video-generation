import React, { useState } from 'react';

import sparkleImage from '../../assets/Icons/sparkle.png';
import chromeImage from '../../assets/Icons/Chrome icon.png';
import appleImage from '../../assets/Icons/Apple icon.png';
import rightArrowIcon from '../../assets/Icons/Right arrow icon.png';
import mailImage from '../../assets/Icons/Mail icon.png';
import lockImage from '../../assets/Icons/Lock icon.png';
import eyeImage from '../../assets/Icons/Eye icon.png';
import alertImage from '../../assets/Icons/Alert icon.png'

const SparkleIcon = () => (
  <img src={sparkleImage} alt="Sparkle" className="w-full h-full object-contain" />
);

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
  <img src={rightArrowIcon} alt="Arrow" className="w-full h-full object-contain" />
);

const ErrorIcon = () => (
  <img src={alertImage} alt="Alert" className="w-full h-full object-contain" />
);

const AuthErrorIcon = () => (
  <img src={alertImage} alt="Alert" className="w-full h-full object-contain" />
);

const SignIn = ({ setActive }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState({ email: false, password: false });
  const [authError, setAuthError] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const handleSignIn = (e) => {
    e.preventDefault();
    const newErrors = {
      email: email.trim() === '',
      password: password.trim() === ''
    };
    setErrors(newErrors);
    setAuthError(false);
    
    if (!newErrors.email && !newErrors.password) {
      // Removed hardcoded credential check for testing
      if (setActive) {
        setActive('Home');
      }
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
          className="bg-[#FFFFFF] flex flex-col items-center justify-start w-full max-w-[551px]"
          style={{ 
            minHeight: '704px',
            padding: '48px 56px',
            borderRadius: '40px',
          }}
        >
          
          <div className="flex flex-col items-center mb-[32px] w-full">
            <h1 
              className="text-[#000000] flex items-center justify-center whitespace-nowrap"
              style={{
                width: '255px',
                height: '68px',
                opacity: 1,
                fontFamily: 'Inter, sans-serif',
                fontSize: '30px',
                fontWeight: 900,
                lineHeight: '40px',
                letterSpacing: '0px',
                textAlign: 'center'
              }}
            >
              VidAI Studio
            </h1>
          </div>
          
          <div className="w-full flex justify-start mb-[20px]">
            <div 
              className="flex items-center justify-center gap-[8px] transition-colors"
              style={{
                width: '125.0625px',
                height: '30px',
                opacity: 1,
                borderRadius: '33554400px',
                border: '1px solid #BDBDBD'
              }}
            >
              <span className="w-[14px] h-[14px] flex justify-center items-center text-[#111111]"><SparkleIcon /></span>
              <span 
                style={{
                  fontFamily: 'Inter, sans-serif',
                  fontSize: '12px',
                  fontWeight: 400,
                  lineHeight: '16px',
                  color: '#1F2937',
                  letterSpacing: '0px'
                }}
              >
                Welcome back
              </span>
            </div>
          </div>
          
          <div className="w-full text-left mb-[32px]">
            <h2 
              className="mb-[14px] text-[#000000] whitespace-nowrap"
              style={{
                width: '448px',
                height: '40px',
                opacity: 1,
                top: '46px',
                fontFamily: 'Inter, sans-serif',
                marginBottom: '10px',
                fontSize: '36px',
                fontWeight: 900,
                lineHeight: '40px',
                letterSpacing: '0px'
              }}
            >
              Sign in
            </h2>
            <div 
              className="flex flex-row items-center justify-start gap-[4px]"
              style={{
                width: '448px',
                height: '24px',
                opacity: 1,
                top: '94px'
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
                Don't have an account?
              </span>
              <button 
                onClick={() => setActive && setActive('SignUp')} 
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
                Sign up free
              </button>
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
            className="flex items-center" 
            style={{ 
              width: '448px', 
              height: '16px', 
              gap: '16px', 
              opacity: 1,
              marginBottom: '16px' 
            }}
          >
            <div style={{ width: '148.875px', height: '1px', backgroundColor: 'rgba(74, 85, 101, 1)', opacity: 1 }}></div>
            <span 
              className="flex items-center justify-center whitespace-nowrap" 
              style={{ 
                width: '118.234375px', 
                height: '16px', 
                opacity: 1,
                fontFamily: 'Inter, sans-serif',
                fontSize: '12px',
                fontWeight: 400,
                lineHeight: '16px',
                color: 'rgba(74, 85, 101, 1)',
                letterSpacing: '0px'
              }}
            >
              or continue with email
            </span>
            <div style={{ width: '148.890625px', height: '1px', backgroundColor: 'rgba(74, 85, 101, 1)', opacity: 1 }}></div>
          </div>

          <form className="w-full flex flex-col" onSubmit={handleSignIn}>
            {authError && (
              <div className="w-full flex items-center gap-[10px] min-h-[44px] px-[16px] py-[12px] bg-[#FFF0F0] rounded-[12px] mb-[16px]">
                <div className="text-[#FF3B30] w-[14px] h-[14px] flex items-center justify-center shrink-0">
                  <AuthErrorIcon />
                </div>
                <span className="text-[13px] text-[#FF3B30] font-normal">Entered email or password is incorrect</span>
              </div>
            )}

            <div className="flex flex-col mb-[14px]">
              <label 
                className="mb-[6px]" 
                style={{ 
                  width: '448px', 
                  height: '20px', 
                  opacity: 1,
                  fontFamily: 'Inter, sans-serif',
                  fontSize: '14px',
                  fontWeight: 500,
                  lineHeight: '20px',
                  color: 'rgba(153, 161, 175, 1)'
                }}
              >
                Email address
              </label>
              <div className="relative flex items-center" style={{ width: '448px', height: '50px' }}>
                <div 
                  className={`absolute pointer-events-none flex items-center justify-center transition-colors`}
                  style={{ 
                    width: '16px', 
                    height: '16px', 
                    opacity: 1, 
                    top: '17px', 
                    left: '17px',
                    zIndex: 10,
                    color: errors.email ? '#FF3B30' : 'rgba(106, 114, 130, 1)'
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
                    if (errors.email) setErrors({...errors, email: false});
                    if (authError) setAuthError(false);
                  }}
                  className={`bg-[#FFFFFF] border ${errors.email ? 'border-[#FF3B30] focus:ring-[#FF3B30]' : 'border-[#D1D5DB] focus:ring-[#000000]'} rounded-[12px] placeholder:text-[#4a5565] focus:outline-none focus:ring-1 transition-colors`}
                  style={{
                    position: 'absolute',
                    width: '446px',
                    height: '48px',
                    opacity: 1,
                    top: '1px',
                    left: '1px',
                    paddingTop: '14px',
                    paddingRight: '16px',
                    paddingBottom: '14px',
                    paddingLeft: '44px',
                    fontFamily: 'Inter, sans-serif',
                    fontSize: '14px',
                    fontWeight: 400,
                    lineHeight: '100%',
                    color: 'rgba(74, 85, 101, 1)'
                  }}
                />
              </div>
              {errors.email && (
                <div 
                  className="flex items-center" 
                  style={{ width: '195px', height: '17px', gap: '12px', marginTop: '6px', opacity: 1 }}
                >
                  <div style={{ width: '17px', height: '17px', opacity: 1 }}>
                    <ErrorIcon />
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
                    Enter your email
                  </span>
                </div>
              )}
            </div>

            <div className="flex flex-col mb-[14px]">
              <div 
                className="flex items-center mb-[6px]" 
                style={{ width: '448px', height: '20px', justifyContent: 'space-between', opacity: 1 }}
              >
                <label 
                  className="" 
                  style={{ 
                    width: '59.5625px', 
                    height: '20px', 
                    opacity: 1,
                    fontFamily: 'Inter, sans-serif',
                    fontSize: '14px',
                    fontWeight: 500,
                    lineHeight: '20px',
                    color: 'rgba(153, 161, 175, 1)'
                  }}
                >
                  Password
                </label>
                <button 
                  type="button" 
                  className="hover:text-[#000000] transition-colors cursor-pointer whitespace-nowrap"
                  style={{ 
                    height: '16px', 
                    opacity: 1,
                    fontFamily: 'Inter, sans-serif',
                    fontSize: '12px',
                    fontWeight: 500,
                    lineHeight: '16px',
                    color: 'rgba(106, 114, 130, 1)',
                    textAlign: 'center'
                  }}
                >
                  Forgot password?
                </button>
              </div>
              <div className="relative flex items-center" style={{ width: '448px', height: '50px' }}>
                <div 
                  className={`absolute pointer-events-none flex items-center justify-center transition-colors`}
                  style={{ 
                    width: '16px', 
                    height: '16px', 
                    opacity: 1, 
                    top: '17px', 
                    left: '17px', 
                    zIndex: 10,
                    color: errors.password ? '#FF3B30' : 'rgba(106, 114, 130, 1)'
                  }}
                >
                  <LockIcon />
                </div>
                <input 
                  type={showPassword ? "text" : "password"} 
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value);
                    if (errors.password) setErrors({...errors, password: false});
                    if (authError) setAuthError(false);
                  }}
                  className={`bg-[#FFFFFF] border ${errors.password ? 'border-[#FF3B30] focus:ring-[#FF3B30]' : 'border-[#D1D5DB] focus:ring-[#000000]'} rounded-[14px] placeholder:text-[#4a5565] focus:outline-none focus:ring-1 transition-colors`}
                  style={{
                    position: 'absolute',
                    width: '446px',
                    height: '48px',
                    opacity: 1,
                    top: '1px',
                    left: '1px',
                    paddingTop: '14px',
                    paddingRight: '44px',
                    paddingBottom: '14px',
                    paddingLeft: '44px',
                    fontFamily: 'Inter, sans-serif',
                    fontSize: '14px',
                    fontWeight: 400,
                    lineHeight: '100%',
                    color: 'rgba(74, 85, 101, 1)'
                  }}
                />
                <button 
                  type="button" 
                  onClick={() => setShowPassword(!showPassword)}
                  className={`absolute transition-colors flex items-center justify-center`}
                  style={{ 
                    width: '16px', 
                    height: '16px', 
                    opacity: showPassword ? 1 : 0.6, 
                    top: '17px', 
                    left: '415px', 
                    zIndex: 10,
                    color: errors.password ? '#FF3B30' : 'rgba(106, 114, 130, 1)'
                  }}
                >
                  <EyeIcon />
                </button>
              </div>
              {errors.password && (
                <div 
                  className="flex items-center" 
                  style={{ width: '195px', height: '17px', gap: '12px', marginTop: '6px', opacity: 1 }}
                >
                  <div style={{ width: '17px', height: '17px', opacity: 1 }}>
                    <ErrorIcon />
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
                    Enter your password
                  </span>
                </div>
              )}
            </div>

            <div className="flex items-center mb-[20px]" style={{ width: '448px', height: '20px', gap: '10px', opacity: 1 }}>
              <div className="relative flex items-center justify-center" style={{ width: '16px', height: '16px', opacity: 1 }}>
                <input 
                  id="remember" 
                  type="checkbox" 
                  className="peer appearance-none w-[16px] h-[16px] rounded-none bg-white checked:bg-[#000000] checked:border-[#000000] focus:ring-1 focus:ring-[#000000] focus:outline-none cursor-pointer transition-colors"
                  style={{ border: '1px solid rgba(0, 0, 0, 0.3)' }}
                />
                <svg className="absolute w-[10px] h-[10px] pointer-events-none hidden peer-checked:block text-white" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
              </div>
              <label 
                htmlFor="remember" 
                className="cursor-pointer select-none"
                style={{ 
                  width: '167.125px', 
                  height: '20px', 
                  opacity: 1,
                  fontFamily: 'Inter, sans-serif',
                  fontSize: '14px',
                  fontWeight: 500,
                  lineHeight: '20px',
                  color: 'rgba(106, 114, 130, 1)'
                }}
              >
                Remember me
              </label>
            </div>

            <button 
              type="submit" 
              className="bg-[#000000] hover:bg-gray-800 text-[#FFFFFF] rounded-[14px] text-[15px] font-medium transition-all duration-200 mb-[14px] relative"
              style={{ width: '448px', height: '56px', opacity: 1 }}
            >
              <span 
                className="absolute flex items-center justify-center whitespace-nowrap" 
                style={{ 
                  width: '120px', 
                  height: '24px', 
                  opacity: 1, 
                  top: '14px', 
                  left: '152.02px',
                  fontFamily: 'Inter, sans-serif',
                  fontSize: '16px',
                  fontWeight: 700,
                  lineHeight: '24px',
                  color: 'rgba(255, 255, 255, 1)',
                  textAlign: 'center'
                }}
              >
                Sign in to VidAI
              </span>
              <span 
                className="absolute flex items-center justify-center" 
                style={{ width: '16px', height: '16px', opacity: 1, top: '20px', left: '278.98px' }}
              >
                <ArrowRightIcon />
              </span>
            </button>
          </form>

          <div className="text-center" style={{ width: '448px', height: '16px', opacity: 1 }}>
            <p 
              className="text-[#64748B]" 
              style={{ 
                width: '448px', 
                height: '16px', 
                opacity: 1,
                fontFamily: 'Inter, sans-serif',
                fontSize: '12px',
                lineHeight: '16px',
                fontWeight: 400,
                textAlign: 'center'
              }}
            >
              By signing in you agree to our <a href="#" className="text-[#94A3B8] hover:text-[#64748B] transition-colors" style={{ fontFamily: 'Inter, sans-serif', fontSize: '12px', fontWeight: 400, lineHeight: '16px' }}>Terms</a> and <a href="#" className="text-[#94A3B8] hover:text-[#64748B] transition-colors" style={{ fontFamily: 'Inter, sans-serif', fontSize: '12px', fontWeight: 400, lineHeight: '16px' }}>Privacy Policy</a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SignIn;
