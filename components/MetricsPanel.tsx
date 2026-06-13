import React, { useState } from 'react';

interface MetricsPanelProps {
  metrics: any;
  isOpen: boolean;
  onClose: () => void;
}

export const MetricsPanel: React.FC<MetricsPanelProps> = ({ metrics, isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'classification' | 'coverage' | 'diagnoses'>('overview');

  if (!isOpen || !metrics) {
    return null;
  }

  const tabs = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'classification', label: 'Classification', icon: '📈' },
    { id: 'coverage', label: 'Coverage', icon: '📋' },
    { id: 'diagnoses', label: 'Top Diagnoses', icon: '🏆' }
  ];

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="w-full max-w-4xl max-h-96 overflow-y-auto bg-gradient-to-br from-[#8B6F47] to-[#6B4423] dark:from-[#5C4033] dark:to-[#3D2817] backdrop-blur-xl rounded-3xl border border-[#A0826D] shadow-2xl p-6 animate-fadeIn">
        
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-4xl font-bold text-white flex items-center gap-2">
            📊 Evaluation Metrics
          </h2>
          <button
            onClick={onClose}
            className="text-3xl font-bold text-white hover:text-gray-200 transition"
          >
            ×
          </button>
        </div>

        {/* Tabs */}
          <div className="flex flex-wrap gap-2 mb-6 border-b border-[#A0826D] pb-4">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-5 py-3 rounded-lg font-bold text-lg transition transform hover:scale-105 ${
                activeTab === tab.id
                  ? 'bg-gradient-to-r from-[#9D7D54] to-[#7D5433] text-white shadow-lg'
                  : 'bg-[#A0956D] text-white hover:bg-[#9D8860]'
              }`}
            >
              {tab.icon} {tab.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="space-y-4 max-h-64 overflow-y-auto">
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="space-y-3">
              <h3 className="text-3xl font-bold text-white">Evaluation Summary</h3>
              <div className="grid grid-cols-2 gap-4">
                <MetricCard 
                  label="Model Type" 
                  value={metrics.model_type || 'Unknown'} 
                  color="blue" 
                />
                <MetricCard 
                  label="Best Diagnosis" 
                  value={metrics.best_diagnosis || 'N/A'} 
                  color="green" 
                />
                <MetricCard 
                  label="Contextual Accuracy" 
                  value={`${(metrics.contextual_accuracy * 100).toFixed(2)}%`} 
                  color="purple" 
                  tooltip="Based on how well your symptoms match the diagnosis"
                />
                <MetricCard 
                  label="Confidence Score" 
                  value={`${(metrics.confidence_score * 100).toFixed(2)}%`} 
                  color="orange" 
                />
                <MetricCard 
                  label="Extracted Symptoms" 
                  value={metrics.extracted_symptoms_count || 0} 
                  color="cyan" 
                />
                <MetricCard 
                  label="Matched Symptoms" 
                  value={`${metrics.matched_symptoms_count || 0} / ${metrics.total_disease_symptoms || 0}`} 
                  color="emerald" 
                />
              </div>
            </div>
          )}

          {/* Classification Tab */}
          {activeTab === 'classification' && (
            <div className="space-y-3">
              <h3 className="text-3xl font-bold text-white">Classification Metrics</h3>
              <div className="grid grid-cols-2 gap-4">
                <MetricCard 
                  label="Precision" 
                  value={`${(metrics.precision * 100).toFixed(2)}%`} 
                  color="blue" 
                />
                <MetricCard 
                  label="Recall" 
                  value={`${(metrics.recall * 100).toFixed(2)}%`} 
                  color="green" 
                />
                <MetricCard 
                  label="F1-Score" 
                  value={`${(metrics.f1_score * 100).toFixed(2)}%`} 
                  color="purple" 
                />
                <MetricCard 
                  label="Sensitivity" 
                  value={`${(metrics.sensitivity * 100).toFixed(2)}%`} 
                  color="orange" 
                />
                <MetricCard 
                  label="Specificity" 
                  value={`${(metrics.specificity * 100).toFixed(2)}%`} 
                  color="red" 
                />
                <MetricCard 
                  label="Diagnosis Separation" 
                  value={`${(metrics.diagnosis_separation * 100).toFixed(2)}%`} 
                  color="cyan" 
                />
              </div>
            </div>
          )}

          {/* Coverage Tab */}
          {activeTab === 'coverage' && (
            <div className="space-y-3">
              <h3 className="text-3xl font-bold text-white">Coverage & Entropy Analysis</h3>
              <div className="grid grid-cols-2 gap-4">
                <MetricCard 
                  label="Symptom Coverage" 
                  value={`${(metrics.symptom_coverage * 100).toFixed(2)}%`} 
                  color="blue" 
                />
                <MetricCard 
                  label="Symptom Match %" 
                  value={`${metrics.symptom_match_percentage?.toFixed(2) || '0.00'}%`} 
                  color="green" 
                />
                <MetricCard 
                  label="Top-5 Match Rate" 
                  value={`${(metrics.top_5_match_rate * 100).toFixed(2)}%`} 
                  color="purple" 
                />
                <MetricCard 
                  label="Match Count Ratio" 
                  value={`${(metrics.match_count_ratio * 100).toFixed(2)}%`} 
                  color="orange" 
                />
                <MetricCard 
                  label="KPE (Entropy)" 
                  value={`${metrics.kpe_entropy?.toFixed(4) || '0.0000'}`} 
                  color="red" 
                />
                <MetricCard 
                  label="KDE (Density)" 
                  value={`${metrics.kde_density?.toFixed(4) || '0.0000'}`} 
                  color="cyan" 
                />
              </div>
            </div>
          )}

          {/* Top Diagnoses Tab */}
          {activeTab === 'diagnoses' && (
            <div className="space-y-3">
              <h3 className="text-3xl font-bold text-white">Top 5 Diagnoses</h3>
              {metrics.top_5_diagnoses && metrics.top_5_diagnoses.length > 0 ? (
                <div className="space-y-2">
                  {metrics.top_5_diagnoses.map((diagnosis: any, idx: number) => (
                    <div
                      key={idx}
                      className="bg-white/10 dark:bg-gray-800/30 border border-white/20 dark:border-gray-700/30 rounded-lg p-3 hover:bg-white/20 dark:hover:bg-gray-800/40 transition"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <span className="font-bold text-purple-600 dark:text-purple-400 w-6">#{idx + 1}</span>
                          <div>
                            <p className="font-bold text-2xl text-white">{diagnosis.name || 'Unknown'}</p>
                            <p className="text-base text-blue-800">
                              {diagnosis.match_count || 0} matches
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <span className="text-lg font-bold text-pink-600">{diagnosis.match_count || 0}</span>
                          <p className="text-base text-blue-800">symptoms matched</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-lg text-blue-800">No diagnoses available</p>
              )}
            </div>
          )}
        </div>

        {/* Model Info */}
        <div className="mt-6 pt-6 border-t border-white/20 dark:border-gray-700/30">
          <div className="text-base text-blue-800">
            <p className="mb-2"><strong>Model:</strong> {metrics.model_type || 'Unknown'}</p>
            <p><strong>Timestamp:</strong> {metrics.timestamp ? new Date(metrics.timestamp).toLocaleString() : 'N/A'}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

interface MetricCardProps {
  label: string;
  value: string | number;
  color: 'blue' | 'green' | 'purple' | 'orange' | 'red' | 'emerald' | 'cyan' | 'yellow' | 'amber';
  tooltip?: string;
}

const MetricCard: React.FC<MetricCardProps> = ({ label, value, color, tooltip }) => {
  const [showTooltip, setShowTooltip] = React.useState(false);
  
  const colorClasses = {
    blue: 'bg-blue-600 border-blue-500 text-white',
    green: 'bg-green-600 border-green-500 text-white',
    purple: 'bg-purple-600 border-purple-500 text-white',
    orange: 'bg-orange-600 border-orange-500 text-white',
    red: 'bg-red-600 border-red-500 text-white',
    emerald: 'bg-emerald-600 border-emerald-500 text-white',
    cyan: 'bg-cyan-600 border-cyan-500 text-white',
    yellow: 'bg-yellow-600 border-yellow-500 text-white',
    amber: 'bg-amber-600 border-amber-500 text-white'
  };

  return (
    <div 
      className={`${colorClasses[color]} border-2 rounded-lg p-4 backdrop-blur-sm hover:scale-105 transition transform relative group`}
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      <p className="text-lg font-bold opacity-90">{label}</p>
      <p className="text-3xl font-bold mt-2 text-white">{value}</p>
      
      {tooltip && showTooltip && (
        <div className="absolute -top-12 left-1/2 transform -translate-x-1/2 bg-gray-900 text-white text-xs px-3 py-2 rounded-lg whitespace-nowrap z-50 animate-slideDown">
          {tooltip}
          <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-l-transparent border-r-transparent border-t-gray-900"></div>
        </div>
      )}
    </div>
  );
};

export default MetricsPanel;

const styles = `
  @keyframes slideDown {
    from {
      opacity: 0;
      transform: translate(-50%, -20px);
    }
    to {
      opacity: 1;
      transform: translate(-50%, 0);
    }
  }

  .animate-slideDown {
    animation: slideDown 0.2s ease-out;
  }
`;

// Add styles to document
if (typeof document !== 'undefined') {
  const styleSheet = document.createElement('style');
  styleSheet.textContent = styles;
  document.head.appendChild(styleSheet);
}
