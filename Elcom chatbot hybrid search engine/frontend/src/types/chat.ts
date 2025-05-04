export interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: number;
}

export interface ChatState {
  isOpen: boolean;
  messages: Message[];
  isLoading: boolean;
} 