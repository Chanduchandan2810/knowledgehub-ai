"use client"
import { BrainCircuit, Send, Database, ShieldCheck, HelpCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { PageTransition } from '@/components/shared/page-transition'
import { motion } from 'framer-motion'
import { useState } from 'react'

export default function EmployeeChat() {
  const [query, setQuery] = useState('')

  return (
    <PageTransition className="flex flex-col h-full bg-slate-50 relative overflow-hidden">
      
      {/* Chat Header */}
      <header className="h-14 flex-shrink-0 bg-white/80 backdrop-blur-md border-b border-slate-200/60 flex items-center justify-between px-6 z-10">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-slate-900 text-sm">New Conversation</span>
        </div>
        <div className="flex items-center gap-3">
          <span className="hidden sm:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 text-xs font-medium border border-emerald-100">
            <ShieldCheck className="w-3.5 h-3.5" /> Secured Workspace
          </span>
          <Button variant="ghost" size="icon" className="h-8 w-8 text-slate-400 hover:text-slate-600"><HelpCircle className="w-4 h-4" /></Button>
        </div>
      </header>

      {/* Main Chat Area */}
      <div className="flex-1 overflow-y-auto p-4 md:p-8 flex flex-col items-center justify-center relative">
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
            I can search through your organization's authorized policies, manuals, and documents to give you precise, grounded answers.
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
      
      {/* Input Area */}
      <div className="p-4 sm:p-6 bg-gradient-to-t from-white via-white to-transparent pt-10 z-20">
        <div className="max-w-3xl mx-auto relative group">
          <Input 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full h-14 pl-6 pr-14 text-sm rounded-full shadow-lg border-slate-200 focus-visible:ring-primary-500 bg-white transition-all" 
            placeholder="Ask about company policies, documents, or knowledge..."
          />
          <Button size="icon" className="absolute right-2 top-2 h-10 w-10 rounded-full bg-primary-600 hover:bg-primary-700 shadow-sm transition-transform hover:scale-105 active:scale-95 disabled:opacity-50">
            <Send className="h-4 w-4" />
          </Button>
        </div>
        <div className="text-center mt-3">
          <span className="text-[10px] text-slate-400 flex items-center justify-center gap-1.5">
            <Database className="w-3 h-3" /> AI responses are generated from internal documents but should be verified for critical decisions.
          </span>
        </div>
      </div>
    </PageTransition>
  )
}
