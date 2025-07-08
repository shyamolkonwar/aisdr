'use client'

import { useState, useRef, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Send, Upload, Plus } from 'lucide-react'
import { Database } from '@/types/supabase'
import ChatMessage from './chat-message'
import AgentStatusBar from './agent-status-bar'
import ThreadSelector from './thread-selector'

type AgentRun = Database['public']['Tables']['agent_runs']['Row']
type ChatMessage = Database['public']['Tables']['chat_messages']['Row']

interface ChatInterfaceProps {
  initialMessages: ChatMessage[]
  agentRun: AgentRun | null
}

export default function ChatInterface({ initialMessages, agentRun }: ChatInterfaceProps) {
  const router = useRouter()
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages || [])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  
  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])
  
  const handleSendMessage = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return
    
    const messageContent = input.trim()
    setInput('')
    setIsLoading(true)
    
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: messageContent,
          agent_run_id: agentRun?.id,
        }),
      })
      
      const data = await response.json()
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to send message')
      }
      
      // Add the user message and AI response to the chat
      if (data.data.user_message) {
        setMessages(prev => [...prev, data.data.user_message])
      }
      
      if (data.data.ai_message) {
        setMessages(prev => [...prev, data.data.ai_message])
      }
      
      // Refresh the page to get the latest messages
      router.refresh()
    } catch (error) {
      console.error('Error sending message:', error)
      // Show error to user
    } finally {
      setIsLoading(false)
    }
  }
  
  // Show welcome message if no messages and no agent run
  const showWelcomeMessage = messages.length === 0 && !agentRun
  
  return (
    <div className="flex h-full">
      {/* Thread selector */}
      <div className="w-64 border-r border-gray-200 bg-gray-50 overflow-y-auto">
        <ThreadSelector />
      </div>
      
      {/* Main chat area */}
      <div className="flex-1 flex flex-col">
        {/* Agent status bar */}
        {agentRun && (
          <AgentStatusBar agentRun={agentRun} />
        )}
        
        {/* Chat messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {showWelcomeMessage ? (
          <div className="flex flex-col items-center justify-center h-full text-center px-4">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Welcome to AI SDR Agent</h2>
            <p className="text-gray-600 mb-6">
              Your AI-powered sales development representative. Click "Run Agent" to get started.
            </p>
          </div>
        ) : (
          messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))
        )}
        <div ref={messagesEndRef} />
      </div>
      
        {/* Chat input */}
        <div className="border-t border-gray-200 p-4">
          <form onSubmit={handleSendMessage} className="flex space-x-4">
            <div className="flex-1 relative">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Type your message or ask the AI SDR agent..."
                className="w-full border border-gray-300 rounded-md py-2 pl-4 pr-12 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={isLoading || !agentRun}
              />
              <button
                type="button"
                className="absolute right-2 top-2 text-gray-400 hover:text-gray-600"
                title="Upload file"
              >
                <Upload className="h-5 w-5" />
              </button>
            </div>
            <div className="flex space-x-2">
              <button
                type="button"
                className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                onClick={() => setInput(prev => prev + ' @')}
              >
                <Plus className="h-4 w-4 mr-1" />
                Insert
              </button>
              <button
                type="submit"
                className={`inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${
                  isLoading || !agentRun ? 'opacity-50 cursor-not-allowed' : ''
                }`}
                disabled={isLoading || !agentRun}
              >
                <Send className="h-4 w-4 mr-2" />
                Send
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
} 