import React, { useState, KeyboardEvent, useRef, useEffect } from 'react';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
}

const ChatInput: React.FC<ChatInputProps> = ({ onSendMessage }) => {
  const [message, setMessage] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = '40px';
      const scrollHeight = inputRef.current.scrollHeight;
      inputRef.current.style.height = Math.min(scrollHeight, 100) + 'px';
    }
  }, [message]);

  const handleSend = () => {
    if (message.trim()) {
      onSendMessage(message.trim());
      setMessage('');
      if (inputRef.current) {
        inputRef.current.style.height = '40px';
      }
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t border-gray-100 p-3">
      <div className={`relative flex items-end rounded-2xl transition-all duration-200
        ${isFocused ? 'bg-white shadow-md' : 'bg-gray-50'}`}>
        <textarea
          ref={inputRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder="Ask your question here"
          rows={1}
          className="w-full pr-12 py-2.5 px-4 max-h-[100px] rounded-2xl border border-gray-200 focus:outline-none focus:border-blue-500 text-gray-600 text-sm placeholder:text-gray-400 bg-transparent resize-none overflow-auto"
          style={{
            minHeight: '40px',
            overflowY: message.includes('\n') ? 'auto' : 'hidden'
          }}
        />
        <div className="absolute right-1 bottom-1.5 flex items-center">
          <button
            onClick={handleSend}
            disabled={!message.trim()}
            className={`p-2 rounded-full transition-all duration-200 flex items-center justify-center ${
              message.trim()
                ? 'bg-blue-600 hover:bg-blue-700 text-white'
                : 'bg-gray-200 text-gray-400 cursor-not-allowed'
            }`}
            aria-label="Send message"
          >
            <svg
              className="w-4 h-4"
              viewBox="0 0 24 24"
              fill="currentColor"
            >
              <path d="M3.4 20.4l17.45-7.48c.81-.35.81-1.49 0-1.84L3.4 3.6c-.66-.29-1.39.2-1.39.91L2 9.12c0 .5.37.93.87.99L17 12 2.87 13.88c-.5.07-.87.5-.87 1l.01 4.61c0 .71.73 1.2 1.39.91z" />
            </svg>
          </button>
        </div>
      </div>
      <div className="mt-1 px-2">
        <span className="text-xs text-gray-400">
          Press Enter to send, Shift + Enter for new line
        </span>
      </div>
    </div>
  );
};

export default ChatInput; 