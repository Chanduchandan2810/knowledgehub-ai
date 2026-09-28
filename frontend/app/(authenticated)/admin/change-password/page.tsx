"use client"
import { AdminTopbar } from '@/components/navigation/admin-topbar'
import { PageTransition } from '@/components/shared/page-transition'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { KeyRound, ArrowLeft } from 'lucide-react'
import { useState } from 'react'
import { createClient } from '@/utils/supabase/client'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

export default function AdminChangePassword() {
  const router = useRouter()
  const supabase = createClient()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setSuccess(null)

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

    const { error: updateError } = await supabase.auth.updateUser({
      password: password
    })

    if (updateError) {
      setError(updateError.message)
      setLoading(false)
      return
    }

    setSuccess("Password updated successfully.")
    setLoading(false)
    router.push('/admin/settings')
  }

  return (
    <div className="flex flex-col h-full bg-slate-50/50">
      <AdminTopbar title="Security" description="Manage your account password." />
      <PageTransition className="flex-1 overflow-y-auto p-6 md:p-8">
        <div className="max-w-[800px] mx-auto">
          
          <Link href="/admin/settings" className="inline-flex items-center text-sm font-medium text-slate-500 hover:text-slate-900 mb-6 transition-colors">
            <ArrowLeft className="w-4 h-4 mr-2" /> Back to Settings
          </Link>

          <Card className="shadow-sm border-slate-200">
            <CardHeader className="border-b border-slate-100 bg-white">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-primary-50 rounded-full flex items-center justify-center text-primary-600">
                  <KeyRound className="w-5 h-5" />
                </div>
                <CardTitle className="text-xl text-slate-900">Change Password</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="p-6 md:p-8">
              <form className="max-w-md space-y-5" onSubmit={handleChangePassword}>
                {error && (
                  <div className="p-3 text-sm text-red-700 bg-red-50 border border-red-200 rounded-md">
                    {error}
                  </div>
                )}
                {success && (
                  <div className="p-3 text-sm text-green-700 bg-green-50 border border-green-200 rounded-md">
                    {success}
                  </div>
                )}
                
                <div className="space-y-1.5">
                  <label className="text-sm font-medium text-slate-700">New Password</label>
                  <Input 
                    type="password" 
                    required 
                    value={password}
                    onChange={e => setPassword(e.target.value)}
                    className="bg-slate-50 focus:bg-white"
                  />
                </div>
                
                <div className="space-y-1.5">
                  <label className="text-sm font-medium text-slate-700">Confirm New Password</label>
                  <Input 
                    type="password" 
                    required 
                    value={confirmPassword}
                    onChange={e => setConfirmPassword(e.target.value)}
                    className="bg-slate-50 focus:bg-white"
                  />
                </div>
                
                <Button type="submit" className="w-full sm:w-auto mt-4" disabled={loading}>
                  {loading ? 'Updating...' : 'Update Password'}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
      </PageTransition>
    </div>
  )
}
