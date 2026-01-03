import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { testApi } from '../services/api';
import { Question, Answer } from '../types';
import QuestionCard from '../components/test/QuestionCard';
import ProgressBar from '../components/common/ProgressBar';

const Test: React.FC = () => {
  const navigate = useNavigate();
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
        const data = await testApi.startTest();
        setSessionId(data.session_id);
        setQuestions(data.questions);
        setLoading(false);
      } catch (err) {
        setError('Failed to load test. Please try again.');
        setLoading(false);
      }
    };

    initTest();
  }, []);

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
      setError('Please answer all questions before submitting.');
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
      setError('Failed to submit test. Please try again.');
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your personality test...</p>
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
            Try Again
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
            Previous
          </button>

          {isLastQuestion ? (
            <button
              onClick={handleSubmit}
              disabled={!canProceed || submitting}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submitting ? 'Submitting...' : 'Submit & See Results'}
            </button>
          ) : (
            <button
              onClick={handleNext}
              disabled={!canProceed}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          )}
        </div>

        <div className="text-center mt-6 text-sm text-gray-600">
          {answers.size} of {questions.length} questions answered
        </div>
      </div>
    </div>
  );
};

export default Test;
