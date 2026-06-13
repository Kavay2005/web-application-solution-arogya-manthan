import React, { useState } from 'react';

interface MedicineAvailabilityProps {
  texts: { [key: string]: string };
}

interface MedicineResult {
  medicine_name: string;
  available: boolean;
  nearest_store: string;
  distance: number;
  price: number;
  store_details: {
    name: string;
    address: string;
    phone: string;
  };
}

const MedicineAvailability: React.FC<MedicineAvailabilityProps> = ({ texts }) => {
  const [medicineName, setMedicineName] = useState('');
  const [results, setResults] = useState<MedicineResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [location, setLocation] = useState<{ latitude: number; longitude: number } | null>(null);

  React.useEffect(() => {
    // Get user's location
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLocation({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
          });
        },
        (err) => {
          console.log('Location access denied');
        }
      );
    }
  }, []);

  const handleSearch = async () => {
    if (!medicineName.trim()) {
      setError('Please enter a medicine name');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:5000/api/medicine-search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          medicine_name: medicineName,
          lat: location?.latitude,
          lon: location?.longitude,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to search medicines');
      }

      const data = await response.json();
      
      if (data.success) {
        setResults(data.results || []);
        if (data.results && data.results.length === 0) {
          setError(`No medicines found matching "${medicineName}". Try a different name.`);
        }
      } else {
        setError(data.message || data.error || 'Failed to fetch medicine data');
        setResults([]);
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'An error occurred';
      setError(errorMsg);
      setResults([]);
      console.error('Medicine search error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-yellow-100 rounded-lg shadow-lg">
      <h2 className="text-4xl font-bold mb-6 text-amber-900">💊 Medicine Availability</h2>

      <div className="mb-6">
        <div className="flex gap-2 mb-4">
          <input
            type="text"
            value={medicineName}
            onChange={(e) => setMedicineName(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="Enter medicine name..."
            className="flex-grow p-3 border border-amber-400 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-amber-500 text-base"
          />
          <button
            onClick={handleSearch}
            disabled={loading}
            className="px-6 py-3 bg-amber-700 text-white rounded-lg hover:bg-amber-800 disabled:bg-gray-400 transition"
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
        {location && (
          <p className="text-lg text-amber-800">
            📍 Searching near: {location.latitude.toFixed(4)}, {location.longitude.toFixed(4)}
          </p>
        )}
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 rounded-lg">
          {error}
        </div>
      )}

      <div className="space-y-4">
        {results.map((result, index) => (
          <div
            key={index}
            className={`p-4 border rounded-lg ${
              result.available
                ? 'border-green-200 bg-green-50 dark:bg-green-900 dark:border-green-700'
                : 'border-red-200 bg-red-50 dark:bg-red-900 dark:border-red-700'
            }`}
          >
            <div className="flex justify-between items-start">
              <div>
                <h3 className="text-2xl font-bold text-amber-900">
                  {result.medicine_name}
                </h3>
                <p className={`text-lg font-semibold ${result.available ? 'text-green-700' : 'text-red-700'}`}>
                  {result.available ? '✓ Available' : '✗ Not Available'}
                </p>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold text-amber-900">₹{result.price}</p>
                <p className="text-lg text-amber-800">{result.distance} km away</p>
              </div>
            </div>

            {result.available && result.store_details && (
              <div className="mt-3 pt-3 border-t border-amber-400">
                <p className="font-semibold text-lg text-amber-900">{result.store_details.name}</p>
                <p className="text-lg text-amber-800">{result.store_details.address}</p>
                <p className="text-lg text-amber-800">📞 {result.store_details.phone}</p>
              </div>
            )}
          </div>
        ))}
      </div>

      {results.length === 0 && !loading && (
        <div className="text-center py-8 text-lg text-amber-800">
          Enter a medicine name and click search to find availability
        </div>
      )}
    </div>
  );
};

export default MedicineAvailability;
