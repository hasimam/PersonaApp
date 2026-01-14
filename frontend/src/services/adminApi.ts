import axios from 'axios';
import {
  AdminStats,
  AdminQuestion,
  AdminQuestionCreate,
  AdminQuestionUpdate,
  AdminIdol,
  AdminIdolCreate,
  AdminIdolUpdate,
  AdminTrait,
  AdminTraitCreate,
  AdminTraitUpdate,
} from '../types/admin';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_BASE = `${API_URL}/api/v1/admin`;

// Get admin key from localStorage
const getAdminKey = (): string => {
  return localStorage.getItem('adminKey') || '';
};

// Create axios instance with admin auth
const adminApi = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth header to all requests
adminApi.interceptors.request.use((config) => {
  config.headers['X-Admin-Key'] = getAdminKey();
  return config;
});

// Stats
export const statsApi = {
  getStats: async (): Promise<AdminStats> => {
    const response = await adminApi.get('/stats');
    return response.data;
  },
};

// Questions
export const questionsApi = {
  list: async (): Promise<AdminQuestion[]> => {
    const response = await adminApi.get('/questions');
    return response.data;
  },

  get: async (id: number): Promise<AdminQuestion> => {
    const response = await adminApi.get(`/questions/${id}`);
    return response.data;
  },

  create: async (data: AdminQuestionCreate): Promise<AdminQuestion> => {
    const response = await adminApi.post('/questions', data);
    return response.data;
  },

  update: async (id: number, data: AdminQuestionUpdate): Promise<AdminQuestion> => {
    const response = await adminApi.put(`/questions/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await adminApi.delete(`/questions/${id}`);
  },
};

// Idols
export const idolsApi = {
  list: async (): Promise<AdminIdol[]> => {
    const response = await adminApi.get('/idols');
    return response.data;
  },

  get: async (id: number): Promise<AdminIdol> => {
    const response = await adminApi.get(`/idols/${id}`);
    return response.data;
  },

  create: async (data: AdminIdolCreate): Promise<AdminIdol> => {
    const response = await adminApi.post('/idols', data);
    return response.data;
  },

  update: async (id: number, data: AdminIdolUpdate): Promise<AdminIdol> => {
    const response = await adminApi.put(`/idols/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await adminApi.delete(`/idols/${id}`);
  },
};

// Traits
export const traitsApi = {
  list: async (): Promise<AdminTrait[]> => {
    const response = await adminApi.get('/traits');
    return response.data;
  },

  get: async (id: number): Promise<AdminTrait> => {
    const response = await adminApi.get(`/traits/${id}`);
    return response.data;
  },

  create: async (data: AdminTraitCreate): Promise<AdminTrait> => {
    const response = await adminApi.post('/traits', data);
    return response.data;
  },

  update: async (id: number, data: AdminTraitUpdate): Promise<AdminTrait> => {
    const response = await adminApi.put(`/traits/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await adminApi.delete(`/traits/${id}`);
  },
};

// Auth helper
export const adminAuth = {
  setKey: (key: string): void => {
    localStorage.setItem('adminKey', key);
  },

  getKey: (): string => {
    return localStorage.getItem('adminKey') || '';
  },

  clearKey: (): void => {
    localStorage.removeItem('adminKey');
  },

  isLoggedIn: (): boolean => {
    return !!localStorage.getItem('adminKey');
  },

  // Verify key by calling stats endpoint
  verifyKey: async (key: string): Promise<boolean> => {
    try {
      await axios.get(`${API_BASE}/stats`, {
        headers: { 'X-Admin-Key': key },
      });
      return true;
    } catch {
      return false;
    }
  },
};

export default adminApi;
