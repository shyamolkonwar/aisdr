'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { X } from 'lucide-react'

interface RunAgentModalProps {
  isOpen: boolean
  onClose: () => void
}

export default function RunAgentModal({ isOpen, onClose }: RunAgentModalProps) {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const [formData, setFormData] = useState({
    target_industry: '',
    target_role: '',
    target_region: '',
    lead_count: 10,
    email_tone: 'professional',
    email_objective: 'book_call'
  })
  const [error, setError] = useState<string | null>(null)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: name === 'lead_count' ? parseInt(value) : value
    }))
  }

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch('/api/agent/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to start agent')
      }

      // Close the modal
      onClose()
      
      // Redirect to chat page with the agent run ID
      router.push(`/?agent_run_id=${data.data.agent_run_id}`)
    } catch (err) {
      console.error('Error starting agent:', err)
      setError(err instanceof Error ? err.message : 'An unexpected error occurred')
    } finally {
      setIsLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed z-50 inset-0 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        {/* Background overlay */}
        <div 
          className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" 
          onClick={onClose}
        />

        {/* Modal panel */}
        <div className="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6">
          <div className="absolute top-0 right-0 pt-4 pr-4">
            <button
              type="button"
              className="bg-white rounded-md text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              onClick={onClose}
            >
              <span className="sr-only">Close</span>
              <X className="h-6 w-6" />
            </button>
          </div>
          
          <div className="sm:flex sm:items-start">
            <div className="mt-3 text-center sm:mt-0 sm:text-left w-full">
              <h3 className="text-lg leading-6 font-medium text-gray-900">
                Configure AI SDR Agent
              </h3>
              <p className="mt-2 text-sm text-gray-500">
                Set your targeting preferences and email settings for the AI agent.
              </p>
              
              {error && (
                <div className="mt-4 rounded-md bg-red-50 p-4">
                  <div className="flex">
                    <div className="ml-3">
                      <h3 className="text-sm font-medium text-red-800">Error</h3>
                      <div className="mt-2 text-sm text-red-700">
                        <p>{error}</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              
              <form onSubmit={handleSubmit} className="mt-6 space-y-4">
                {/* Target Industry */}
                <div>
                  <label htmlFor="target_industry" className="block text-sm font-medium text-gray-700">
                    Target Industry
                  </label>
                  <input
                    type="text"
                    name="target_industry"
                    id="target_industry"
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    placeholder="e.g., Software, Healthcare, Finance"
                    value={formData.target_industry}
                    onChange={handleChange}
                    required
                    disabled={isLoading}
                  />
                </div>
                
                {/* Target Role */}
                <div>
                  <label htmlFor="target_role" className="block text-sm font-medium text-gray-700">
                    Target Job Title
                  </label>
                  <input
                    type="text"
                    name="target_role"
                    id="target_role"
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    placeholder="e.g., CTO, Marketing Director, VP of Sales"
                    value={formData.target_role}
                    onChange={handleChange}
                    required
                    disabled={isLoading}
                  />
                </div>
                
                {/* Target Region */}
                <div>
                  <label htmlFor="target_region" className="block text-sm font-medium text-gray-700">
                    Target Region
                  </label>
                  <input
                    type="text"
                    name="target_region"
                    id="target_region"
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    placeholder="e.g., US, Europe, Global"
                    value={formData.target_region}
                    onChange={handleChange}
                    required
                    disabled={isLoading}
                  />
                </div>
                
                {/* Lead Count */}
                <div>
                  <label htmlFor="lead_count" className="block text-sm font-medium text-gray-700">
                    Number of Leads to Reach
                  </label>
                  <input
                    type="number"
                    name="lead_count"
                    id="lead_count"
                    min="1"
                    max="100"
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    value={formData.lead_count}
                    onChange={handleChange}
                    required
                    disabled={isLoading}
                  />
                </div>
                
                {/* Email Tone */}
                <div>
                  <label htmlFor="email_tone" className="block text-sm font-medium text-gray-700">
                    Email Tone
                  </label>
                  <select
                    id="email_tone"
                    name="email_tone"
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    value={formData.email_tone}
                    onChange={handleChange}
                    disabled={isLoading}
                  >
                    <option value="professional">Professional</option>
                    <option value="friendly">Friendly</option>
                    <option value="casual">Casual</option>
                    <option value="direct">Direct</option>
                  </select>
                </div>
                
                {/* Email Objective */}
                <div>
                  <label htmlFor="email_objective" className="block text-sm font-medium text-gray-700">
                    Email Objective
                  </label>
                  <select
                    id="email_objective"
                    name="email_objective"
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    value={formData.email_objective}
                    onChange={handleChange}
                    disabled={isLoading}
                  >
                    <option value="book_call">Book a Call</option>
                    <option value="get_reply">Get a Reply</option>
                    <option value="share_info">Share Information</option>
                    <option value="request_intro">Request Introduction</option>
                  </select>
                </div>
                
                <div className="mt-5 sm:mt-6">
                  <button
                    type="submit"
                    className={`inline-flex justify-center w-full rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:text-sm ${
                      isLoading ? 'opacity-50 cursor-not-allowed' : ''
                    }`}
                    disabled={isLoading}
                  >
                    {isLoading ? 'Starting Agent...' : 'Start SDR Agent'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 