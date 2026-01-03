import axios from 'axios';
import { TestStartResponse, Answer, ResultResponse } from '../types';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_BASE = `${API_URL}/api/v1`;

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const testApi = {
  startTest: async (): Promise<TestStartResponse> => {
    const response = await api.get('/test/start');
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
  getResult: async (resultId: number): Promise<ResultResponse> => {
    const response = await api.get(`/results/${resultId}`);
    return response.data;
  },
};

export default api;
