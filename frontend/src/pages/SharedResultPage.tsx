import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import LanguageSwitcher from '../components/LanguageSwitcher';
import ResultSharingActions from '../components/sharing/ResultSharingActions';
import SharedResultSummary from '../components/sharing/SharedResultSummary';
import { useLanguage } from '../i18n/LanguageContext';
import { journeyApi } from '../services/api';
import { SharedJourneyResult } from '../types';
import logo from '../assets/logo.png';

const SharedResultPage: React.FC = () => {
  const navigate = useNavigate();
  const { t, language, setLanguage } = useLanguage();
  const [report, setReport] = useState<SharedJourneyResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [unavailable, setUnavailable] = useState(false);

  useEffect(() => {
    let meta = document.querySelector('meta[name="referrer"]') as HTMLMetaElement | null;
    const previous = meta?.content;
    if (!meta) {
      meta = document.createElement('meta');
      meta.name = 'referrer';
      document.head.appendChild(meta);
    }
    meta.content = 'no-referrer';
    return () => {
      if (meta && previous !== undefined) meta.content = previous;
    };
  }, []);

  useEffect(() => {
    const token = window.location.hash.slice(1).trim();
    if (!token) {
      setUnavailable(true);
      setLoading(false);
      return;
    }
    journeyApi
      .getSharedResult(token)
      .then((result) => {
        setReport(result);
        setLanguage(result.language);
      })
      .catch(() => setUnavailable(true))
      .finally(() => setLoading(false));
  }, [setLanguage]);

  const shared = t.journey.sharing.sharedPage;
  return (
    <div className="min-h-screen bg-cream px-4 pb-16 pt-8 text-ink" dir={language === 'ar' ? 'rtl' : 'ltr'}>
      <header className="mx-auto flex max-w-5xl items-center justify-between">
        <img src={logo} alt="PersonaApp" className="h-20 w-auto" />
        <LanguageSwitcher />
      </header>
      <main className="mx-auto mt-6 max-w-5xl">
        {loading && <p className="py-20 text-center text-muted">{shared.loading}</p>}
        {unavailable && !loading && (
          <div className="mx-auto max-w-xl rounded-soft border border-sand bg-white/70 p-8 text-center shadow-soft-card">
            <h1 className="text-3xl font-semibold">{shared.unavailableTitle}</h1>
            <p className="mt-3 text-muted">{shared.unavailableBody}</p>
            <button type="button" className="btn-primary mt-6" onClick={() => navigate('/')}>{shared.startOwn}</button>
          </div>
        )}
        {report && !loading && (
          <div className="space-y-6">
            <div className="text-center">
              <p className="text-sm uppercase tracking-wide text-primary">
                {report.journey_type === 'deep' ? t.journey.typeLabels.deep : t.journey.typeLabels.quick}
              </p>
              <h1 className="mt-2 text-4xl font-semibold">{shared.title}</h1>
              <p className="mt-2 text-muted">
                {new Intl.DateTimeFormat(language, { dateStyle: 'long' }).format(new Date(report.completed_at))}
              </p>
            </div>
            <SharedResultSummary report={report} />
            <ResultSharingActions report={report} existingLink={window.location.href} />
            <div className="text-center">
              <button type="button" className="btn-primary" onClick={() => navigate('/')}>{shared.startOwn}</button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default SharedResultPage;
