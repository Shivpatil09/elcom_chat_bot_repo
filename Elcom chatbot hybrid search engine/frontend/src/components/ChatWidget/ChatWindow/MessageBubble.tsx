import React from 'react';
import { Message } from '../../../types/chat';
import ReactMarkdown from 'react-markdown';
import type { Components } from 'react-markdown';

interface MessageBubbleProps {
  message: Message;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.sender === 'user';
  const formattedTime = new Date(message.timestamp).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit'
  });

  const components: Components = {
    h3: ({ children }) => (
      <h3 className="text-lg font-bold text-gray-800 mb-4 border-b border-gray-200 pb-2">
        {children}
      </h3>
    ),
    p: ({ children }) => (
      <p className="text-gray-700 mb-3 leading-relaxed">{children}</p>
    ),
    strong: ({ children }) => (
      <strong className="text-gray-900 font-semibold">{children}</strong>
    ),
    ul: ({ children }) => (
      <ul className="list-none space-y-2 mb-4">{children}</ul>
    ),
    li: ({ children }) => (
      <li className="flex items-start space-x-2">
        <span className="text-blue-500 mt-1.5 flex-shrink-0">•</span>
        <span className="text-gray-700">{children}</span>
      </li>
    ),
    hr: () => <hr className="my-6 border-gray-200" />,
    // Section styling
    section: ({ children }) => (
      <section className="mb-6 last:mb-0">{children}</section>
    )
  };

  const renderContent = () => {
    if (message.text.includes("Product Assistant")) {
      return (
        <div className="text-center space-y-4">
          <p className="font-medium text-lg">{message.text.split('\n')[0]}</p>
          <div className="space-y-2 text-gray-600">
            {message.text.split('\n').slice(2).map((line, i) => (
              <p key={i}>{line}</p>
            ))}
          </div>
        </div>
      );
    }

    // Product information display
    if (message.text.includes("###")) {
      return (
        <div className="prose prose-sm max-w-none prose-headings:mb-4 prose-headings:border-b prose-headings:border-gray-200 prose-headings:pb-2 prose-p:text-gray-700 prose-p:leading-relaxed prose-strong:text-gray-900 prose-strong:font-semibold prose-ul:list-none prose-ul:pl-0 prose-li:flex prose-li:items-start prose-li:space-x-2">
          <ReactMarkdown components={components}>
            {message.text}
          </ReactMarkdown>
        </div>
      );
    }

    // Regular message
    return <span className="text-inherit">{message.text}</span>;
  };

  return (
    <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} mb-4`}>
      <div
        className={`max-w-[85%] rounded-lg px-4 py-3 ${
          isUser
            ? 'bg-blue-600 text-white'
            : 'bg-gray-50 text-gray-900 border border-gray-100'
        }`}
      >
        {renderContent()}
      </div>
      <span className="text-xs text-gray-500 mt-1">{formattedTime}</span>
    </div>
  );
};

export default MessageBubble;