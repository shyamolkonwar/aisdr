'use client'

import { useRouter, usePathname } from 'next/navigation'
import { Database } from '@/types/supabase'
import { Filter } from 'lucide-react'

type AgentRun = Database['public']['Tables']['agent_runs']['Row']

interface EmailFiltersProps {
  agentRuns: Partial<AgentRun>[]
  currentStatus?: string
  currentAgentRunId?: string
}

export default function EmailFilters({ 
  agentRuns, 
  currentStatus, 
  currentAgentRunId 
}: EmailFiltersProps) {
  const router = useRouter()
  const pathname = usePathname()
  
  const statusOptions = [
    { value: '', label: 'All Statuses' },
    { value: 'draft', label: 'Draft' },
    { value: 'approved', label: 'Approved' },
    { value: 'sent', label: 'Sent' },
    { value: 'opened', label: 'Opened' },
    { value: 'replied', label: 'Replied' },
  ]
  
  const handleStatusChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const status = e.target.value
    updateFilters({ status })
  }
  
  const handleAgentRunChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const agentRunId = e.target.value
    updateFilters({ agent_run_id: agentRunId })
  }
  
  const updateFilters = (params: Record<string, string>) => {
    // Create new URLSearchParams object with current search params
    const searchParams = new URLSearchParams()
    
    // Add current params that we want to keep
    if (currentStatus && !('status' in params)) {
      searchParams.set('status', currentStatus)
    }
    
    if (currentAgentRunId && !('agent_run_id' in params)) {
      searchParams.set('agent_run_id', currentAgentRunId)
    }
    
    // Add new params
    Object.entries(params).forEach(([key, value]) => {
      if (value) {
        searchParams.set(key, value)
      } else {
        searchParams.delete(key)
      }
    })
    
    // Construct new URL and navigate
    const query = searchParams.toString()
    const url = query ? `${pathname}?${query}` : pathname
    router.push(url)
  }
  
  const clearFilters = () => {
    router.push(pathname)
  }
  
  const hasActiveFilters = !!(currentStatus || currentAgentRunId)
  
  return (
    <div className="bg-white shadow rounded-md p-4">
      <div className="flex items-center mb-4">
        <Filter className="h-5 w-5 text-gray-400 mr-2" />
        <h2 className="text-lg font-medium text-gray-900">Filters</h2>
        
        {hasActiveFilters && (
          <button
            onClick={clearFilters}
            className="ml-auto text-sm text-blue-600 hover:text-blue-500"
          >
            Clear all filters
          </button>
        )}
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Status filter */}
        <div>
          <label htmlFor="status" className="block text-sm font-medium text-gray-700">
            Email Status
          </label>
          <select
            id="status"
            name="status"
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            value={currentStatus || ''}
            onChange={handleStatusChange}
          >
            {statusOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
        
        {/* Agent run filter */}
        <div>
          <label htmlFor="agent_run" className="block text-sm font-medium text-gray-700">
            Campaign
          </label>
          <select
            id="agent_run"
            name="agent_run"
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            value={currentAgentRunId || ''}
            onChange={handleAgentRunChange}
          >
            <option value="">All Campaigns</option>
            {agentRuns.map((run) => (
              <option key={run.id} value={run.id}>
                {run.target_role || 'Campaign'} {run.target_industry ? `- ${run.target_industry}` : ''}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  )
} 