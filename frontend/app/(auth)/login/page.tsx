"use client"
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { BrainCircuit } from 'lucide-react'
import Link from 'next/link'
import { useState } from 'react'
import { createClient } from '@/utils/supabase/client'
import { useRouter } from 'next/navigation'
import { PageTransition } from '@/components/shared/page-transition'

export default function LoginPage() {
  const router = useRouter()
  const supabase = createClient()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    // Clear any active demo cookies before logging in
    document.cookie = 'demo_role=; path=/; max-age=0'
    document.cookie = 'khub_role=; path=/; max-age=0'

    const { data, error: signInError } = await supabase.auth.signInWithPassword({
      email,
      password,
    })

    if (signInError) {
      setError("Invalid email or password.")
      setLoading(false)
      return
    }

    if (data.session) {
      try {
        const res = await fetch('/api/v1/auth/me', {
          headers: {
            'Authorization': `Bearer ${data.session.access_token}`
          }
        })
        
        if (res.ok) {
          // Check content type before parsing JSON to prevent SyntaxError
          const contentType = res.headers.get("content-type");
          if (!contentType || !contentType.includes("application/json")) {
            setError("Unexpected response from server. Please try again.");
            setLoading(false);
            return;
          }

          const userContext = await res.json()
          
          document.cookie = `khub_org_id=${userContext.organization_id}; path=/; max-age=86400; SameSite=Lax`
          document.cookie = `khub_role=${userContext.role}; path=/; max-age=86400; SameSite=Lax`
          
          // Completely removed automatic password change redirection.
          // Login strictly directs the user to their designated portal.
          if (userContext.role === 'ADMIN') {
            router.push('/admin/dashboard')
          } else if (userContext.role === 'EMPLOYEE') {
            router.push('/employee/chat')
          } else {
            setError('Unrecognized role assigned to account.')
            setLoading(false)
            await supabase.auth.signOut()
          }
        } else {
          const errText = await res.text();
          console.error(`Auth fetch failed: ${res.status} ${errText}`);
          if (res.status === 500) {
            setError(`Backend server error (500). Please ensure the FastAPI backend is running on port 8000.`);
          } else {
            setError(`Failed to retrieve account information: ${res.status} ${errText.substring(0, 50)}`)
          }
          setLoading(false)
        }
      } catch (err) {
        console.error(err)
        setError("An unexpected error occurred.")
        setLoading(false)
      }
    }
  }

  return (
    <PageTransition className="min-h-screen lg:h-[100dvh] flex flex-col lg:flex-row w-full bg-white">
      {/* Brand Side - Fixed height on desktop */}
      <div className="hidden lg:flex flex-col w-1/2 bg-navy-900 text-white p-12 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary-900 to-navy-900"></div>
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-10"></div>
        
        <div className="relative z-10">
          <Link href="/" className="flex items-center gap-2 font-bold text-2xl tracking-tight text-white">
            <BrainCircuit className="w-8 h-8 text-primary-400" /> KnowledgeHub AI
          </Link>
        </div>
        
        <div className="relative z-10 max-w-md mt-auto mb-auto lg:mb-20">
          <h2 className="text-4xl font-bold mb-6 leading-tight">Secure organizational intelligence.</h2>
          <p className="text-slate-300 text-lg leading-relaxed">Sign in to access your knowledge base and query institutional data securely.</p>
        </div>
      </div>

      {/* Form Side - Scrolls independently on desktop if needed */}
      <div className="flex-1 flex flex-col px-6 py-10 sm:p-12 bg-white relative lg:overflow-y-auto">
        <div className="flex-1 w-full max-w-md mx-auto flex flex-col justify-center">
          
          <div className="text-center lg:text-left mb-8">
            <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Welcome back</h1>
            <p className="text-slate-500 mt-2">Sign in to your account to continue.</p>
          </div>
          
          <form className="space-y-5" onSubmit={handleLogin}>
            {error && (
              <div className="p-3 text-sm text-red-700 bg-red-50 border border-red-200 rounded-md leading-relaxed">
                {error}
              </div>
            )}
            
            <div className="space-y-1.5">
              <label className="text-sm font-medium text-slate-700">Work Email</label>
              <Input 
                type="email" 
                placeholder="name@company.com" 
                required 
                value={email}
                onChange={e => setEmail(e.target.value)}
                className="bg-slate-50 h-11" 
              />
            </div>
            
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium text-slate-700">Password</label>
                <button type="button" onClick={() => setError('Forgot password is not available yet.')} className="text-xs font-semibold text-primary-600 hover:text-primary-700 bg-transparent border-none p-0 cursor-pointer">Forgot password?</button>
              </div>
              <Input 
                type="password" 
                placeholder="•••••••••" 
                required 
                value={password}
                onChange={e => setPassword(e.target.value)}
                className="bg-slate-50 h-11" 
              />
            </div>
            
            <Button type="submit" className="w-full h-11 text-base mt-4 shadow-sm" disabled={loading}>
              {loading ? 'Signing in...' : 'Sign In'}
            </Button>
          </form>
          
          <div className="text-center text-sm text-slate-500 mt-8 pt-6 border-t border-slate-100">
            Don't have a workspace yet? <Link href="/register" className="font-semibold text-primary-600 hover:text-primary-700">Create workspace</Link>
          </div>
          
        </div>
      </div>
    </PageTransition>
  )
}
