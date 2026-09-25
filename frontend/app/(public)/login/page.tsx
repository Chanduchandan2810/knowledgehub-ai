"use client"
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { BrainCircuit } from 'lucide-react'
import Link from 'next/link'
import { PageTransition } from '@/components/shared/page-transition'

export default function Login() {
  return (
    <PageTransition className="min-h-[calc(100vh-4rem)] flex">
      {/* Brand Side */}
      <div className="hidden lg:flex flex-col justify-between w-1/2 bg-navy-900 text-white p-12 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary-900 to-navy-900"></div>
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-10"></div>
        
        <div className="relative z-10">
          <Link href="/" className="flex items-center gap-2 font-bold text-2xl tracking-tight text-white mb-12">
            <BrainCircuit className="w-8 h-8 text-primary-400" /> KnowledgeHub AI
          </Link>
        </div>
        
        <div className="relative z-10 max-w-md">
          <h2 className="text-4xl font-bold mb-6 leading-tight">Secure organizational intelligence.</h2>
          <p className="text-slate-300 text-lg leading-relaxed">Access your company's proprietary knowledge base with strict RLS permissions and enterprise-grade security.</p>
        </div>
      </div>

      {/* Form Side */}
      <div className="flex-1 flex items-center justify-center p-8 bg-white">
        <div className="w-full max-w-sm space-y-8">
          <div className="text-center lg:text-left">
            <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Welcome back</h1>
            <p className="text-slate-500 mt-2">Enter your credentials to access your workspace.</p>
          </div>
          
          <form className="space-y-5" onSubmit={(e) => e.preventDefault()}>
            <div className="space-y-1">
              <label className="text-sm font-medium text-slate-700">Work Email</label>
              <Input type="email" placeholder="name@company.com" required className="bg-slate-50" />
            </div>
            <div className="space-y-1">
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium text-slate-700">Password</label>
                <Link href="#" className="text-xs font-medium text-primary-600 hover:text-primary-700">Forgot password?</Link>
              </div>
              <Input type="password" placeholder="••••••••" required className="bg-slate-50" />
            </div>
            <Button type="button" className="w-full" size="lg">Sign In</Button>
          </form>
          
          <div className="text-center text-sm text-slate-500 mt-6">
            Don't have an account? <Link href="/register" className="font-semibold text-primary-600 hover:text-primary-700">Create workspace</Link>
          </div>
        </div>
      </div>
    </PageTransition>
  )
}
