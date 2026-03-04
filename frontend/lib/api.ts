const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface RequestOptions {
  method?: string;
  body?: unknown;
  headers?: Record<string, string>;
}

async function request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, headers = {} } = options;

  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;

  const res = await fetch(`${API_BASE}${endpoint}`, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...headers,
    },
    ...(body ? { body: JSON.stringify(body) } : {}),
  });

  if (res.status === 401) {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
      window.location.href = '/auth';
    }
    throw new Error('Unauthorized');
  }

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || 'Request failed');
  }

  return res.json();
}

export const api = {
  get: <T>(url: string) => request<T>(url),
  post: <T>(url: string, body: unknown) => request<T>(url, { method: 'POST', body }),
  put: <T>(url: string, body: unknown) => request<T>(url, { method: 'PUT', body }),
  delete: <T>(url: string) => request<T>(url, { method: 'DELETE' }),
};

// Auth
export const authApi = {
  login: (email: string, password: string) =>
    api.post<{ access_token: string }>('/api/auth/login', { email, password }),
  register: (data: { email: string; password: string; name: string }) =>
    api.post<{ access_token: string }>('/api/auth/register', data),
  me: () => api.get<{ id: string; email: string; name: string }>('/api/auth/me'),
};

// Transactions
export const transactionsApi = {
  list: (params?: string) => api.get<any[]>(`/api/transactions${params ? `?${params}` : ''}`),
  create: (data: any) => api.post<any>('/api/transactions', data),
  update: (id: string, data: any) => api.put<any>(`/api/transactions/${id}`, data),
  delete: (id: string) => api.delete(`/api/transactions/${id}`),
  stats: () => api.get<any>('/api/transactions/stats'),
};

// Investments
export const investmentsApi = {
  portfolio: () => api.get<any>('/api/investments/portfolio'),
  search: (query: string) => api.get<any[]>(`/api/investments/search?q=${query}`),
  buy: (data: any) => api.post<any>('/api/investments/buy', data),
  sell: (data: any) => api.post<any>('/api/investments/sell', data),
  history: () => api.get<any[]>('/api/investments/history'),
};

// Gamification
export const gamificationApi = {
  profile: () => api.get<any>('/api/gamification/profile'),
  badges: () => api.get<any[]>('/api/gamification/badges'),
  leaderboard: () => api.get<any[]>('/api/gamification/leaderboard'),
};

// Notifications
export const notificationsApi = {
  list: () => api.get<any[]>('/api/notifications'),
  markRead: (id: string) => api.put<any>(`/api/notifications/${id}/read`, {}),
  markAllRead: () => api.put<any>('/api/notifications/read-all', {}),
};

// Settings
export const settingsApi = {
  get: () => api.get<any>('/api/settings'),
  update: (data: any) => api.put<any>('/api/settings', data),
  updatePassword: (data: { current: string; newPassword: string }) =>
    api.put<any>('/api/settings/password', data),
};
