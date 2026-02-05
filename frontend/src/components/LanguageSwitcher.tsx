import React from 'react';
import { useLanguage } from '../i18n/LanguageContext';

interface LanguageSwitcherProps {
  className?: string;
}

const LanguageSwitcher: React.FC<LanguageSwitcherProps> = ({ className = '' }) => {
  const { language, setLanguage } = useLanguage();

    return (
    <div dir="ltr" className={`flex items-center space-x-1 ${className}`}>
      <button
        onClick={() => setLanguage('en')}
        className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
          language === 'en'
            ? 'bg-primary-600 text-white'
            : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
        }`}
      >
        English
      </button>
      <button
        onClick={() => setLanguage('ar')}
        className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
          language === 'ar'
            ? 'bg-primary-600 text-white'
            : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
        }`}
      >
        العربية
      </button>
    </div>
  );
};

export default LanguageSwitcher;
