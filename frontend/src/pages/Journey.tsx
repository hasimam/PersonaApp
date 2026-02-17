import React, { useEffect, useMemo, useRef, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import LanguageSwitcher from '../components/LanguageSwitcher';
import { useLanguage } from '../i18n/LanguageContext';
import { journeyApi } from '../services/api';
import { JourneyStartResponse, JourneySubmitAnswersResponse, JourneyType } from '../types';
import logo from '../assets/logo.png';
import decoImageOne from '../assets/deco-image-1.png';
import decoImageTwo from '../assets/deco-image-2.png';
import quickIcon from '../assets/icon-1.png';
import deepIcon from '../assets/icon-2.png';
import resultsIconOne from '../assets/icon-3.png';
import resultsIconTwo from '../assets/icon-4.png';
import resultsIconThree from '../assets/icon-5.png';
import resultsIconFour from '../assets/icon-6.png';
import activationIcon from '../assets/icon-7.png';

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
const RESULT_RATING_SCORES = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
const AUTO_NEXT_DELAY_MS = 180;
const RESUME_STORAGE_KEY = 'journey_resume_v1';
const RESUME_TTL_MS = 24 * 60 * 60 * 1000;
const SHOW_SAFETY_STEP = false;
const DEFAULT_JUDGED_SCORE = 3;

type StoredJourneyState = {
  test_run_id: number;
  version_id: string;
  journey_type: JourneyType;
  step: JourneyStep;
  currentScenarioIndex: number;
  scenarioAnswers: Record<string, string>;
  judgedScore: number | null;
  selectedActivationId: string | null;
  saved_at: number;
};

const loadStoredJourney = (): StoredJourneyState | null => {
  try {
    const raw = window.localStorage.getItem(RESUME_STORAGE_KEY);
    if (!raw) {
      return null;
    }
    return JSON.parse(raw) as StoredJourneyState;
  } catch {
    return null;
  }
};

const saveStoredJourney = (state: StoredJourneyState) => {
  window.localStorage.setItem(RESUME_STORAGE_KEY, JSON.stringify(state));
};

const clearStoredJourney = () => {
  window.localStorage.removeItem(RESUME_STORAGE_KEY);
};

const Journey: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { t, language } = useLanguage();
  const [step, setStep] = useState<JourneyStep>('intro');
  const [journey, setJourney] = useState<JourneyStartResponse | null>(null);
  const [submitResult, setSubmitResult] = useState<JourneySubmitAnswersResponse | null>(null);
  const [currentScenarioIndex, setCurrentScenarioIndex] = useState(0);
  const [scenarioAnswers, setScenarioAnswers] = useState<Record<string, string>>({});
  const [judgedScore, setJudgedScore] = useState<number | null>(null);
  const [accuracyScore, setAccuracyScore] = useState<number | null>(null);
  const [personalityMatchScore, setPersonalityMatchScore] = useState<number | null>(null);
  const [selectedActivationId, setSelectedActivationId] = useState<string | null>(null);
  const [journeyType, setJourneyType] = useState<JourneyType>('quick');
  const [busy, setBusy] = useState(false);
  const [isAdvancing, setIsAdvancing] = useState(false);
  const [error, setError] = useState('');
  const startedPreviewTokenRef = useRef<string | null>(null);
  const previewToken = useMemo(() => {
    const token = new URLSearchParams(location.search).get('preview');
    return token ? token.trim() : '';
  }, [location.search]);
  const isPreviewMode = previewToken.length > 0;

  useEffect(() => {
    if (step === 'intro') {
      setError('');
    }
  }, [step]);

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
    setAccuracyScore(null);
    setPersonalityMatchScore(null);
    setSelectedActivationId(null);
    setJourneyType('quick');
    setBusy(false);
    setIsAdvancing(false);
    setError('');
    setStep('intro');
    clearStoredJourney();
  };

  useEffect(() => {
    if (isPreviewMode) {
      return;
    }
    const stored = loadStoredJourney();
    if (!stored) {
      return;
    }
    const now = Date.now();
    if (now - stored.saved_at > RESUME_TTL_MS) {
      clearStoredJourney();
      return;
    }
    if (!['scenarios', 'safety'].includes(stored.step)) {
      clearStoredJourney();
      return;
    }
    setBusy(true);
    setError('');
    journeyApi
      .resumeJourney({ test_run_id: stored.test_run_id })
      .then((data) => {
        const resumeStep =
          stored.step === 'safety' && !SHOW_SAFETY_STEP ? 'scenarios' : stored.step;
        const resumeScore = SHOW_SAFETY_STEP
          ? stored.judgedScore ?? null
          : stored.judgedScore ?? DEFAULT_JUDGED_SCORE;
        setJourneyType(stored.journey_type ?? 'quick');
        setJourney(data);
        setScenarioAnswers(stored.scenarioAnswers ?? {});
        setCurrentScenarioIndex(
          Math.min(stored.currentScenarioIndex ?? 0, Math.max(data.scenarios.length - 1, 0))
        );
        setJudgedScore(resumeScore);
        setAccuracyScore(null);
        setPersonalityMatchScore(null);
        setSelectedActivationId(stored.selectedActivationId ?? null);
        setSubmitResult(null);
        setIsAdvancing(false);
        setStep(resumeStep);
      })
      .catch(() => {
        clearStoredJourney();
      })
      .finally(() => {
        setBusy(false);
      });
  }, [isPreviewMode]);

  useEffect(() => {
    if (!isPreviewMode) {
      startedPreviewTokenRef.current = null;
      return;
    }
    if (startedPreviewTokenRef.current === previewToken && journey) {
      return;
    }
    startedPreviewTokenRef.current = previewToken;
    clearStoredJourney();
    setBusy(true);
    setError('');
    journeyApi
      .startPreviewJourney({ preview_token: previewToken })
      .then((data) => {
        setJourneyType(data.version_id.startsWith('v2') ? 'deep' : 'quick');
        setJourney(data);
        setCurrentScenarioIndex(0);
        setScenarioAnswers({});
        setJudgedScore(DEFAULT_JUDGED_SCORE);
        setAccuracyScore(null);
        setPersonalityMatchScore(null);
        setSelectedActivationId(null);
        setSubmitResult(null);
        setIsAdvancing(false);
        setStep('scenarios');
      })
      .catch(() => {
        startedPreviewTokenRef.current = null;
        // Fallback to the regular production journey when preview token is invalid/expired.
        const params = new URLSearchParams(location.search);
        params.delete('preview');
        const nextSearch = params.toString();
        navigate(
          {
            pathname: location.pathname,
            search: nextSearch ? `?${nextSearch}` : '',
          },
          { replace: true }
        );
      })
      .finally(() => {
        setBusy(false);
      });
  }, [isPreviewMode, previewToken, journey, location.pathname, location.search, navigate]);

  useEffect(() => {
    if (!journey) {
      return;
    }
    if (isPreviewMode) {
      return;
    }
    if (
      step === 'intro' ||
      step === 'prep' ||
      step === 'loading' ||
      step === 'results' ||
      step === 'activation' ||
      step === 'closing'
    ) {
      return;
    }
    saveStoredJourney({
      test_run_id: journey.test_run_id,
      version_id: journey.version_id,
      journey_type: journeyType,
      step,
      currentScenarioIndex,
      scenarioAnswers,
      judgedScore,
      selectedActivationId,
      saved_at: Date.now(),
    });
  }, [
    journey,
    journeyType,
    step,
    currentScenarioIndex,
    scenarioAnswers,
    judgedScore,
    selectedActivationId,
    isPreviewMode,
  ]);

  const startJourney = async () => {
    setBusy(true);
    setError('');
    try {
      const data = isPreviewMode
        ? await journeyApi.startPreviewJourney({ preview_token: previewToken })
        : await journeyApi.startJourney({ journey_type: journeyType });
      setJourney(data);
      setCurrentScenarioIndex(0);
      setScenarioAnswers({});
      setJudgedScore(SHOW_SAFETY_STEP ? null : DEFAULT_JUDGED_SCORE);
      setAccuracyScore(null);
      setPersonalityMatchScore(null);
      setSelectedActivationId(null);
      setIsAdvancing(false);
      setStep('scenarios');
    } catch (e) {
      setError(t.journey.startError);
    } finally {
      setBusy(false);
    }
  };

  const submitJourneyWithAnswers = async (answersMap: Record<string, string>) => {
    if (!journey) {
      return;
    }

    if (SHOW_SAFETY_STEP && !judgedScore) {
      return;
    }

    if (Object.keys(answersMap).length !== journey.scenarios.length) {
      setError(t.journey.answerAllScenarios);
      setStep('scenarios');
      return;
    }

    setError('');
    setStep('loading');
    try {
      const response = isPreviewMode
        ? await journeyApi.submitPreviewAnswers({
            preview_token: previewToken,
            answers: journey.scenarios.map((scenario) => ({
              scenario_code: scenario.scenario_code,
              option_code: answersMap[scenario.scenario_code],
            })),
          })
        : await journeyApi.submitAnswers({
            version_id: journey.version_id,
            test_run_id: journey.test_run_id,
            answers: journey.scenarios.map((scenario) => ({
              scenario_code: scenario.scenario_code,
              option_code: answersMap[scenario.scenario_code],
            })),
          });

      setSubmitResult(response);
      clearStoredJourney();

      setStep('results');
    } catch (e) {
      setError(t.journey.submitError);
      setStep(SHOW_SAFETY_STEP ? 'safety' : 'scenarios');
    }
  };

  const handleScenarioAnswer = (optionCode: string) => {
    if (!currentScenario || isAdvancing) {
      return;
    }

    setIsAdvancing(true);
    setError('');
    const nextAnswers = {
      ...scenarioAnswers,
      [currentScenario.scenario_code]: optionCode,
    };
    setScenarioAnswers(nextAnswers);

    if (currentScenarioIndex >= scenarios.length - 1) {
      window.setTimeout(() => {
        setIsAdvancing(false);
        if (SHOW_SAFETY_STEP) {
          setStep('safety');
          return;
        }
        if (!judgedScore) {
          setJudgedScore(DEFAULT_JUDGED_SCORE);
        }
        void submitJourneyWithAnswers(nextAnswers);
      }, AUTO_NEXT_DELAY_MS);
      return;
    }

    window.setTimeout(() => {
      setIsAdvancing(false);
      setCurrentScenarioIndex((value) => value + 1);
    }, AUTO_NEXT_DELAY_MS);
  };

  const submitJourney = async () => {
    await submitJourneyWithAnswers(scenarioAnswers);
  };

  const moveToActivation = async () => {
    if (!journey || !accuracyScore || !personalityMatchScore) {
      setError(t.journey.resultsFeedbackRequired);
      return;
    }

    if (isPreviewMode) {
      setError('');
      setStep('activation');
      return;
    }

    setBusy(true);
    setError('');
    try {
      await journeyApi.submitFeedback({
        test_run_id: journey.test_run_id,
        accuracy_score: accuracyScore,
        personality_match_score: personalityMatchScore,
      });
      setStep('activation');
    } catch (e) {
      setError(t.journey.resultsFeedbackSaveError);
    } finally {
      setBusy(false);
    }
  };

  const finalizeActivation = async () => {
    if (!journey || isPreviewMode) {
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
        selected_activation_id: selectedActivationId,
      });
      clearStoredJourney();
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

    if (journey?.test_run_id && !isPreviewMode) {
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
  const resultRatingOrder = language === 'ar' ? [...RESULT_RATING_SCORES].reverse() : RESULT_RATING_SCORES;
  const isResultsFeedbackComplete = accuracyScore !== null && personalityMatchScore !== null;

  const isIntroView = step === 'intro';
  const iconMap: Record<JourneyType, string> = {
    quick: quickIcon,
    deep: deepIcon,
  };

  return (
    <div className="relative min-h-screen overflow-hidden bg-cream text-ink">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top,_rgba(197,168,128,0.18)_0%,_rgba(246,241,234,0)_60%)]" />
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_bottom,_rgba(58,80,107,0.08)_0%,_rgba(246,241,234,0)_70%)]" />
      <div className="pointer-events-none absolute inset-0 opacity-[0.35] [background-image:radial-gradient(rgba(58,80,107,0.06)_1px,transparent_1px)] [background-size:28px_28px]" />

      {isIntroView && (
        <>
          <div className="pointer-events-none absolute left-6 top-20 hidden md:block">
            <div className="h-[360px] w-[300px] overflow-hidden">
              <img
                src={decoImageOne}
                alt=""
                aria-hidden="true"
                className="h-full w-full object-cover object-[45%_0%] opacity-70"
              />
            </div>
          </div>
          <div className="pointer-events-none absolute bottom-0 right-0 hidden sm:block">
            <div className="h-[280px] w-[240px] overflow-hidden">
              <img
                src={decoImageTwo}
                alt=""
                aria-hidden="true"
                className="h-full w-full object-cover object-[70%_100%] opacity-75"
              />
            </div>
          </div>
        </>
      )}
      {canExitJourney && (
        <div className="absolute top-4 left-4 z-20">
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

      <div className="absolute top-4 right-4 z-20 sm:right-8 sm:top-6">
        <LanguageSwitcher className="border border-sand/70 shadow-soft-card backdrop-blur-sm" />
      </div>

      <div
        className="relative z-10 mx-auto w-full max-w-5xl px-4 pb-16 pt-24 sm:px-6 sm:pt-24 md:pt-28 lg:px-8 lg:pt-32"
      >
        {step === 'intro' && (
          <div className="text-center">
            <div className="relative">
              <img
                src={logo}
                alt="PersonaApp logo"
                className="mx-auto h-40 w-auto object-contain md:h-60 lg:h-80"
              />
              <h1 className="mt-5 text-3xl font-semibold tracking-tight text-ink sm:text-4xl lg:text-5xl">
                {t.journey.introTitle}
              </h1>
              <p className="mx-auto mt-4 max-w-2xl text-sm leading-relaxed text-muted sm:text-base lg:text-lg">
                {t.journey.introSubtitle}
              </p>
            </div>

            <div className="mt-8 flex flex-col items-center sm:mt-10">
              <div className="flex items-center gap-3 text-accent/70">
                <span className="h-px w-16 bg-accent/40" />
                <span className="h-2 w-2 rotate-45 bg-accent/60" />
                <span className="h-px w-16 bg-accent/40" />
              </div>
              <p className="mt-3 text-sm font-medium text-primary/80 sm:text-base">
                {t.journey.typeLabel}
              </p>
            </div>

            <div className="mt-8 grid grid-cols-1 gap-5 md:grid-cols-2 md:gap-6">
              {(['quick', 'deep'] as const).map((type) => {
                const isSelected = journeyType === type;
                return (
                  <div
                    key={type}
                    role="button"
                    tabIndex={0}
                    aria-pressed={isSelected}
                    onClick={() => setJourneyType(type)}
                    onKeyDown={(event) => {
                      if (event.key === 'Enter' || event.key === ' ') {
                        event.preventDefault();
                        setJourneyType(type);
                      }
                    }}
                    className={`flex min-h-[220px] flex-col rounded-soft border px-6 py-6 text-start shadow-soft-card backdrop-blur-sm transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-cream sm:min-h-[240px] ${
                      isSelected
                        ? 'border-accent/80 bg-white shadow-soft-float'
                        : 'border-sand/80 bg-white/70 hover:border-accent/60'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <span className="flex h-10 w-10 items-center justify-center rounded-full border border-sand/70 bg-[#F0EBE5]">
                        <img
                          src={iconMap[type]}
                          alt=""
                          aria-hidden="true"
                          className="h-6 w-6 object-contain"
                        />
                      </span>
                      <h3 className="text-lg font-semibold text-ink sm:text-xl">
                        {t.journey.typeLabels[type]}
                      </h3>
                    </div>
                    <p className="mt-3 text-sm leading-relaxed text-muted sm:text-base">
                      {t.journey.typeDescriptions[type]}
                    </p>
                    {isSelected && (
                      <div className="mt-auto pt-6">
                        <div className="mb-4 flex items-center justify-center gap-2 text-accent/70">
                          <span className="h-px w-10 bg-accent/40" />
                          <span className="h-2 w-2 rotate-45 bg-accent/60" />
                          <span className="h-px w-10 bg-accent/40" />
                        </div>
                        <button
                          onClick={(event) => {
                            event.stopPropagation();
                            setStep('prep');
                          }}
                          className="mx-auto flex h-11 min-w-[200px] items-center justify-center rounded-full bg-primary px-6 pt-0.5 text-base font-semibold leading-none text-white shadow-[0_12px_24px_rgba(58,80,107,0.18)] transition duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-cream sm:h-12 sm:text-lg lg:hover:-translate-y-0.5 lg:hover:bg-[#31465E]"
                        >
                          {t.journey.introCta}
                        </button>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {(step === 'prep' || step === 'closing') && (
          <div className="mx-auto max-w-3xl space-y-6 rounded-soft border border-accent/80 bg-white/70 px-6 py-6 text-center shadow-soft-card backdrop-blur-sm">
            {step === 'prep' && (
              <>
                <h2 className="text-3xl font-semibold text-ink">{t.journey.prepTitle}</h2>
                <ul
                  className={`${language === 'ar' ? 'text-right' : 'text-left'} text-muted space-y-2 max-w-xl mx-auto`}
                >
                  <li>- {t.journey.prepPointOne}</li>
                  <li>- {t.journey.prepPointTwo}</li>
                  <li>- {t.journey.prepPointThree}</li>
                </ul>
                <div className="flex justify-center gap-3">
                  <button
                    onClick={() => setStep('intro')}
                    className="flex h-11 items-center justify-center rounded-full border border-sand/80 bg-white/60 px-6 pt-0.5 text-base font-semibold leading-none text-ink shadow-soft-card backdrop-blur-sm transition duration-200 hover:bg-white/80 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-cream sm:h-12 sm:text-lg"
                  >
                    {t.journey.back}
                  </button>
                  <button
                    onClick={startJourney}
                    disabled={busy}
                    className="flex h-11 min-w-[200px] items-center justify-center rounded-full bg-primary px-6 pt-0.5 text-base font-semibold leading-none text-white shadow-[0_12px_24px_rgba(58,80,107,0.18)] transition duration-200 hover:bg-[#31465E] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-cream disabled:cursor-not-allowed disabled:opacity-60 sm:h-12 sm:text-lg"
                  >
                    {busy ? t.journey.starting : t.journey.beginScenarios}
                  </button>
                </div>
              </>
            )}

            {step === 'closing' && (
              <>
                <h2 className="text-3xl font-semibold text-ink">{t.journey.closingTitle}</h2>
                <p className="text-muted">{t.journey.closingBody}</p>
                <button
                  className="mx-auto flex h-11 min-w-[200px] items-center justify-center rounded-full bg-primary px-6 pt-0.5 text-base font-semibold leading-none text-white shadow-[0_12px_24px_rgba(58,80,107,0.18)] transition duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-cream sm:h-12 sm:text-lg lg:hover:-translate-y-0.5 lg:hover:bg-[#31465E]"
                  onClick={resetFlow}
                  type="button"
                >
                  {t.journey.restart}
                </button>
              </>
            )}
          </div>
        )}

        {step === 'scenarios' && currentScenario && (
          <div className="mx-auto max-w-3xl space-y-6 rounded-soft border border-accent/80 bg-white/70 px-6 py-6 text-center shadow-soft-card backdrop-blur-sm">
            <div>
              <div
                className={`mb-3 flex justify-between text-sm text-muted ${
                  language === 'ar' ? 'text-right' : 'text-left'
                }`}
              >
                <span>{t.journey.scenarioProgress}</span>
                <span>
                  {currentScenarioIndex + 1} / {scenarios.length}
                </span>
              </div>
              <div className="h-2 w-full overflow-hidden rounded-full bg-sand/60">
                <div
                  className="h-2 rounded-full bg-primary transition-all"
                  style={{ width: `${((currentScenarioIndex + 1) / scenarios.length) * 100}%` }}
                />
              </div>
            </div>

            <h2 className="text-2xl font-semibold text-ink">
              {localizeText(currentScenario.scenario_text_en, currentScenario.scenario_text_ar)}
            </h2>

            <div className="grid grid-cols-1 gap-3">
              {currentScenario.options.map((option) => {
                const isSelected =
                  scenarioAnswers[currentScenario.scenario_code] === option.option_code;
                return (
                  <button
                    key={option.option_code}
                    type="button"
                    aria-pressed={isSelected}
                    onClick={() => handleScenarioAnswer(option.option_code)}
                    disabled={isAdvancing}
                    className={`w-full rounded-soft border px-5 py-4 text-sm font-medium leading-relaxed text-ink shadow-soft-card backdrop-blur-sm transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-cream disabled:cursor-not-allowed disabled:opacity-60 sm:text-base ${
                      language === 'ar' ? 'text-right' : 'text-left'
                    } ${
                      isSelected
                        ? 'border-accent/80 bg-white shadow-soft-float'
                        : 'border-sand/80 bg-white/60 hover:border-accent/60 hover:bg-white/75'
                    }`}
                  >
                    {localizeText(option.option_text_en, option.option_text_ar)}
                  </button>
                );
              })}
            </div>

            <p className="text-sm text-muted">{t.journey.autoNextHint}</p>
          </div>
        )}

        {step === 'safety' && SHOW_SAFETY_STEP && (
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
          <div className="mx-auto max-w-4xl space-y-6">
            <div className="space-y-4 rounded-soft border border-accent/80 bg-white/70 px-6 py-6 shadow-soft-card backdrop-blur-sm">
              <div className="flex items-center gap-3">
                <span className="flex h-10 w-10 items-center justify-center rounded-full border border-sand/70 bg-[#F0EBE5]">
                  <img
                    src={resultsIconOne}
                    alt=""
                    aria-hidden="true"
                    className="h-6 w-6 object-contain"
                  />
                </span>
                <h2 className="text-3xl font-semibold text-ink">{t.journey.resultsTitle}</h2>
              </div>
              <p className="text-muted">{t.journey.resultsSubtitle}</p>
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                {submitResult.top_genes.map((gene) => (
                  <div
                    key={gene.gene_code}
                    className="rounded-soft border border-sand/80 bg-white/60 p-4 shadow-soft-card backdrop-blur-sm"
                  >
                    <p className="mb-1 text-xs uppercase tracking-wide text-primary/80">
                      {gene.role
                        ? t.journey.geneRoles[gene.role as 'dominant' | 'secondary' | 'support'] ?? gene.role
                        : `${t.journey.geneRankLabel} ${gene.rank}`}
                    </p>
                    <h3 className="text-lg font-semibold text-ink">
                      {localizeText(gene.name_en, gene.name_ar)}
                    </h3>
                    <p className="mt-2 text-sm leading-relaxed text-muted">
                      {localizeText(gene.desc_en, gene.desc_ar)}
                    </p>
                    <p className="mt-3 text-sm font-semibold text-primary/90">
                      {gene.normalized_score.toFixed(2)}%
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {submitResult.archetype_matches.length > 0 && (
              <div className="space-y-4 rounded-soft border border-accent/80 bg-white/70 px-6 py-6 shadow-soft-card backdrop-blur-sm">
                <div className="flex items-center gap-3">
                  <span className="flex h-10 w-10 items-center justify-center rounded-full border border-sand/70 bg-[#F0EBE5]">
                    <img
                      src={resultsIconTwo}
                      alt=""
                      aria-hidden="true"
                      className="h-6 w-6 object-contain"
                    />
                  </span>
                  <h3 className="text-2xl font-semibold text-ink">{t.journey.archetypesTitle}</h3>
                </div>
                <div className="space-y-3">
                  {submitResult.archetype_matches.map((match) => (
                    <div
                      key={match.model_code}
                      className="rounded-soft border border-sand/80 bg-white/60 p-4 shadow-soft-card backdrop-blur-sm"
                    >
                      <div className="flex justify-between gap-3">
                        <h4 className="font-semibold text-ink">
                          {localizeText(match.name_en, match.name_ar)}
                        </h4>
                        <span className="text-sm font-semibold text-primary/90">
                          {(match.similarity * 100).toFixed(1)}%
                        </span>
                      </div>
                      {match.summary_ar && language === 'ar' && (
                        <p className="mt-2 text-sm leading-relaxed text-ink">{match.summary_ar}</p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {submitResult.quran_values.length > 0 && (
              <div className="space-y-4 rounded-soft border border-accent/80 bg-white/70 px-6 py-6 shadow-soft-card backdrop-blur-sm">
                <div className="flex items-center gap-3">
                  <span className="flex h-10 w-10 items-center justify-center rounded-full border border-sand/70 bg-[#F0EBE5]">
                    <img
                      src={resultsIconThree}
                      alt=""
                      aria-hidden="true"
                      className="h-6 w-6 object-contain"
                    />
                  </span>
                  <h3 className="text-2xl font-semibold text-ink">{t.journey.quranValuesTitle}</h3>
                </div>
                <div className="space-y-3">
                  {submitResult.quran_values.map((value) => (
                    <div
                      key={value.quran_value_code}
                      className="rounded-soft border border-sand/80 bg-white/60 p-4 shadow-soft-card backdrop-blur-sm"
                    >
                      <div className="flex justify-between gap-3">
                        <h4 className="font-semibold text-ink">
                          {localizeText(value.name_en, value.name_ar)}
                        </h4>
                        <span className="text-sm font-semibold text-primary/90">
                          {value.score.toFixed(1)}
                        </span>
                      </div>
                      <p className="mt-2 text-sm leading-relaxed text-muted">
                        {localizeText(value.desc_en, value.desc_ar)}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {submitResult.prophet_traits.length > 0 && (
              <div className="space-y-4 rounded-soft border border-accent/80 bg-white/70 px-6 py-6 shadow-soft-card backdrop-blur-sm">
                <div className="flex items-center gap-3">
                  <span className="flex h-10 w-10 items-center justify-center rounded-full border border-sand/70 bg-[#F0EBE5]">
                    <img
                      src={resultsIconFour}
                      alt=""
                      aria-hidden="true"
                      className="h-6 w-6 object-contain"
                    />
                  </span>
                  <h3 className="text-2xl font-semibold text-ink">{t.journey.prophetTraitsTitle}</h3>
                </div>
                <div className="space-y-3">
                  {submitResult.prophet_traits.map((trait) => (
                    <div
                      key={trait.trait_code}
                      className="rounded-soft border border-sand/80 bg-white/60 p-4 shadow-soft-card backdrop-blur-sm"
                    >
                      <div className="flex justify-between gap-3">
                        <h4 className="font-semibold text-ink">
                          {localizeText(trait.name_en, trait.name_ar)}
                        </h4>
                        <span className="text-sm font-semibold text-primary/90">
                          {trait.score.toFixed(1)}
                        </span>
                      </div>
                      <p className="mt-2 text-sm leading-relaxed text-muted">
                        {localizeText(trait.desc_en, trait.desc_ar)}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="flex justify-center">
              <div className="w-full max-w-3xl space-y-4 rounded-soft border border-accent/80 bg-white/70 px-6 py-6 shadow-soft-card backdrop-blur-sm">
                <h3 className="text-2xl font-semibold text-ink">{t.journey.resultsFeedbackTitle}</h3>
                <p className="text-muted">{t.journey.resultsFeedbackSubtitle}</p>

                <div className="space-y-3">
                  <p className={`${language === 'ar' ? 'text-right' : 'text-left'} text-sm font-medium text-ink`}>
                    {t.journey.resultsAccuracyQuestion}
                  </p>
                  <div
                    className={`flex flex-wrap gap-2 ${language === 'ar' ? 'justify-end' : 'justify-start'}`}
                    dir="ltr"
                  >
                    {resultRatingOrder.map((score) => (
                      <button
                        key={`accuracy-${score}`}
                        type="button"
                        aria-pressed={accuracyScore === score}
                        onClick={() => {
                          setAccuracyScore(score);
                          setError('');
                        }}
                        className={`h-10 w-10 rounded-full border text-sm font-semibold transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-cream ${
                          accuracyScore === score
                            ? 'border-accent/80 bg-primary text-white'
                            : 'border-sand/80 bg-white/70 text-ink hover:border-accent/60'
                        }`}
                      >
                        {score}
                      </button>
                    ))}
                  </div>
                  <p className="text-xs text-muted">{t.journey.resultsScaleHint}</p>
                </div>

                <div className="space-y-3">
                  <p className={`${language === 'ar' ? 'text-right' : 'text-left'} text-sm font-medium text-ink`}>
                    {t.journey.resultsPersonalityQuestion}
                  </p>
                  <div
                    className={`flex flex-wrap gap-2 ${language === 'ar' ? 'justify-end' : 'justify-start'}`}
                    dir="ltr"
                  >
                    {resultRatingOrder.map((score) => (
                      <button
                        key={`personality-${score}`}
                        type="button"
                        aria-pressed={personalityMatchScore === score}
                        onClick={() => {
                          setPersonalityMatchScore(score);
                          setError('');
                        }}
                        className={`h-10 w-10 rounded-full border text-sm font-semibold transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-cream ${
                          personalityMatchScore === score
                            ? 'border-accent/80 bg-primary text-white'
                            : 'border-sand/80 bg-white/70 text-ink hover:border-accent/60'
                        }`}
                      >
                        {score}
                      </button>
                    ))}
                  </div>
                  <p className="text-xs text-muted">{t.journey.resultsScaleHint}</p>
                </div>
              </div>
            </div>

            <div className="flex justify-center">
              <button
                className="flex h-11 min-w-[200px] items-center justify-center rounded-full bg-primary px-6 pt-0.5 text-base font-semibold leading-none text-white shadow-[0_12px_24px_rgba(58,80,107,0.18)] transition duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-cream sm:h-12 sm:text-lg lg:hover:-translate-y-0.5 lg:hover:bg-[#31465E]"
                onClick={() => {
                  void moveToActivation();
                }}
                disabled={busy || !isResultsFeedbackComplete}
              >
                {busy ? t.journey.saving : t.journey.toActivation}
              </button>
            </div>
          </div>
        )}

        {step === 'activation' && submitResult && (
          <div className="mx-auto max-w-3xl space-y-6 rounded-soft border border-accent/80 bg-white/70 px-6 py-6 shadow-soft-card backdrop-blur-sm">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <span className="flex h-10 w-10 items-center justify-center rounded-full border border-sand/70 bg-[#F0EBE5]">
                  <img
                    src={activationIcon}
                    alt=""
                    aria-hidden="true"
                    className="h-6 w-6 object-contain"
                  />
                </span>
                <h2 className="text-3xl font-semibold text-ink">{t.journey.activationTitle}</h2>
              </div>
              <p className="text-muted">{t.journey.activationSubtitle}</p>
            </div>

            <div className="space-y-3">
              {activationItems.map((item) => {
                const isSelected = selectedActivationId === item.advice_id;
                return (
                  <button
                    key={item.advice_id}
                    type="button"
                    aria-pressed={isSelected}
                    onClick={() => {
                      setSelectedActivationId(item.advice_id);
                      setError('');
                    }}
                    className={`w-full rounded-soft border px-5 py-4 text-sm font-medium leading-relaxed text-ink shadow-soft-card backdrop-blur-sm transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-cream disabled:cursor-not-allowed disabled:opacity-60 sm:text-base ${
                      language === 'ar' ? 'text-right' : 'text-left'
                    } ${
                      isSelected
                        ? 'border-accent/80 bg-white shadow-soft-float'
                        : 'border-sand/80 bg-white/60 hover:border-accent/60 hover:bg-white/75'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="text-xs uppercase tracking-wide text-primary/80 mb-1">
                          {t.journey.channels[item.channel as 'behavior' | 'reflection' | 'social'] ?? item.channel}
                        </p>
                        <h3 className="text-lg font-semibold text-ink">
                          {localizeText(item.title_en, item.title_ar)}
                        </h3>
                        <p className="text-sm text-muted mt-1">
                          {localizeText(item.body_en, item.body_ar)}
                        </p>
                      </div>
                      {isSelected && (
                        <span className="text-primary/90 font-semibold text-sm">{t.journey.selected}</span>
                      )}
                    </div>
                  </button>
                );
              })}
            </div>

            <div className="flex justify-center">
              <button
                className="flex h-11 min-w-[200px] items-center justify-center rounded-full bg-primary px-6 pt-0.5 text-base font-semibold leading-none text-white shadow-[0_12px_24px_rgba(58,80,107,0.18)] transition duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-cream disabled:cursor-not-allowed disabled:opacity-60 sm:h-12 sm:text-lg lg:hover:-translate-y-0.5 lg:hover:bg-[#31465E]"
                onClick={finalizeActivation}
                disabled={busy}
              >
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
