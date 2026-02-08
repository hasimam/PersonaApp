import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useLanguage } from '../i18n/LanguageContext';
import LanguageSwitcher from '../components/LanguageSwitcher';
import logo from '../assets/logo.png';
import decoImageOne from '../assets/deco-image-1.png';
import decoImageTwo from '../assets/deco-image-2.png';

const Landing: React.FC = () => {
  const navigate = useNavigate();
  const { t, isRTL } = useLanguage();
  const cards = [
    {
      title: t.landing.quickQuestions,
      description: t.landing.quickQuestionsDesc,
    },
    {
      title: t.landing.personalityProfile,
      description: t.landing.personalityProfileDesc,
      extraTitle: t.landing.topMatches,
      extraDescription: t.landing.topMatchesDesc,
    },
  ];
  const selectedIndex = 1;

  return (
    <div
      dir={isRTL ? 'rtl' : 'ltr'}
      className="relative min-h-screen overflow-hidden bg-cream text-ink"
    >
      <div className="pointer-events-none absolute inset-x-0 bottom-0 top-12 bg-[radial-gradient(ellipse_at_top,_rgba(197,168,128,0.18)_0%,_rgba(246,241,234,0)_60%)]" />
      <div className="pointer-events-none absolute inset-x-0 bottom-0 top-12 bg-[radial-gradient(ellipse_at_bottom,_rgba(58,80,107,0.08)_0%,_rgba(246,241,234,0)_70%)]" />
      <div className="pointer-events-none absolute inset-x-0 bottom-0 top-12 opacity-[0.35] [background-image:radial-gradient(rgba(58,80,107,0.06)_1px,transparent_1px)] [background-size:28px_28px]" />

      <div className="pointer-events-none absolute left-6 top-24 hidden md:block">
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

      <div className="absolute right-4 top-4 z-10 sm:right-8 sm:top-6">
        <LanguageSwitcher className="border border-sand/70 shadow-soft-card backdrop-blur-sm" />
      </div>

      <div className="relative z-10 mx-auto flex min-h-screen w-full max-w-5xl flex-col px-4 pb-16 pt-16 sm:px-6 sm:pt-20 lg:px-8">
        <div className="relative mt-6 text-center sm:mt-10">
          <img
            src={logo}
            alt="PersonaApp logo"
            className="mx-auto h-40 w-auto object-contain md:h-60 lg:h-80"
          />
          <h1 className="mt-5 text-3xl font-semibold tracking-tight text-ink sm:text-4xl lg:text-5xl">
            {t.landing.title}
          </h1>
          <p className="mx-auto mt-4 max-w-2xl text-sm leading-relaxed text-muted sm:text-base lg:text-lg">
            {t.landing.subtitle}
          </p>
        </div>

        <div className="mt-8 flex flex-col items-center sm:mt-10">
          <div className="flex items-center gap-3 text-accent/70">
            <span className="h-px w-16 bg-accent/40" />
            <span className="h-2 w-2 rotate-45 bg-accent/60" />
            <span className="h-px w-16 bg-accent/40" />
          </div>
          <p className="mt-3 text-sm font-medium text-primary/80 sm:text-base">
            {t.landing.whatToExpect}
          </p>
        </div>

        <div className="mt-8 grid grid-cols-1 gap-5 md:grid-cols-2 md:gap-6">
          {cards.map((card, index) => {
            const isSelected = index === selectedIndex;
            return (
              <div
                key={card.title}
                className={`flex h-full flex-col rounded-soft border px-6 py-6 text-start shadow-soft-card backdrop-blur-sm transition ${
                  isSelected
                    ? 'border-accent/80 bg-white shadow-soft-float'
                    : 'border-sand/80 bg-white/70'
                }`}
              >
                <h3 className="text-lg font-semibold text-ink sm:text-xl">
                  {card.title}
                </h3>
                <p className="mt-3 text-sm leading-relaxed text-muted sm:text-base">
                  {card.description}
                </p>
                {card.extraTitle && (
                  <div className="mt-5 border-t border-accent/25 pt-4">
                    <p className="text-sm font-semibold text-ink sm:text-base">
                      {card.extraTitle}
                    </p>
                    <p className="mt-2 text-sm leading-relaxed text-muted sm:text-base">
                      {card.extraDescription}
                    </p>
                  </div>
                )}
                {isSelected && (
                  <div className="mt-auto pt-6">
                    <div className="mb-4 flex items-center justify-center gap-2 text-accent/70">
                      <span className="h-px w-10 bg-accent/40" />
                      <span className="h-2 w-2 rotate-45 bg-accent/60" />
                      <span className="h-px w-10 bg-accent/40" />
                    </div>
                    <button
                      onClick={() => navigate('/test')}
                      className="mx-auto flex h-11 min-w-[200px] items-center justify-center rounded-full bg-primary px-6 pt-0.5 text-base font-semibold leading-none text-white shadow-[0_12px_24px_rgba(58,80,107,0.18)] transition duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-cream sm:h-12 sm:text-lg lg:hover:-translate-y-0.5 lg:hover:bg-[#31465E]"
                    >
                      {t.landing.startTest}
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        <p className="mx-auto mt-8 max-w-3xl text-center text-xs leading-relaxed text-muted sm:text-sm">
          <strong className="text-ink">{t.landing.disclaimer}</strong>{' '}
          {t.landing.disclaimerText}
        </p>
      </div>
    </div>
  );
};

export default Landing;
