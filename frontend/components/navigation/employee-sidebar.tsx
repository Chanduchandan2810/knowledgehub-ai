"use client"
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { MessageSquare, Plus, BrainCircuit, Search, LogOut, Settings } from 'lucide-react'
import { Button, cn } from '../ui/button'

export function EmployeeSidebar() {
  const pathname = usePathname()

  return (
    <aside className="hidden md:flex flex-col w-[260px] flex-shrink-0 border-r border-slate-200 bg-slate-50/50 z-20">
      <div className="h-16 flex items-center px-4 border-b border-slate-200/60 bg-transparent">
        <Link href="/employee/chat" className="flex items-center gap-2 font-bold text-lg tracking-tight text-slate-900 group w-full">
          <div className="bg-primary-600 text-white p-1 rounded-md shadow-sm group-hover:bg-primary-700 transition-colors">
            <BrainCircuit className="w-4 h-4" />
          </div>
          KnowledgeHub
        </Link>
      </div>
      
      <div className="p-4">
        <Button className="w-full justify-start shadow-sm bg-primary-600 hover:bg-primary-700 text-white font-medium h-10 rounded-lg">
          <Plus className="mr-2 h-4 w-4" /> New Chat
        </Button>
      </div>

      <div className="px-4 pb-2">
        <div className="relative">
          <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-slate-400" />
          <input type="text" placeholder="Search conversations..." className="w-full pl-8 pr-3 py-1.5 text-sm bg-white border border-slate-200 rounded-md shadow-sm focus:outline-none focus:border-primary-400 focus:ring-1 focus:ring-primary-400 transition-all" />
        </div>
      </div>

      <div className="flex-1 py-4 overflow-y-auto custom-scrollbar">
        <h3 className="px-5 text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2">History</h3>
        <nav className="space-y-0.5 px-3">
          {[
            { id: 1, title: 'Annual Leave Policy & Carryover', active: true },
            { id: 2, title: 'Hardware Request Process', active: false },
            { id: 3, title: 'Q3 Financial Summary Review', active: false },
            { id: 4, title: 'Onboarding Checklist 2024', active: false },
          ].map(chat => (
            <Link key={chat.id} href="/employee/conversations" className={cn(
              "flex items-center px-3 py-2 text-sm font-medium rounded-md transition-all duration-200 group",
              chat.active ? "bg-white border border-slate-200 shadow-sm text-slate-900" : "text-slate-600 hover:bg-slate-100 hover:text-slate-900 border border-transparent"
            )}>
              <MessageSquare className={cn("mr-3 h-4 w-4", chat.active ? "text-primary-500" : "text-slate-400 group-hover:text-slate-500")} />
              <span className="truncate flex-1">{chat.title}</span>
            </Link>
          ))}
        </nav>
      </div>

      <div className="p-4 border-t border-slate-200/60 bg-transparent flex flex-col gap-1">
        <Link href="/employee/profile" className={cn(
          "flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors",
          pathname === "/employee/profile" ? "bg-slate-200/50 text-slate-900" : "text-slate-600 hover:bg-slate-200/50 hover:text-slate-900"
        )}>
          <Settings className="w-4 h-4 mr-3 text-slate-400" /> Profile Settings
        </Link>
        <button className="flex items-center px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-200/50 hover:text-slate-900 rounded-md transition-colors">
          <LogOut className="w-4 h-4 mr-3 text-slate-400" /> Sign Out
        </button>
      </div>
    </aside>
  )
}
