import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { testApi } from '../services/api';
import { Question, Answer } from '../types';
import QuestionCard from '../components/test/QuestionCard';
import ProgressBar from '../components/common/ProgressBar';
import { useLanguage } from '../i18n/LanguageContext';
import LanguageSwitcher from '../components/LanguageSwitcher';

const Test: React.FC = () => {
  const navigate = useNavigate();
  const { t, language } = useLanguage();
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<Map<number, number>>(new Map());
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const initTest = async () => {
      try {
        const data = await testApi.startTest(language);
        setSessionId(data.session_id);
        setQuestions(data.questions);
        setLoading(false);
      } catch (err) {
        setError(t.test.error);
        setLoading(false);
      }
    };

    initTest();
  }, [language, t.test.error]);

  const handleAnswer = (answer: number) => {
    const newAnswers = new Map(answers);
    newAnswers.set(questions[currentIndex].id, answer);
    setAnswers(newAnswers);
  };

  const handleNext = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  const handleSubmit = async () => {
    if (answers.size < questions.length) {
      setError(t.test.answerAllQuestions);
      return;
    }

    setSubmitting(true);
    try {
      const responses: Answer[] = Array.from(answers.entries()).map(([question_id, answer]) => ({
        question_id,
        answer,
      }));

      const result = await testApi.submitTest(sessionId, responses);
      navigate(`/results/${result.result_id}`);
    } catch (err) {
      setError(t.test.submitError);
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">{t.test.loading}</p>
        </div>
      </div>
    );
  }

  if (error && questions.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="card max-w-md text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button onClick={() => window.location.reload()} className="btn-primary">
            {t.test.tryAgain}
          </button>
        </div>
      </div>
    );
  }

  const currentQuestion = questions[currentIndex];
  const currentAnswer = answers.get(currentQuestion.id) || null;
  const isLastQuestion = currentIndex === questions.length - 1;
  const canProceed = currentAnswer !== null;

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      {/* Language Switcher */}
      <div className="absolute top-4 end-4">
        <LanguageSwitcher />
      </div>

      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <ProgressBar current={currentIndex + 1} total={questions.length} />
        </div>

        <QuestionCard
          question={currentQuestion}
          selectedAnswer={currentAnswer}
          onSelectAnswer={handleAnswer}
        />

        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-center">
            {error}
          </div>
        )}

        <div className="flex justify-between mt-8">
          <button
            onClick={handlePrevious}
            disabled={currentIndex === 0}
            className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {t.test.previous}
          </button>

          {isLastQuestion ? (
            <button
              onClick={handleSubmit}
              disabled={!canProceed || submitting}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submitting ? t.test.submitting : t.test.submitResults}
            </button>
          ) : (
            <button
              onClick={handleNext}
              disabled={!canProceed}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {t.test.next}
            </button>
          )}
        </div>

        <div className="text-center mt-6 text-sm text-gray-600">
          {answers.size} {t.test.of} {questions.length} {t.test.questionsAnswered}
        </div>
      </div>
    </div>
  );
};

export default Test;
