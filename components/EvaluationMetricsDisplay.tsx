import React, { useState } from 'react';

interface MetricsData {
  [key: string]: any;
}

interface EvaluationMetricsDisplayProps {
  metrics?: MetricsData | null;
  isLoading?: boolean;
  title?: string;
}

export const EvaluationMetricsDisplay: React.FC<EvaluationMetricsDisplayProps> = ({
  metrics,
  isLoading = false,
  title = '📊 Evaluation Metrics'
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [hoveredMetric, setHoveredMetric] = useState<string | null>(null);

  if (!metrics && !isLoading) {
    return null;
  }

  const MetricCard: React.FC<{ 
    label: string; 
    value: string | number; 
    unit?: string;
    color?: string;
    tooltip?: string;
  }> = ({ label, value, unit = '', color = 'from-blue-500 to-cyan-500', tooltip }) => (
    <div
      className={`group relative backdrop-blur-md bg-gradient-to-br ${color} bg-opacity-10 rounded-lg p-4 border border-white/20 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:scale-105 hover:border-white/40`}
      onMouseEnter={() => setHoveredMetric(label)}
      onMouseLeave={() => setHoveredMetric(null)}
    >
      {/* Glassmorphism effect */}
      <div className="absolute inset-0 rounded-lg bg-gradient-to-br from-white/10 to-transparent pointer-events-none"></div>
      
      <div className="relative z-10">
        <p className="font-semibold text-blue-900 mb-2" style={{fontSize: '0.875rem'}}>{label}</p>
        <p className="font-bold bg-gradient-to-r from-health-600 to-emergency-600 bg-clip-text text-transparent" style={{fontSize: '1.875rem'}}>
          {value}
          {unit && <span className="ml-1" style={{fontSize: '1.125rem'}}>{unit}</span>}
        </p>
      </div>

      {/* Hover tooltip */}
      {tooltip && hoveredMetric === label && (
        <div className="absolute -top-12 left-1/2 transform -translate-x-1/2 bg-amber-900 text-white text-xs px-3 py-2 rounded-lg whitespace-nowrap z-50 animate-slideDown">
          {tooltip}
          <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-l-transparent border-r-transparent border-t-neutral-900"></div>
        </div>
      )}
    </div>
  );

  return (
    <div className="mt-6 space-y-4">
      {/* Main Container with Glassmorphism */}
      <div className="backdrop-blur-xl bg-gradient-to-br from-white/10 via-health-500/5 to-emergency-500/5 rounded-2xl border border-white/30 shadow-2xl overflow-hidden">
        {/* Header */}
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full flex items-center justify-between p-6 hover:bg-white/5 transition-colors duration-200 group"
        >
          <div className="flex items-center gap-3">
            <div style={{fontSize: '1.875rem'}} className="group-hover:scale-110 transition-transform duration-300">{title.split('-')[0]}</div>
            <h3 className="font-bold bg-gradient-to-r from-health-600 to-emergency-600 bg-clip-text text-transparent" style={{fontSize: '1.25rem'}}>
              {title.split('-').slice(1).join('-').trim()}
            </h3>
          </div>
          <span
            style={{fontSize: '1.4rem'}}
            className={`transition-all duration-300 ${
              isExpanded ? 'rotate-180' : ''
            } group-hover:scale-125`}
          >
            ▼
          </span>
        </button>

        {/* Divider */}
        <div className="h-px bg-gradient-to-r from-transparent via-white/30 to-transparent"></div>

        {/* Content */}
        {isExpanded && (
          <div className="p-6 space-y-6 animate-fadeIn">
            {isLoading ? (
              <div className="flex items-center justify-center py-8">
                <div className="relative w-8 h-8">
                  <div className="absolute inset-0 rounded-full border-4 border-neutral-400"></div>
                  <div className="absolute inset-0 rounded-full border-4 border-transparent border-t-health-600 border-r-emergency-600 animate-spin"></div>
                </div>
                <span className="ml-3 text-health-700 font-semibold">Loading metrics...</span>
              </div>
            ) : (
              <>
                {/* Classification Report */}
                {metrics?.classification_report && (
                  <div className="space-y-4">
                    <h4 className="font-bold uppercase tracking-wider text-blue-800 flex items-center gap-2" style={{fontSize: '0.875rem'}}>
                      <span style={{fontSize: '1.125rem'}}>📋</span> Classification Report
                    </h4>
                    <div className="grid grid-cols-2 gap-3">
                      <MetricCard
                        label="Precision"
                        value={(metrics.classification_report.precision * 100).toFixed(2)}
                        unit="%"
                        color="from-primary-600 to-health-600"
                        tooltip="Accuracy of positive predictions"
                      />
                      <MetricCard
                        label="Recall"
                        value={(metrics.classification_report.recall * 100).toFixed(2)}
                        unit="%"
                        color="from-health-600 to-health-700"
                        tooltip="Coverage of disease symptoms"
                      />
                      <MetricCard
                        label="F1-Score"
                        value={metrics.classification_report.f1_score.toFixed(4)}
                        color="from-warning-600 to-warning-500"
                        tooltip="Harmonic mean of precision & recall"
                      />
                      <MetricCard
                        label="Accuracy"
                        value={(metrics.classification_report.accuracy * 100).toFixed(2)}
                        unit="%"
                        color="from-emergency-600 to-emergency-700"
                        tooltip="Overall classification accuracy"
                      />
                    </div>
                  </div>
                )}

                {/* Confusion Matrix */}
                {metrics?.confusion_matrix && (
                  <div className="space-y-4">
                    <h4 className="font-bold uppercase tracking-wider text-blue-800 flex items-center gap-2" style={{fontSize: '0.875rem'}}>
                      <span style={{fontSize: '1.125rem'}}>🔲</span> Confusion Matrix
                    </h4>
                    <div className="grid grid-cols-2 gap-3">
                      <MetricCard
                        label="True Positives"
                        value={metrics.confusion_matrix.true_positives}
                        color="from-health-600 to-health-700"
                        tooltip="Correctly identified symptoms"
                      />
                      <MetricCard
                        label="False Positives"
                        value={metrics.confusion_matrix.false_positives}
                        color="from-emergency-500 to-emergency-600"
                        tooltip="Incorrectly identified symptoms"
                      />
                      <MetricCard
                        label="True Negatives"
                        value={metrics.confusion_matrix.true_negatives}
                        color="from-primary-600 to-health-600"
                        tooltip="Correctly rejected symptoms"
                      />
                      <MetricCard
                        label="False Negatives"
                        value={metrics.confusion_matrix.false_negatives}
                        color="from-warning-600 to-warning-500"
                        tooltip="Missed disease symptoms"
                      />
                    </div>
                  </div>
                )}

                {/* Key Metrics */}
                <div className="space-y-4">
                  <h4 className="font-bold uppercase tracking-wider text-blue-700 dark:text-blue-300 flex items-center gap-2" style={{fontSize: '0.875rem'}}>
                    <span style={{fontSize: '1.125rem'}}>📊</span> Key Performance Metrics
                  </h4>
                  <div className="grid grid-cols-2 gap-3">
                    <MetricCard
                      label="Error Rate"
                      value={metrics?.error_rate?.toFixed(2)}
                      unit="%"
                      color="from-emergency-500 to-warning-600"
                      tooltip="Percentage of misclassifications"
                    />
                    <MetricCard
                      label="Response Consistency"
                      value={metrics?.response_consistency?.toFixed(2)}
                      unit="%"
                      color="from-health-600 to-health-700"
                      tooltip="Ranking stability of predictions"
                    />
                    <MetricCard
                      label="Rule Coverage"
                      value={metrics?.rule_coverage_percentage?.toFixed(2)}
                      unit="%"
                      color="from-primary-600 to-health-600"
                      tooltip="Percentage of disease symptoms covered"
                    />
                    <MetricCard
                      label="Sensitivity"
                      value={metrics?.sensitivity?.toFixed(4)}
                      color="from-health-600 to-health-700"
                      tooltip="True positive rate"
                    />
                  </div>
                </div>

                {/* Additional Metrics */}
                <div className="space-y-4">
                  <h4 className="font-bold uppercase tracking-wider text-gray-700 dark:text-gray-300 flex items-center gap-2" style={{fontSize: '8.75rem'}}>
                    <span style={{fontSize: '11.25rem'}}>🎯</span> Additional Metrics
                  </h4>
                  <div className="grid grid-cols-2 gap-3">
                    <MetricCard
                      label="Top-K Accuracy"
                      value={metrics?.top_k_accuracy?.toFixed(2)}
                      unit="%"
                      color="from-health-600 to-health-700"
                      tooltip="Top-5 diagnosis accuracy"
                    />
                    <MetricCard
                      label="Specificity"
                      value={metrics?.specificity?.toFixed(4)}
                      color="from-primary-600 to-health-600"
                      tooltip="True negative rate"
                    />
                    <MetricCard
                      label="KPE (Entropy)"
                      value={metrics?.kpe?.toFixed(4)}
                      color="from-warning-600 to-warning-500"
                      tooltip="Uncertainty measurement"
                    />
                    <MetricCard
                      label="KDE (Density)"
                      value={metrics?.kde?.toFixed(4)}
                      color="from-health-600 to-health-700"
                      tooltip="Probability concentration"
                    />
                  </div>
                </div>

                {/* Diagnosis Information */}
                {metrics?.best_diagnosis && (
                  <div className="space-y-3 pt-4 border-t border-white/20">
                    <h4 className="text-sm font-bold uppercase tracking-wider text-gray-700 dark:text-gray-300">
                      📌 Diagnosis Information
                    </h4>
                    <div className="backdrop-blur-md bg-gradient-to-br from-purple-500/10 to-pink-500/10 rounded-lg p-4 border border-white/20">
                      <div className="space-y-2">
                        <div className="flex justify-between items-center">
                          <span className="text-amber-800">Best Diagnosis:</span>
                          <span className="text-amber-900 font-semibold">{metrics.best_diagnosis}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-amber-800">Matched Symptoms:</span>
                          <span className="font-semibold text-gray-900 dark:text-white">
                            {metrics.symptom_match_count} / {metrics.total_disease_symptoms}
                          </span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-amber-800">Model Type:</span>
                          <span className="font-semibold text-purple-600 dark:text-purple-400">{metrics.model_type}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Top 5 Diagnoses */}
                {metrics?.top_5_diagnoses && metrics.top_5_diagnoses.length > 0 && (
                  <div className="space-y-3 pt-4 border-t border-white/20">
                    <h4 className="font-bold uppercase tracking-wider text-gray-700 dark:text-gray-300" style={{fontSize: '1.375rem'}}>
                      🏆 Top 5 Diagnoses
                    </h4>
                    <div className="space-y-2">
                      {metrics.top_5_diagnoses.map((diagnosis: any, idx: number) => (
                        <div
                          key={idx}
                          className="backdrop-blur-md bg-gradient-to-r from-purple-500/10 to-pink-500/10 rounded-lg p-4 border border-white/20 hover:border-white/40 hover:bg-white/5 transition-all duration-300 transform hover:translate-x-1"
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                              <span className="font-bold w-6" style={{fontSize: '1.375rem', color: '#CD853F'}}>#{diagnosis.rank}</span>
                              <div>
                                <p className="font-semibold" style={{fontSize: '1.375rem', color: '#F5F5DC'}}>{diagnosis.name}</p>
                                <p style={{fontSize: '1.375rem', color: '#F5F5DC'}}>
                                  {diagnosis.match_count} matches • <span style={{color: '#6b7f39'}}>{diagnosis.likelihood}</span>
                                </p>
                              </div>
                            </div>
                            <div className="text-right">
                              <span className="font-bold" style={{fontSize: '1.875rem', color: '#90EE90'}}>{diagnosis.match_count}</span>
                              <p style={{fontSize: '1.375rem', color: '#F5F5DC'}}>matches</p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </div>

      {/* CSS for animations */}
      <style>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

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

        .animate-fadeIn {
          animation: fadeIn 0.3s ease-out;
        }

        .animate-slideDown {
          animation: slideDown 0.2s ease-out;
        }

        /* Glassmorphism gradient background */
        .backdrop-blur-xl {
          background-clip: padding-box;
        }
      `}</style>
    </div>
  );
};

export default EvaluationMetricsDisplay;