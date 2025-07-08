'use client'

import { Database } from '@/types/supabase'
import { Clock, CheckCircle, AlertCircle, Loader2 } from 'lucide-react'

type AgentRun = Database['public']['Tables']['agent_runs']['Row']

interface AgentStatusBarProps {
  agentRun: AgentRun
}

export default function AgentStatusBar({ agentRun }: AgentStatusBarProps) {
  const getStatusColor = () => {
    switch (agentRun.status) {
      case 'completed':
        return 'bg-green-50 text-green-800 border-green-200'
      case 'running':
        return 'bg-yellow-50 text-yellow-800 border-yellow-200'
      case 'failed':
        return 'bg-red-50 text-red-800 border-red-200'
      default:
        return 'bg-gray-50 text-gray-800 border-gray-200'
    }
  }
  
  const getStatusIcon = () => {
    switch (agentRun.status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />
      case 'running':
        return <Loader2 className="h-5 w-5 text-yellow-500 animate-spin" />
      case 'failed':
        return <AlertCircle className="h-5 w-5 text-red-500" />
      default:
        return <Clock className="h-5 w-5 text-gray-500" />
    }
  }
  
  const getStatusText = () => {
    switch (agentRun.status) {
      case 'completed':
        return 'Agent task completed'
      case 'running':
        return 'Agent is running...'
      case 'failed':
        return 'Agent encountered an error'
      default:
        return 'Agent is waiting to start'
    }
  }
  
  return (
    <div className={`px-4 py-2 border-b ${getStatusColor()}`}>
      <div className="flex items-center">
        <div className="mr-2">
          {getStatusIcon()}
        </div>
        <div className="flex-1">
          <p className="text-sm font-medium">
            {getStatusText()}
          </p>
          <p className="text-xs">
            Target: {agentRun.target_role || 'Not specified'} 
            {agentRun.target_industry ? ` in ${agentRun.target_industry}` : ''}
            {agentRun.target_region ? ` (${agentRun.target_region})` : ''}
          </p>
        </div>
      </div>
    </div>
  )
} 