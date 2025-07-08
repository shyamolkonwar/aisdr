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
    const status = url.searchParams.get('status')
    const leadId = url.searchParams.get('lead_id')
    
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
      .eq('user_id', userId)
    
    if (agentRunId) {
      query = query.eq('leads.agent_run_id', agentRunId)
    }
    
    if (status) {
      query = query.eq('status', status)
    }
    
    if (leadId) {
      query = query.eq('lead_id', leadId)
    }
    
    const { data: emails, error } = await query
    
    if (error) {
      console.error('Error fetching emails:', error)
      return NextResponse.json(
        { error: 'Failed to fetch emails' },
        { status: 500 }
      )
    }
    
    return NextResponse.json({
      success: true,
      data: emails
    })
    
  } catch (error) {
    console.error('Error fetching emails:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

export async function PUT(request: Request) {
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
    const { id, subject, body: emailBody, status } = body
    
    if (!id) {
      return NextResponse.json(
        { error: 'Email ID is required' },
        { status: 400 }
      )
    }
    
    // Verify the email belongs to the user
    const { data: existingEmail } = await supabase
      .from('emails')
      .select('id')
      .eq('id', id)
      .eq('user_id', userId)
      .single()
      
    if (!existingEmail) {
      return NextResponse.json(
        { error: 'Email not found or access denied' },
        { status: 404 }
      )
    }
    
    // Update the email
    const updateData: any = {}
    if (subject) updateData.subject = subject
    if (emailBody) updateData.body = emailBody
    if (status) updateData.status = status
    
    // Add timestamps based on status
    if (status === 'sent') updateData.sent_at = new Date().toISOString()
    if (status === 'opened') updateData.opened_at = new Date().toISOString()
    if (status === 'replied') updateData.replied_at = new Date().toISOString()
    
    const { data: updatedEmail, error } = await supabase
      .from('emails')
      .update(updateData)
      .eq('id', id)
      .select()
      .single()
      
    if (error) {
      console.error('Error updating email:', error)
      return NextResponse.json(
        { error: 'Failed to update email' },
        { status: 500 }
      )
    }
    
    return NextResponse.json({
      success: true,
      data: updatedEmail
    })
    
  } catch (error) {
    console.error('Error updating email:', error)
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
    const { lead_id, subject, body: emailBody, action } = body
    
    if (!lead_id || !subject || !emailBody) {
      return NextResponse.json(
        { error: 'Lead ID, subject, and body are required' },
        { status: 400 }
      )
    }
    
    // Verify the lead belongs to the user
    const { data: lead } = await supabase
      .from('leads')
      .select('id')
      .eq('id', lead_id)
      .eq('user_id', userId)
      .single()
      
    if (!lead) {
      return NextResponse.json(
        { error: 'Lead not found or access denied' },
        { status: 404 }
      )
    }
    
    // Determine the status based on the action
    let status = 'draft'
    let sentAt = null
    
    if (action === 'send') {
      status = 'sent'
      sentAt = new Date().toISOString()
      // In a real implementation, you would send the email here
    }
    
    // Create the email
    const { data: email, error } = await supabase
      .from('emails')
      .insert({
        user_id: userId,
        lead_id,
        subject,
        body: emailBody,
        status,
        sent_at: sentAt
      })
      .select()
      .single()
      
    if (error) {
      console.error('Error creating email:', error)
      return NextResponse.json(
        { error: 'Failed to create email' },
        { status: 500 }
      )
    }
    
    return NextResponse.json({
      success: true,
      data: email
    })
    
  } catch (error) {
    console.error('Error creating email:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
} 