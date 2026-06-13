import React, { useState } from 'react';
import { Language } from '../types';

interface LoginPageProps {
  onLogin: (phone: string, name: string) => void;
  language: Language;
  texts: { [key: string]: string };
  onLanguageChange: (lang: Language) => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({
  onLogin,
  language,
  texts,
  onLanguageChange,
}) => {
  const [phone, setPhone] = useState('');
  const [name, setName] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validation
    if (!phone.trim()) {
      setError(
        language === 'HI'
          ? 'कृपया फोन नंबर दर्ज करें'
          : language === 'PA'
          ? 'ਕਿਰਪਾ ਕਰਕੇ ਫੋਨ ਨੰਬਰ ਦਿਓ'
          : 'Please enter phone number'
      );
      return;
    }

    if (!name.trim()) {
      setError(
        language === 'HI'
          ? 'कृपया नाम दर्ज करें'
          : language === 'PA'
          ? 'ਕਿਰਪਾ ਕਰਕੇ ਨਾਮ ਦਿਓ'
          : 'Please enter your name'
      );
      return;
    }

    // Simulate loading
    setIsLoading(true);
    setTimeout(() => {
      onLogin(phone, name);
      setIsLoading(false);
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-600 to-primary-700 flex items-center justify-center p-4">
      {/* Language Selector - Top Right */}
      <div className="absolute top-4 right-4">
        <div className="flex gap-2">
          {(['EN', 'HI', 'PA'] as Language[]).map((lang) => (
            <button
              key={lang}
              onClick={() => onLanguageChange(lang)}
              className={`px-3 py-1 rounded-lg text-sm font-semibold transition ${
                language === lang
                  ? 'bg-white text-primary-600'
                  : 'bg-primary-500 text-white hover:bg-primary-400'
              }`}
            >
              {lang}
            </button>
          ))}
        </div>
      </div>

      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8 text-health-600">
          <svg className="w-32 h-32 mx-auto mb-4" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
            {/* Blue Sky */}
            <circle cx="100" cy="80" r="80" fill="#2E5F8A"/>
            
            {/* Green Trees Left */}
            <ellipse cx="30" cy="90" rx="20" ry="25" fill="#3FA860"/>
            <ellipse cx="20" cy="100" rx="12" ry="18" fill="#2D8C4A"/>
            <ellipse cx="40" cy="105" rx="15" ry="20" fill="#3FA860"/>
            
            {/* White House */}
            <rect x="55" y="85" width="35" height="30" fill="white" stroke="#000" strokeWidth="1.5"/>
            
            {/* Red Roof */}
            <polygon points="55,85 90,85 72.5,70" fill="#DC143C" stroke="#000" strokeWidth="1.5"/>
            
            {/* Roof stripes */}
            <line x1="60" y1="78" x2="75" y2="78" stroke="#A00000" strokeWidth="1.5"/>
            <line x1="65" y1="74" x2="80" y2="74" stroke="#A00000" strokeWidth="1.5"/>
            <line x1="70" y1="70" x2="85" y2="70" stroke="#A00000" strokeWidth="1.5"/>
            
            {/* House window */}
            <rect x="62" y="92" width="8" height="8" fill="#87CEEB" stroke="#000" strokeWidth="0.8"/>
            <line x1="66" y1="92" x2="66" y2="100" stroke="#000" strokeWidth="0.5"/>
            <line x1="62" y1="96" x2="70" y2="96" stroke="#000" strokeWidth="0.5"/>
            
            {/* House door */}
            <rect x="75" y="100" width="8" height="15" fill="#8B4513" stroke="#000" strokeWidth="0.8"/>
            <circle cx="82" cy="107" r="1.5" fill="#FFD700"/>
            
            {/* Fence */}
            <line x1="45" y1="115" x2="95" y2="115" stroke="#000" strokeWidth="1"/>
            <line x1="50" y1="115" x2="50" y2="120" stroke="#000" strokeWidth="0.8"/>
            <line x1="60" y1="115" x2="60" y2="120" stroke="#000" strokeWidth="0.8"/>
            <line x1="70" y1="115" x2="70" y2="120" stroke="#000" strokeWidth="0.8"/>
            <line x1="80" y1="115" x2="80" y2="120" stroke="#000" strokeWidth="0.8"/>
            <line x1="90" y1="115" x2="90" y2="120" stroke="#000" strokeWidth="0.8"/>
            
            {/* White Clouds */}
            <ellipse cx="120" cy="40" rx="15" ry="10" fill="white"/>
            <ellipse cx="130" cy="38" rx="12" ry="9" fill="white"/>
            <ellipse cx="110" cy="38" rx="10" ry="8" fill="white"/>
            
            <ellipse cx="160" cy="55" rx="14" ry="9" fill="white"/>
            <ellipse cx="170" cy="53" rx="11" ry="8" fill="white"/>
            <ellipse cx="150" cy="54" rx="10" ry="7" fill="white"/>
            
            {/* Yellow Fields - curved lines */}
            <path d="M 30 120 Q 70 115 140 125" stroke="#FFD700" strokeWidth="6" fill="none"/>
            <path d="M 25 135 Q 80 128 150 140" stroke="#F0C000" strokeWidth="6" fill="none"/>
            <path d="M 35 150 Q 90 140 160 155" stroke="#FFD700" strokeWidth="5" fill="none"/>
            
            {/* Red Medical Cross */}
            <g transform="translate(155, 120)">
              <rect x="-18" y="-3" width="36" height="6" fill="#DC143C" stroke="#000" strokeWidth="1.5"/>
              <rect x="-3" y="-18" width="6" height="36" fill="#DC143C" stroke="#000" strokeWidth="1.5"/>
            </g>
            
            {/* Black border circle */}
            <circle cx="100" cy="80" r="80" fill="none" stroke="#000" strokeWidth="3"/>
          </svg>
          <h1 className="text-4xl font-bold mb-2">Arogya Manthan</h1>
          <p className="text-2xl opacity-90">
            {language === 'HI'
              ? 'आरोग्य मंथन - स्वास्थ्य सेवा'
              : language === 'PA'
              ? 'ਆਰੋਗਯ ਮੰਥਨ - ਸਿਹਤ ਸੇਵਾ'
              : 'Arogya Manthan - Health Service'}
          </p>
          <p className="text-sm opacity-75 mt-2">
            {language === 'HI'
              ? 'आपकी स्वास्थ्य सहायक हमेशा आपके साथ'
              : language === 'PA'
              ? 'ਤੁਹਾਡੀ ਸਿਹਤ ਦੀ ਸਹਾਇਤਾ'
              : 'Your health companion always here'}
          </p>
        </div>

        {/* Login Card */}
        <div className="bg-amber-600 rounded-2xl shadow-2xl p-8">
          <h2 className="text-4xl font-bold text-health-600 mb-6 text-center">
            {language === 'HI'
              ? 'स्वागत है'
              : language === 'PA'
              ? 'ਸਵਾਗਤ ਹੈ'
              : 'Welcome'}
          </h2>

          {error && (
            <div className="mb-4 p-4 bg-emergency-100 border-l-4 border-emergency-600 text-emergency-700 rounded">
              <p className="font-semibold text-sm">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Name Input */}
            <div>
              <label className="block text-sm font-semibold text-white mb-2">
                {language === 'HI'
                  ? 'आपका नाम'
                  : language === 'PA'
                  ? 'ਤੁਹਾਡਾ ਨਾਮ'
                  : 'Your Name'}
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder={
                  language === 'HI'
                    ? 'नाम दर्ज करें'
                    : language === 'PA'
                    ? 'ਨਾਮ ਦਿਓ'
                    : 'Enter your name'
                }
                className="w-full px-6 py-4 border-2 border-amber-400 rounded-lg bg-amber-50 focus:outline-none focus:border-white focus:ring-1 focus:ring-white text-amber-900 placeholder-amber-600 text-base"
                disabled={isLoading}
              />
            </div>

            {/* Phone Input */}
            <div>
              <label className="block text-sm font-semibold text-white mb-2">
                {language === 'HI'
                  ? 'फोन नंबर'
                  : language === 'PA'
                  ? 'ਫੋਨ ਨੰਬਰ'
                  : 'Phone Number'}
              </label>
              <div className="flex">
                <span className="flex items-center px-4 py-3 bg-amber-700 border-2 border-amber-400 border-r-0 rounded-l-lg text-white font-semibold">
                  +91
                </span>
                <input
                  type="tel"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value.replace(/\D/g, '').slice(0, 10))}
                  placeholder={
                    language === 'HI'
                      ? '98765 43210'
                      : language === 'PA'
                      ? '98765 43210'
                      : '98765 43210'
                  }
                  className="flex-1 px-4 py-3 border-2 border-amber-400 rounded-r-lg bg-amber-50 focus:outline-none focus:border-white focus:ring-1 focus:ring-white text-amber-900 placeholder-amber-600"
                  disabled={isLoading}
                />
              </div>
              <p className="text-lg text-health-600 mt-1">
                {language === 'HI'
                  ? '10 अंकों का नंबर'
                  : language === 'PA'
                  ? '10 ਅੰਕ'
                  : '10 digits'}
              </p>
            </div>

            {/* Login Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full mt-6 py-3 bg-amber-700 hover:bg-amber-800 disabled:bg-neutral-400 text-white font-bold rounded-lg transition transform active:scale-95 flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>
                    {language === 'HI'
                      ? 'लोड हो रहा है...'
                      : language === 'PA'
                      ? 'ਲੋਡ ਹੋ ਰਿਹਾ ਹੈ...'
                      : 'Loading...'}
                  </span>
                </>
              ) : (
                <>
                  <span>
                    {language === 'HI'
                      ? 'शुरू करें'
                      : language === 'PA'
                      ? 'ਸ਼ੁਰੂ ਕਰੋ'
                      : 'Get Started'}
                  </span>
                  <span>→</span>
                </>
              )}
            </button>
          </form>

          {/* Disclaimer */}
          <p className="text-xs text-amber-100 mt-6 text-center">
            {language === 'HI'
              ? 'यह एक प्रदর्शन संस्करण है। आपके डेटा सुरक्षित है।'
              : language === 'PA'
              ? 'ਇਹ ਇੱਕ ਡੈਮੋ ਹੈ। ਤੁਹਾਡਾ ਡੇਟਾ ਸੁਰੱਖਿਅਤ ਹੈ।'
              : 'This is a demo version. Your data is secure.'}
          </p>
        </div>

        {/* Footer */}
        <div className="text-center text-white mt-8 text-sm opacity-75">
          <p>
            {language === 'HI'
              ? '© 2025 Arogya Manthan | आरोग्य मंथन - स्वास्थ्य सेवा'
              : language === 'PA'
              ? '© 2025 Arogya Manthan | ਆਰੋਗਿਆ ਮੰਥਨ - ਸਿਹਤ ਸੇਵਾ'
              : '© 2025 Arogya Manthan | Health Service'}
          </p>
        </div>
      </div>
    </div>
  );
};
