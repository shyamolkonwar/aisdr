'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Play } from 'lucide-react'
import RunAgentModal from './run-agent-modal'

export default function RunAgentButton() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  
  return (
    <>
      <button
        type="button"
        onClick={() => setIsModalOpen(true)}
        className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
      >
        <Play className="mr-2 h-4 w-4" />
        Run Agent
      </button>
      
      {isModalOpen && (
        <RunAgentModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
        />
      )}
    </>
  )
} 