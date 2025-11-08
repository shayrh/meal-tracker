const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;
const API_KEY = process.env.REACT_APP_API_SECRET;

if (!API_BASE_URL) {
  throw new Error('REACT_APP_API_BASE_URL is not defined. Set it in frontend/.env.local');
}

if (!API_KEY) {
  throw new Error('REACT_APP_API_SECRET is not defined. Set it in frontend/.env.local');
}

export async function fetchWithAuth(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': API_KEY,
      ...(options.headers || {}),
    },
    ...options,
  });
  if (!response.ok) {
    let message = 'Request failed';
    try {
      const body = await response.json();
      message = body.error || JSON.stringify(body);
    } catch (error) {
      // noop
    }
    throw new Error(message);
  }
  return response.json();
}

export function fetchMeals() {
  return fetchWithAuth('/meals');
}

export function createMeal(payload) {
  return fetchWithAuth('/meals', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function fetchInsights() {
  return fetchWithAuth('/api/meals/insights');
}

export function fetchProfile() {
  return fetchWithAuth('/api/users/profile');
}

export function updateProfile(payload) {
  return fetchWithAuth('/api/users/profile', {
    method: 'PUT',
    body: JSON.stringify(payload),
  });
}

export function fetchSummary() {
  return fetchWithAuth('/summary');
}
