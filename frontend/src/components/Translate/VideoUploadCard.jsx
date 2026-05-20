import React, { useRef, useState } from 'react';

const UploadIcon = () => (
  <svg
    width="44"
    height="44"
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    {/* Arrow stem */}
    <line
      x1="12" y1="3"
      x2="12" y2="13"
      stroke="#5A6473"
      strokeWidth="1.75"
      strokeLinecap="round"
    />
    {/* Arrow head */}
    <polyline
      points="8,7 12,3 16,7"
      stroke="#5A6473"
      strokeWidth="1.75"
      strokeLinecap="round"
      strokeLinejoin="round"
      fill="none"
    />
    {/* Tray — left wall + bottom + right wall */}
    <polyline
      points="5,15 5,20 19,20 19,15"
      stroke="#5A6473"
      strokeWidth="1.75"
      strokeLinecap="round"
      strokeLinejoin="round"
      fill="none"
    />
  </svg>
);

const VideoUploadCard = () => {
  const fileInputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [urlValue, setUrlValue] = useState('');

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) setUploadedFile(file);
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) setUploadedFile(file);
  };

  return (
    <div
      style={{
        background: '#0D0D0D',
        border: '1px solid #1C1C1C',
        borderRadius: '16px',
        padding: '24px',
        display: 'flex',
        flexDirection: 'column',
        gap: '20px',
      }}
    >
      {/* Title */}
      <p
        style={{
          fontSize: '15px',
          fontWeight: '600',
          color: '#FFFFFF',
          margin: 0,
          letterSpacing: '-0.01em',
        }}
      >
        Upload Video
      </p>

      {/* Upload Zone */}
      <div
        onClick={() => fileInputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        style={{
          background: '#030303',
          borderRadius: '12px',
          height: '280px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '12px',
          cursor: 'pointer',
          border: isDragging ? '1.5px dashed #4B5563' : 'none',
          transition: 'all 0.2s ease',
        }}
      >
        {uploadedFile ? (
          <span style={{ color: '#9CA3AF', fontSize: '13px', textAlign: 'center', padding: '0 16px' }}>
            ✅ {uploadedFile.name}
          </span>
        ) : (
          <>
            <UploadIcon />
            <span
              style={{
                fontSize: '14px',
                color: '#6B7280',
                marginTop: '4px',
              }}
            >
              Upload your video
            </span>
          </>
        )}
        <input
          ref={fileInputRef}
          type="file"
          accept="video/*"
          style={{ display: 'none' }}
          onChange={handleFileChange}
        />
      </div>

      {/* White Bar — matches Figma UI exactly */}
      <div
        style={{
          width: '100%',
          height: '34px',
          background: '#FFFFFF',
          borderRadius: '8px',
          marginTop: '4px',
        }}
      />
    </div>
  );
};

export default VideoUploadCard;
