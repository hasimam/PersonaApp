import '@testing-library/jest-dom';
import React from 'react';
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Journey from './Journey';
import { LanguageProvider } from '../i18n/LanguageContext';
import { journeyApi } from '../services/api';

jest.mock('../services/api', () => ({
  journeyApi: {
    startJourney: jest.fn(),
    startPreviewJourney: jest.fn(),
    submitAnswers: jest.fn(),
    submitPreviewAnswers: jest.fn(),
    submitFeedback: jest.fn(),
    cancelJourney: jest.fn(),
    resumeJourney: jest.fn(),
  },
}));

const mockedJourneyApi = journeyApi as jest.Mocked<typeof journeyApi>;
const realConsoleError = console.error;

let consoleErrorSpy: jest.SpyInstance;
const renderJourney = (initialEntry = '/') =>
  render(
    <MemoryRouter initialEntries={[initialEntry]}>
      <LanguageProvider>
        <Journey />
      </LanguageProvider>
    </MemoryRouter>
  );

describe('Journey smoke test', () => {
  beforeEach(() => {
    localStorage.setItem('personaapp_language', 'en');
    consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation((...args: any[]) => {
      const message = args.map((arg) => String(arg)).join(' ');
      if (message.includes('ReactDOMTestUtils.act')) {
        return;
      }
      realConsoleError(...args);
    });

    jest.useFakeTimers();
    mockedJourneyApi.startJourney.mockResolvedValue({
      test_run_id: 99,
      version_id: 'v_test',
      scenarios: [
        {
          scenario_code: 'S01',
          order_index: 1,
          scenario_text_en: 'Scenario 1',
          scenario_text_ar: 'الموقف 1',
          options: [
            { option_code: 'A', option_text_en: 'Option A', option_text_ar: 'الخيار أ' },
            { option_code: 'B', option_text_en: 'Option B', option_text_ar: 'الخيار ب' },
          ],
        },
      ],
    });
    mockedJourneyApi.submitAnswers.mockResolvedValue({
      version_id: 'v_test',
      test_run_id: 99,
      top_genes: [
        {
          gene_code: 'WIS',
          name_en: 'Wisdom',
          name_ar: 'حكمة',
          desc_en: 'Wisdom gene',
          desc_ar: 'جين الحكمة',
          raw_score: 8,
          normalized_score: 100,
          rank: 1,
          role: 'dominant',
        },
        {
          gene_code: 'CRG',
          name_en: 'Courage',
          name_ar: 'شجاعة',
          desc_en: 'Courage gene',
          desc_ar: 'جين الشجاعة',
          raw_score: 6,
          normalized_score: 75,
          rank: 2,
          role: 'secondary',
        },
        {
          gene_code: 'EMP',
          name_en: 'Empathy',
          name_ar: 'تعاطف',
          desc_en: 'Empathy gene',
          desc_ar: 'جين التعاطف',
          raw_score: 4,
          normalized_score: 50,
          rank: 3,
          role: 'support',
        },
      ],
      archetype_matches: [],
      quran_values: [],
      prophet_traits: [],
      activation_items: [
        {
          channel: 'behavior',
          advice_id: 'ACT_BEH',
          advice_type: 'activation',
          title_en: 'Behavior action',
          title_ar: 'سلوك',
          body_en: 'Do one behavior action',
          body_ar: 'قم بسلوك واحد',
          priority: 100,
        },
        {
          channel: 'reflection',
          advice_id: 'ACT_REF',
          advice_type: 'activation',
          title_en: 'Reflection action',
          title_ar: 'تأمل',
          body_en: 'Do one reflection action',
          body_ar: 'قم بتأمل واحد',
          priority: 100,
        },
        {
          channel: 'social',
          advice_id: 'ACT_SOC',
          advice_type: 'activation',
          title_en: 'Social action',
          title_ar: 'اجتماعي',
          body_en: 'Do one social action',
          body_ar: 'قم بفعل اجتماعي',
          priority: 100,
        },
      ],
    });
    mockedJourneyApi.submitFeedback.mockResolvedValue({
      test_run_id: 99,
      accuracy_score: 8,
      personality_match_score: 7,
      selected_activation_id: null,
      status: 'recorded',
    });
    mockedJourneyApi.startPreviewJourney.mockResolvedValue({
      test_run_id: 999,
      version_id: 'v_test',
      scenarios: [],
    });
    mockedJourneyApi.submitPreviewAnswers.mockResolvedValue({
      version_id: 'v_test',
      test_run_id: 999,
      top_genes: [],
      archetype_matches: [],
      quran_values: [],
      prophet_traits: [],
      activation_items: [],
    });
    mockedJourneyApi.resumeJourney.mockRejectedValue(new Error('no saved run'));
    mockedJourneyApi.cancelJourney.mockResolvedValue({
      test_run_id: 99,
      status: 'cancelled',
    });
  });

  afterEach(() => {
    localStorage.removeItem('personaapp_language');
    jest.clearAllMocks();
    consoleErrorSpy.mockRestore();
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  test('completes the happy path from intro to closing', async () => {
    renderJourney();

    fireEvent.click(screen.getByRole('button', { name: 'Start Journey' }));
    fireEvent.click(screen.getByRole('button', { name: 'Begin Scenarios' }));

    await waitFor(() => expect(mockedJourneyApi.startJourney).toHaveBeenCalledTimes(1));
    expect(await screen.findByText('Scenario 1')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Option A' }));
    act(() => {
      jest.advanceTimersByTime(250);
    });

    await waitFor(() => expect(mockedJourneyApi.submitAnswers).toHaveBeenCalledTimes(1));
    expect(await screen.findByText('Your Gene Results')).toBeInTheDocument();
    fireEvent.click(screen.getAllByRole('button', { name: '8' })[0]);
    fireEvent.click(screen.getAllByRole('button', { name: '7' })[1]);
    fireEvent.click(screen.getByRole('button', { name: 'Choose Activation' }));
    await waitFor(() => expect(mockedJourneyApi.submitFeedback).toHaveBeenCalledTimes(1));
    expect(mockedJourneyApi.submitFeedback).toHaveBeenNthCalledWith(1, {
      test_run_id: 99,
      accuracy_score: 8,
      personality_match_score: 7,
    });

    expect(await screen.findByText('Behavior action')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /Behavior action/i }));
    fireEvent.click(screen.getByRole('button', { name: 'Finish Journey' }));

    await waitFor(() => expect(mockedJourneyApi.submitFeedback).toHaveBeenCalledTimes(2));
    expect(mockedJourneyApi.submitFeedback).toHaveBeenNthCalledWith(2, {
      test_run_id: 99,
      selected_activation_id: 'ACT_BEH',
    });
    expect(await screen.findByText('Journey Complete')).toBeInTheDocument();
  });

  test('allows exiting mid-journey and returns to intro', async () => {
    const confirmSpy = jest.spyOn(window, 'confirm').mockReturnValue(true);
    renderJourney('/test');

    fireEvent.click(screen.getByRole('button', { name: 'Start Journey' }));
    fireEvent.click(screen.getByRole('button', { name: 'Begin Scenarios' }));

    await waitFor(() => expect(mockedJourneyApi.startJourney).toHaveBeenCalledTimes(1));
    expect(await screen.findByText('Scenario 1')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /End Journey/i }));

    expect(confirmSpy).toHaveBeenCalledWith(
      'Are you sure you want to end the journey? Your progress will be lost.'
    );
    await waitFor(() => {
      expect(mockedJourneyApi.cancelJourney).toHaveBeenCalledWith({ test_run_id: 99 });
    });
    expect(await screen.findByText('Self-Discovery Journey')).toBeInTheDocument();

    confirmSpy.mockRestore();
  });

  test('does not restart preview run when switching language', async () => {
    mockedJourneyApi.startPreviewJourney.mockResolvedValue({
      test_run_id: 211002,
      version_id: 'v2',
      scenarios: [
        {
          scenario_code: 'D11_01',
          order_index: 1,
          scenario_text_en: 'Preview Scenario 1',
          scenario_text_ar: 'سيناريو المعاينة 1',
          options: [
            { option_code: 'A', option_text_en: 'Option A', option_text_ar: 'الخيار أ' },
            { option_code: 'B', option_text_en: 'Option B', option_text_ar: 'الخيار ب' },
          ],
        },
      ],
    });

    renderJourney('/test?preview=token123');

    await waitFor(() => expect(mockedJourneyApi.startPreviewJourney).toHaveBeenCalledTimes(1));
    expect(await screen.findByText('Preview Scenario 1')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'العربية' }));

    expect(await screen.findByText('سيناريو المعاينة 1')).toBeInTheDocument();
    expect(mockedJourneyApi.startPreviewJourney).toHaveBeenCalledTimes(1);
  });
});
