
import type { ReactNode } from 'react';
import React from 'react';

interface FeatureCardProps {
  icon: ReactNode;
  title: string;
  description: string;
  onClick: () => void;
}

const FeatureCard: React.FC<FeatureCardProps> = ({ icon, title, description, onClick }) => {
  return (
    <div
      className="bg-[#FF9500] rounded-xl shadow-lg p-6 flex flex-col items-start space-y-4 cursor-pointer hover:bg-[#E68900] transition-all duration-300 transform hover:-translate-y-1"
      onClick={onClick}
    >
      {title === 'Find Medicine' ? (
        <svg className="w-12 h-12" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
          {/* Medical Cross */}
          <rect x="30" y="70" width="140" height="60" fill="none"/>
          {/* Vertical bar of cross */}
          <rect x="80" y="30" width="40" height="140" fill="#1e88e5" rx="8"/>
          {/* Horizontal bar of cross */}
          <rect x="30" y="80" width="140" height="40" fill="#1e88e5" rx="8"/>
          
          {/* Green Leaf */}
          <g transform="translate(120, 60)">
            {/* Leaf shape */}
            <path d="M 0 -10 Q 15 0 10 20 Q 5 15 0 20 Q -5 15 -10 20 Q -15 0 0 -10" fill="#26c6da" stroke="#1e88e5" strokeWidth="1.5"/>
            {/* Leaf vein */}
            <line x1="0" y1="-10" x2="0" y2="20" stroke="#1e88e5" strokeWidth="1" opacity="0.6"/>
          </g>
        </svg>
      ) : (
        <div className="bg-health-600 dark:bg-health-600 text-white p-3 rounded-full">
          {icon}
        </div>
      )}
      <h3 className="text-4xl font-bold text-amber-100">{title}</h3>
      <p className="text-2xl text-amber-100">{description}</p>
    </div>
  );
};

export default FeatureCard;
