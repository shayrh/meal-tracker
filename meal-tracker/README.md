![Meal Tracker banner](frontend/public/logo192.png)

# Meal Tracker

## Understanding the Project (LLM-style explanation)

From an LLM’s vantage point, Meal Tracker turns day-to-day eating into machine-readable signals. It blends lightweight “image recognition” (hash-based food detection stubs), calorie estimation heuristics, BMI math, and behavioral nudges (points + achievements) into one narrative:

- **Capture**: Users describe or photograph meals. The system infers foods, estimates calories, and attaches mood/notes for richer context.
- **Quantify**: A BMI calculator plus weekly summaries translate meals into health indicators that can be compared over time.
- **Gamify**: Every logged meal yields points. Consistency unlocks achievements (first meal, streaks, variety) to reinforce positive habits.
- **Surfacing insights**: Frontend dashboards show history, calorie averages, and achievements—creating a loop where awareness drives better choices.

In short, it converts qualitative eating behavior into quantifiable, gamified health insights.

## Architecture at a glance

- **Backend (Flask)**  
  - `/api/meals` handles creation + retrieval. Foods can be provided manually or inferred from a photo reference via a deterministic hash-based detector.  
  - `/api/meals/insights` returns weekly calorie aggregates, streak-based achievements, and lifetime points.  
  - `/api/users/profile` persists height/weight (in-memory) and exposes BMI readings.  
  - `/bmi` and `/api/users/bmi` keep backward compatibility for programmatic BMI checks.  
  - Data is stored in-memory (`data_store.py`) for rapid prototyping; swap with a database when persisting between sessions matters.

- **Frontend (React + Vite-ready CRA)**  
  - Dashboard-driven UI with sections for meal logging, BMI/profile management, meal history, and gamification insights.  
  - Camera/file picker converts images to base64 for the stub detector while still supporting remote URLs.  
  - API helpers centralize fetch logic with override-friendly `REACT_APP_API_BASE_URL`.

## Getting started

1. **Backend**
   ```bash
   cd backend
   python -m venv .venv && source .venv/bin/activate  # optional but recommended
   pip install -r requirements.txt
   python app.py
   ```
   The server listens on `http://localhost:5000`.

2. **Frontend**
   ```bash
   cd frontend
   npm install
   npm start
   ```
   Optionally set `REACT_APP_API_BASE_URL` (defaults to `http://localhost:5000`).

## API surface

| Endpoint | Method | Description |
| --- | --- | --- |
| `/healthz`, `/api/healthz` | GET | Basic health checks |
| `/bmi` | POST | `{ weight, height }` → BMI (cm/kg) |
| `/api/users/bmi` | POST | Same as `/bmi`, namespaced |
| `/api/users/profile` | GET | Current stored profile + BMI |
| `/api/users/profile` | PUT | Update `{ height, weight }` |
| `/api/meals` | GET | All logged meals (most recent first) |
| `/api/meals` | POST | Create meal `{ foods[], notes?, mood?, photoUrl?, photoData? }` |
| `/api/meals/insights` | GET | Weekly stats, achievements, and lifetime points |

## Frontend experience

- **Record a Meal**: Provide foods, optional calorie override, mood/notes, and either a URL or inline photo. Backend infers calories if unspecified.
- **BMI & Profile**: Save height/weight once; BMI updates automatically. Visual state labels highlight ranges (underweight → obese).
- **Meal History**: Chronological cards show calories, foods, moods, photos, and notes.
- **Gamification**: Insight panels reveal streaks, weekly calorie highs/lows, coach tips, and achievement progress to reinforce consistency.

## Next steps / ideas

1. Replace the hash-based detector with a real vision endpoint (Azure Custom Vision, Google AutoML, custom PyTorch model, etc.).  
2. Persist data via SQLite/Postgres and add auth for multi-user support.  
3. Expand analytics (macro split, nutrient goals, reminders).  
4. Ship the React UI as a PWA and add push notifications for streak preservation.
