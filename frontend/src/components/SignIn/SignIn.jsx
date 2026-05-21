import React, { useState, useEffect } from 'react';
import videoFile from '../../assets/sign in video.mp4';

import sparkleImage from '../../assets/Icons/sparkle.png';
import blackSparkleImage from '../../assets/Icons/Black Sparkle.png';
import chromeImage from '../../assets/Icons/Chrome icon.png';
import appleImage from '../../assets/Icons/Apple icon.png';
import rightArrowIcon from '../../assets/Icons/Right arrow icon.png';
import mailImage from '../../assets/Icons/Mail icon.png';
import lockImage from '../../assets/Icons/Lock icon.png';
import eyeImage from '../../assets/Icons/Eye icon.png';
import alertImage from '../../assets/Icons/Alert icon.png';

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
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

const EyeOffIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M3.98 8.223A10.477 10.477 0 0 0 1.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.451 10.451 0 0 1 12 4.5c4.756 0 8.773 3.162 10.065 7.498a10.522 10.522 0 0 1-4.293 5.774M6.228 6.228 3 3m3.228 3.228 3.65 3.65m7.894 7.894L21 21m-3.228-3.228-3.65-3.65m0 0a3 3 0 1 0-4.243-4.243m4.242 4.242L9.88 9.88" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
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
  const [rememberMe, setRememberMe] = useState(false);

  useEffect(() => {
    const savedEmail = localStorage.getItem('rememberedEmail');
    const savedPassword = localStorage.getItem('rememberedPassword');
    if (savedEmail && savedPassword) {
      setEmail(savedEmail);
      setPassword(savedPassword);
      setRememberMe(true);
    }
  }, []);

  const validateEmail = (email) => {
    return String(email)
      .toLowerCase()
      .match(
        /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
      );
  };

  const handleSignIn = (e) => {
    e.preventDefault();
    
    const emailEmpty = email.trim() === '';
    const passwordEmpty = password.trim() === '';
    const emailInvalid = !validateEmail(email) && !emailEmpty;
    const passwordInvalid = password.length < 8 && !passwordEmpty;

    const newErrors = {
      email: emailEmpty || emailInvalid,
      password: passwordEmpty || passwordInvalid
    };
    
    setErrors(newErrors);
    setAuthError(false);
    
    if (!newErrors.email && !newErrors.password) {
      // Mock validation: check for a specific demo account
      const mockValidEmail = 'validuser@test.com';

      if (email.toLowerCase() === mockValidEmail && (password === 'Password123' || password === 'Password@123')) {
        if (rememberMe) {
          localStorage.setItem('rememberedEmail', email);
          localStorage.setItem('rememberedPassword', password);
        } else {
          localStorage.removeItem('rememberedEmail');
          localStorage.removeItem('rememberedPassword');
        }
        localStorage.setItem('isAuthenticated', 'true');
        if (setActive) {
          setActive('Home');
        }
      } else {
        // If credentials don't match the mock account, show the auth error
        setAuthError(true);
      }
    }
  };

  const isFormValid = email.trim() !== '' && validateEmail(email) && password.length >= 8;
  return (
    <div className="relative flex w-full h-screen bg-black overflow-hidden font-sans">
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
      <div className="w-1/2 h-full flex items-center justify-center py-10 z-20 overflow-y-auto">
        <div 
          className="bg-[#FFFFFF] flex flex-col items-center justify-start w-full max-w-[551px]"
          style={{ 
            padding: '48px 56px',
            borderRadius: '40px',
          }}
        >
          
          <div className="flex flex-col items-center mb-[16px] w-full">
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
          
          <div className="w-full flex flex-col items-start mb-[32px]" style={{ width: '448px' }}>
            <div 
              className="flex items-center mb-[4px]"
              style={{
                width: '125.0625px',
                height: '30px',
                borderRadius: '33554400px',
                border: '1px solid rgba(0, 0, 0, 0.26)',
                background: 'rgba(255, 255, 255, 0.06)',
                display: 'flex',
                alignItems: 'center',
                paddingLeft: '13px',
                gap: '6px'
              }}
            >
              <img 
                src={blackSparkleImage} 
                alt="Sparkle" 
                style={{ 
                  width: '14px', 
                  height: '14px',
                  opacity: 1
                }} 
              />
              <span 
                style={{ 
                  width: '83px',
                  height: '16px',
                  fontFamily: 'Inter, sans-serif', 
                  fontSize: '12px', 
                  fontWeight: 400, 
                  color: 'rgba(0, 0, 0, 1)',
                  lineHeight: '16px',
                  letterSpacing: '0px',
                  whiteSpace: 'nowrap'
                }}
              >
                Welcome back
              </span>
            </div>
            <h2 
              className="text-[#000000] whitespace-nowrap"
              style={{
                fontFamily: 'Inter, sans-serif',
                fontSize: '36px',
                fontWeight: 900,
                lineHeight: '40px',
                letterSpacing: '0px',
                marginBottom: '4px'
              }}
            >
              Sign in
            </h2>
            <div className="flex flex-row items-center justify-start gap-[4px]">
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
                Email address <span style={{ color: '#EF4444' }}>*</span>
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
                  style={{ width: '100%', height: '17px', gap: '12px', marginTop: '6px', opacity: 1 }}
                >
                  <div style={{ width: '17px', height: '17px', opacity: 1 }}>
                    <ErrorIcon />
                  </div>
                  <span 
                    style={{ 
                      width: 'auto', 
                      whiteSpace: 'nowrap',
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
                    {email.trim() === '' ? 'Enter your email' : 'Please enter a valid email'}
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
                    width: 'auto', 
                    height: '20px', 
                    opacity: 1,
                    fontFamily: 'Inter, sans-serif',
                    fontSize: '14px',
                    fontWeight: 500,
                    lineHeight: '20px',
                    color: 'rgba(153, 161, 175, 1)'
                  }}
                >
                  Password <span style={{ color: '#EF4444' }}>*</span>
                </label>
                <span 
                  role="button"
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    if (setActive) setActive('ForgotPassword');
                  }}
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
                </span>
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
                    width: '18px', 
                    height: '18px', 
                    top: '17px', 
                    left: '415px', 
                    zIndex: 10,
                    color: errors.password ? '#FF3B30' : (showPassword ? '#000000' : 'rgba(106, 114, 130, 0.6)')
                  }}
                >
                  {showPassword ? <EyeIcon /> : <EyeOffIcon />}
                </button>
              </div>
              {errors.password && (
                <div 
                  className="flex items-center" 
                  style={{ width: '100%', height: '17px', gap: '12px', marginTop: '6px', opacity: 1 }}
                >
                  <div style={{ width: '17px', height: '17px', opacity: 1 }}>
                    <ErrorIcon />
                  </div>
                  <span 
                    style={{ 
                      width: 'auto', 
                      whiteSpace: 'nowrap',
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
                    {password.trim() === '' ? 'Enter your password' : 'Password must be at least 8 characters'}
                  </span>
                </div>
              )}
            </div>

            <div className="flex items-center mb-[20px]" style={{ width: '448px', height: '20px', gap: '10px', opacity: 1 }}>
              <div className="relative flex items-center justify-center" style={{ width: '16px', height: '16px', opacity: 1 }}>
                <input 
                  id="remember" 
                  type="checkbox" 
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
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
              disabled={!isFormValid}
              className={`bg-[#000000] text-[#FFFFFF] rounded-[14px] text-[15px] font-medium transition-all duration-200 mb-[14px] relative ${!isFormValid ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-800'}`}
              style={{ width: '448px', height: '56px' }}
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
