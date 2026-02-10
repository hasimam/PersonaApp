import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { resultsApi } from '../services/api';
import { ResultResponse } from '../types';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { useLanguage } from '../i18n/LanguageContext';
import LanguageSwitcher from '../components/LanguageSwitcher';

const Results: React.FC = () => {
  const { resultId } = useParams<{ resultId: string }>();
  const navigate = useNavigate();
  const { t, language } = useLanguage();
  const [loading, setLoading] = useState(true);
  const [result, setResult] = useState<ResultResponse | null>(null);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const fetchResults = async () => {
      if (!resultId) return;

      try {
        const data = await resultsApi.getResult(parseInt(resultId), language);
        setResult(data);
        setLoading(false);
      } catch (err) {
        setError(t.results.loadError);
        setLoading(false);
      }
    };

    fetchResults();
  }, [resultId, language, t.results.loadError]);

  if (loading) {
    return (
      <div className="relative min-h-screen overflow-hidden bg-cream px-4 py-10 text-ink sm:px-6 flex items-center justify-center">
        <div className="text-center">
          <div className="mx-auto mb-4 h-16 w-16 animate-spin rounded-full border-b-2 border-primary" />
          <p className="text-muted">{t.results.analyzing}</p>
        </div>
      </div>
    );
  }

  if (error || !result) {
    return (
      <div className="relative min-h-screen overflow-hidden bg-cream px-4 py-10 text-ink sm:px-6 flex items-center justify-center">
        <div className="mx-auto w-full max-w-md space-y-5 rounded-soft border border-accent/80 bg-white/70 px-6 py-6 text-center shadow-soft-card backdrop-blur-sm">
          <p className="text-sm font-semibold text-red-700">{error || t.results.notFound}</p>
          <button
            onClick={() => navigate('/')}
            className="mx-auto flex h-11 min-w-[200px] items-center justify-center rounded-full bg-primary px-6 pt-0.5 text-base font-semibold leading-none text-white shadow-[0_12px_24px_rgba(58,80,107,0.18)] transition duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-cream sm:h-12 sm:text-lg lg:hover:-translate-y-0.5 lg:hover:bg-[#31465E]"
          >
            {t.results.backHome}
          </button>
        </div>
      </div>
    );
  }

  const chartData = result.user_trait_scores.map((trait) => ({
    trait: trait.trait_name,
    score: trait.score,
  }));

  return (
    <div className="relative min-h-screen overflow-hidden bg-cream px-4 py-10 text-ink sm:px-6">
      {/* Language Switcher - Top right corner */}
      <div className="absolute top-4 right-4 z-10 sm:right-8 sm:top-6">
        <LanguageSwitcher className="border border-sand/70 shadow-soft-card backdrop-blur-sm" />
      </div>

      <div className="mx-auto max-w-6xl">
        <div className="mb-10 text-center sm:mb-12">
          <h1 className="text-3xl font-semibold tracking-tight text-ink sm:text-4xl lg:text-5xl">
            {t.results.title}
          </h1>
          <p className="mx-auto mt-4 max-w-2xl text-sm leading-relaxed text-muted sm:text-base lg:text-lg">
            {t.results.subtitle}
          </p>
        </div>

        {/* Top Matches */}
        <div className="mb-10 sm:mb-12">
          <h2 className="mb-6 text-center text-2xl font-semibold text-ink">
            {t.results.topMatches}
          </h2>
          <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
            {result.top_matches.map((match, index) => (
              <div
                key={match.idol_id}
                className="rounded-soft border border-sand/80 bg-white/70 px-6 py-6 text-center shadow-soft-card backdrop-blur-sm transition hover:border-accent/60 hover:shadow-soft-float"
              >
                <div className="relative mb-4">
                  <div className="absolute -top-4 -end-4 flex h-12 w-12 items-center justify-center rounded-full bg-primary text-lg font-bold text-white shadow-soft-card">
                    #{index + 1}
                  </div>
                  <img
                    src={match.image_url || '/placeholder.png'}
                    alt={match.name}
                    className="mb-4 h-64 w-full rounded-soft object-cover"
                    onError={(e) => {
                      e.currentTarget.src = '/placeholder.png';
                    }}
                  />
                </div>
                <h3 className="mb-2 text-xl font-semibold text-ink">{match.name}</h3>
                <p className="mb-4 text-sm leading-relaxed text-muted">{match.description}</p>
                <div className="rounded-soft border border-sand/70 bg-white/60 p-4 shadow-soft-card backdrop-blur-sm">
                  <p className="text-3xl font-bold text-primary">
                    {match.similarity_percentage}%
                  </p>
                  <p className="text-sm text-muted">{t.results.personalityMatch}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Personality Profile Chart */}
        <div className="mb-10 rounded-soft border border-accent/80 bg-white/70 px-6 py-6 shadow-soft-card backdrop-blur-sm sm:mb-12">
          <h2 className="mb-6 text-center text-2xl font-semibold text-ink">
            {t.results.personalityProfile}
          </h2>
          <ResponsiveContainer width="100%" height={400}>
            <RadarChart data={chartData}>
              <PolarGrid />
              <PolarAngleAxis dataKey="trait" />
              <PolarRadiusAxis angle={90} domain={[0, 100]} />
              <Radar
                name={t.results.yourScore}
                dataKey="score"
                stroke="#3A506B"
                fill="#3A506B"
                fillOpacity={0.6}
              />
              <Legend />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        {/* Trait Scores */}
        <div className="mb-10 rounded-soft border border-accent/80 bg-white/70 px-6 py-6 shadow-soft-card backdrop-blur-sm sm:mb-12">
          <h2 className="mb-6 text-2xl font-semibold text-ink">{t.results.traitScores}</h2>
          <div className="space-y-4">
            {result.user_trait_scores.map((trait) => (
              <div key={trait.trait_id}>
                <div
                  className={`mb-2 flex justify-between ${
                    language === 'ar' ? 'text-right' : 'text-left'
                  }`}
                >
                  <span className="font-medium text-ink">{trait.trait_name}</span>
                  <span className="font-semibold text-primary">{trait.score.toFixed(1)}</span>
                </div>
                <div className="h-3 w-full rounded-full bg-sand/60">
                  <div
                    className="h-3 rounded-full bg-primary transition-all"
                    style={{ width: `${trait.score}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Actions */}
        <div className="flex flex-col justify-center gap-3 sm:flex-row sm:gap-4">
          <button
            onClick={() => navigate('/')}
            className="flex h-11 min-w-[200px] items-center justify-center rounded-full bg-primary px-6 pt-0.5 text-base font-semibold leading-none text-white shadow-[0_12px_24px_rgba(58,80,107,0.18)] transition duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-cream sm:h-12 sm:text-lg lg:hover:-translate-y-0.5 lg:hover:bg-[#31465E]"
          >
            {t.results.retakeTest}
          </button>
          <button
            onClick={() => {
              alert(t.results.shareComingSoon);
            }}
            className="flex h-11 items-center justify-center rounded-full border border-sand/80 bg-white/60 px-6 pt-0.5 text-base font-semibold leading-none text-ink shadow-soft-card backdrop-blur-sm transition duration-200 hover:bg-white/80 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-cream sm:h-12 sm:text-lg"
          >
            {t.results.shareResults}
          </button>
        </div>

        {/* Disclaimer */}
        <p className="mx-auto mt-8 max-w-2xl text-center text-sm text-muted">
          {t.results.disclaimerText}
        </p>
      </div>
    </div>
  );
};

export default Results;
