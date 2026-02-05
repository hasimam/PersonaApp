import React from 'react';
import { Question } from '../../types';
import { useLanguage } from '../../i18n/LanguageContext';

interface QuestionCardProps {
  question: Question;
  selectedAnswer: number | null;
  onSelectAnswer: (answer: number) => void;
}

const QuestionCard: React.FC<QuestionCardProps> = ({
  question,
  selectedAnswer,
  onSelectAnswer,
}) => {
  const { t, language } = useLanguage();
  const likertOptions = [
    { value: 1, label: t.likert.stronglyDisagree },
    { value: 2, label: t.likert.disagree },
    { value: 3, label: t.likert.neutral },
    { value: 4, label: t.likert.agree },
    { value: 5, label: t.likert.stronglyAgree },
  ];

  return (
    <div className="card max-w-3xl mx-auto">
      <h2 className="text-2xl font-semibold text-gray-800 mb-8 text-center">
        {question.text}
      </h2>

      <div className="space-y-3">
        {likertOptions.map((option) => (
          <button
            key={option.value}
            onClick={() => onSelectAnswer(option.value)}
            className={`w-full p-4 rounded-lg border-2 transition-all ${
              language === 'ar' ? 'text-right' : 'text-left'
            } ${
              selectedAnswer === option.value
                ? 'border-primary-600 bg-primary-50 shadow-md'
                : 'border-gray-200 hover:border-primary-300 hover:bg-gray-50'
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="font-medium text-gray-800">{option.label}</span>
              <div
                className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                  selectedAnswer === option.value
                    ? 'border-primary-600 bg-primary-600'
                    : 'border-gray-300'
                }`}
              >
                {selectedAnswer === option.value && (
                  <div className="w-3 h-3 bg-white rounded-full" />
                )}
              </div>
            </div>
          </button>
        ))}
      </div>

      <p className="text-sm text-gray-500 mt-6 text-center">
        {t.test.selectOption}
      </p>
    </div>
  );
};

export default QuestionCard;
