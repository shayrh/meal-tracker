import { useState } from 'react';
import CameraButton from './CameraButton';

const moods = ['Energized', 'Balanced', 'Hungry', 'Sleepy'];
const mealTypes = ['Breakfast', 'Lunch', 'Dinner'];

export default function MealForm({ onSubmit }) {
  const [photoData, setPhotoData] = useState('');
  const [photoUrl, setPhotoUrl] = useState('');
  const [mealType, setMealType] = useState('');
  const [mood, setMood] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [cameraVersion, setCameraVersion] = useState(0);
  const [error, setError] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    setError('');
    const payload = {
      foods: [],
      ingredients: [],
      mood: mood || undefined,
      mealType: mealType || undefined,
    };
    if (photoData) {
      payload.photoData = photoData;
    }
    if (photoUrl) {
      payload.photoUrl = photoUrl;
    }
    if (!payload.photoData && !payload.photoUrl && !mealType) {
      setError('Select a meal type or attach a photo to continue.');
      setSubmitting(false);
      return;
    }
    try {
      await onSubmit(payload);
      setPhotoData('');
      setPhotoUrl('');
      setCameraVersion((version) => version + 1);
      setMealType('');
      setMood('');
    } catch (err) {
      setError(err.message || 'Unable to log meal');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2>Record a Meal</h2>
        <p>Choose your meal type, add an optional photo, and we will estimate the calories.</p>
      </div>
      <form className="meal-form" onSubmit={handleSubmit}>
        <label>
          Meal Type
          <select value={mealType} onChange={(event) => setMealType(event.target.value)}>
            <option value="">Select meal</option>
            {mealTypes.map((option) => (
              <option key={option} value={option.toLowerCase()}>
                {option}
              </option>
            ))}
          </select>
        </label>
        <label>
          Mood
          <select value={mood} onChange={(event) => setMood(event.target.value)}>
            <option value="">Select mood</option>
            {moods.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </label>
        <label>
          Photo URL
          <input
            type="url"
            placeholder="https://example.com/meal.jpg"
            value={photoUrl}
            onChange={(event) => setPhotoUrl(event.target.value)}
          />
        </label>
        <CameraButton key={cameraVersion} onCapture={setPhotoData} />
        <button type="submit" disabled={submitting}>
          {submitting ? 'Logging…' : 'Log Meal'}
        </button>
        {error && <p className="error-text">{error}</p>}
      </form>
    </div>
  );
}
