import React from 'react';

interface ChatHeaderProps {
  onClose: () => void;
  onMinimize: () => void;
  onToggleFullScreen: () => void;
  isMinimized: boolean;
  isFullScreen: boolean;
}

const ChatHeader: React.FC<ChatHeaderProps> = ({ 
  onClose, 
  onMinimize, 
  onToggleFullScreen,
  isMinimized,
  isFullScreen 
}) => {
  return (
    <div className="px-4 py-2.5 border-b border-gray-100 flex items-center justify-between bg-white shadow-sm">
      <div className="flex items-center space-x-3">
        <div className="w-8 h-8 flex items-center justify-center">
          <svg 
            viewBox="0 0 32 32" 
            className="w-7 h-7"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M2 16C2 8.268 8.268 2 16 2s14 6.268 14 14c0 3.177-1.075 6.103-2.879 8.459l.544 4.354a1.5 1.5 0 01-1.682 1.682l-4.354-.544A13.936 13.936 0 0116 30C8.268 30 2 23.732 2 16z"
              fill="#2563EB"
            />
            <path
              d="M12 11h8v2h-8v-2zm0 4h8v2h-8v-2z"
              fill="#FFFFFF"
            />
          </svg>
        </div>
        <div>
          <h2 className="text-base font-semibold text-gray-800">Chat with us</h2>
          <span className="text-xs text-green-500">Online</span>
        </div>
      </div>
      <div className="flex items-center space-x-0.5">
        <button
          className="p-2 hover:bg-gray-50 rounded-full transition-colors group"
          onClick={onMinimize}
          aria-label={isMinimized ? "Maximize chat" : "Minimize chat"}
        >
          <svg
            className="w-5 h-5 text-gray-500 transition-transform duration-200 group-hover:scale-110"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            {isMinimized ? (
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 8h16M4 16h16"
              />
            ) : (
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M20 12H4"
              />
            )}
          </svg>
        </button>
        <button
          className="p-2 hover:bg-gray-50 rounded-full transition-colors group"
          onClick={onToggleFullScreen}
          aria-label={isFullScreen ? "Exit full screen" : "Enter full screen"}
        >
          <svg
            className="w-5 h-5 text-gray-500 transition-transform duration-200 group-hover:scale-110"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            {isFullScreen ? (
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 14h6m0 0v6m0-6L4 20M20 10h-6m0 0V4m0 6l6-6"
              />
            ) : (
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 8V4m0 0h4M4 4l5 5m11-5v4m0-4h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5v-4m0 4h-4m4 0l-5-5"
              />
            )}
          </svg>
        </button>
        <button
          onClick={onClose}
          className="p-2 hover:bg-gray-50 rounded-full transition-colors group"
          aria-label="Close chat"
        >
          <svg
            className="w-5 h-5 text-gray-500 transition-transform duration-200 group-hover:scale-110"
            fill="currentColor"
            viewBox="0 0 24 24"
          >
            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" />
          </svg>
        </button>
      </div>
    </div>
  );
};

export default ChatHeader;