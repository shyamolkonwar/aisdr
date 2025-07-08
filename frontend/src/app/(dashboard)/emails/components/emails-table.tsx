'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Database } from '@/types/supabase'
import { Edit, Send, Check, RefreshCw, Save, ExternalLink } from 'lucide-react'
import EmailDetailModal from './email-detail-modal'

type Email = Database['public']['Tables']['emails']['Row'] & {
  leads: Database['public']['Tables']['leads']['Row']
}

interface EmailsTableProps {
  emails: Email[]
}

export default function EmailsTable({ emails }: EmailsTableProps) {
  const router = useRouter()
  const [selectedEmail, setSelectedEmail] = useState<Email | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isLoading, setIsLoading] = useState<Record<string, boolean>>({})
  
  const handleAction = async (email: Email, action: string) => {
    setIsLoading(prev => ({ ...prev, [email.id]: true }))
    
    try {
      let endpoint = '/api/emails'
      let method = 'PUT'
      let body: any = { id: email.id }
      
      switch (action) {
        case 'approve':
          body.status = 'approved'
          break
        case 'send':
          body.status = 'sent'
          break
        case 'regenerate':
          // This would call a different endpoint to regenerate the email
          endpoint = '/api/emails/regenerate'
          method = 'POST'
          body = { email_id: email.id }
          break
        default:
          break
      }
      
      const response = await fetch(endpoint, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      })
      
      if (!response.ok) {
        throw new Error('Failed to perform action')
      }
      
      // Refresh the page to get updated data
      router.refresh()
    } catch (error) {
      console.error(`Error performing ${action}:`, error)
      // Show error to user
    } finally {
      setIsLoading(prev => ({ ...prev, [email.id]: false }))
    }
  }
  
  const openEmailDetail = (email: Email) => {
    setSelectedEmail(email)
    setIsModalOpen(true)
  }
  
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'draft':
        return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">Draft</span>
      case 'approved':
        return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">Approved</span>
      case 'sent':
        return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">Sent</span>
      case 'opened':
        return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">Opened</span>
      case 'replied':
        return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">Replied</span>
      default:
        return null
    }
  }
  
  return (
    <>
      <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
        {emails.length === 0 ? (
          <div className="p-6 text-center">
            <p className="text-gray-500">No emails found. Run the AI SDR Agent to generate personalized emails.</p>
          </div>
        ) : (
          <table className="min-w-full divide-y divide-gray-300">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">Lead</th>
                <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Company</th>
                <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Subject</th>
                <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Status</th>
                <th scope="col" className="relative py-3.5 pl-3 pr-4 sm:pr-6">
                  <span className="sr-only">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              {emails.map((email) => (
                <tr 
                  key={email.id} 
                  className="hover:bg-gray-50 cursor-pointer"
                  onClick={() => openEmailDetail(email)}
                >
                  <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6">
                    {email.leads?.full_name || 'Unknown'}
                  </td>
                  <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                    {email.leads?.company || 'Unknown'}
                  </td>
                  <td className="px-3 py-4 text-sm text-gray-500 max-w-xs truncate">
                    {email.subject}
                  </td>
                  <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                    {getStatusBadge(email.status)}
                  </td>
                  <td className="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                    <div className="flex space-x-2 justify-end" onClick={(e) => e.stopPropagation()}>
                      <button
                        type="button"
                        className="inline-flex items-center px-2.5 py-1.5 border border-transparent text-xs font-medium rounded text-blue-700 bg-blue-100 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                        onClick={() => openEmailDetail(email)}
                        disabled={isLoading[email.id]}
                      >
                        <Edit className="h-4 w-4 mr-1" />
                        Edit
                      </button>
                      
                      {email.status === 'draft' && (
                        <button
                          type="button"
                          className="inline-flex items-center px-2.5 py-1.5 border border-transparent text-xs font-medium rounded text-green-700 bg-green-100 hover:bg-green-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                          onClick={() => handleAction(email, 'approve')}
                          disabled={isLoading[email.id]}
                        >
                          <Check className="h-4 w-4 mr-1" />
                          Approve
                        </button>
                      )}
                      
                      {(email.status === 'draft' || email.status === 'approved') && (
                        <button
                          type="button"
                          className="inline-flex items-center px-2.5 py-1.5 border border-transparent text-xs font-medium rounded text-yellow-700 bg-yellow-100 hover:bg-yellow-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500"
                          onClick={() => handleAction(email, 'send')}
                          disabled={isLoading[email.id]}
                        >
                          <Send className="h-4 w-4 mr-1" />
                          Send
                        </button>
                      )}
                      
                      <button
                        type="button"
                        className="inline-flex items-center px-2.5 py-1.5 border border-transparent text-xs font-medium rounded text-purple-700 bg-purple-100 hover:bg-purple-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500"
                        onClick={() => handleAction(email, 'regenerate')}
                        disabled={isLoading[email.id]}
                      >
                        <RefreshCw className="h-4 w-4 mr-1" />
                        Regenerate
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
      
      {/* Email detail modal */}
      {selectedEmail && (
        <EmailDetailModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          email={selectedEmail}
        />
      )}
    </>
  )
} 