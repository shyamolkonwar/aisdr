import { NextResponse } from 'next/server'
import { createServerSupabaseClient } from '@/lib/supabase/server'

export async function POST(request: Request) {
  try {
    const supabase = createServerSupabaseClient()
    const body = await request.json()
    const { email, password, full_name, company, role } = body
    
    if (!email || !password) {
      return NextResponse.json(
        { error: 'Email and password are required' },
        { status: 400 }
      )
    }
    
    // Sign up the user
    const { data: authData, error: authError } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: {
          full_name,
        },
      },
    })
    
    if (authError) {
      return NextResponse.json(
        { error: authError.message },
        { status: 400 }
      )
    }
    
    if (authData.user) {
      // Create profile entry
      const { error: profileError } = await supabase.from('profiles').insert({
        id: authData.user.id,
        email,
        full_name,
        company,
        role,
      })
      
      if (profileError) {
        console.error('Error creating profile:', profileError)
        return NextResponse.json(
          { error: 'Account created, but there was an issue setting up your profile.' },
          { status: 500 }
        )
      }
      
      return NextResponse.json({
        success: true,
        data: {
          user: authData.user,
          session: authData.session
        }
      })
    }
    
    return NextResponse.json(
      { error: 'Failed to create user account' },
      { status: 500 }
    )
  } catch (error) {
    console.error('Signup error:', error)
    return NextResponse.json(
      { error: 'An unexpected error occurred' },
      { status: 500 }
    )
  }
} 