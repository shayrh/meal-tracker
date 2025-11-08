import { useState } from 'react';
import CameraButton from './CameraButton';

const moods = ['Energized', 'Balanced', 'Hungry', 'Sleepy'];

export default function MealForm({ onSubmit }) {
  const [foods, setFoods] = useState('');
  const [notes, setNotes] = useState('');
  const [calories, setCalories] = useState('');
  const [photoData, setPhotoData] = useState('');
  const [photoUrl, setPhotoUrl] = useState('');
  const [mood, setMood] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [cameraVersion, setCameraVersion] = useState(0);
  const [error, setError] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    setError('');
    const payload = {
      foods: foods
        .split(',')
        .map((item) => item.trim())
        .filter(Boolean),
      notes,
      mood: mood || undefined,
      calories: calories ? Number(calories) : undefined,
    };
    if (!notes) {
      delete payload.notes;
    }
    if (photoData) {
      payload.photoData = photoData;
    }
    if (photoUrl) {
      payload.photoUrl = photoUrl;
    }
    if (!payload.foods.length && !payload.photoData && !payload.photoUrl) {
      setError('Add at least one food or attach a photo to continue.');
      setSubmitting(false);
      return;
    }
    try {
      await onSubmit(payload);
      setFoods('');
      setNotes('');
      setCalories('');
      setPhotoData('');
      setPhotoUrl('');
      setCameraVersion((version) => version + 1);
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
        <p>Describe your plate or snap a picture and we will estimate the calories.</p>
      </div>
      <form className="meal-form" onSubmit={handleSubmit}>
        <label>
          Foods
          <input
            type="text"
            placeholder="e.g. grilled chicken, salad, rice"
            value={foods}
            onChange={(event) => setFoods(event.target.value)}
          />
          <span className="help-text">Comma separated list of foods.</span>
        </label>
        <label>
          Estimated Calories
          <input
            type="number"
            value={calories}
            onChange={(event) => setCalories(event.target.value)}
            placeholder="Optional override"
            min="0"
          />
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
          Notes
          <textarea
            rows="3"
            value={notes}
            onChange={(event) => setNotes(event.target.value)}
            placeholder="How did you feel, what did you notice?"
          />
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
