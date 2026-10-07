"use client"
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { BrainCircuit, CheckCircle } from 'lucide-react'
import Link from 'next/link'
import { useState } from 'react'
import { createClient } from '@/utils/supabase/client'
import { useRouter } from 'next/navigation'
import { PageTransition } from '@/components/shared/page-transition'
import { Textarea } from '@/components/ui/textarea'

export default function RegisterPage() {
  const router = useRouter()
  const supabase = createClient()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Step State
  const [step, setStep] = useState<1 | 2>(1)

  // Step 1: Admin
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')

  // Step 2: Org
  const [orgName, setOrgName] = useState('')
  const [website, setWebsite] = useState('')
  const [industry, setIndustry] = useState('')
  const [description, setDescription] = useState('')

  const handleStep1 = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    if (password !== confirmPassword) {
      setError("Passwords do not match.")
      setLoading(false)
      return
    }

    const { data, error: signUpError } = await supabase.auth.signUp({
      email,
      password,
      options: { data: { full_name: fullName } }
    })

    if (signUpError) {
      if (signUpError.message.includes('rate limit')) {
        setError("Signup email limit reached. Please wait a while before trying again.")
      } else {
        setError(signUpError.message)
      }
      setLoading(false)
      return
    }

    if (data.session) {
      setStep(2)
      setLoading(false)
    } else {
      setError("Registration successful! Please check your email to confirm your account before proceeding to workspace setup.")
      setLoading(false)
    }
  }

  const handleStep2 = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const { data: { session } } = await supabase.auth.getSession()
      if (!session) throw new Error("Authentication required")

      const res = await fetch('/api/v1/organizations/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`
        },
        body: JSON.stringify({
          name: orgName,
          website: website || null,
          industry: industry || null,
          description: description || null
        })
      })

      if (!res.ok) {
        const errData = await res.json()
        throw new Error(errData.detail || 'Failed to create workspace')
      }

      const org = await res.json()
      document.cookie = `khub_org_id=${org.id}; path=/; max-age=86400; SameSite=Lax`
      document.cookie = `khub_role=ADMIN; path=/; max-age=86400; SameSite=Lax`
      router.push('/admin/documents')
    } catch (err: any) {
      setError(err.message)
      setLoading(false)
    }
  }

  return (
    <PageTransition className="min-h-screen lg:h-[100dvh] flex flex-col lg:flex-row w-full bg-white">
      <div className="hidden lg:flex flex-col w-1/2 bg-navy-900 text-white p-12 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary-900 to-navy-900"></div>
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-10"></div>

        <div className="relative z-10">
          <Link href="/" className="flex items-center gap-2 font-bold text-2xl tracking-tight text-white">
            <BrainCircuit className="w-8 h-8 text-primary-400" /> KnowledgeHub AI
          </Link>
        </div>

        <div className="relative z-10 max-w-md mt-auto mb-auto lg:mb-20">
          <h2 className="text-4xl font-bold mb-6 leading-tight">Create your secure workspace.</h2>
          <p className="text-slate-300 text-lg leading-relaxed">Join thousands of teams who organize, secure, and query their institutional knowledge with AI.</p>
        </div>
      </div>

      <div className="flex-1 flex flex-col px-6 py-10 sm:p-12 bg-white relative lg:overflow-y-auto">
        <div className="absolute top-4 right-4 sm:top-6 sm:right-6 z-10">
          <Link href="/">
            <Button variant="ghost" className="text-slate-500 hover:text-slate-900">
              Back to Home
            </Button>
          </Link>
        </div>

        <div className="flex-1 w-full max-w-md mx-auto flex flex-col justify-center">

          <div className="w-full mb-10 flex items-center justify-between relative mt-4">
            <div className={`absolute left-0 right-0 top-1/2 h-0.5 -z-10 -translate-y-1/2 ${step === 2 ? 'bg-primary-200' : 'bg-slate-100'}`}></div>

            <div className="flex flex-col items-center gap-2 bg-white px-2">
              {step === 2 ? (
                <div className="w-8 h-8 rounded-full bg-primary-100 text-primary-700 flex items-center justify-center font-bold text-sm ring-4 ring-white shadow-sm"><CheckCircle className="w-5 h-5"/></div>
              ) : (
                <div className="w-8 h-8 rounded-full bg-primary-600 text-white flex items-center justify-center font-bold text-sm shadow-sm ring-4 ring-white">1</div>
              )}
              <span className={`text-xs font-semibold uppercase tracking-wider ${step === 2 ? 'text-primary-700' : 'text-primary-700'}`}>Account</span>
            </div>

            <div className="flex flex-col items-center gap-2 bg-white px-2">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ring-4 ring-white ${step === 2 ? 'bg-primary-600 text-white shadow-sm' : 'bg-slate-100 text-slate-400 border border-slate-200'}`}>2</div>
              <span className={`text-xs uppercase tracking-wider ${step === 2 ? 'font-bold text-primary-700' : 'font-medium text-slate-400'}`}>Workspace</span>
            </div>
          </div>

          <div className="text-center lg:text-left mb-8">
            <h1 className="text-3xl font-bold text-slate-900 tracking-tight">{step === 1 ? 'Create Account' : 'Create Workspace'}</h1>
            <p className="text-slate-500 mt-2">{step === 1 ? 'Step 1: Setup your personal administrator account.' : 'Step 2: You will become the administrator of this workspace.'}</p>
          </div>

          {step === 1 ? (
            <form className="space-y-5" onSubmit={handleStep1}>
              {error && (
                <div className="p-3 text-sm text-red-700 bg-red-50 border border-red-200 rounded-md leading-relaxed">
                  {error}
                </div>
              )}

              <div className="space-y-1.5">
                <label className="text-sm font-medium text-slate-700">Full Name</label>
                <Input type="text" placeholder="John Doe" required value={fullName} onChange={e => setFullName(e.target.value)} className="bg-slate-50 h-11" />
              </div>
              <div className="space-y-1.5">
                <label className="text-sm font-medium text-slate-700">Work Email</label>
                <Input type="email" placeholder="name@company.com" required value={email} onChange={e => setEmail(e.target.value)} className="bg-slate-50 h-11" />
              </div>
              <div className="space-y-1.5">
                <label className="text-sm font-medium text-slate-700">Password</label>
                <Input type="password" placeholder="••••••••" required value={password} onChange={e => setPassword(e.target.value)} className="bg-slate-50 h-11" />
              </div>
              <div className="space-y-1.5">
                <label className="text-sm font-medium text-slate-700">Confirm Password</label>
                <Input type="password" placeholder="••••••••" required value={confirmPassword} onChange={e => setConfirmPassword(e.target.value)} className="bg-slate-50 h-11" />
              </div>

              <Button type="submit" className="w-full h-11 text-base mt-4 shadow-sm" disabled={loading}>
                {loading ? 'Creating Account...' : 'Continue to Workspace Setup'}
              </Button>
            </form>
          ) : (
            <form className="space-y-5" onSubmit={handleStep2}>
              {error && (
                <div className="p-3 text-sm text-red-700 bg-red-50 border border-red-200 rounded-md leading-relaxed">
                  {error}
                </div>
              )}

              <div className="space-y-1.5">
                <label className="text-sm font-medium text-slate-700">Organization / Company Name <span className="text-red-500">*</span></label>
                <Input type="text" placeholder="Acme Corp" required value={orgName} onChange={e => setOrgName(e.target.value)} className="bg-slate-50 h-11" />
              </div>

              <div className="space-y-1.5">
                <label className="text-sm font-medium text-slate-700">Website <span className="text-slate-400 font-normal">(Optional)</span></label>
                <Input type="url" placeholder="https://acme.com" value={website} onChange={e => setWebsite(e.target.value)} className="bg-slate-50 h-11" />
              </div>

              <div className="space-y-1.5">
                <label className="text-sm font-medium text-slate-700">Industry <span className="text-slate-400 font-normal">(Optional)</span></label>
                <Input type="text" placeholder="e.g. Financial Services" value={industry} onChange={e => setIndustry(e.target.value)} className="bg-slate-50 h-11" />
              </div>

              <div className="space-y-1.5">
                <label className="text-sm font-medium text-slate-700">Organization Description <span className="text-slate-400 font-normal">(Optional)</span></label>
                <Textarea
                  placeholder="Briefly describe your organization..."
                  value={description}
                  onChange={e => setDescription(e.target.value)}
                  className="bg-slate-50 resize-none h-20"
                />
              </div>

              <Button type="submit" className="w-full h-11 text-base mt-4 shadow-sm" disabled={loading}>
                {loading ? 'Creating Workspace...' : 'Create Workspace'}
              </Button>
            </form>
          )}

          <div className="text-center text-sm text-slate-500 mt-8 pt-6 border-t border-slate-100">
            Already have an account? <Link href="/login" className="font-semibold text-primary-600 hover:text-primary-700">Sign in here</Link>
          </div>

        </div>
      </div>
    </PageTransition>
  )
}
