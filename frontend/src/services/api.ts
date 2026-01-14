import axios from 'axios';
import { TestStartResponse, Answer, ResultResponse } from '../types';
import { Language } from '../i18n/translations';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_BASE = `${API_URL}/api/v1`;

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const testApi = {
  startTest: async (lang: Language = 'en'): Promise<TestStartResponse> => {
    const response = await api.get(`/test/start?lang=${lang}`);
    return response.data;
  },

  submitTest: async (sessionId: string, responses: Answer[]): Promise<{ result_id: number }> => {
    const response = await api.post('/test/submit', {
      session_id: sessionId,
      responses,
    });
    return response.data;
  },
};

export const resultsApi = {
  getResult: async (resultId: number, lang: Language = 'en'): Promise<ResultResponse> => {
    const response = await api.get(`/results/${resultId}?lang=${lang}`);
    return response.data;
  },
};

export default api;
