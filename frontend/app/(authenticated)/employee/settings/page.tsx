"use client"
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { ShieldCheck, Building2, User, Mail, CheckCircle, KeyRound } from 'lucide-react'
import { PageTransition } from '@/components/shared/page-transition'
import { LogoutButton } from '@/components/shared/logout-button'
import { useEffect, useState } from 'react'
import { createClient } from '@/utils/supabase/client'
import Link from 'next/link'

export default function EmployeeProfile() {
  const [user, setUser] = useState<Record<string, string> | null>(null)
  const [userContext, setUserContext] = useState<Record<string, string> | null>(null)
  const supabase = createClient()

  useEffect(() => {
    async function loadProfile() {
      const { data: { session } } = await supabase.auth.getSession()
      if (!session) return

      setUser(session.user as unknown as Record<string, string>)

      // Fetch user context from backend
      try {
        const res = await fetch('/api/v1/auth/me', {
          headers: {
            'Authorization': `Bearer ${session.access_token}`
          }
        })
        if (res.ok) {
          const contentType = res.headers.get("content-type");
          if (!contentType || !contentType.includes("application/json")) {
             throw new Error("Invalid content type from server.");
          }
          const ctx = await res.json()
          setUserContext(ctx)
        }
      } catch (err) {
        console.error("Failed to load user context", err)
      }
    }
    loadProfile()
  }, [supabase])

  interface UserProfile { full_name?: string; user_metadata?: { full_name?: string; }; email?: string; }
  const fullName = (userContext as unknown as UserProfile)?.full_name || (user as unknown as UserProfile)?.user_metadata?.full_name || 'Employee'
  const initials = fullName.split(' ').map((n: string) => n[0]).join('').substring(0, 2).toUpperCase()

  return (
    <div className="flex flex-col h-full bg-slate-50/50">
      <header className="h-14 flex-shrink-0 bg-white/80 backdrop-blur-md border-b border-slate-200/60 flex items-center justify-between px-6 z-10">
        <h1 className="font-semibold text-slate-900 text-sm">Account Settings</h1>
      </header>

      <PageTransition className="flex-1 overflow-y-auto p-6 md:p-8">
        <div className="max-w-3xl mx-auto space-y-6">
          
          <Card className="overflow-hidden border-slate-200 shadow-sm">
            <div className="bg-gradient-to-r from-navy-900 to-primary-900 p-8 flex flex-col sm:flex-row items-center sm:items-start gap-6">
              <div className="w-24 h-24 bg-white rounded-full flex items-center justify-center text-3xl font-bold text-primary-700 shadow-lg border-4 border-white/20">
                {initials}
              </div>
              <div className="text-center sm:text-left mt-2">
                <h2 className="text-2xl font-bold text-white mb-1">{fullName}</h2>
                <p className="text-primary-100 flex items-center justify-center sm:justify-start gap-2 text-sm font-medium">
                  <Building2 className="w-4 h-4"/> Authorized Employee
                </p>
                <div className="mt-4 inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/10 text-white text-xs font-medium border border-white/20">
                  <CheckCircle className="w-3.5 h-3.5" /> Verified Identity
                </div>
              </div>
            </div>
            
            <CardContent className="p-0">
              <div className="divide-y divide-slate-100">
                <div className="px-8 py-6 flex flex-col sm:flex-row sm:items-center gap-4 sm:gap-8">
                  <div className="w-32 text-sm font-medium text-slate-500 flex items-center gap-2"><User className="w-4 h-4" /> Full Name</div>
                  <div className="text-base font-semibold text-slate-900 flex-1">{fullName}</div>
                </div>
                
                <div className="px-8 py-6 flex flex-col sm:flex-row sm:items-center gap-4 sm:gap-8">
                  <div className="w-32 text-sm font-medium text-slate-500 flex items-center gap-2"><Mail className="w-4 h-4" /> Account Email</div>
                  <div className="text-base font-semibold text-slate-900 flex-1">{user?.email as string}</div>
                </div>
                
                <div className="px-8 py-6 flex flex-col sm:flex-row sm:items-start gap-4 sm:gap-8">
                  <div className="w-32 text-sm font-medium text-slate-500 flex items-center gap-2 mt-0.5"><ShieldCheck className="w-4 h-4" /> Access Level</div>
                  <div className="flex-1">
                    <span className="inline-flex items-center rounded-md bg-blue-50 px-2.5 py-1 text-xs font-semibold text-blue-700 border border-blue-200 mb-2">
                      {userContext ? userContext.role : 'LOADING...'}
                    </span>
                    <p className="text-xs text-slate-500 leading-relaxed max-w-md">
                      You are authenticated. Your access level determines which organizational documents the AI can retrieve for you.
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-slate-200 shadow-sm overflow-hidden">
            <div className="px-8 py-5 border-b border-slate-100 bg-slate-50/50">
              <h2 className="text-sm font-semibold text-slate-900">Security Actions</h2>
            </div>
            <CardContent className="p-8 space-y-6">
              
              <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pb-6 border-b border-slate-100">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-slate-50 border border-slate-200 rounded-full flex items-center justify-center text-slate-600">
                    <KeyRound className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-sm font-medium text-slate-900">Password</h3>
                    <p className="text-xs text-slate-500 mt-1">Change your account password.</p>
                  </div>
                </div>
                <div className="w-full sm:w-auto">
                  {user?.email !== 'employee@demo.knowledgehub.local' ? (
                    <Link href="/employee/change-password">
                      <Button variant="outline" className="w-full sm:w-auto text-sm font-medium">
                        Change Password
                      </Button>
                    </Link>
                  ) : (
                    <Button variant="outline" disabled className="w-full sm:w-auto text-sm font-medium">
                      Disabled in Demo
                    </Button>
                  )}
                </div>
              </div>

              <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
                <div>
                  <h3 className="text-sm font-medium text-slate-900">Sign Out</h3>
                  <p className="text-xs text-slate-500 mt-1">Securely end your current session on this device.</p>
                </div>
                <div className="w-full sm:w-auto">
                  <LogoutButton variant="full" className="bg-red-50 text-red-600 hover:bg-red-100" />
                </div>
              </div>

            </CardContent>
          </Card>

        </div>
      </PageTransition>
    </div>
  )
}
