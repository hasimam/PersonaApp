import axios from 'axios';
import {
  TestStartResponse,
  Answer,
  ResultResponse,
  JourneyStartResponse,
  JourneySubmitAnswersRequest,
  JourneySubmitAnswersResponse,
  JourneyFeedbackRequest,
  JourneyFeedbackResponse,
  JourneyCancelRequest,
  JourneyCancelResponse,
} from '../types';
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

export const journeyApi = {
  startJourney: async (versionId?: string): Promise<JourneyStartResponse> => {
    const response = await api.post('/journey/start', versionId ? { version_id: versionId } : undefined);
    return response.data;
  },

  submitAnswers: async (payload: JourneySubmitAnswersRequest): Promise<JourneySubmitAnswersResponse> => {
    const response = await api.post('/journey/submit-answers', payload);
    return response.data;
  },

  submitFeedback: async (payload: JourneyFeedbackRequest): Promise<JourneyFeedbackResponse> => {
    const response = await api.post('/journey/feedback', payload);
    return response.data;
  },

  cancelJourney: async (payload: JourneyCancelRequest): Promise<JourneyCancelResponse> => {
    const response = await api.post('/journey/cancel', payload);
    return response.data;
  },
};

export default api;
