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
    
    // If agent_run_id is provided, get messages for that specific run
    // Otherwise, get the latest messages
    let query = supabase
      .from('chat_messages')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: true })
      
    if (agentRunId) {
      query = query.eq('agent_run_id', agentRunId)
    } else {
      // Get the latest agent run
      const { data: latestRun } = await supabase
        .from('agent_runs')
        .select('id')
        .eq('user_id', userId)
        .order('created_at', { ascending: false })
        .limit(1)
        .single()
        
      if (latestRun) {
        query = query.eq('agent_run_id', latestRun.id)
      }
    }
    
    const { data: messages, error } = await query
    
    if (error) {
      console.error('Error fetching chat messages:', error)
      return NextResponse.json(
        { error: 'Failed to fetch messages' },
        { status: 500 }
      )
    }
    
    return NextResponse.json({
      success: true,
      data: messages
    })
    
  } catch (error) {
    console.error('Error fetching chat messages:', error)
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
    const { content, agent_run_id } = body
    
    if (!content) {
      return NextResponse.json(
        { error: 'Message content is required' },
        { status: 400 }
      )
    }
    
    // Insert the user message
    const { data: userMessage, error: userMessageError } = await supabase
      .from('chat_messages')
      .insert({
        user_id: userId,
        agent_run_id,
        role: 'user',
        content
      })
      .select()
      .single()
      
    if (userMessageError) {
      console.error('Error saving user message:', userMessageError)
      return NextResponse.json(
        { error: 'Failed to save message' },
        { status: 500 }
      )
    }
    
    // In a real implementation, you would call the AI backend here
    // For now, we'll simulate an AI response
    const { data: aiMessage, error: aiMessageError } = await supabase
      .from('chat_messages')
      .insert({
        user_id: userId,
        agent_run_id,
        role: 'assistant',
        content: 'I received your message. I am processing your request...'
      })
      .select()
      .single()
      
    if (aiMessageError) {
      console.error('Error saving AI message:', aiMessageError)
    }
    
    return NextResponse.json({
      success: true,
      data: {
        user_message: userMessage,
        ai_message: aiMessageError ? null : aiMessage
      }
    })
    
  } catch (error) {
    console.error('Error sending message:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
} 