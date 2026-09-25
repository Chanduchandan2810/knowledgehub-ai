"use client"
import { MessageSquare, Search, Calendar } from 'lucide-react'
import { EmptyState } from '@/components/shared/empty-state'
import { PageTransition } from '@/components/shared/page-transition'
import { Input } from '@/components/ui/input'

export default function EmployeeConversations() {
  return (
    <div className="flex flex-col h-full bg-slate-50/50">
      <header className="h-14 flex-shrink-0 bg-white/80 backdrop-blur-md border-b border-slate-200/60 flex items-center justify-between px-6 z-10">
        <h1 className="font-semibold text-slate-900 text-sm">Conversation History</h1>
      </header>

      <PageTransition className="flex-1 overflow-y-auto p-6 md:p-8">
        <div className="max-w-4xl mx-auto">
          <div className="relative mb-6">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
            <Input placeholder="Search previous conversations..." className="pl-9 bg-white shadow-sm" />
          </div>

          <div className="bg-white border border-slate-200/80 rounded-xl shadow-sm overflow-hidden min-h-[400px] flex flex-col">
            <div className="grid grid-cols-12 px-6 py-3 border-b border-slate-100 bg-slate-50/80 text-xs font-semibold text-slate-500 uppercase tracking-wider">
              <div className="col-span-8 md:col-span-9">Topic</div>
              <div className="col-span-4 md:col-span-3 text-right">Date</div>
            </div>
            
            <div className="divide-y divide-slate-100">
              <div className="grid grid-cols-12 px-6 py-4 items-center hover:bg-slate-50 transition-colors cursor-pointer group">
                <div className="col-span-8 md:col-span-9 flex items-center gap-3">
                  <MessageSquare className="w-4 h-4 text-slate-400 group-hover:text-primary-500" />
                  <span className="text-sm font-medium text-slate-800">Annual Leave Policy & Carryover</span>
                </div>
                <div className="col-span-4 md:col-span-3 text-right flex items-center justify-end gap-1.5 text-xs text-slate-500">
                  <Calendar className="w-3.5 h-3.5" /> Oct 24, 2024
                </div>
              </div>
              
              <div className="grid grid-cols-12 px-6 py-4 items-center hover:bg-slate-50 transition-colors cursor-pointer group">
                <div className="col-span-8 md:col-span-9 flex items-center gap-3">
                  <MessageSquare className="w-4 h-4 text-slate-400 group-hover:text-primary-500" />
                  <span className="text-sm font-medium text-slate-800">Hardware Request Process</span>
                </div>
                <div className="col-span-4 md:col-span-3 text-right flex items-center justify-end gap-1.5 text-xs text-slate-500">
                  <Calendar className="w-3.5 h-3.5" /> Oct 22, 2024
                </div>
              </div>
            </div>
          </div>
        </div>
      </PageTransition>
    </div>
  )
}
