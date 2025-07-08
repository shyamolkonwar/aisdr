import { createServerSupabaseClient } from '@/lib/supabase/server'
import ChatInterface from './components/chat/chat-interface'
import ThreadSelector from './components/chat/thread-selector'

export default async function ChatPage({
  searchParams,
}: {
  searchParams: { [key: string]: string | string[] | undefined }
}) {
  const supabase = createServerSupabaseClient()
  const { data: { session } } = await supabase.auth.getSession()
  
  if (!session) {
    return null // Will be handled by middleware
  }
  
  // Get agent run ID from query params or use the latest
  const agentRunId = searchParams.agent_run_id as string | undefined
  
  // Get agent runs for the thread selector
  const { data: agentRuns } = await supabase
    .from('agents')
    .select('*')
    .eq('user_id', session.user.id)
    .order('created_at', { ascending: false })
    .limit(10)
  
  // Get messages for the current agent run
  let messages = []
  let currentAgentRun = null
  
  if (agentRunId) {
    // Get messages for specific agent run
    // Get both tasks and emails for the agent run
    const { data: tasks } = await supabase
      .from('tasks')
      .select('*')
      .eq('agent_id', agentRunId)
      .order('created_at', { ascending: true })
    
    const { data: emails } = await supabase
      .from('emails')
      .select('*')
      .eq('agent_id', agentRunId)
      .order('created_at', { ascending: true })
    
    const runMessages = [...tasks || [], ...emails || []]
    
    if (runMessages) {
      messages = runMessages
    }
    
    // Get the current agent run details
    const { data: runDetails } = await supabase
      .from('agents')
      .select('*')
      .eq('id', agentRunId)
      .eq('user_id', session.user.id)
      .single()
    
    if (runDetails) {
      currentAgentRun = runDetails
    }
  } else if (agentRuns && agentRuns.length > 0) {
    // Get messages for the latest agent run
    const latestRunId = agentRuns[0].id
    
    // Get both tasks and emails for the latest agent run
    const { data: tasks } = await supabase
      .from('tasks')
      .select('*')
      .eq('agent_id', latestRunId)
      .order('created_at', { ascending: true })
    
    const { data: emails } = await supabase
      .from('emails')
      .select('*')
      .eq('agent_id', latestRunId)
      .order('created_at', { ascending: true })
    
    const latestMessages = [...tasks || [], ...emails || []]
    
    if (latestMessages) {
      messages = latestMessages
    }
    
    currentAgentRun = agentRuns[0]
  }
  
  return (
    <div className="flex h-[calc(100vh-64px)]">
      {/* Thread selector (left sidebar) */}
      <div className="hidden md:block w-64 border-r border-gray-200 bg-white overflow-y-auto">
        <ThreadSelector agentRuns={agentRuns || []} currentRunId={currentAgentRun?.id} />
      </div>
      
      {/* Main chat area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <ChatInterface 
          initialMessages={messages} 
          agentRun={currentAgentRun}
        />
      </div>
    </div>
  )
} 