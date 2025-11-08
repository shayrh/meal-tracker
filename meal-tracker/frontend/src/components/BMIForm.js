import { useEffect, useState } from 'react';

const ranges = [
  { label: 'Underweight', max: 18.5, color: '#3778c2' },
  { label: 'Healthy', max: 24.9, color: '#42b883' },
  { label: 'Overweight', max: 29.9, color: '#ffb347' },
  { label: 'Obese', max: Infinity, color: '#ff6b6b' },
];

export default function BMIForm({ profile, onSave }) {
  const [height, setHeight] = useState('');
  const [weight, setWeight] = useState('');
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const bmi = profile?.bmi ?? null;

  useEffect(() => {
    setHeight(profile?.height ?? '');
    setWeight(profile?.weight ?? '');
  }, [profile]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSaving(true);
    setMessage('');
    try {
      await onSave({
        height: height ? Number(height) : null,
        weight: weight ? Number(weight) : null,
      });
      setMessage('Profile saved');
    } catch (error) {
      setMessage(error.message || 'Unable to save profile');
    } finally {
      setSaving(false);
    }
  };

  const bmiLabel = () => {
    if (!bmi) {
      return null;
    }
    return ranges.find((range) => bmi <= range.max) ?? ranges[ranges.length - 1];
  };

  const activeRange = bmiLabel();

  return (
    <div className="card bmi-card">
      <div className="card-header">
        <h2>BMI &amp; Profile</h2>
        <p>Store your stats to unlock personalized guidance.</p>
      </div>
      <form onSubmit={handleSubmit} className="bmi-form">
        <label>
          Height (cm)
          <input
            type="number"
            value={height}
            min="0"
            onChange={(event) => setHeight(event.target.value)}
            placeholder="170"
          />
        </label>
        <label>
          Weight (kg)
          <input
            type="number"
            value={weight}
            min="0"
            onChange={(event) => setWeight(event.target.value)}
            placeholder="68"
          />
        </label>
        <button type="submit" disabled={saving}>
          {saving ? 'Saving…' : 'Save Profile'}
        </button>
        {message && <p className="status-message">{message}</p>}
      </form>
      {bmi && (
        <div className="bmi-result" style={{ borderColor: activeRange?.color }}>
          <strong>Current BMI:</strong> {bmi}
          <span className="bmi-range" style={{ backgroundColor: activeRange?.color }}>
            {activeRange?.label}
          </span>
        </div>
      )}
    </div>
  );
}
