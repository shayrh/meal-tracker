const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000';

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
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
  return request('/meals');
}

export function createMeal(payload) {
  return request('/meals', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function fetchInsights() {
  return request('/api/meals/insights');
}

export function fetchProfile() {
  return request('/api/users/profile');
}

export function updateProfile(payload) {
  return request('/api/users/profile', {
    method: 'PUT',
    body: JSON.stringify(payload),
  });
}
