import React, { forwardRef, useEffect, useRef } from 'react';
import { Message } from '../../../types/chat';
import MessageBubble from './MessageBubble';
import LoadingIndicator from './LoadingIndicator';

interface MessageListProps {
  messages: Message[];
  isLoading?: boolean;
}

const MessageList = forwardRef<HTMLDivElement, MessageListProps>(
  ({ messages, isLoading }, ref) => {
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
      scrollToBottom();
    }, [messages]);

    return (
      <div ref={ref} className="flex-1 overflow-y-auto px-4 py-3 space-y-4">
        <div className="space-y-6">
          {messages.map((message) => (
            <MessageBubble key={message.id + message.timestamp} message={message} />
          ))}
        </div>
        {isLoading && (
          <div className="flex justify-center py-2">
            <LoadingIndicator />
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
    );
  }
);

MessageList.displayName = 'MessageList';

export default MessageList;