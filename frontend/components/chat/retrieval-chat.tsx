"use client"
import { BrainCircuit, Send, Database, ShieldCheck, HelpCircle, Loader2, FileText } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { PageTransition } from '@/components/shared/page-transition'
import { motion } from 'framer-motion'
import { useState } from 'react'
import { createClient } from '@/utils/supabase/client'

interface RetrievedChunk {
  chunk_id: string
  document_id: string
  filename: string
  page_number: number | null
  chunk_index: number
  content: string
  distance: number
  similarity: number
}

interface RetrievalResponse {
  query: string
  results: RetrievedChunk[]
  has_relevant_results: boolean
}

export function RetrievalChat({ role }: { role: 'Admin' | 'Employee' }) {
  const [query, setQuery] = useState('')
  const [isSearching, setIsSearching] = useState(false)
  const [retrievedData, setRetrievedData] = useState<RetrievalResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault()
    if (!query.trim()) return

    setIsSearching(true)
    setError(null)
    setRetrievedData(null)

    try {
      const supabase = createClient()
      const { data: { session } } = await supabase.auth.getSession()
      
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'}/api/v1/retrieval`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session?.access_token}`
        },
        body: JSON.stringify({ question: query })
      })

      if (!res.ok) {
        throw new Error(`Error: ${res.statusText}`)
      }

      const data: RetrievalResponse = await res.json()
      setRetrievedData(data)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred during retrieval.'
      setError(errorMessage)
    } finally {
      setIsSearching(false)
    }
  }

  return (
    <PageTransition className="flex flex-col h-full bg-slate-50 relative overflow-hidden">
      <div className="flex-1 overflow-y-auto p-4 md:p-8 flex flex-col relative">
        {(!retrievedData && !isSearching) ? (
          <div className="flex-1 flex flex-col items-center justify-center">
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
              <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">Phase 5: Knowledge Retrieval</h1>
              <p className="text-slate-500 text-sm sm:text-base max-w-xl mx-auto leading-relaxed">
                Enter a question below. I will embed it using MiniLM and retrieve the most relevant authorized document chunks using pgvector.
              </p>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-8 text-left w-full max-w-xl mx-auto">
                {[
                  "What is our annual leave policy?",
                  "What is the hardware reimbursement process?",
                  "Where can I find the compliance manual?",
                  "How do I request a new laptop?"
                ].map((q, i) => (
                  <motion.div 
                    key={i}
                    whileHover={{ scale: 1.01 }}
                    whileTap={{ scale: 0.99 }}
                    className="p-3.5 bg-white border border-slate-200/80 rounded-xl hover:border-primary-300 hover:shadow-sm cursor-pointer transition-all shadow-sm group"
                    onClick={() => setQuery(q)}
                  >
                    <p className="text-xs font-medium text-slate-600 group-hover:text-primary-700 transition-colors">{q}</p>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </div>
        ) : (
          <div className="max-w-4xl mx-auto w-full space-y-6 pb-24">
            <div className="flex items-center gap-3 border-b border-slate-200 pb-4">
              <h2 className="text-xl font-semibold text-slate-900">Retrieval Results</h2>
              <span className="text-sm text-slate-500">Query: &quot;{query}&quot;</span>
            </div>

            {isSearching && (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-primary-500" />
                <span className="ml-3 text-slate-600">Embedding and searching...</span>
              </div>
            )}

            {error && (
              <div className="p-4 bg-red-50 text-red-700 border border-red-200 rounded-lg">
                {error}
              </div>
            )}

            {retrievedData && !isSearching && (
              <div className="space-y-6">
                {!retrievedData.has_relevant_results && (
                  <div className="p-4 bg-amber-50 text-amber-700 border border-amber-200 rounded-lg">
                    No authorized documents were found that closely match your question based on the relevance threshold.
                  </div>
                )}
                
                {retrievedData.results.map((chunk, i) => (
                  <motion.div 
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.05 }}
                    key={chunk.chunk_id} 
                    className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-3"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-2 text-sm font-medium text-slate-700">
                        <FileText className="w-4 h-4 text-primary-600" />
                        {chunk.filename}
                      </div>
                      <div className="text-xs font-mono bg-slate-100 text-slate-500 px-2 py-1 rounded">
                        Sim: {(chunk.similarity * 100).toFixed(1)}%
                      </div>
                    </div>
                    <p className="text-slate-800 text-sm leading-relaxed whitespace-pre-wrap">
                      {chunk.content}
                    </p>
                    <div className="flex items-center gap-4 text-xs text-slate-400">
                      <span>Page {chunk.page_number || 'N/A'}</span>
                      <span>Chunk {chunk.chunk_index}</span>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
      
      <div className="absolute bottom-0 left-0 right-0 p-4 sm:p-6 bg-gradient-to-t from-white via-white to-transparent pt-10 z-20 pointer-events-none">
        <form onSubmit={handleSearch} className="max-w-3xl mx-auto relative group pointer-events-auto shadow-2xl rounded-full">
          <Input 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full h-14 pl-6 pr-14 text-sm rounded-full border-slate-300 focus-visible:ring-primary-500 bg-white transition-all shadow-sm" 
            placeholder="Ask about company policies, documents, or knowledge..."
          />
          <Button 
            type="submit"
            disabled={isSearching || !query.trim()}
            size="icon" 
            className="absolute right-2 top-2 h-10 w-10 rounded-full bg-primary-600 hover:bg-primary-700 shadow-sm transition-transform hover:scale-105 active:scale-95 disabled:opacity-50"
          >
            {isSearching ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
          </Button>
        </form>
        <div className="text-center mt-3 pointer-events-auto">
          <span className="text-[10px] text-slate-400 flex items-center justify-center gap-1.5 drop-shadow-sm">
            <Database className="w-3 h-3" /> Phase 5: Semantic Retrieval only. AI answer generation will be added in Phase 6.
          </span>
        </div>
      </div>
    </PageTransition>
  )
}
