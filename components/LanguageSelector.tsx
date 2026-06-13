
import React from 'react';
import { Language } from '../types';

interface LanguageSelectorProps {
  currentLanguage: Language;
  onLanguageChange: (lang: Language) => void;
}

const LanguageSelector: React.FC<LanguageSelectorProps> = ({ currentLanguage, onLanguageChange }) => {
  return (
    <div className="flex space-x-2 bg-blue-200 p-1 rounded-full">
      {(Object.keys(Language) as Array<keyof typeof Language>).map((key) => (
        <button
          key={key}
          onClick={() => onLanguageChange(Language[key])}
          className={`px-4 py-2 text-base font-semibold rounded-full transition-colors duration-300 ${
            currentLanguage === Language[key]
              ? 'bg-blue-50 text-blue-600 shadow'
              : 'text-blue-800 hover:bg-blue-200'
          }`}
        >
          {Language[key]}
        </button>
      ))}
    </div>
  );
};

export default LanguageSelector;
