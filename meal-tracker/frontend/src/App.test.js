import { render, screen } from '@testing-library/react';
import App from './App';

const mockResponse = (data) =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve(data),
  });

beforeEach(() => {
  global.fetch = jest.fn((url) => {
    if (url.endsWith('/api/meals')) {
      return mockResponse({ meals: [] });
    }
    if (url.endsWith('/api/meals/insights')) {
      return mockResponse({
        weekly: {
          totalCalories: 0,
          averageCalories: 0,
          count: 0,
          caloriesByDay: [],
          bestDay: { date: null, calories: null },
          indulgentDay: { date: null, calories: null },
        },
        achievements: [],
        points: 0,
        totalMeals: 0,
        streaks: { current: 0, longest: 0 },
        recommendations: [],
      });
    }
    if (url.endsWith('/api/users/profile')) {
      return mockResponse({ profile: { height: null, weight: null }, bmi: null });
    }
    return mockResponse({});
  });
});

afterEach(() => {
  jest.resetAllMocks();
});

test('renders dashboard heading', async () => {
  render(<App />);
  const heading = await screen.findByRole('heading', { name: /meal tracker/i });
  expect(heading).toBeInTheDocument();
});
