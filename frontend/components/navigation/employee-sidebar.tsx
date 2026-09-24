"use client"

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { MessageSquare, Clock, User, Plus } from 'lucide-react'
import { Button, cn } from '../ui/button'

const recentChats = [
  "Annual leave policy",
  "Travel reimbursement",
  "Security policy",
  "Employee onboarding"
]

export function EmployeeSidebar() {
  const pathname = usePathname()

  return (
    <div className="flex flex-col w-72 bg-slate-50 h-screen fixed left-0 top-0 border-r">
      <div className="p-4 border-b">
        <Link href="/employee/chat">
          <Button className="w-full justify-start shadow-sm" variant="outline">
            <Plus className="mr-2 h-4 w-4" /> New Chat
          </Button>
        </Link>
      </div>
      <div className="flex-1 overflow-y-auto py-4">
        <div className="px-3">
          <h3 className="px-4 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Recent</h3>
          <nav className="space-y-1">
            {recentChats.map((chat) => (
              <Link key={chat} href="/employee/conversations" className="flex items-center px-4 py-2 text-sm text-slate-700 rounded-md hover:bg-slate-200 truncate">
                <MessageSquare className="mr-3 h-4 w-4 text-slate-400 shrink-0" />
                <span className="truncate">{chat}</span>
              </Link>
            ))}
          </nav>
        </div>
      </div>
      <div className="p-4 border-t">
        <nav className="space-y-1">
          <Link href="/employee/profile" className={cn("flex items-center px-4 py-2 text-sm font-medium rounded-md", pathname === '/employee/profile' ? "bg-slate-200 text-slate-900" : "text-slate-700 hover:bg-slate-200")}>
            <User className="mr-3 h-4 w-4 text-slate-500" /> Profile & Settings
          </Link>
        </nav>
      </div>
    </div>
  )
}
