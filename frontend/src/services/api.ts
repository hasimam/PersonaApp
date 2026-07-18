import axios from 'axios';
import {
  TestStartResponse,
  Answer,
  ResultResponse,
  JourneyStartResponse,
  JourneyStartRequest,
  JourneySubmitAnswersRequest,
  JourneyPreviewStartRequest,
  JourneyPreviewSubmitAnswersRequest,
  JourneySubmitAnswersResponse,
  JourneyFeedbackRequest,
  JourneyFeedbackResponse,
  JourneyCancelRequest,
  JourneyCancelResponse,
  JourneyResumeRequest,
  CreateResultShareResponse,
  SharedJourneyResult,
} from '../types';
import { Language } from '../i18n/translations';

const normalizeUrl = (url: string): string => url.replace(/\/+$/, '');

const isLocalHostname = (hostname: string): boolean =>
  hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '0.0.0.0' || hostname === '::1';

const resolveRemoteApiUrl = (): string => {
  const envUrl = normalizeUrl(process.env.REACT_APP_API_URL || '');
  if (envUrl) {
    return envUrl;
  }
  if (typeof window === 'undefined') {
    return '';
  }
  if (isLocalHostname(window.location.hostname)) {
    return 'https://personaapp-backend.fly.dev';
  }
  return window.location.origin;
};

const localApiUrl = typeof window !== 'undefined' && isLocalHostname(window.location.hostname)
  ? 'http://localhost:8000'
  : '';
const remoteApiUrl = resolveRemoteApiUrl();

const toApiBase = (url: string): string => (url ? `${normalizeUrl(url)}/api/v1` : '/api/v1');
const localApiBase = localApiUrl ? toApiBase(localApiUrl) : '';
const remoteApiBase = toApiBase(remoteApiUrl);

const api = axios.create({
  baseURL: localApiBase || remoteApiBase,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error?.config as typeof error.config & { __retryWithRemote?: boolean };
    if (!config || config.__retryWithRemote || !localApiBase || error?.response) {
      return Promise.reject(error);
    }
    if (config.baseURL === localApiBase) {
      config.__retryWithRemote = true;
      config.baseURL = remoteApiBase;
      return api.request(config);
    }
    return Promise.reject(error);
  }
);

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
  startJourney: async (payload?: JourneyStartRequest): Promise<JourneyStartResponse> => {
    const response = await api.post('/journey/start', payload);
    return response.data;
  },

  startPreviewJourney: async (payload: JourneyPreviewStartRequest): Promise<JourneyStartResponse> => {
    const response = await api.post('/journey/preview/start', payload);
    return response.data;
  },

  resumeJourney: async (payload: JourneyResumeRequest, ownerToken: string): Promise<JourneyStartResponse> => {
    const response = await api.post('/journey/resume', payload, {
      headers: { 'X-Result-Owner-Token': ownerToken },
    });
    return response.data;
  },

  submitAnswers: async (
    payload: JourneySubmitAnswersRequest,
    ownerToken: string
  ): Promise<JourneySubmitAnswersResponse> => {
    const response = await api.post('/journey/submit-answers', payload, {
      headers: { 'X-Result-Owner-Token': ownerToken },
    });
    return response.data;
  },

  submitPreviewAnswers: async (
    payload: JourneyPreviewSubmitAnswersRequest
  ): Promise<JourneySubmitAnswersResponse> => {
    const response = await api.post('/journey/preview/submit', payload);
    return response.data;
  },

  submitFeedback: async (
    payload: JourneyFeedbackRequest,
    ownerToken: string
  ): Promise<JourneyFeedbackResponse> => {
    const response = await api.post('/journey/feedback', payload, {
      headers: { 'X-Result-Owner-Token': ownerToken },
    });
    return response.data;
  },

  cancelJourney: async (
    payload: JourneyCancelRequest,
    ownerToken: string
  ): Promise<JourneyCancelResponse> => {
    const response = await api.post('/journey/cancel', payload, {
      headers: { 'X-Result-Owner-Token': ownerToken },
    });
    return response.data;
  },

  createResultShare: async (
    testRunId: number,
    language: Language,
    ownerToken: string
  ): Promise<CreateResultShareResponse> => {
    const response = await api.post(
      '/journey/shares',
      { test_run_id: testRunId, language },
      { headers: { 'X-Result-Owner-Token': ownerToken } }
    );
    return response.data;
  },

  getSharedResult: async (shareToken: string): Promise<SharedJourneyResult> => {
    const response = await api.get('/shares/report', {
      headers: { 'X-Result-Share-Token': shareToken },
    });
    return response.data;
  },
};

export default api;
