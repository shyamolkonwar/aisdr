import { NextResponse } from 'next/server'
import { createServerSupabaseClient } from '@/lib/supabase/server'

export async function POST(request: Request) {
  try {
    const supabase = createServerSupabaseClient()
    const { data: { session } } = await supabase.auth.getSession()
    
    if (!session) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      )
    }
    
    const userId = session.user.id
    const body = await request.json()
    
    // Extract agent run settings from the request body
    const {
      target_industry,
      target_role,
      target_region,
      lead_count,
      email_tone,
      email_objective
    } = body
    
    // Create a new agent run in the database
    const { data: agentRun, error: agentRunError } = await supabase
      .from('agents')
      .insert({
        user_id: userId,
        status: 'active',
        inputs: {
          industry: target_industry,
          role: target_role,
          region: target_region,
          lead_count,
          email_tone,
          objective: email_objective
        }
      })
      .select()
      .single()
      
    if (agentRunError) {
      console.error('Error creating agent run:', agentRunError)
      return NextResponse.json(
        { error: 'Failed to create agent run' },
        { status: 500 }
      )
    }
    
    // In a real implementation, you would trigger the backend AI SDR agent here
    // For example, by calling a serverless function or sending a message to a queue
    
    // For now, we'll simulate starting the agent
    // Update the agent run status to 'running'
    // Create initial task record
    await supabase
      .from('tasks')
      .insert({
        agent_id: agentRun.id,
        task_type: 'initialize',
        status: 'done',
        input_data: {
          message: 'AI SDR Agent started. I will help you generate leads and write personalized emails.'
        }
      })
    
    return NextResponse.json({
      success: true,
      data: {
        agent_id: agentRun.id,
        status: 'active'
      }
    })
    
  } catch (error) {
    console.error('Error running agent:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
} 