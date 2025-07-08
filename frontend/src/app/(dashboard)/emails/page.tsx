import { createServerSupabaseClient } from '@/lib/supabase/server'
import EmailsTable from './components/emails-table'
import EmailFilters from './components/email-filters'

export default async function EmailsPage({
  searchParams,
}: {
  searchParams: { [key: string]: string | string[] | undefined }
}) {
  const supabase = createServerSupabaseClient()
  const { data: { session } } = await supabase.auth.getSession()
  
  if (!session) {
    return null // Will be handled by middleware
  }
  
  // Get filter params
  const status = searchParams.status as string | undefined
  const agentRunId = searchParams.agent_run_id as string | undefined
  const leadId = searchParams.lead_id as string | undefined
  
  // Fetch emails with filters
  let query = supabase
    .from('emails')
    .select(`
      *,
      leads (
        id,
        full_name,
        email,
        company,
        title
      )
    `)
    .eq('user_id', session.user.id)
    .order('created_at', { ascending: false })
  
  if (status) {
    query = query.eq('status', status)
  }
  
  if (leadId) {
    query = query.eq('lead_id', leadId)
  }
  
  if (agentRunId) {
    query = query.eq('leads.agent_run_id', agentRunId)
  }
  
  const { data: emails, error } = await query
  
  // Get agent runs for filtering
  const { data: agentRuns } = await supabase
    .from('agent_runs')
    .select('id, created_at, target_industry, target_role')
    .eq('user_id', session.user.id)
    .order('created_at', { ascending: false })
    .limit(10)
  
  return (
    <div>
      <div className="pb-5 border-b border-gray-200 sm:flex sm:items-center sm:justify-between">
        <h1 className="text-2xl font-semibold text-gray-900">Generated Emails</h1>
      </div>
      
      <div className="mt-6">
        <EmailFilters 
          agentRuns={agentRuns || []}
          currentStatus={status}
          currentAgentRunId={agentRunId}
        />
      </div>
      
      <div className="mt-6">
        <EmailsTable emails={emails || []} />
      </div>
    </div>
  )
} 