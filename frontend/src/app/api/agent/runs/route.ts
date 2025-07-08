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
    const status = url.searchParams.get('status')
    const limit = parseInt(url.searchParams.get('limit') || '10')
    const page = parseInt(url.searchParams.get('page') || '0')
    const offset = page * limit
    
    let query = supabase
      .from('agents')
      .select('id, created_at, status, inputs')
      .eq('user_id', userId)
      .order('created_at', { ascending: false })
      .range(offset, offset + limit - 1)
      
    if (status) {
      query = query.eq('status', status)
    }
    
    const { data: runs, error, count } = await query
    
    if (error) {
      console.error('Error fetching agent runs:', error)
      return NextResponse.json(
        { error: 'Failed to fetch agent runs' },
        { status: 500 }
      )
    }
    
    // Get additional stats for each run
    const runsWithStats = await Promise.all(
      runs.map(async (run) => {
        // Get lead count
        const { count: leadCount } = await supabase
          .from('leads')
          .select('*', { count: 'exact', head: true })
          .eq('agent_id', run.id)
        
        // Get email counts by status
        // Get email counts by status
        const { count: draftEmails } = await supabase
          .from('emails')
          .select('*', { count: 'exact', head: true })
          .eq('agent_id', run.id)
          .eq('status', 'draft')
          
        const { count: sentEmails } = await supabase
          .from('emails')
          .select('*', { count: 'exact', head: true })
          .eq('agent_id', run.id)
          .eq('status', 'sent')
          
        const { count: failedEmails } = await supabase
          .from('emails')
          .select('*', { count: 'exact', head: true })
          .eq('agent_id', run.id)
          .eq('status', 'failed')
        
        // Format email stats
        const stats = {
          leads: leadCount || 0,
          emails: {
            draft: draftEmails || 0,
            sent: sentEmails || 0,
            failed: failedEmails || 0
          }
        }
        
        
        return {
          ...run,
          stats
        }
      })
    )
    
    return NextResponse.json({
      success: true,
      data: runsWithStats,
      pagination: {
        page,
        limit,
        total: count
      }
    })
    
  } catch (error) {
    console.error('Error fetching agent runs:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
} 