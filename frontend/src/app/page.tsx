'use client'

import { useState } from 'react'
import { Menu } from 'lucide-react'
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs'
import { Database } from '@/types/supabase'
import ChatInterface from '@/app/(dashboard)/components/chat/chat-interface'

export default function HomePage() {
  const supabase = createClientComponentClient<Database>()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Collapsible sidebar button */}
      <button
        className="fixed left-4 top-4 z-20 md:hidden"
        onClick={() => setSidebarOpen(!sidebarOpen)}
      >
        <Menu className="h-6 w-6 text-gray-600" />
      </button>

      {/* Sidebar - hidden on mobile when closed */}
      <div className={`${sidebarOpen ? 'block' : 'hidden'} md:block w-64 border-r border-gray-200 bg-white z-10`}>
        {/* Sidebar content would go here */}
      </div>

      {/* Main chat area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <div className="flex-1 overflow-y-auto">
          <ChatInterface 
            initialMessages={[]}
            agentRun={null}
          />
        </div>
      </div>
    </div>
  )
}
