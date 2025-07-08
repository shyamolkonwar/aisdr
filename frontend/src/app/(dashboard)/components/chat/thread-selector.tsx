'use client'

import { useRouter } from 'next/navigation'
import { formatDistanceToNow } from 'date-fns'
import { Database } from '@/types/supabase'
import { Plus } from 'lucide-react'

type AgentRun = Database['public']['Tables']['agents']['Row']

interface ThreadSelectorProps {
  agentRuns: AgentRun[]
  currentRunId?: string
}

export default function ThreadSelector({ 
  agentRuns = [], 
  currentRunId 
}: ThreadSelectorProps) {
  const router = useRouter()

  const handleSelectThread = (runId: string) => {
    router.push(`/?agent_run_id=${runId}`)
  }

  const handleNewThread = () => {
    router.push('/')
  }

  return (
    <div className="h-full flex flex-col">
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="font-medium text-gray-900">Chat Threads</h3>
          <button
            type="button"
            className="text-blue-600 hover:text-blue-800"
            onClick={handleNewThread}
          >
            <Plus className="h-4 w-4" />
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto">
        {agentRuns.length === 0 ? (
          <div className="px-4 py-2 text-sm text-gray-500">
            No chat history yet. Start a new chat by clicking "Run Agent".
          </div>
        ) : (
          agentRuns.map((run) => {
            const isActive = run.id === currentRunId
            const formattedDate = run.created_at 
              ? formatDistanceToNow(new Date(run.created_at), { addSuffix: true })
              : 'Unknown date'
            
            return (
              <button
                key={run.id}
                onClick={() => run.id && handleSelectThread(run.id)}
                className={`w-full text-left px-4 py-2 focus:outline-none ${
                  isActive 
                    ? 'bg-gray-100 text-gray-900'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <div className="flex justify-between items-center">
                  <div className="truncate">
                    <p className="text-sm font-medium">
                      {run.target_role || 'New Chat'} {run.target_industry ? `- ${run.target_industry}` : ''}
                    </p>
                    <p className="text-xs text-gray-500 truncate">
                      {formattedDate}
                    </p>
                  </div>
                  
                  {run.status && (
                    <div className={`h-2 w-2 rounded-full ${
                      run.status === 'completed' ? 'bg-green-500' :
                      run.status === 'running' ? 'bg-yellow-500' :
                      run.status === 'failed' ? 'bg-red-500' :
                      'bg-gray-500'
                    }`} />
                  )}
                </div>
              </button>
            )
          })
        )}
      </div>
    </div>
  )
}