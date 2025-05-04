import React, { useRef, useState, useEffect } from 'react';
import ChatHeader from './ChatHeader';
import MessageList from './MessageList';
import ChatInput from './ChatInput';
import { Message } from '../../../types/chat';

interface ChatWindowProps {
  messages: Message[];
  isLoading: boolean;
  onSendMessage: (message: string) => void;
  onClose: () => void;
}

// Constants for window sizing and positioning
const MIN_WIDTH = 300;
const MAX_WIDTH = 600;
const MIN_HEIGHT = 400;
const MAX_HEIGHT = 700;
const WIDGET_SIZE = 56;
const WIDGET_MARGIN = 16;
const WIDGET_AREA_HEIGHT = WIDGET_SIZE + WIDGET_MARGIN * 2;

const ChatWindow: React.FC<ChatWindowProps> = ({
  messages,
  isLoading,
  onSendMessage,
  onClose
}) => {
  const messageListRef = useRef<HTMLDivElement>(null);
  const [isFullScreen, setIsFullScreen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  
  // Initialize with maximum dimensions
  const [size, setSize] = useState({ 
    width: Math.min(MAX_WIDTH, window.innerWidth - WIDGET_MARGIN * 2), 
    height: Math.min(MAX_HEIGHT, window.innerHeight - WIDGET_AREA_HEIGHT - WIDGET_MARGIN)
  });
  
  const [isResizing, setIsResizing] = useState(false);
  const resizingRef = useRef(false);
  const initialPosRef = useRef({ x: 0, y: 0, width: 0, height: 0 });

  // Update size when window is resized
  useEffect(() => {
    const handleWindowResize = () => {
      if (!isFullScreen) {
        setSize(prevSize => ({
          width: Math.min(prevSize.width, window.innerWidth - WIDGET_MARGIN * 2),
          height: Math.min(prevSize.height, window.innerHeight - WIDGET_AREA_HEIGHT - WIDGET_MARGIN)
        }));
      }
    };

    window.addEventListener('resize', handleWindowResize);
    return () => window.removeEventListener('resize', handleWindowResize);
  }, [isFullScreen]);

  const handleMouseDown = (e: React.MouseEvent) => {
    if (isFullScreen) return;
    e.preventDefault();
    setIsResizing(true);
    resizingRef.current = true;
    initialPosRef.current = {
      x: e.clientX,
      y: e.clientY,
      width: size.width,
      height: size.height
    };
  };

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!resizingRef.current) return;

      const deltaX = initialPosRef.current.x - e.clientX;
      const deltaY = initialPosRef.current.y - e.clientY;

      // Calculate new dimensions while respecting min/max constraints
      const newWidth = Math.max(
        MIN_WIDTH,
        Math.min(
          MAX_WIDTH,
          Math.min(window.innerWidth - WIDGET_MARGIN * 2, initialPosRef.current.width + deltaX)
        )
      );
      const newHeight = Math.max(
        MIN_HEIGHT,
        Math.min(
          MAX_HEIGHT,
          Math.min(window.innerHeight - WIDGET_AREA_HEIGHT - WIDGET_MARGIN, initialPosRef.current.height + deltaY)
        )
      );

      setSize({ width: newWidth, height: newHeight });
    };

    const handleMouseUp = () => {
      setIsResizing(false);
      resizingRef.current = false;
    };

    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizing]);

  const handleToggleFullScreen = () => {
    setIsFullScreen(!isFullScreen);
    if (!isFullScreen) {
      // Save current size before going fullscreen
      initialPosRef.current = {
        ...initialPosRef.current,
        width: size.width,
        height: size.height
      };
    } else {
      // Restore previous size when exiting fullscreen
      setSize({
        width: initialPosRef.current.width,
        height: initialPosRef.current.height
      });
    }
  };

  return (
    <div 
      className={`fixed bg-white rounded-lg shadow-xl flex flex-col overflow-hidden transition-all duration-200
        ${isFullScreen ? 'inset-0 rounded-none' : 'bottom-20 right-4'}
        ${isResizing ? 'transition-none' : ''}
      `}
      style={{ 
        width: isFullScreen ? '100%' : size.width,
        height: isFullScreen ? '100%' : size.height,
        maxHeight: isFullScreen ? '100%' : 'calc(100vh - 100px)',
        border: isFullScreen ? 'none' : '1px solid rgba(0, 0, 0, 0.1)',
        cursor: isResizing ? 'nwse-resize' : 'auto'
      }}
    >
      {/* Resize handle - only show when not in fullscreen */}
      {!isFullScreen && (
        <div
          className="absolute top-0 left-0 w-4 h-4 cursor-nwse-resize z-[1000] group"
          onMouseDown={handleMouseDown}
        >
          <div className="absolute inset-0 bg-gradient-to-br from-gray-200/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
          <svg
            className="w-4 h-4 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity"
            viewBox="0 0 24 24"
            fill="currentColor"
            style={{ transform: 'rotate(180deg)' }}
          >
            <path d="M22 22H20V20H22V22ZM22 18H18V20H22V18ZM18 22H16V24H18V22ZM22 14H14V16H22V14ZM14 22H12V24H14V22ZM22 10H10V12H22V10ZM10 22H8V24H10V22ZM22 6H6V8H22V6ZM6 22H4V24H6V22ZM22 2H2V4H22V2ZM2 22H0V24H2V22Z" />
          </svg>
        </div>
      )}

      <ChatHeader 
        onClose={onClose}
        onMinimize={() => setIsMinimized(!isMinimized)}
        onToggleFullScreen={handleToggleFullScreen}
        isMinimized={isMinimized}
        isFullScreen={isFullScreen}
      />
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        <MessageList
          ref={messageListRef}
          messages={messages}
          isLoading={isLoading}
        />
        <ChatInput onSendMessage={onSendMessage} />
      </div>
    </div>
  );
};

export default ChatWindow;