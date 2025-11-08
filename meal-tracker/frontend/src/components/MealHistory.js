const formatDate = (isoString) => {
  if (!isoString) {
    return '';
  }
  return new Date(isoString).toLocaleString();
};

export default function MealHistory({ meals }) {
  if (!meals?.length) {
    return (
      <div className="card">
        <div className="card-header">
          <h2>Meal History</h2>
          <p>Logged meals will appear here for quick analysis.</p>
        </div>
        <p className="empty-state">No meals tracked yet.</p>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="card-header">
        <h2>Meal History</h2>
        <p>Review what you ate and how many points you earned.</p>
      </div>
      <ul className="meal-history-list">
        {meals.map((meal) => (
          <li key={meal.id} className="meal-history-item">
            <header>
              <strong>Meal #{meal.id}</strong>
              <span>{formatDate(meal.created_at)}</span>
            </header>
            <div className="meal-meta">
              <span>{meal.calories} kcal</span>
              <span>{meal.points} pts</span>
              {meal.mood && <span>{meal.mood}</span>}
            </div>
            <ul className="food-list">
              {meal.foods?.map((food) => (
                <li key={food.name}>
                  {food.name}
                  {food.calories && <span>{food.calories} kcal</span>}
                </li>
              ))}
            </ul>
            {meal.notes && <p className="notes">{meal.notes}</p>}
            {meal.photo && <img src={meal.photo} alt={`Meal ${meal.id}`} className="meal-photo" />}
          </li>
        ))}
      </ul>
    </div>
  );
}
