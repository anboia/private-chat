import React from 'react';
import { User, Bot } from 'lucide-react';
import type { ChatMessage as ChatMessageType } from '../lib/api';

interface ChatMessageProps {
  message: ChatMessageType;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';
  
  return (
    <div className={`flex gap-3 p-4 ${isUser ? 'bg-transparent' : 'bg-gray-50 dark:bg-gray-800'}`}>
      <div className="flex-shrink-0">
        {isUser ? (
          <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
            <User size={16} className="text-white" />
          </div>
        ) : (
          <div className="w-8 h-8 bg-green-600 rounded-full flex items-center justify-center">
            <Bot size={16} className="text-white" />
          </div>
        )}
      </div>
      <div className="flex-1 min-w-0">
        <div className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-1">
          {isUser ? 'You' : 'Assistant'}
        </div>
        <div className="text-gray-800 dark:text-gray-200 whitespace-pre-wrap leading-relaxed">
          {message.content}
        </div>
      </div>
    </div>
  );
};