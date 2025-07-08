'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs'
import { Database } from '@/types/supabase'
import { ChevronDown, LogOut, User, Settings } from 'lucide-react'
import RunAgentButton from './run-agent-button'

type UserProfile = Database['public']['Tables']['profiles']['Row']

export default function TopBar({ user }: { user: UserProfile | null }) {
  const router = useRouter()
  const supabase = createClientComponentClient<Database>()
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false)

  const handleSignOut = async () => {
    await supabase.auth.signOut()
    router.refresh()
    router.push('/auth/login')
  }

  return (
    <header className="bg-white shadow-sm z-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              {/* Mobile logo - visible on small screens */}
              <div className="lg:hidden">
                <span className="text-blue-600 text-lg font-bold">AI SDR Agent</span>
              </div>
            </div>
          </div>
          
          <div className="flex items-center">
            {/* Run Agent Button */}
            <div className="mr-4">
              <RunAgentButton />
            </div>
            
            {/* User Profile Dropdown */}
            <div className="ml-3 relative">
              <div>
                <button
                  type="button"
                  className="max-w-xs bg-white flex items-center text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  id="user-menu"
                  aria-expanded="false"
                  aria-haspopup="true"
                  onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                >
                  <span className="sr-only">Open user menu</span>
                  <div className="h-8 w-8 rounded-full bg-gray-200 flex items-center justify-center text-gray-600">
                    {user?.avatar_url ? (
                      <img
                        className="h-8 w-8 rounded-full"
                        src={user.avatar_url}
                        alt={user.full_name || 'User'}
                      />
                    ) : (
                      <User className="h-5 w-5" />
                    )}
                  </div>
                  <span className="ml-2 hidden md:block text-gray-700">
                    {user?.full_name || 'User'}
                  </span>
                  <ChevronDown className="ml-1 h-4 w-4 text-gray-500" />
                </button>
              </div>

              {isUserMenuOpen && (
                <div
                  className="origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg py-1 bg-white ring-1 ring-black ring-opacity-5 focus:outline-none"
                  role="menu"
                  aria-orientation="vertical"
                  aria-labelledby="user-menu"
                >
                  <a
                    href="/profile"
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    role="menuitem"
                  >
                    <div className="flex items-center">
                      <User className="mr-3 h-4 w-4 text-gray-500" />
                      Your Profile
                    </div>
                  </a>
                  <a
                    href="/settings"
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    role="menuitem"
                  >
                    <div className="flex items-center">
                      <Settings className="mr-3 h-4 w-4 text-gray-500" />
                      Settings
                    </div>
                  </a>
                  <button
                    onClick={handleSignOut}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    role="menuitem"
                  >
                    <div className="flex items-center">
                      <LogOut className="mr-3 h-4 w-4 text-gray-500" />
                      Sign out
                    </div>
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  )
} 