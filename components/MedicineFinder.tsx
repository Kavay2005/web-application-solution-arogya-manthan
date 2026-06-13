import React, { useState } from 'react';
import MedicineAvailability from './MedicineAvailability';

interface MedicineFinderProps {
  texts: { [key: string]: string };
}

const MedicineFinder: React.FC<MedicineFinderProps> = ({ texts }) => {
  const [view, setView] = useState<'search' | 'availability'>('search');

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-100 to-yellow-50 dark:from-gray-900 dark:to-gray-800 p-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-4 mb-4">
            <svg className="w-16 h-16" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
              {/* Medical Cross */}
              <rect x="30" y="70" width="140" height="60" fill="none"/>
              {/* Vertical bar of cross */}
              <rect x="80" y="30" width="40" height="140" fill="#8B6F47" rx="8"/>
              {/* Horizontal bar of cross */}
              <rect x="30" y="80" width="140" height="40" fill="#8B6F47" rx="8"/>
              
              {/* Green Leaf */}
              <g transform="translate(120, 60)">
                {/* Leaf shape */}
                <path d="M 0 -10 Q 15 0 10 20 Q 5 15 0 20 Q -5 15 -10 20 Q -15 0 0 -10" fill="#9B8B48" stroke="#8B6F47" strokeWidth="1.5"/>
                {/* Leaf vein */}
                <line x1="0" y1="-10" x2="0" y2="20" stroke="#8B6F47" strokeWidth="1" opacity="0.6"/>
              </g>
            </svg>
            <div>
              <h1 className="text-5xl font-bold text-white mb-2">Medicine Finder</h1>
              <p className="text-2xl text-white">
                Find nearby pharmacies and check medicine availability
              </p>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex gap-4 mb-6">
          <button
            onClick={() => setView('search')}
            className={`px-6 py-3 rounded-lg font-semibold text-lg transition ${
              view === 'search'
                ? 'bg-amber-700 text-white shadow-lg'
                : 'bg-amber-100 text-amber-900 border-2 border-amber-400'
            }`}
          >
            Search Nearby
          </button>
          <button
            onClick={() => setView('availability')}
            className={`px-6 py-3 rounded-lg font-semibold text-lg transition ${
              view === 'availability'
                ? 'bg-amber-700 text-white shadow-lg'
                : 'bg-amber-100 text-amber-900 border-2 border-amber-400'
            }`}
          >
            Check Availability
          </button>
        </div>

        {/* Search View */}
        {view === 'search' && (
          <div className="bg-amber-100 rounded-lg shadow-lg p-8">
            <h2 className="text-4xl font-bold mb-6 text-amber-900">Find Pharmacies Near You</h2>
            <p className="text-xl text-amber-800 mb-4">
              Enable location access to find nearby pharmacies and medical shops.
            </p>
            <button
              onClick={() => {
                if (navigator.geolocation) {
                  navigator.geolocation.getCurrentPosition(
                    (position) => {
                      const lat = position.coords.latitude;
                      const lon = position.coords.longitude;
                      const mapsUrl = `https://www.google.com/maps/search/pharmacy/@${lat},${lon},15z`;
                      window.open(mapsUrl, '_blank');
                    },
                    () => alert('Location access denied')
                  );
                }
              }}
              className="px-6 py-3 bg-amber-700 text-white rounded-lg hover:bg-amber-800 transition"
            >
              📍 Find Nearby Pharmacies
            </button>
          </div>
        )}

        {/* Availability View */}
        {view === 'availability' && <MedicineAvailability texts={texts} />}
      </div>
    </div>
  );
};

export default MedicineFinder;
