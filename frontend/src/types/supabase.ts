export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export interface Database {
  public: {
    Tables: {
      profiles: {
        Row: {
          id: string
          created_at: string
          updated_at: string
          email: string
          full_name: string | null
          avatar_url: string | null
          company: string | null
          role: string | null
        }
        Insert: {
          id: string
          created_at?: string
          updated_at?: string
          email: string
          full_name?: string | null
          avatar_url?: string | null
          company?: string | null
          role?: string | null
        }
        Update: {
          id?: string
          created_at?: string
          updated_at?: string
          email?: string
          full_name?: string | null
          avatar_url?: string | null
          company?: string | null
          role?: string | null
        }
      }
      agents: {
        Row: {
          id: string
          created_at: string
          user_id: string
          status: 'pending' | 'running' | 'completed' | 'failed'
          target_industry: string | null
          target_role: string | null
          target_region: string | null
          lead_count: number | null
          email_tone: string | null
          email_objective: string | null
        }
        Insert: {
          id?: string
          created_at?: string
          user_id: string
          status?: 'pending' | 'running' | 'completed' | 'failed'
          target_industry?: string | null
          target_role?: string | null
          target_region?: string | null
          lead_count?: number | null
          email_tone?: string | null
          email_objective?: string | null
        }
        Update: {
          id?: string
          created_at?: string
          user_id?: string
          status?: 'pending' | 'running' | 'completed' | 'failed'
          target_industry?: string | null
          target_role?: string | null
          target_region?: string | null
          lead_count?: number | null
          email_tone?: string | null
          email_objective?: string | null
        }
      }
      agent_memory: {
        Row: {
          id: string
          created_at: string
          user_id: string
          agent_run_id: string
          memory_key: string
          memory_value: Json
        }
        Insert: {
          id?: string
          created_at?: string
          user_id: string
          agent_run_id: string
          memory_key: string
          memory_value: Json
        }
        Update: {
          id?: string
          created_at?: string
          user_id?: string
          agent_run_id?: string
          memory_key?: string
          memory_value?: Json
        }
      }
      leads: {
        Row: {
          id: string
          created_at: string
          user_id: string
          agent_run_id: string
          full_name: string
          email: string
          company: string
          title: string
          linkedin_url: string | null
          website_url: string | null
          notes: string | null
        }
        Insert: {
          id?: string
          created_at?: string
          user_id: string
          agent_run_id: string
          full_name: string
          email: string
          company: string
          title: string
          linkedin_url?: string | null
          website_url?: string | null
          notes?: string | null
        }
        Update: {
          id?: string
          created_at?: string
          user_id?: string
          agent_run_id?: string
          full_name?: string
          email?: string
          company?: string
          title?: string
          linkedin_url?: string | null
          website_url?: string | null
          notes?: string | null
        }
      }
      emails: {
        Row: {
          id: string
          created_at: string
          user_id: string
          lead_id: string
          subject: string
          body: string
          status: 'draft' | 'approved' | 'sent' | 'opened' | 'replied'
          sent_at: string | null
          opened_at: string | null
          replied_at: string | null
        }
        Insert: {
          id?: string
          created_at?: string
          user_id: string
          lead_id: string
          subject: string
          body: string
          status?: 'draft' | 'approved' | 'sent' | 'opened' | 'replied'
          sent_at?: string | null
          opened_at?: string | null
          replied_at?: string | null
        }
        Update: {
          id?: string
          created_at?: string
          user_id?: string
          lead_id?: string
          subject?: string
          body?: string
          status?: 'draft' | 'approved' | 'sent' | 'opened' | 'replied'
          sent_at?: string | null
          opened_at?: string | null
          replied_at?: string | null
        }
      }
      chat_messages: {
        Row: {
          id: string
          created_at: string
          user_id: string
          agent_run_id: string | null
          role: 'user' | 'assistant' | 'system'
          content: string
        }
        Insert: {
          id?: string
          created_at?: string
          user_id: string
          agent_run_id?: string | null
          role: 'user' | 'assistant' | 'system'
          content: string
        }
        Update: {
          id?: string
          created_at?: string
          user_id?: string
          agent_run_id?: string | null
          role?: 'user' | 'assistant' | 'system'
          content?: string
        }
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      [_ in never]: never
    }
  }
} 