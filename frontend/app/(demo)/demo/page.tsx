"use client"
import { BrainCircuit, ShieldCheck, Users } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { PageTransition } from '@/components/shared/page-transition'
import { motion } from 'framer-motion'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useState } from 'react'

import { createClient } from '@/utils/supabase/client'

export default function DemoPage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState<string | null>(null)

  const handleDemoLogin = async (role: 'ADMIN' | 'EMPLOYEE') => {
    console.log('handleDemoLogin called with role:', role)
    setIsLoading(role)
    try {
      console.log('Sending fetch request to /api/v1/auth/demo/start...')
      const res = await fetch('/api/v1/auth/demo/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ role })
      })
      console.log('Fetch response status:', res.status)
      if (!res.ok) throw new Error('Failed to start demo')
      const tokenData = await res.json()
      
      console.log('Setting Supabase session...')
      const supabase = createClient()
      const { error } = await supabase.auth.setSession({
        access_token: tokenData.access_token,
        refresh_token: tokenData.refresh_token
      })
      if (error) {
        console.error("Supabase auth error:", error)
        throw error
      }
      
      // Set the necessary cookies for middleware routing
      document.cookie = `khub_role=${role}; path=/; max-age=86400; SameSite=Lax`
      // For demo, we can just set a dummy org id if needed, or let the backend handle it.
      document.cookie = `khub_org_id=demo-org-id; path=/; max-age=86400; SameSite=Lax`
      
      console.log('Session set correctly, pushing router...')
      
      if (role === 'ADMIN') {
        router.push('/admin/dashboard')
      } else {
        router.push('/employee/chat')
      }
    } catch (err) {
      console.error("Error in handleDemoLogin:", err)
      setIsLoading(null)
    }
  }

  return (
    <PageTransition className="flex flex-col min-h-screen bg-slate-50 relative overflow-hidden">
      <header className="h-14 flex-shrink-0 bg-white/80 backdrop-blur-md border-b border-slate-200/60 flex items-center justify-between px-6 z-10">
        <div className="flex items-center gap-4 sm:gap-6">
          <div className="font-bold text-slate-900 text-sm flex items-center gap-2">
             <BrainCircuit className="w-5 h-5 text-primary-600" /> 
             <span className="hidden sm:inline-block">KnowledgeHub AI</span>
          </div>
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-blue-50 text-blue-700 text-[10px] sm:text-xs font-semibold uppercase tracking-wider border border-blue-200 shadow-sm">
            Interactive Demo Sandbox
          </span>
        </div>
        <div className="flex items-center gap-3">
          <Link href="/">
            <Button variant="ghost" size="sm" className="h-8 text-xs text-slate-600">
              Back to Website
            </Button>
          </Link>
        </div>
      </header>

      <div className="flex-1 overflow-y-auto p-4 md:p-8 flex flex-col items-center justify-center relative">
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-[0.02]">
          <BrainCircuit className="w-96 h-96" />
        </div>

        <motion.div 
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="max-w-3xl w-full text-center space-y-8 z-10"
        >
          <div className="space-y-4">
            <h1 className="text-3xl sm:text-4xl font-bold text-slate-900 tracking-tight">
              KnowledgeHub AI <br/> Interactive Demo
            </h1>
            <p className="text-slate-500 text-base max-w-xl mx-auto leading-relaxed">
              Choose how you want to explore the platform. Changes in this sandbox are isolated to a secure demo environment.
            </p>
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 max-w-2xl mx-auto pt-6">
            <motion.div 
              whileHover={{ y: -4 }}
              className="bg-white rounded-2xl p-8 border border-slate-200 shadow-sm text-left flex flex-col items-start gap-4 cursor-pointer hover:border-primary-300 hover:shadow-md transition-all"
              onClick={() => handleDemoLogin('ADMIN')}
            >
              <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center border border-blue-100">
                <ShieldCheck className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-slate-900 mb-2">Demo Admin</h3>
                <p className="text-sm text-slate-500 leading-relaxed">
                  Experience the full knowledge management suite. Upload documents, manage permissions, and query the AI.
                </p>
              </div>
              <Button 
                className="mt-auto w-full" 
                disabled={isLoading !== null}
              >
                {isLoading === 'ADMIN' ? 'Entering...' : 'Enter as Admin'}
              </Button>
            </motion.div>

            <motion.div 
              whileHover={{ y: -4 }}
              className="bg-white rounded-2xl p-8 border border-slate-200 shadow-sm text-left flex flex-col items-start gap-4 cursor-pointer hover:border-emerald-300 hover:shadow-md transition-all"
              onClick={() => handleDemoLogin('EMPLOYEE')}
            >
              <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center border border-emerald-100">
                <Users className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-slate-900 mb-2">Demo Employee</h3>
                <p className="text-sm text-slate-500 leading-relaxed">
                  Experience the end-user portal. Query the AI chat and see strict document access controls in action.
                </p>
              </div>
              <Button 
                variant="outline" 
                className="mt-auto w-full border-emerald-200 hover:bg-emerald-50 hover:text-emerald-700"
                disabled={isLoading !== null}
              >
                {isLoading === 'EMPLOYEE' ? 'Entering...' : 'Enter as Employee'}
              </Button>
            </motion.div>
          </div>
        </motion.div>
      </div>
    </PageTransition>
  )
}
