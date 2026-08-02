import React from 'react';
import { useLanguage } from '../i18n/LanguageContext';

interface LanguageSwitcherProps {
  className?: string;
}

const LanguageSwitcher: React.FC<LanguageSwitcherProps> = ({ className = '' }) => {
  const { language, setLanguage } = useLanguage();

  return (
    <div
      dir="ltr"
      className={`mb-4 inline-flex items-center gap-1 rounded-full bg-[#EAE3DB] p-1 ${className}`}
    >
      <button
        onClick={() => setLanguage('en')}
        className={`inline-flex h-10 items-center justify-center rounded-full px-4 text-sm font-medium leading-none transition ${
          language === 'en'
            ? 'bg-primary text-white shadow-soft-card'
            : 'text-muted hover:text-ink'
        } focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-cream`}
      >
        English
      </button>
      <button
        onClick={() => setLanguage('ar')}
        className={`inline-flex h-10 items-center justify-center rounded-full px-4 text-sm font-medium leading-none transition ${
          language === 'ar'
            ? 'bg-primary text-white shadow-soft-card'
            : 'text-muted hover:text-ink'
        } focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-cream`}
      >
        العربية
      </button>
    </div>
  );
};

export default LanguageSwitcher;
