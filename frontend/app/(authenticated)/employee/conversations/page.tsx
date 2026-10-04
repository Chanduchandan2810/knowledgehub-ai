"use client"
import { MessageSquare, Search, Calendar, Loader2 } from 'lucide-react'
import { EmptyState } from '@/components/shared/empty-state'
import { PageTransition } from '@/components/shared/page-transition'
import { Input } from '@/components/ui/input'
import { useEffect, useState } from 'react'
import { createClient } from '@/utils/supabase/client'
import { useRouter } from 'next/navigation'

interface Conversation {
  id: string
  title: string
  created_at: string
}

export default function EmployeeConversations() {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [loading, setLoading] = useState(true)
  const router = useRouter()
  const supabase = createClient()

  useEffect(() => {
    const fetchConversations = async () => {
      try {
        const { data: { session } } = await supabase.auth.getSession()
        if (!session) return
        
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'}/api/v1/conversations`, {
          headers: { 'Authorization': `Bearer ${session.access_token}` }
        })
        if (res.ok) {
          const data = await res.json()
          setConversations(data)
        }
      } catch (err) {
        console.error('Failed to fetch conversations', err)
      } finally {
        setLoading(false)
      }
    }
    fetchConversations()
  }, [])

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
            
            <div className="divide-y divide-slate-100 flex-1">
              {loading ? (
                <div className="flex items-center justify-center h-48">
                  <Loader2 className="w-6 h-6 animate-spin text-slate-400" />
                </div>
              ) : conversations.length === 0 ? (
                <div className="flex items-center justify-center h-48 text-sm text-slate-500">
                  No conversations found.
                </div>
              ) : (
                conversations.map(conv => (
                  <div 
                    key={conv.id} 
                    onClick={() => router.push(`/employee/chat?id=${conv.id}`)}
                    className="grid grid-cols-12 px-6 py-4 items-center hover:bg-slate-50 transition-colors cursor-pointer group"
                  >
                    <div className="col-span-8 md:col-span-9 flex items-center gap-3">
                      <MessageSquare className="w-4 h-4 text-slate-400 group-hover:text-primary-500" />
                      <span className="text-sm font-medium text-slate-800 line-clamp-1">{conv.title}</span>
                    </div>
                    <div className="col-span-4 md:col-span-3 text-right flex items-center justify-end gap-1.5 text-xs text-slate-500">
                      <Calendar className="w-3.5 h-3.5" /> 
                      {new Date(conv.created_at).toLocaleDateString()}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </PageTransition>
    </div>
  )
}
