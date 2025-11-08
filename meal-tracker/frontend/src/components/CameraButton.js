import { useRef, useState } from 'react';

export default function CameraButton({ onCapture }) {
  const fileInputRef = useRef(null);
  const [preview, setPreview] = useState('');

  const handleFileChange = (event) => {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }
    const reader = new FileReader();
    reader.onloadend = () => {
      const result = reader.result?.toString() ?? '';
      setPreview(result);
      onCapture(result);
    };
    reader.readAsDataURL(file);
  };

  return (
    <div className="camera-button">
      <button type="button" onClick={() => fileInputRef.current?.click()}>
        {preview ? 'Retake Photo' : 'Attach Meal Photo'}
      </button>
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        style={{ display: 'none' }}
        onChange={handleFileChange}
      />
      {preview && <img src={preview} alt="Meal preview" className="camera-preview" />}
    </div>
  );
}
