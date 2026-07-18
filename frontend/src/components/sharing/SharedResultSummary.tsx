import React from 'react';
import { useLanguage } from '../../i18n/LanguageContext';
import { SharedJourneyResult, SharedScoreItem } from '../../types';

const ScoreRows: React.FC<{ rows: SharedScoreItem[]; suffix?: string }> = ({ rows, suffix = '' }) => (
  <div className="space-y-2">
    {rows.map((item) => (
      <div key={`${item.rank}-${item.name}`} className="flex justify-between gap-4 rounded-lg bg-white/70 px-4 py-3">
        <span>{item.rank}. {item.name}</span>
        <span className="font-semibold text-primary">{item.score.toFixed(1)}{suffix}</span>
      </div>
    ))}
  </div>
);

const SharedResultSummary: React.FC<{ report: SharedJourneyResult }> = ({ report }) => {
  const { t } = useLanguage();
  const sections = t.journey.sharing.sections;
  return (
    <div className="space-y-5 text-start">
      <div className="grid gap-5 md:grid-cols-2">
        <section className="rounded-soft border border-sand/80 bg-white/60 p-5">
          <h2 className="mb-3 text-xl font-semibold text-ink">{sections.genes}</h2>
          <div className="space-y-2">
            {report.top_genes.map((item) => (
              <div key={`${item.rank}-${item.name}`} className="rounded-lg bg-white/70 px-4 py-3">
                <div className="flex justify-between gap-4">
                  <span>{item.rank}. {item.name}</span>
                  <span className="font-semibold text-primary">{item.score.toFixed(1)}%</span>
                </div>
                <p className="mt-1 text-xs text-muted">{item.role}</p>
              </div>
            ))}
          </div>
        </section>
        <section className="rounded-soft border border-sand/80 bg-white/60 p-5">
          <h2 className="mb-3 text-xl font-semibold text-ink">{sections.archetypes}</h2>
          <ScoreRows rows={report.archetype_matches} suffix="%" />
        </section>
        {report.quran_values.length > 0 && (
          <section className="rounded-soft border border-sand/80 bg-white/60 p-5">
            <h2 className="mb-3 text-xl font-semibold text-ink">{sections.quranValues}</h2>
            <ScoreRows rows={report.quran_values} />
          </section>
        )}
        {report.prophet_traits.length > 0 && (
          <section className="rounded-soft border border-sand/80 bg-white/60 p-5">
            <h2 className="mb-3 text-xl font-semibold text-ink">{sections.prophetTraits}</h2>
            <ScoreRows rows={report.prophet_traits} />
          </section>
        )}
      </div>
      {report.selected_activation && (
        <section className="rounded-soft border border-accent/80 bg-white/70 p-5">
          <h2 className="text-xl font-semibold text-ink">{sections.activation}</h2>
          <p className="mt-2 text-xs uppercase tracking-wide text-primary">{report.selected_activation.channel}</p>
          <h3 className="mt-1 font-semibold">{report.selected_activation.title}</h3>
          <p className="mt-1 text-muted">{report.selected_activation.body}</p>
        </section>
      )}
    </div>
  );
};

export default SharedResultSummary;
