'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  Brain,
  BarChart2,
  ListTodo,
  Mail,
  User,
  Settings,
  Menu,
  X
} from 'lucide-react'

const navigation = [
  { name: 'Chat', href: '/', icon: Brain, emoji: '🧠' },
  { name: 'Dashboard', href: '/dashboard', icon: BarChart2, emoji: '📊' },
  { name: 'Tasks', href: '/tasks', icon: ListTodo, emoji: '📁' },
  { name: 'Emails', href: '/emails', icon: Mail, emoji: '🧾' },
  { name: 'Profile', href: '/profile', icon: User, emoji: '👤' },
  { name: 'Settings', href: '/settings', icon: Settings, emoji: '⚙️' },
]

export default function Sidebar() {
  const pathname = usePathname()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <>
      {/* Mobile sidebar */}
      <div className="lg:hidden">
        <div className="fixed inset-0 flex z-40">
          {/* Sidebar overlay */}
          {sidebarOpen && (
            <div 
              className="fixed inset-0 bg-gray-600 bg-opacity-75" 
              onClick={() => setSidebarOpen(false)}
            />
          )}

          {/* Sidebar */}
          <div className={`
            relative flex-1 flex flex-col max-w-xs w-full bg-white transform transition-transform ease-in-out duration-300
            ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
          `}>
            {/* Close button */}
            <div className="absolute top-0 right-0 -mr-12 pt-2">
              <button
                type="button"
                className="ml-1 flex items-center justify-center h-10 w-10 rounded-full focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white"
                onClick={() => setSidebarOpen(false)}
              >
                <span className="sr-only">Close sidebar</span>
                <X className="h-6 w-6 text-white" />
              </button>
            </div>

            {/* Logo */}
            <div className="flex-shrink-0 flex items-center px-4 h-16 bg-blue-600">
              <span className="text-white text-lg font-bold">AI SDR Agent</span>
            </div>

            {/* Navigation */}
            <div className="mt-5 flex-1 h-0 overflow-y-auto">
              <nav className="px-2 space-y-1">
                {navigation.map((item) => {
                  const isActive = pathname === item.href
                  return (
                    <Link
                      key={item.name}
                      href={item.href}
                      className={`
                        group flex items-center px-2 py-2 text-base font-medium rounded-md
                        ${isActive 
                          ? 'bg-gray-100 text-blue-600' 
                          : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                        }
                      `}
                    >
                      <span className="mr-2">{item.emoji}</span>
                      <item.icon
                        className={`
                          mr-2 h-5 w-5
                          ${isActive ? 'text-blue-600' : 'text-gray-400 group-hover:text-gray-500'}
                        `}
                      />
                      <span className="font-medium">{item.name}</span>
                    </Link>
                  )
                })}
              </nav>
            </div>
          </div>

          {/* Toggle button */}
          <div className="flex-shrink-0 w-14">
            {!sidebarOpen && (
              <button
                type="button"
                className="flex items-center justify-center h-12 w-12 rounded-full focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white"
                onClick={() => setSidebarOpen(true)}
              >
                <span className="sr-only">Open sidebar</span>
                <Menu className="h-6 w-6 text-white" />
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:flex lg:flex-shrink-0">
        <div className="flex flex-col w-64">
          {/* Logo */}
          <div className="flex items-center h-16 flex-shrink-0 px-4 bg-blue-600">
            <span className="text-white text-lg font-bold">AI SDR Agent</span>
          </div>

          {/* Navigation */}
          <div className="h-0 flex-1 flex flex-col overflow-y-auto">
            <nav className="flex-1 px-2 py-4 bg-white space-y-1">
              {navigation.map((item) => {
                const isActive = pathname === item.href
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={`
                      group flex items-center px-2 py-2 text-sm font-medium rounded-md
                      ${isActive 
                        ? 'bg-gray-100 text-blue-600' 
                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                      }
                    `}
                  >
                    <span className="mr-2">{item.emoji}</span>
                    <item.icon
                      className={`
                        mr-2 h-5 w-5
                        ${isActive ? 'text-blue-600' : 'text-gray-400 group-hover:text-gray-500'}
                      `}
                    />
                    <span className="font-medium">{item.name}</span>
                  </Link>
                )
              })}
            </nav>
          </div>
        </div>
      </div>
    </>
  )
} 