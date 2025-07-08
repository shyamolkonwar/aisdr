'use client'

interface AgentRun {
  id: string
  created_at: string
  status: 'active' | 'completed' | 'failed'
  inputs: {
    industry?: string
    role?: string
  }
}

interface RecentActivityProps {
  agentRuns: AgentRun[]
}

export default function RecentActivity({ agentRuns }: RecentActivityProps) {
  return (
    <div className="overflow-hidden bg-white shadow sm:rounded-lg">
      <ul className="divide-y divide-gray-200">
        {agentRuns.map((run) => (
          <li key={run.id} className="px-4 py-4 sm:px-6">
            <div className="flex items-center justify-between">
              <p className="truncate text-sm font-medium text-blue-600">
                {run.inputs.industry ? `${run.inputs.industry} outreach` : 'Agent run'}
              </p>
              <div className="ml-2 flex flex-shrink-0">
                <p className={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${
                  run.status === 'completed' ? 'bg-green-100 text-green-800' :
                  run.status === 'active' ? 'bg-blue-100 text-blue-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {run.status}
                </p>
              </div>
            </div>
            <div className="mt-2 sm:flex sm:justify-between">
              <div className="sm:flex">
                <p className="flex items-center text-sm text-gray-500">
                  {new Date(run.created_at).toLocaleString()}
                </p>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}