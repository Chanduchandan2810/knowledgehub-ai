"use client"
import React, { useState, useEffect, useRef } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { createClient } from '@/utils/supabase/client'
import { motion, AnimatePresence } from 'framer-motion'
import { BrainCircuit, Send, Loader2, FileText, Database, Plus, MessageSquare, Menu, X, ChevronRight } from 'lucide-react'
import { Button, cn } from '../ui/button'
import { Input } from '../ui/input'
import { PageTransition } from '../shared/page-transition'

interface Citation {
  id: string
  chunk_id: string
  document_id: string
  filename?: string
}

interface Message {
  id: string
  role: string
  content: string
  created_at: string
  citations: Citation[]
}

interface Conversation {
  id: string
  title: string
  created_at: string
  updated_at: string
}

export function ChatInterface({ role }: { role: 'Admin' | 'Employee' }) {
  const router = useRouter()
  const searchParams = useSearchParams()
  const conversationId = searchParams.get('id')


  const [query, setQuery] = useState('')
  const [agentStatus, setAgentStatus] = useState<string | null>(null)

  const [isSearching, setIsSearching] = useState(false)
  const [messages, setMessages] = useState<Message[]>([])
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [error, setError] = useState<string | null>(null)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const supabase = createClient()

  const fetchConversations = async () => {
    try {
      const { data: { session } } = await supabase.auth.getSession()
      if (!session) return

      const res = await fetch(`/api/v1/conversations`, {
        headers: { 'Authorization': `Bearer ${session.access_token}` }
      })
      if (res.ok) {
        const data = await res.json()
        setConversations(data)
      }
    } catch (err) {
      console.error('Failed to fetch conversations', err)
    }
  }

  const scrollRafRef = useRef<number | null>(null)

  const scrollToBottom = () => {
    if (scrollRafRef.current) cancelAnimationFrame(scrollRafRef.current)
    scrollRafRef.current = requestAnimationFrame(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    })
  }

  const fetchMessages = async (id: string) => {
    try {
      const { data: { session } } = await supabase.auth.getSession()
      if (!session) return

      const res = await fetch(`/api/v1/conversations/${id}/messages`, {
        headers: { 'Authorization': `Bearer ${session.access_token}` }
      })
      if (res.ok) {
        const data = await res.json()
        setMessages(data)
        scrollToBottom()
      } else {
        setError('Failed to load conversation.')
      }
    } catch (err) {
      setError('An error occurred while loading the conversation.')
    }
  }

  useEffect(() => {
    const t = setTimeout(() => fetchConversations(), 0)
    return () => clearTimeout(t)
  }, [])

  useEffect(() => {
    const t = setTimeout(() => {
      if (conversationId) {
        fetchMessages(conversationId)
      } else {
        setMessages([])
      }
    }, 0)
    return () => clearTimeout(t)
  }, [conversationId])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleCreateNew = async () => {
    try {
      const { data: { session } } = await supabase.auth.getSession()
      if (!session) return

      const res = await fetch(`/api/v1/conversations`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ title: 'New Conversation' })
      })

      if (res.ok) {
        const data = await res.json()
        router.push(`/${role.toLowerCase()}/chat?id=${data.id}`)
        fetchConversations()
        if (window.innerWidth < 768) setSidebarOpen(false)
      }
    } catch (err) {
      console.error(err)
    }
  }

  const handleSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault()
    if (!query.trim() || isSearching) return

    const userMessageContent = query.trim()

    setQuery('')
    setAgentStatus(null)
    setIsSearching(true)

    setError(null)

    let currentConvId = conversationId

    try {
      const { data: { session } } = await supabase.auth.getSession()
      if (!session) throw new Error('Not authenticated')

      if (!currentConvId) {
        const convRes = await fetch(`/api/v1/conversations`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${session.access_token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ title: userMessageContent.substring(0, 30) + '...' })
        })
        if (!convRes.ok) throw new Error('Failed to create conversation')
        const convData = await convRes.json()
        currentConvId = convData.id
        window.history.pushState({}, '', `/${role.toLowerCase()}/chat?id=${currentConvId}`)
        fetchConversations()
      }

      const tempUserId = `temp-${Date.now()}`
      setMessages(prev => [...prev, { id: tempUserId, role: 'USER', content: userMessageContent, created_at: new Date().toISOString(), citations: [] }])
      scrollToBottom()

      const res = await fetch(`/api/v1/conversations/${currentConvId}/messages/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`
        },
        body: JSON.stringify({ content: userMessageContent })
      })

      if (!res.ok) {
        let msg = 'Failed to send message.'
        try {
           const errData = await res.json()
           msg = errData.detail || msg
        } catch(e) {}
        throw new Error(msg)
      }

      const reader = res.body?.getReader()
      const decoder = new TextDecoder()
      const tempAssistantId = `temp-assistant-${Date.now()}`

      setMessages(prev => [...prev, { id: tempAssistantId, role: 'ASSISTANT', content: '', created_at: new Date().toISOString(), citations: [] }])

      if (reader) {
        let buffer = ''
        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          buffer += decoder.decode(value, { stream: true })
          const blocks = buffer.split('\n\n')
          buffer = blocks.pop() || ''

          for (const block of blocks) {
            const lines = block.split('\n')
            let event = ''
            let dataStr = ''

            for (const line of lines) {
              if (line.startsWith('event:')) {
                event = line.substring(6).trim()
              } else if (line.startsWith('data:')) {
                dataStr = line.substring(5).trim()
              }
            }

            if (event && dataStr) {
              try {
                const data = JSON.parse(dataStr)

                if (event === 'start') {
                  setMessages(prev => prev.map(m => m.id === tempUserId ? { ...m, id: data.message_id } : m))
                } else if (event === 'agent_status') {
                  setAgentStatus(data.message)
                } else if (event === 'token') {
                  setAgentStatus(null) // clear when tokens start
                  setMessages(prev => prev.map(m => m.id === tempAssistantId ? { ...m, content: m.content + (data.text || '') } : m))

                } else if (event === 'citations') {
                  setMessages(prev => prev.map(m => m.id === tempAssistantId ? { ...m, citations: data.citations || [] } : m))
                } else if (event === 'done') {
                  setMessages(prev => prev.map(m => m.id === tempAssistantId ? { ...m, id: data.message_id } : m))
                } else if (event === 'error') {
                  setError(data.message)
                  setMessages(prev => prev.filter(m => m.id !== tempAssistantId))
                }
              } catch (e) {
                console.error("Failed to parse SSE block:", block, e)
              }
            }
          }
        }
      }

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred.'
      setError(errorMessage)
      setMessages(prev => prev.filter(m => !m.id.startsWith('temp-')))
    } finally {
      setIsSearching(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <PageTransition className="flex h-full bg-slate-50 relative overflow-hidden">

      <div className="md:hidden absolute top-4 left-4 z-50">
        <Button size="icon" variant="outline" className="bg-white/80 backdrop-blur-md" onClick={() => setSidebarOpen(true)}>
          <Menu className="w-4 h-4" />
        </Button>
      </div>

      <div className={cn(
        "fixed md:static inset-y-0 left-0 z-40 w-[260px] bg-white border-r border-slate-200 transform transition-transform duration-300 flex flex-col",
        sidebarOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
      )}>
        <div className="p-4 flex items-center justify-between border-b border-slate-100">
          <Button onClick={handleCreateNew} className="flex-1 justify-start shadow-sm bg-primary-600 hover:bg-primary-700 text-white font-medium h-10 rounded-lg">
            <Plus className="mr-2 h-4 w-4" /> New Chat
          </Button>
          <Button size="icon" variant="ghost" className="md:hidden ml-2" onClick={() => setSidebarOpen(false)}>
            <X className="w-4 h-4" />
          </Button>
        </div>

        <div className="flex-1 overflow-y-auto custom-scrollbar py-3 px-3 space-y-1">
          {conversations.length === 0 ? (
            <p className="text-xs text-center text-slate-400 mt-4">No conversations yet.</p>
          ) : (
            conversations.map(conv => (
              <Button
                key={conv.id}
                variant="ghost"
                onClick={() => {
                  router.push(`/${role.toLowerCase()}/chat?id=${conv.id}`)
                  if (window.innerWidth < 768) setSidebarOpen(false)
                }}
                className={cn(
                  "w-full justify-start font-normal text-sm px-3 py-6 h-auto whitespace-normal text-left",
                  conversationId === conv.id ? "bg-primary-50 text-primary-700 hover:bg-primary-100" : "text-slate-600 hover:bg-slate-100"
                )}
              >
                <MessageSquare className={cn("mr-3 h-4 w-4 shrink-0", conversationId === conv.id ? "text-primary-600" : "text-slate-400")} />
                <span className="line-clamp-2 leading-tight">{conv.title || 'Untitled Conversation'}</span>
              </Button>
            ))
          )}
        </div>
      </div>

      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-slate-900/20 backdrop-blur-sm z-30 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <div className="flex-1 flex flex-col relative w-full max-w-full overflow-hidden">
        <div className="flex-1 overflow-y-auto p-4 md:p-8 pb-32">
          {error && (
             <div className="max-w-3xl mx-auto mb-4 p-4 bg-red-50 text-red-700 border border-red-200 rounded-lg text-sm shadow-sm flex items-center justify-between">
               <span>{error}</span>
               <Button variant="ghost" size="sm" onClick={() => setError(null)} className="h-6 w-6 p-0 rounded-full hover:bg-red-100"><X className="w-4 h-4"/></Button>
             </div>
          )}

          {!conversationId && messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center pt-10">
              <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-[0.02]">
                <BrainCircuit className="w-96 h-96" />
              </div>
              <motion.div
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4 }}
                className="max-w-2xl w-full text-center space-y-6 z-10"
              >
                <div className="mx-auto w-14 h-14 bg-white text-primary-600 rounded-2xl flex items-center justify-center mb-6 shadow-sm border border-slate-200/60">
                  <BrainCircuit className="w-7 h-7" />
                </div>
                <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">How can I help you today?</h1>
                <p className="text-slate-500 text-sm sm:text-base max-w-xl mx-auto leading-relaxed">
                  I can answer questions based on your organization&apos;s authorized documents.
                </p>
              </motion.div>
            </div>
          ) : (
            <div className="max-w-3xl mx-auto space-y-8 pb-10">
              {messages.map((msg, idx) => (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  key={msg.id}
                  className={cn(
                    "flex gap-4 w-full",
                    msg.role === 'USER' ? "justify-end" : "justify-start"
                  )}
                >
                  {msg.role !== 'USER' && (
                    <div className="w-8 h-8 rounded-lg bg-primary-600 text-white flex items-center justify-center shrink-0 shadow-sm mt-1">
                      <BrainCircuit className="w-5 h-5" />
                    </div>
                  )}

                  <div className={cn(
                    "max-w-[85%] rounded-2xl px-5 py-4 shadow-sm",
                    msg.role === 'USER' ? "bg-slate-900 text-white" : "bg-white border border-slate-200/80"
                  )}>
                    <div className={cn(
                      "prose prose-sm max-w-none break-words leading-relaxed whitespace-pre-wrap",
                      msg.role === 'USER' ? "text-slate-50" : "text-slate-800"
                    )}>
                      {msg.content}
                    </div>

                    {msg.citations && msg.citations.length > 0 && (
                      <div className="mt-4 pt-4 border-t border-slate-100">
                        <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                          <Database className="w-3.5 h-3.5" /> Sources
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {Array.from(new Map(msg.citations.map(cit => [cit.document_id, cit])).values()).map((cit, i) => (
                            <div key={i} className="inline-flex items-center gap-1.5 text-[11px] font-medium bg-slate-50 text-slate-600 px-2 py-1 rounded border border-slate-200/60 hover:bg-slate-100 transition-colors cursor-default">
                              <FileText className="w-3 h-3 text-primary-500" />
                              {cit.filename ? cit.filename : `Doc ${cit.document_id.substring(0,8)}`}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {msg.role === 'USER' && (
                    <div className="w-8 h-8 rounded-lg bg-slate-200 text-slate-600 flex items-center justify-center shrink-0 shadow-sm mt-1">
                      <MessageSquare className="w-4 h-4" />
                    </div>
                  )}
                </motion.div>
              ))}

              {isSearching && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-4 w-full">
                  <div className="w-8 h-8 rounded-lg bg-primary-600 text-white flex items-center justify-center shrink-0 shadow-sm mt-1">
                    <Loader2 className="w-5 h-5 animate-spin" />
                  </div>
                  <div className="bg-white border border-slate-200/80 rounded-2xl px-5 py-4 shadow-sm flex flex-col gap-1 text-slate-500 text-sm">
                    {agentStatus && (
                        <div className="flex items-center gap-2 text-primary-600 font-medium mb-1">
                            <BrainCircuit className="w-4 h-4 animate-pulse" />
                            {agentStatus}
                        </div>
                    )}
                    <div className="flex items-center gap-2">
                        <span className="flex gap-1">
                        <span className="w-1.5 h-1.5 rounded-full bg-slate-300 animate-bounce [animation-delay:-0.3s]"></span>
                        <span className="w-1.5 h-1.5 rounded-full bg-slate-300 animate-bounce [animation-delay:-0.15s]"></span>
                        <span className="w-1.5 h-1.5 rounded-full bg-slate-300 animate-bounce"></span>
                        </span>
                        {agentStatus ? "Processing context..." : "Generating response..."}
                    </div>
                  </div>
                </motion.div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        <div className="absolute bottom-0 left-0 right-0 p-4 sm:p-6 bg-gradient-to-t from-slate-50 via-slate-50 to-transparent pt-10 z-20">
          <form onSubmit={handleSubmit} className="max-w-3xl mx-auto relative group shadow-2xl rounded-2xl bg-white flex items-end p-2 border border-slate-200 focus-within:ring-2 focus-within:ring-primary-500/20 focus-within:border-primary-500 transition-all">
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              className="w-full max-h-32 min-h-[44px] resize-none bg-transparent outline-none text-sm p-3 placeholder:text-slate-400 custom-scrollbar"
              placeholder="Message KnowledgeHub AI..."
              rows={1}
              style={{ height: Math.max(44, Math.min(120, query.split('\n').length * 20 + 24)) + 'px' }}
            />
            <Button
              type="submit"
              disabled={isSearching || !query.trim()}
              size="icon"
              className="h-10 w-10 shrink-0 rounded-xl bg-primary-600 hover:bg-primary-700 shadow-sm transition-transform hover:scale-105 active:scale-95 disabled:opacity-50 ml-2 self-end mb-0.5"
            >
              {isSearching ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
            </Button>
          </form>
          <div className="text-center mt-3">
            <span className="text-[10px] text-slate-400 flex items-center justify-center gap-1.5 drop-shadow-sm">
              <Database className="w-3 h-3" /> Phase 6: Answers are grounded by authorized retrieved chunks.
            </span>
          </div>
        </div>
      </div>
    </PageTransition>
  )
}
