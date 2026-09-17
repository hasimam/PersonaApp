import '@testing-library/jest-dom';
import React from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import MothersMirror from './MothersMirror';
import { LanguageProvider } from '../i18n/LanguageContext';
import api from '../services/api';
jest.mock('../services/api', () => ({ __esModule: true, default: { get: jest.fn(), put: jest.fn() } }));
const mockedApi = api as jest.Mocked<typeof api>;
const pendingKey = 'miraati_mother_pending';
const state = {
  id: 'mother-1', status: 'baseline', current_day: 1, focus_code: null,
  timezone: 'UTC', next_available_at: null, answers: {}, result: null, practice: null, checkins: [],
  content: { version: 'test', areas: [], practices: [], situations: [1, 2].map(n => ({
    id: `s${n}`, area: 'a', text: { en: `Situation ${n}`, ar: `موقف ${n}` },
    options: ['A', 'B'].map(id => ({ id, text: { en: `Option ${id}`, ar: id } })),
  })) },
};
const mount = () => render(<MemoryRouter><LanguageProvider><MothersMirror /></LanguageProvider></MemoryRouter>);
beforeEach(() => {
  jest.resetAllMocks(); localStorage.clear();
  localStorage.setItem('personaapp_language', 'en');
  localStorage.setItem('miraati_mother_journey', JSON.stringify({ id: state.id, token: 'owner' }));
  mockedApi.get.mockResolvedValue({ data: state });
});
test('answers update immediately without requests and survive remount', async () => {
  const view = mount();
  fireEvent.click(await screen.findByRole('button', { name: 'Option A' }));
  expect(screen.getByRole('button', { name: 'Option A' })).toHaveAttribute('aria-pressed', 'true');
  fireEvent.click(screen.getByRole('button', { name: 'Option B' }));
  fireEvent.click(screen.getByRole('button', { name: 'Next' }));
  expect(screen.getByRole('heading', { name: 'Situation 2' })).toBeInTheDocument();
  expect(mockedApi.put).not.toHaveBeenCalled();
  view.unmount(); mount();
  await screen.findByRole('heading', { name: 'Situation 2' });
  fireEvent.click(screen.getByRole('button', { name: 'Back' }));
  expect(screen.getByRole('button', { name: 'Option B' })).toHaveAttribute('aria-pressed', 'true');
  expect(mockedApi.put).not.toHaveBeenCalled();
});
test('submission sends current answers and clears draft after success', async () => {
  mockedApi.put.mockResolvedValue({ data: { ...state, status: 'preview_complete' } });
  mount();
  fireEvent.click(await screen.findByRole('button', { name: 'Option A' }));
  fireEvent.click(screen.getByRole('button', { name: 'Next' }));
  fireEvent.click(screen.getByRole('button', { name: 'I did not encounter a similar situation' }));
  fireEvent.click(screen.getByRole('button', { name: 'See my mirror' }));
  await screen.findByRole('heading', { name: 'You reached the end of this preview' });
  expect(mockedApi.put).toHaveBeenCalledTimes(1);
  expect(mockedApi.put).toHaveBeenCalledWith('/mothers-mirror/journeys/mother-1/assessments/baseline',
    { answers: { s1: 'A', s2: null }, submit: true }, { headers: { 'X-Mother-Owner-Token': 'owner' } });
  expect(localStorage.getItem(pendingKey)).toBeNull();
});
test('failed submission retains draft through retry', async () => {
  localStorage.setItem(pendingKey, JSON.stringify({ id: state.id, payload: { answers: { s1: 'B', s2: 'A' }, submit: false } }));
  mockedApi.put.mockRejectedValue(new Error('offline'));
  mount();
  fireEvent.click(await screen.findByRole('button', { name: 'See my mirror' }));
  await screen.findByRole('alert');
  expect(localStorage.getItem(pendingKey)).not.toBeNull();
  fireEvent.click(screen.getByRole('button', { name: 'Retry saved journey' }));
  await waitFor(() => expect(screen.getByRole('button', { name: 'See my mirror' })).toBeEnabled());
  expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  expect(screen.getByRole('button', { name: 'Option A' })).toHaveAttribute('aria-pressed', 'true');
  expect(mockedApi.put).toHaveBeenCalledTimes(1);
});
