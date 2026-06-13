import React from 'react';

interface MetricProps {
  label: string;
  value: string | number;
  unit?: string;
  icon: string;
}

interface MedicineMetricsDisplayProps {
  metrics?: {
    total_searches: number;
    successful_matches: number;
    average_price: number;
    pharmacies_nearby: number;
  };
}

const MedicineMetricsDisplay: React.FC<MedicineMetricsDisplayProps> = ({
  metrics = {
    total_searches: 0,
    successful_matches: 0,
    average_price: 0,
    pharmacies_nearby: 0,
  },
}) => {
  const metricsList: MetricProps[] = [
    {
      label: 'Total Searches',
      value: metrics.total_searches,
      icon: '🔍',
    },
    {
      label: 'Matched Medicines',
      value: metrics.successful_matches,
      icon: '✓',
    },
    {
      label: 'Average Price',
      value: `₹${metrics.average_price.toFixed(2)}`,
      icon: '💰',
    },
    {
      label: 'Pharmacies Nearby',
      value: metrics.pharmacies_nearby,
      icon: '🏪',
    },
  ];

  return (
    <div className="bg-gradient-to-r from-amber-50 to-orange-50 dark:from-gray-800 dark:to-gray-700 rounded-lg p-6 mb-6">
      <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-6">📊 Medicine Search Metrics</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {metricsList.map((metric, idx) => (
          <div key={idx} className="bg-neutral-50 rounded-lg p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">{metric.label}</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {metric.value} {metric.unit}
                </p>
              </div>
              <div className="text-3xl">{metric.icon}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MedicineMetricsDisplay;
