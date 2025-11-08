import { useCallback, useEffect, useState } from 'react';
import AchievementsPanel from '../components/AchievementsPanel';
import BMIForm from '../components/BMIForm';
import MealForm from '../components/MealForm';
import MealHistory from '../components/MealHistory';
import { createMeal, fetchInsights, fetchMeals, fetchProfile, updateProfile } from '../services/api';

export default function Dashboard() {
  const [meals, setMeals] = useState([]);
  const [insights, setInsights] = useState(null);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const hydrate = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const [mealResponse, insightResponse, profileResponse] = await Promise.all([
        fetchMeals(),
        fetchInsights(),
        fetchProfile(),
      ]);
      setMeals(mealResponse.meals ?? []);
      setInsights(insightResponse);
      setProfile({
        height: profileResponse.profile?.height ?? null,
        weight: profileResponse.profile?.weight ?? null,
        bmi: profileResponse.bmi ?? null,
      });
    } catch (err) {
      setError(err.message || 'Unable to load data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    hydrate();
  }, [hydrate]);

  const handleMealSubmit = async (payload) => {
    const meal = await createMeal(payload);
    setMeals((previous) => [meal, ...previous]);
    const refreshedInsights = await fetchInsights();
    setInsights(refreshedInsights);
  };

  const handleProfileSave = async (values) => {
    const response = await updateProfile(values);
    setProfile({
      height: response.profile.height,
      weight: response.profile.weight,
      bmi: response.bmi,
    });
  };

  return (
    <div className="dashboard">
      <header className="page-header">
        <div>
          <h1>Meal Tracker</h1>
          <p>
            Capture meals, estimate calories, compute BMI, and earn achievements powered by a friendly AI
            nutrition coach.
          </p>
        </div>
        <div className="status-pill">{loading ? 'Loading data…' : 'Live sync enabled'}</div>
      </header>
      {error && <p className="error-text">{error}</p>}
      <section className="grid two-column">
        <MealForm onSubmit={handleMealSubmit} />
        <BMIForm profile={profile} onSave={handleProfileSave} />
      </section>
      <section className="grid two-column">
        <MealHistory meals={meals} />
        <AchievementsPanel insights={insights} />
      </section>
    </div>
  );
}
