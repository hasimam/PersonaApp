import '@testing-library/jest-dom';
import React from 'react';
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import Journey from './Journey';
import { LanguageProvider } from '../i18n/LanguageContext';
import { journeyApi } from '../services/api';

jest.mock('../services/api', () => ({
  journeyApi: {
    startJourney: jest.fn(),
    submitAnswers: jest.fn(),
    submitFeedback: jest.fn(),
  },
}));

const mockedJourneyApi = journeyApi as jest.Mocked<typeof journeyApi>;

describe('Journey smoke test', () => {
  beforeEach(() => {
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
      judged_score: 4,
      selected_activation_id: null,
      status: 'recorded',
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  test('completes the happy path from intro to closing', async () => {
    render(
      <LanguageProvider>
        <Journey />
      </LanguageProvider>
    );

    fireEvent.click(screen.getByRole('button', { name: 'Start Journey' }));
    fireEvent.click(screen.getByRole('button', { name: 'Begin Scenarios' }));

    await waitFor(() => expect(mockedJourneyApi.startJourney).toHaveBeenCalledTimes(1));
    expect(await screen.findByText('Scenario 1')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Option A' }));
    act(() => {
      jest.advanceTimersByTime(250);
    });

    expect(await screen.findByText('Psychological Safety Check')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: '4' }));
    fireEvent.click(screen.getByRole('button', { name: 'See My Results' }));

    await waitFor(() => expect(mockedJourneyApi.submitAnswers).toHaveBeenCalledTimes(1));
    expect(await screen.findByText('Your Gene Results')).toBeInTheDocument();
    expect(mockedJourneyApi.submitFeedback).toHaveBeenCalledWith({
      test_run_id: 99,
      judged_score: 4,
    });

    fireEvent.click(screen.getByRole('button', { name: 'Choose Activation' }));
    fireEvent.click(screen.getByRole('button', { name: /Behavior action/i }));
    fireEvent.click(screen.getByRole('button', { name: 'Finish Journey' }));

    await waitFor(() => expect(mockedJourneyApi.submitFeedback).toHaveBeenCalledTimes(2));
    expect(mockedJourneyApi.submitFeedback).toHaveBeenNthCalledWith(2, {
      test_run_id: 99,
      judged_score: 4,
      selected_activation_id: 'ACT_BEH',
    });
    expect(await screen.findByText('Journey Complete')).toBeInTheDocument();
  });
});
