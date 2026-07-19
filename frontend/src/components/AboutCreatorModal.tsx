import React, { useEffect, useState } from 'react';
import { useLanguage } from '../i18n/LanguageContext';

const AboutCreatorModal: React.FC = () => {
  const { t, isRTL } = useLanguage();
  const copy = t.aboutCreator;
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    if (!isOpen) return undefined;

    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setIsOpen(false);
    };
    document.addEventListener('keydown', closeOnEscape);
    document.body.style.overflow = 'hidden';

    return () => {
      document.removeEventListener('keydown', closeOnEscape);
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  return (
    <>
      <div className="mt-10 border-t border-sand/60 pt-6 text-center">
        <button
          type="button"
          onClick={() => setIsOpen(true)}
          className="rounded-full border border-sand/80 bg-white/70 px-5 py-2.5 text-sm font-semibold text-primary shadow-soft-card transition hover:border-accent/70 hover:bg-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-cream"
        >
          {copy.button}
        </button>
      </div>

      {isOpen && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-ink/55 px-4 py-6"
          role="presentation"
          onClick={(event) => {
            if (event.target === event.currentTarget) setIsOpen(false);
          }}
        >
          <section
            role="dialog"
            aria-modal="true"
            aria-labelledby="about-creator-title"
            dir={isRTL ? 'rtl' : 'ltr'}
            className="flex max-h-[calc(100vh-3rem)] w-full max-w-4xl flex-col overflow-hidden rounded-soft border border-accent/70 bg-cream text-ink shadow-soft-float"
            onClick={(event) => event.stopPropagation()}
          >
            <header className="flex items-start justify-between gap-4 border-b border-sand/70 bg-white/70 px-5 py-4 sm:px-7">
              <h2 id="about-creator-title" className="text-2xl font-semibold leading-tight sm:text-3xl">
                {copy.title}
              </h2>
              <button
                type="button"
                aria-label={copy.close}
                onClick={() => setIsOpen(false)}
                className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full border border-sand/80 bg-white/70 text-2xl leading-none text-muted transition hover:border-accent/70 hover:text-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
              >
                ×
              </button>
            </header>

            <div className="overflow-y-auto px-5 py-6 text-sm leading-8 sm:px-7 sm:text-base">
              <p>{copy.intro}</p>
              <p className="mt-5">{copy.resultIntro}</p>

              <CreatorSection title={copy.keyTraitsTitle}>
                <ol className="list-decimal space-y-1 ps-6">
                  {copy.keyTraits.map((trait) => (
                    <li key={trait.name}>
                      {trait.name} — {trait.role}
                    </li>
                  ))}
                </ol>
              </CreatorSection>

              <CreatorSection title={copy.modelsTitle}>
                <ol className="list-decimal space-y-1 ps-6">
                  {copy.models.map((model) => (
                    <li key={model.name}>
                      {model.name} — {model.description}
                    </li>
                  ))}
                </ol>
              </CreatorSection>

              <CreatorSection title={copy.quranValuesTitle}>
                <p>{copy.quranValues}</p>
              </CreatorSection>

              <CreatorSection title={copy.propheticQualitiesTitle}>
                <p>{copy.propheticQualities}</p>
              </CreatorSection>

              {copy.reflectionParagraphs.map((paragraph) => (
                <p key={paragraph} className="mt-5">
                  {paragraph}
                </p>
              ))}

              <CreatorSection title={copy.activationTitle}>
                <p>{copy.activationIntro}</p>
                <blockquote className="mt-4 border-s-4 border-accent bg-white/70 px-4 py-3 text-ink">
                  {copy.activationQuote}
                </blockquote>
                <p className="mt-4">{copy.activationParagraph}</p>
              </CreatorSection>

              <CreatorSection title={copy.closingTitle}>
                {copy.closingParagraphs.map((paragraph) => (
                  <p key={paragraph} className="mt-4 first:mt-0">
                    {paragraph}
                  </p>
                ))}
                <p className="mt-5">{copy.thanksParagraph}</p>
                <blockquote className="mt-4 border-s-4 border-accent bg-white/70 px-4 py-3 text-ink">
                  {copy.finalQuote}
                </blockquote>
              </CreatorSection>
            </div>
          </section>
        </div>
      )}
    </>
  );
};

const CreatorSection: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => (
  <section className="mt-7 first:mt-6">
    <h3 className="text-lg font-semibold leading-7 text-primary sm:text-xl">{title}</h3>
    <div className="mt-2">{children}</div>
  </section>
);

export default AboutCreatorModal;
