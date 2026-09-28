"use client"
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useState } from 'react'
import { createClient } from '@/utils/supabase/client'
import { useRouter } from 'next/navigation'
import { PageTransition } from '@/components/shared/page-transition'
import { KeyRound } from 'lucide-react'

export default function ChangePasswordPage() {
  const router = useRouter()
  const supabase = createClient()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    if (password !== confirmPassword) {
      setError("Passwords do not match.")
      setLoading(false)
      return
    }

    if (password.length < 6) {
      setError("Password must be at least 6 characters.")
      setLoading(false)
      return
    }

    const { data: { session } } = await supabase.auth.getSession()
    if (!session) return

    // Update password in Supabase Auth
    const { error: updateError } = await supabase.auth.updateUser({
      password: password
    })

    if (updateError) {
      setError(updateError.message)
      setLoading(false)
      return
    }

    // Success
    setLoading(false)
    router.push('/employee/settings')
  }

  return (
    <PageTransition className="min-h-screen flex items-center justify-center bg-slate-50 p-6">
      <div className="max-w-md w-full bg-white p-8 rounded-xl border border-slate-200 shadow-sm">
        <div className="flex flex-col items-center mb-8 text-center">
          <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center mb-4 text-primary-600">
            <KeyRound className="w-6 h-6" />
          </div>
          <h1 className="text-2xl font-bold text-slate-900">Change Password</h1>
          <p className="text-sm text-slate-500 mt-2">
            Enter a new secure password for your account.
          </p>
        </div>

        <form className="space-y-5" onSubmit={handleChangePassword}>
          {error && (
            <div className="p-3 text-sm text-red-700 bg-red-50 border border-red-200 rounded-md">
              {error}
            </div>
          )}
          
          <div className="space-y-1.5">
            <label className="text-sm font-medium text-slate-700">New Password</label>
            <Input 
              type="password" 
              required 
              value={password}
              onChange={e => setPassword(e.target.value)}
            />
          </div>
          
          <div className="space-y-1.5">
            <label className="text-sm font-medium text-slate-700">Confirm New Password</label>
            <Input 
              type="password" 
              required 
              value={confirmPassword}
              onChange={e => setConfirmPassword(e.target.value)}
            />
          </div>
          
          <Button type="submit" className="w-full mt-4" disabled={loading}>
            {loading ? 'Updating...' : 'Set New Password'}
          </Button>
        </form>
      </div>
    </PageTransition>
  )
}
