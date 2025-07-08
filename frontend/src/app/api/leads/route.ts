import { NextResponse } from 'next/server'
import { createServerSupabaseClient } from '@/lib/supabase/server'

export async function GET(request: Request) {
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
    const url = new URL(request.url)
    const agentRunId = url.searchParams.get('agent_run_id')
    
    let query = supabase
      .from('leads')
      .select('*')
      .eq('user_id', userId)
      
    if (agentRunId) {
      query = query.eq('agent_run_id', agentRunId)
    }
    
    const { data: leads, error } = await query
    
    if (error) {
      console.error('Error fetching leads:', error)
      return NextResponse.json(
        { error: 'Failed to fetch leads' },
        { status: 500 }
      )
    }
    
    return NextResponse.json({
      success: true,
      data: leads
    })
    
  } catch (error) {
    console.error('Error fetching leads:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

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
    const { 
      agent_run_id, 
      full_name, 
      email, 
      company, 
      title,
      linkedin_url,
      website_url,
      notes
    } = body
    
    if (!agent_run_id || !full_name || !email || !company || !title) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      )
    }
    
    // Verify the agent run belongs to the user
    const { data: agentRun } = await supabase
      .from('agent_runs')
      .select('id')
      .eq('id', agent_run_id)
      .eq('user_id', userId)
      .single()
      
    if (!agentRun) {
      return NextResponse.json(
        { error: 'Agent run not found or access denied' },
        { status: 404 }
      )
    }
    
    // Create the lead
    const { data: lead, error } = await supabase
      .from('leads')
      .insert({
        user_id: userId,
        agent_run_id,
        full_name,
        email,
        company,
        title,
        linkedin_url,
        website_url,
        notes
      })
      .select()
      .single()
      
    if (error) {
      console.error('Error creating lead:', error)
      return NextResponse.json(
        { error: 'Failed to create lead' },
        { status: 500 }
      )
    }
    
    return NextResponse.json({
      success: true,
      data: lead
    })
    
  } catch (error) {
    console.error('Error creating lead:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
} 