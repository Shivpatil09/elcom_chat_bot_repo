import React from 'react';

const LoadingIndicator: React.FC = () => {
  return (
    <div className="flex justify-start animate-fade-in">
      <div className="bg-gray-100 rounded-2xl px-4 py-3 flex items-center space-x-1.5">
        <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse" style={{ animationDelay: '0ms' }} />
        <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse" style={{ animationDelay: '300ms' }} />
        <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse" style={{ animationDelay: '600ms' }} />
      </div>
    </div>
  );
};

export default LoadingIndicator; 