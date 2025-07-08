'use client'

import { useState } from 'react'
import { User, Bot } from 'lucide-react'
import { Database } from '@/types/supabase'
import ReactMarkdown from 'react-markdown'

type ChatMessage = Database['public']['Tables']['chat_messages']['Row']

interface ChatMessageProps {
  message: ChatMessage
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const [isExpanded, setIsExpanded] = useState(false)
  
  const isUser = message.role === 'user'
  const isSystem = message.role === 'system'
  
  // Determine if message is long and should be truncated
  const isLongMessage = message.content.length > 500
  const displayContent = isLongMessage && !isExpanded 
    ? `${message.content.substring(0, 500)}...` 
    : message.content
  
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`flex max-w-3xl ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 ${isUser ? 'ml-4' : 'mr-4'}`}>
          <div className={`h-8 w-8 rounded-full flex items-center justify-center ${
            isUser 
              ? 'bg-blue-100 text-blue-600' 
              : isSystem
                ? 'bg-gray-100 text-gray-600'
                : 'bg-green-100 text-green-600'
          }`}>
            {isUser ? (
              <User className="h-5 w-5" />
            ) : (
              <Bot className="h-5 w-5" />
            )}
          </div>
        </div>
        
        {/* Message content */}
        <div className={`rounded-lg px-4 py-2 ${
          isUser 
            ? 'bg-blue-600 text-white' 
            : isSystem
              ? 'bg-gray-100 text-gray-800 italic'
              : 'bg-white border border-gray-200 text-gray-800'
        }`}>
          <div className="prose max-w-none">
            <ReactMarkdown>{displayContent}</ReactMarkdown>
          </div>
          
          {/* Show more/less button for long messages */}
          {isLongMessage && (
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className={`text-xs mt-2 ${
                isUser ? 'text-blue-200' : 'text-gray-500'
              }`}
            >
              {isExpanded ? 'Show less' : 'Show more'}
            </button>
          )}
        </div>
      </div>
    </div>
  )
} 