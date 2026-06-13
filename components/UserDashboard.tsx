import React, { useState } from 'react';
import { Language } from '../types';

interface UserProfile {
  name: string;
  phone: string;
  age?: number;
  gender?: string;
  location?: string;
  lastVisit?: string;
}

interface UserDashboardProps {
  language: Language;
  texts: { [key: string]: string };
  user?: UserProfile | null;
  onLogout?: () => void;
}

export const UserDashboard: React.FC<UserDashboardProps> = ({
  language,
  texts,
  user,
  onLogout,
}) => {
  const [isOpen, setIsOpen] = useState(false);

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (language === 'HI') {
      if (hour < 12) return 'सुप्रभात';
      if (hour < 18) return 'नमस्ते';
      return 'शुभ संध्या';
    } else if (language === 'PA') {
      if (hour < 12) return 'ਸਵੇਰ';
      if (hour < 18) return 'ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ';
      return 'ਸ਼ਾਮ';
    } else {
      if (hour < 12) return 'Good Morning';
      if (hour < 18) return 'Hello';
      return 'Good Evening';
    }
  };

  return (
    <>
      {/* Mobile Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed top-4 left-4 z-50 md:hidden p-2 bg-primary-600 text-white rounded-lg"
      >
        <span className="text-xl">👤</span>
      </button>

      {/* Sidebar Overlay (Mobile) */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div
        className={`fixed left-0 top-0 h-screen w-64 bg-blue-100 border-r border-blue-300 z-40 transition-transform transform ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        } md:translate-x-0 md:relative md:w-64 overflow-y-auto`}
      >
        {/* Header */}
        <div className="bg-gradient-to-b from-primary-600 to-primary-700 text-white p-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <svg className="w-8 h-8" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
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
              <h2 className="text-lg font-bold text-white">Arogya Manthan</h2>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="md:hidden text-xl"
            >
              ✕
            </button>
          </div>
          <p className="text-primary-100 text-sm">
            {language === 'HI'
              ? 'ग्रामीण स्वास्थ्य सेवा'
              : language === 'PA'
              ? 'ਪਿੰਡ ਸਿਹਤ ਸੇਵਾ'
              : 'Rural Health Service'}
          </p>
        </div>

        {/* User Profile Section */}
        {user ? (
          <div className="p-4 border-b border-blue-200 dark:border-gray-700">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-full bg-health-600 text-white flex items-center justify-center text-lg font-bold">
                {user.name?.charAt(0).toUpperCase() || 'U'}
              </div>
              <div className="flex-1">
                <p className="font-semibold text-blue-900 text-base">
                  {user.name}
                </p>
                <p className="text-sm text-blue-600 dark:text-gray-400">
                  {user.phone}
                </p>
              </div>
            </div>

            {/* User Details Grid */}
            <div className="space-y-2 text-sm">
              {user.age && (
                <div className="bg-primary-50 dark:bg-primary-900/20 p-2 rounded">
                  <p className="text-xs text-blue-700">
                    {language === 'HI'
                      ? 'आयु'
                      : language === 'PA'
                      ? 'ਉਮਰ'
                      : 'Age'}
                  </p>
                  <p className="font-semibold text-blue-900">
                    {user.age} {language === 'HI' ? 'वर्ष' : language === 'PA' ? 'ਸਾਲ' : 'years'}
                  </p>
                </div>
              )}

              {user.gender && (
                <div className="bg-health-50 dark:bg-health-900/20 p-2 rounded">
                  <p className="text-xs text-blue-700">
                    {language === 'HI'
                      ? 'लिंग'
                      : language === 'PA'
                      ? 'ਲਿਂਗ'
                      : 'Gender'}
                  </p>
                  <p className="font-semibold text-blue-900">
                    {user.gender === 'M'
                      ? language === 'HI'
                        ? 'पुरुष'
                        : language === 'PA'
                        ? 'ਮਰਦ'
                        : 'Male'
                      : language === 'HI'
                      ? 'महिला'
                      : language === 'PA'
                      ? 'ਔਰਤ'
                      : 'Female'}
                  </p>
                </div>
              )}

              {user.location && (
                <div className="bg-warning-50 dark:bg-warning-900/20 p-2 rounded">
                  <p className="text-xs text-neutral-600 dark:text-gray-400">
                    {language === 'HI'
                      ? 'स्थान'
                      : language === 'PA'
                      ? 'ਸਥਾਨ'
                      : 'Location'}
                  </p>
                  <p className="font-semibold text-neutral-900 dark:text-white truncate">
                    {user.location}
                  </p>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="p-4 text-center text-base text-blue-800">
            {language === 'HI'
              ? 'लॉगिन करें'
              : language === 'PA'
              ? 'ਲਾਗਇਨ ਕਰੋ'
              : 'Please login'}
          </div>
        )}

        {/* Quick Stats */}
        <div className="p-4 space-y-3 border-b border-blue-200 dark:border-gray-700">
          <div className="text-sm font-semibold text-blue-900 uppercase">
            📊 {language === 'HI' ? 'सारांश' : language === 'PA' ? 'ਸਾਰ' : 'Summary'}
          </div>
          <div className="grid grid-cols-2 gap-2">
            <div className="bg-primary-50 dark:bg-primary-900/20 p-3 rounded-lg text-center">
              <p className="text-2xl font-bold text-primary-600">3</p>
              <p className="text-xs text-neutral-600 dark:text-gray-400">
                {language === 'HI'
                  ? 'जांच'
                  : language === 'PA'
                  ? 'ਜਾਂਚ'
                  : 'Check-ups'}
              </p>
            </div>
            <div className="bg-health-50 dark:bg-health-900/20 p-3 rounded-lg text-center">
              <p className="text-2xl font-bold text-health-600">5</p>
              <p className="text-xs text-neutral-600 dark:text-gray-400">
                {language === 'HI'
                  ? 'रिकॉर्ड'
                  : language === 'PA'
                  ? 'ਰਿਕਾਰਡ'
                  : 'Records'}
              </p>
            </div>
          </div>
        </div>

        {/* Menu Items */}
        <div className="p-4 space-y-2">
          {user && (
            <button
              onClick={onLogout}
              className="w-full px-4 py-2 bg-emergency-600 hover:bg-emergency-700 text-white rounded-lg text-sm font-medium transition"
            >
              {language === 'HI'
                ? 'लॉगआउट'
                : language === 'PA'
                ? 'Logout'
                : 'Logout'}
            </button>
          )}
        </div>

        {/* Footer */}
        <div className="absolute bottom-4 left-4 right-4 text-sm text-blue-800 text-center">
          <p>
            {language === 'HI'
              ? 'संस्करण 1.0'
              : language === 'PA'
              ? 'ਸੰਸਕਰਣ 1.0'
              : 'v1.0'}
          </p>
        </div>
      </div>
    </>
  );
};
