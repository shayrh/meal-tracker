const formatDayStat = (entry) => {
  if (!entry?.date) {
    return '—';
  }
  const date = new Date(entry.date);
  const calories = entry.calories ?? 0;
  return `${date.toLocaleDateString(undefined, { weekday: 'short' })} · ${calories} kcal`;
};

const formatDailyCalories = (item) => {
  if (!item?.date) {
    return null;
  }
  const date = new Date(item.date);
  return {
    id: item.date,
    label: date.toLocaleDateString(undefined, { weekday: 'short' }),
    calories: item.calories ?? 0,
  };
};

export default function AchievementsPanel({ insights }) {
  const weekly =
    insights?.weekly ?? {
      totalCalories: 0,
      averageCalories: 0,
      count: 0,
      caloriesByDay: [],
      bestDay: { date: null, calories: null },
      indulgentDay: { date: null, calories: null },
    };
  const achievements = insights?.achievements ?? [];
  const points = insights?.points ?? 0;
  const totalMeals = insights?.totalMeals ?? 0;
  const streaks = insights?.streaks ?? { current: 0, longest: 0 };
  const recommendations = insights?.recommendations ?? [];
  const dailyCalories = (weekly.caloriesByDay ?? []).map(formatDailyCalories).filter(Boolean);

  return (
    <div className="card achievements-card">
      <div className="card-header">
        <h2>Insights &amp; Gamification</h2>
        <p>Points, streaks, and achievements keep you motivated.</p>
      </div>
      <div className="insight-grid">
        <div className="insight-tile">
          <span className="label">Weekly Meals</span>
          <strong>{weekly.count}</strong>
        </div>
        <div className="insight-tile">
          <span className="label">Weekly Calories</span>
          <strong>{weekly.totalCalories}</strong>
        </div>
        <div className="insight-tile">
          <span className="label">Avg Calories</span>
          <strong>{weekly.averageCalories}</strong>
        </div>
        <div className="insight-tile">
          <span className="label">Lifetime Points</span>
          <strong>{points}</strong>
        </div>
        <div className="insight-tile">
          <span className="label">Total Meals</span>
          <strong>{totalMeals}</strong>
        </div>
        <div className="insight-tile">
          <span className="label">Current Streak</span>
          <strong>{streaks.current}d</strong>
        </div>
        <div className="insight-tile">
          <span className="label">Longest Streak</span>
          <strong>{streaks.longest}d</strong>
        </div>
      </div>
      <div className="highlight-row">
        <div className="highlight">
          <span className="label">Lightest Day</span>
          <strong>{formatDayStat(weekly.bestDay)}</strong>
        </div>
        <div className="highlight indulgent">
          <span className="label">Indulgent Day</span>
          <strong>{formatDayStat(weekly.indulgentDay)}</strong>
        </div>
      </div>
      {dailyCalories.length > 0 && (
        <div className="daily-trend">
          <h3>Daily calories</h3>
          <ul>
            {dailyCalories.map((entry) => (
              <li key={entry.id}>
                <span>{entry.label}</span>
                <strong>{entry.calories}</strong>
              </li>
            ))}
          </ul>
        </div>
      )}
      <ul className="achievement-list">
        {achievements.map((achievement) => (
          <li key={achievement.id} className={achievement.achieved ? 'achieved' : ''}>
            <div>
              <strong>{achievement.label}</strong>
              <p>{achievement.details}</p>
              {achievement.progress && <span className="progress">{achievement.progress}</span>}
            </div>
            <span>{achievement.achieved ? 'Unlocked' : 'Locked'}</span>
          </li>
        ))}
      </ul>
      {!!recommendations.length && (
        <div className="coach-tips">
          <h3>Coach tips</h3>
          <ul>
            {recommendations.map((tip, index) => (
              <li key={index}>{tip}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
