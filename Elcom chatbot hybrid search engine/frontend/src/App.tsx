import React, { useState, useEffect, useCallback } from 'react';
import FloatingButton from './components/ChatWidget/FloatingButton';
import ChatWindow from './components/ChatWidget/ChatWindow/ChatWindow';
import { Message } from './types/chat';
import { sendMessage } from './services/chatService';
import { AxiosError } from 'axios';
import './App.css';

function App() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Add welcome message when chat is first opened
    if (isOpen && messages.length === 0) {
      const welcomeMessage: Message = {
        id: Date.now().toString(),
        text: "Hello! I'm Elcom's Product Assistant. I can help you with:\n\n• Product specifications (voltage, current ratings)\n\n• Mounting types and technical details\n\n• Finding similar or related products\n\n• General product information\n\nFeel free to ask any questions about our product catalog!",
        sender: 'bot',
        timestamp: Date.now()
      };
      setMessages([welcomeMessage]);
    }
  }, [isOpen, messages.length]);

  const formatProductDetails = (products: any[]) => {
    return products
      .map((product) => {
        // Split the text into lines and clean them
        const lines = product.text.split('\n')
          .map((line: string) => line.trim())
          .filter(Boolean);

        const sections: string[] = [];
        let currentSection = '';

        for (const line of lines) {
          // If line ends with colon, it's a section header
          if (line.endsWith(':')) {
            if (currentSection) {
              sections.push(currentSection.trim());
            }
            currentSection = line + '\n';
          } else {
            currentSection += line + '\n';
          }
        }
        
        if (currentSection) {
          sections.push(currentSection.trim());
        }

        // Join sections with double newlines
        return sections.join('\n\n');
      })
      .join('\n\n---\n\n'); // Separate products with horizontal rule
  };

  const handleSendMessage = useCallback(async (text: string) => {
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      text,
      sender: 'user',
      timestamp: Date.now()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await sendMessage(text);
      
      // Handle Rasa response format
      if (Array.isArray(response) && response.length > 0) {
        const botMessage: Message = {
          id: Date.now().toString(),
          text: formatProductDetails(response),
          sender: 'bot',
          timestamp: Date.now()
        };
        setMessages(prev => [...prev, botMessage]);
      } else {
        const botMessage: Message = {
          id: Date.now().toString(),
          text: 'Sorry, I received an empty response. Please try again.',
          sender: 'bot',
          timestamp: Date.now()
        };
        setMessages(prev => [...prev, botMessage]);
      }
    } catch (error) {
      console.error('Chat error:', error);
      const axiosError = error as AxiosError;
      const errorMessage: Message = {
        id: Date.now().toString(),
        text: `Error: ${axiosError.message || 'Sorry, I encountered an error. Please try again.'}`,
        sender: 'bot',
        timestamp: Date.now()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return (
    <div className="App">
      <div className="fixed bottom-4 right-4 z-50">
        <FloatingButton 
          isOpen={isOpen} 
          onClick={() => setIsOpen(!isOpen)} 
        />
        {isOpen && (
          <ChatWindow
            messages={messages}
            isLoading={isLoading}
            onSendMessage={handleSendMessage}
            onClose={() => setIsOpen(false)}
          />
        )}
      </div>
    </div>
  );
}

export default App;
