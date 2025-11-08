# Meal Tracker Frontend

React-based dashboard for logging meals, estimating calories, tracking BMI, and surfacing achievements that encourage consistent healthy habits.

## Quick start

```bash
cd frontend
npm install
npm start
```

By default the app points to `http://localhost:5000`. Override via `REACT_APP_API_BASE_URL` if your Flask server runs elsewhere.

## Screens & flows

- **Meal Logger**: Enter foods (comma separated), optional calorie override, mood/notes, and either a photo URL or inline upload. The UI calls `POST /api/meals`, which in turn estimates calories if you skip the number.
- **BMI & Profile**: Save height/weight (cm/kg) via `PUT /api/users/profile`. The card displays the calculated BMI and highlights the range.
- **Meal History**: Lists the meals returned by `GET /api/meals` including foods, calories, points, mood, notes, and optional photos.
- **Insights & Gamification**: Pulls `GET /api/meals/insights` to show weekly totals, streaks, best/worst days, coach tips, achievement status, and lifetime points.

## Testing

```
npm test
```

The default test mocks API calls and asserts that the dashboard heading renders.

## Customization tips

- Update `src/services/api.js` if you want advanced auth headers or retry logic.
- Swap the placeholder camera/file picker in `CameraButton` with native device capture if deploying to mobile browsers.
- Add new achievements or streak logic server-side and they will automatically surface in the Insights panel.
