import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useLanguage } from '../i18n/LanguageContext';
import LanguageSwitcher from '../components/LanguageSwitcher';

const Landing: React.FC = () => {
  const navigate = useNavigate();
  const { t } = useLanguage();

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center p-4">
      {/* Language Switcher - Fixed position */}
      <div className="absolute top-4 end-4">
        <LanguageSwitcher />
      </div>

      <div className="max-w-2xl text-center">
        <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
          {t.landing.title}
        </h1>

        <p className="text-xl text-gray-700 mb-8">
          {t.landing.subtitle}
        </p>

        <div className="card mb-8">
          <h2 className="text-2xl font-semibold mb-4">{t.landing.whatToExpect}</h2>
          <div className="space-y-4 text-start">
            <div className="flex items-start">
              <span className="text-primary-600 me-3 text-2xl">✓</span>
              <div>
                <h3 className="font-semibold">{t.landing.quickQuestions}</h3>
                <p className="text-gray-600">{t.landing.quickQuestionsDesc}</p>
              </div>
            </div>
            <div className="flex items-start">
              <span className="text-primary-600 me-3 text-2xl">✓</span>
              <div>
                <h3 className="font-semibold">{t.landing.personalityProfile}</h3>
                <p className="text-gray-600">{t.landing.personalityProfileDesc}</p>
              </div>
            </div>
            <div className="flex items-start">
              <span className="text-primary-600 me-3 text-2xl">✓</span>
              <div>
                <h3 className="font-semibold">{t.landing.topMatches}</h3>
                <p className="text-gray-600">{t.landing.topMatchesDesc}</p>
              </div>
            </div>
          </div>
        </div>

        <button
          onClick={() => navigate('/test')}
          className="btn-primary text-lg px-10 py-4"
        >
          {t.landing.startTest}
        </button>

        <p className="text-sm text-gray-600 mt-6 max-w-lg mx-auto">
          <strong>{t.landing.disclaimer}</strong> {t.landing.disclaimerText}
        </p>
      </div>
    </div>
  );
};

export default Landing;
