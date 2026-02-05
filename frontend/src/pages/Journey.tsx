import React, { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import LanguageSwitcher from '../components/LanguageSwitcher';
import { useLanguage } from '../i18n/LanguageContext';
import { journeyApi } from '../services/api';
import { JourneyStartResponse, JourneySubmitAnswersResponse } from '../types';

type JourneyStep =
  | 'intro'
  | 'prep'
  | 'scenarios'
  | 'safety'
  | 'loading'
  | 'results'
  | 'activation'
  | 'closing';

const SAFETY_SCORES = [1, 2, 3, 4, 5];
const AUTO_NEXT_DELAY_MS = 180;

const Journey: React.FC = () => {
  const navigate = useNavigate();
  const { t, language } = useLanguage();
  const [step, setStep] = useState<JourneyStep>('intro');
  const [journey, setJourney] = useState<JourneyStartResponse | null>(null);
  const [submitResult, setSubmitResult] = useState<JourneySubmitAnswersResponse | null>(null);
  const [currentScenarioIndex, setCurrentScenarioIndex] = useState(0);
  const [scenarioAnswers, setScenarioAnswers] = useState<Record<string, string>>({});
  const [judgedScore, setJudgedScore] = useState<number | null>(null);
  const [selectedActivationId, setSelectedActivationId] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [isAdvancing, setIsAdvancing] = useState(false);
  const [error, setError] = useState('');

  const scenarios = journey?.scenarios ?? [];
  const currentScenario = scenarios[currentScenarioIndex];

  const activationItems = useMemo(
    () => (submitResult?.activation_items ?? []).slice(0, 3),
    [submitResult]
  );

  const localizeText = (en: string, ar: string | null): string => {
    if (language === 'ar' && ar) {
      return ar;
    }
    return en;
  };

  const resetFlow = () => {
    setJourney(null);
    setSubmitResult(null);
    setCurrentScenarioIndex(0);
    setScenarioAnswers({});
    setJudgedScore(null);
    setSelectedActivationId(null);
    setBusy(false);
    setIsAdvancing(false);
    setError('');
    setStep('intro');
  };

  const startJourney = async () => {
    setBusy(true);
    setError('');
    try {
      const data = await journeyApi.startJourney();
      setJourney(data);
      setCurrentScenarioIndex(0);
      setScenarioAnswers({});
      setJudgedScore(null);
      setSelectedActivationId(null);
      setIsAdvancing(false);
      setStep('scenarios');
    } catch (e) {
      setError(t.journey.startError);
    } finally {
      setBusy(false);
    }
  };

  const handleScenarioAnswer = (optionCode: string) => {
    if (!currentScenario || isAdvancing) {
      return;
    }

    setIsAdvancing(true);
    setError('');
    setScenarioAnswers((previous) => ({
      ...previous,
      [currentScenario.scenario_code]: optionCode,
    }));

    if (currentScenarioIndex >= scenarios.length - 1) {
      window.setTimeout(() => {
        setIsAdvancing(false);
        setStep('safety');
      }, AUTO_NEXT_DELAY_MS);
      return;
    }

    window.setTimeout(() => {
      setIsAdvancing(false);
      setCurrentScenarioIndex((value) => value + 1);
    }, AUTO_NEXT_DELAY_MS);
  };

  const submitJourney = async () => {
    if (!journey || !judgedScore) {
      return;
    }

    if (Object.keys(scenarioAnswers).length !== journey.scenarios.length) {
      setError(t.journey.answerAllScenarios);
      setStep('scenarios');
      return;
    }

    setError('');
    setStep('loading');
    try {
      const response = await journeyApi.submitAnswers({
        version_id: journey.version_id,
        test_run_id: journey.test_run_id,
        answers: journey.scenarios.map((scenario) => ({
          scenario_code: scenario.scenario_code,
          option_code: scenarioAnswers[scenario.scenario_code],
        })),
      });

      setSubmitResult(response);

      try {
        await journeyApi.submitFeedback({
          test_run_id: journey.test_run_id,
          judged_score: judgedScore,
        });
      } catch (e) {
        // Non-blocking, user should still receive results.
      }

      setStep('results');
    } catch (e) {
      setError(t.journey.submitError);
      setStep('safety');
    }
  };

  const finalizeActivation = async () => {
    if (!journey || !judgedScore) {
      setStep('closing');
      return;
    }

    if (!selectedActivationId) {
      setError(t.journey.selectActivationPrompt);
      return;
    }

    setBusy(true);
    setError('');
    try {
      await journeyApi.submitFeedback({
        test_run_id: journey.test_run_id,
        judged_score: judgedScore,
        selected_activation_id: selectedActivationId,
      });
      setStep('closing');
    } catch (e) {
      setError(t.journey.activationSaveError);
    } finally {
      setBusy(false);
    }
  };

  const handleExit = async () => {
    if (!window.confirm(t.journey.exitConfirm)) {
      return;
    }

    if (journey?.test_run_id) {
      try {
        await journeyApi.cancelJourney({ test_run_id: journey.test_run_id });
      } catch (e) {
        // Non-blocking: user should still be able to leave the flow.
      }
    }

    resetFlow();
    navigate('/');
  };

  const canExitJourney = step !== 'intro' && step !== 'closing';

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-primary-100 px-4 py-8 relative">
      {canExitJourney && (
        <div className="absolute top-4 left-4 z-10">
          <button
            onClick={() => {
              void handleExit();
            }}
            className="text-gray-500 hover:text-gray-700 text-sm flex items-center gap-1"
          >
            <span>&larr;</span> {t.journey.exitJourney}
          </button>
        </div>
      )}

      <div className="absolute top-4 right-4 z-10">
        <LanguageSwitcher />
      </div>

      <div className="max-w-3xl mx-auto mt-10">
        {(step === 'intro' || step === 'prep' || step === 'closing') && (
          <div className="card text-center space-y-6">
            {step === 'intro' && (
              <>
                <h1 className="text-4xl font-bold text-gray-900">{t.journey.introTitle}</h1>
                <p className="text-lg text-gray-700">{t.journey.introSubtitle}</p>
                <button className="btn-primary" onClick={() => setStep('prep')}>
                  {t.journey.introCta}
                </button>
              </>
            )}

            {step === 'prep' && (
              <>
                <h2 className="text-3xl font-semibold text-gray-900">{t.journey.prepTitle}</h2>
                <ul
                  className={`${language === 'ar' ? 'text-right' : 'text-left'} text-gray-700 space-y-2 max-w-xl mx-auto`}
                >
                  <li>- {t.journey.prepPointOne}</li>
                  <li>- {t.journey.prepPointTwo}</li>
                  <li>- {t.journey.prepPointThree}</li>
                </ul>
                <div className="flex justify-center gap-3">
                  <button className="btn-secondary" onClick={() => setStep('intro')}>
                    {t.journey.back}
                  </button>
                  <button className="btn-primary" onClick={startJourney} disabled={busy}>
                    {busy ? t.journey.starting : t.journey.beginScenarios}
                  </button>
                </div>
              </>
            )}

            {step === 'closing' && (
              <>
                <h2 className="text-3xl font-semibold text-gray-900">{t.journey.closingTitle}</h2>
                <p className="text-gray-700">{t.journey.closingBody}</p>
                <button className="btn-primary" onClick={resetFlow}>
                  {t.journey.restart}
                </button>
              </>
            )}
          </div>
        )}

        {step === 'scenarios' && currentScenario && (
          <div className="card space-y-6">
            <div>
              <div className="flex justify-between text-sm text-gray-600 mb-2">
                <span>{t.journey.scenarioProgress}</span>
                <span>
                  {currentScenarioIndex + 1} / {scenarios.length}
                </span>
              </div>
              <div className="w-full bg-gray-200 h-2 rounded-full">
                <div
                  className="bg-primary-600 h-2 rounded-full transition-all"
                  style={{ width: `${((currentScenarioIndex + 1) / scenarios.length) * 100}%` }}
                />
              </div>
            </div>

            <h2 className="text-2xl font-semibold text-gray-900 text-center">
              {localizeText(currentScenario.scenario_text_en, currentScenario.scenario_text_ar)}
            </h2>

            <div className="grid grid-cols-1 gap-3">
              {currentScenario.options.map((option) => {
                const isSelected =
                  scenarioAnswers[currentScenario.scenario_code] === option.option_code;
                return (
                  <button
                    key={option.option_code}
                    onClick={() => handleScenarioAnswer(option.option_code)}
                    disabled={isAdvancing}
                    className={`w-full ${language === 'ar' ? 'text-right' : 'text-left'} rounded-lg border-2 p-4 transition-colors ${
                      isSelected
                        ? 'border-primary-600 bg-primary-50'
                        : 'border-gray-200 hover:border-primary-400'
                    }`}
                  >
                    {localizeText(option.option_text_en, option.option_text_ar)}
                  </button>
                );
              })}
            </div>

            <p className="text-sm text-gray-600 text-center">{t.journey.autoNextHint}</p>
          </div>
        )}

        {step === 'safety' && (
          <div className="card text-center space-y-6">
            <h2 className="text-2xl font-semibold text-gray-900">{t.journey.safetyTitle}</h2>
            <p className="text-gray-700">{t.journey.safetySubtitle}</p>

            <div className="grid grid-cols-5 gap-2 max-w-md mx-auto">
              {SAFETY_SCORES.map((score) => (
                <button
                  key={score}
                  onClick={() => {
                    setJudgedScore(score);
                    setError('');
                  }}
                  className={`rounded-lg border-2 py-3 font-semibold ${
                    judgedScore === score
                      ? 'border-primary-600 bg-primary-600 text-white'
                      : 'border-gray-200 hover:border-primary-300'
                  }`}
                >
                  {score}
                </button>
              ))}
            </div>

            <p className="text-sm text-gray-600">{t.journey.safetyScaleHint}</p>

            <button
              className="btn-primary"
              onClick={submitJourney}
              disabled={!judgedScore}
            >
              {t.journey.seeResults}
            </button>
          </div>
        )}

        {step === 'loading' && (
          <div className="card text-center py-16">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-600 mx-auto mb-4" />
            <p className="text-gray-700">{t.journey.loading}</p>
          </div>
        )}

        {step === 'results' && submitResult && (
          <div className="space-y-6">
            <div className="card">
              <h2 className="text-3xl font-semibold text-gray-900 mb-4">{t.journey.resultsTitle}</h2>
              <p className="text-gray-700 mb-6">{t.journey.resultsSubtitle}</p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {submitResult.top_genes.slice(0, 3).map((gene) => (
                  <div key={gene.gene_code} className="rounded-lg border border-gray-200 p-4">
                    <p className="text-xs uppercase tracking-wide text-primary-700 mb-1">
                      {t.journey.geneRoles[gene.role as 'dominant' | 'secondary' | 'support'] ?? gene.role}
                    </p>
                    <h3 className="text-lg font-semibold text-gray-900">
                      {localizeText(gene.name_en, gene.name_ar)}
                    </h3>
                    <p className="text-sm text-gray-600 mt-2">
                      {localizeText(gene.desc_en, gene.desc_ar)}
                    </p>
                    <p className="text-sm font-semibold text-primary-700 mt-3">
                      {gene.normalized_score.toFixed(2)}%
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {submitResult.archetype_matches.length > 0 && (
              <div className="card">
                <h3 className="text-2xl font-semibold text-gray-900 mb-4">{t.journey.archetypesTitle}</h3>
                <div className="space-y-3">
                  {submitResult.archetype_matches.map((match) => (
                    <div key={match.model_code} className="rounded-lg border border-gray-200 p-4">
                      <div className="flex justify-between gap-3">
                        <h4 className="font-semibold text-gray-900">
                          {localizeText(match.name_en, match.name_ar)}
                        </h4>
                        <span className="text-sm text-primary-700 font-semibold">
                          {(match.similarity * 100).toFixed(1)}%
                        </span>
                      </div>
                      {match.summary_ar && language === 'ar' && (
                        <p className="text-sm text-gray-700 mt-2">{match.summary_ar}</p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="flex justify-center">
              <button className="btn-primary" onClick={() => setStep('activation')}>
                {t.journey.toActivation}
              </button>
            </div>
          </div>
        )}

        {step === 'activation' && submitResult && (
          <div className="card space-y-6">
            <div>
              <h2 className="text-3xl font-semibold text-gray-900 mb-2">{t.journey.activationTitle}</h2>
              <p className="text-gray-700">{t.journey.activationSubtitle}</p>
            </div>

            <div className="space-y-3">
              {activationItems.map((item) => {
                const isSelected = selectedActivationId === item.advice_id;
                return (
                  <button
                    key={item.advice_id}
                    onClick={() => {
                      setSelectedActivationId(item.advice_id);
                      setError('');
                    }}
                    className={`w-full ${language === 'ar' ? 'text-right' : 'text-left'} rounded-lg border-2 p-4 transition-colors ${
                      isSelected
                        ? 'border-primary-600 bg-primary-50'
                        : 'border-gray-200 hover:border-primary-400'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="text-xs uppercase tracking-wide text-primary-700 mb-1">
                          {t.journey.channels[item.channel as 'behavior' | 'reflection' | 'social'] ?? item.channel}
                        </p>
                        <h3 className="text-lg font-semibold text-gray-900">
                          {localizeText(item.title_en, item.title_ar)}
                        </h3>
                        <p className="text-sm text-gray-700 mt-1">
                          {localizeText(item.body_en, item.body_ar)}
                        </p>
                      </div>
                      {isSelected && (
                        <span className="text-primary-700 font-semibold text-sm">{t.journey.selected}</span>
                      )}
                    </div>
                  </button>
                );
              })}
            </div>

            <div className="flex justify-center">
              <button className="btn-primary" onClick={finalizeActivation} disabled={busy}>
                {busy ? t.journey.saving : t.journey.finish}
              </button>
            </div>
          </div>
        )}

        {error && (
          <div className="mt-4 p-4 border border-red-200 bg-red-50 text-red-700 rounded-lg text-center">
            {error}
          </div>
        )}
      </div>
    </div>
  );
};

export default Journey;
