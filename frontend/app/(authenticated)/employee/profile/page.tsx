"use client"

import { useEffect, useState } from 'react'
import { createClient } from '@/utils/supabase/client'
import { User, Building, Mail, ShieldCheck } from 'lucide-react'
import { PageTransition } from '@/components/shared/page-transition'
import { Button } from '@/components/ui/button'

export default function EmployeeProfile() {
  const [loading, setLoading] = useState(true)
  const [profile, setProfile] = useState<{
    full_name: string
    email: string
    role: string
    organization_name: string
  } | null>(null)
  
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function loadProfile() {
      try {
        const supabase = createClient()
        const { data: { session } } = await supabase.auth.getSession()
        
        if (!session) {
          setError("Not authenticated")
          setLoading(false)
          return
        }

        const match = document.cookie.match(/(^|;)\s*khub_org_id\s*=\s*([^;]+)/)
        const orgId = match ? match.pop() : ''

        const [userRes, orgRes] = await Promise.all([
          fetch('/api/v1/auth/me', {
            headers: { 'Authorization': `Bearer ${session.access_token}` }
          }),
          orgId ? fetch('/api/v1/organizations/current', {
            headers: { 
              'Authorization': `Bearer ${session.access_token}`,
              'X-Organization-Id': orgId
            }
          }) : Promise.resolve(null)
        ])

        if (!userRes.ok) {
          throw new Error("Failed to load user profile")
        }

        const userData = await userRes.json()
        let orgName = "Unknown Organization"
        
        if (orgRes && orgRes.ok) {
          const orgData = await orgRes.json()
          orgName = orgData.name || orgName
        }

        setProfile({
          full_name: userData.full_name || userData.email,
          email: userData.email,
          role: userData.role || 'EMPLOYEE',
          organization_name: orgName
        })
      } catch (err: any) {
        setError(err.message || "An unexpected error occurred.")
      } finally {
        setLoading(false)
      }
    }

    loadProfile()
  }, [])

  return (
    <PageTransition>
      <div className="flex flex-col h-full bg-slate-50/50">
        <header className="h-16 flex flex-shrink-0 items-center justify-between px-6 border-b border-slate-200 bg-white">
          <h1 className="text-lg font-semibold text-slate-900">My Profile</h1>
        </header>

        <div className="flex-1 overflow-auto p-6 md:p-8">
          <div className="max-w-3xl mx-auto space-y-8">
            <div>
              <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Account Information</h2>
              <p className="text-slate-500 mt-1">View your personal and organizational details.</p>
            </div>

            {loading ? (
              <div className="animate-pulse space-y-4">
                <div className="h-24 bg-slate-200 rounded-xl w-full"></div>
                <div className="h-24 bg-slate-200 rounded-xl w-full"></div>
              </div>
            ) : error ? (
              <div className="p-4 bg-red-50 text-red-700 rounded-lg border border-red-100">
                {error}
              </div>
            ) : profile ? (
              <div className="grid gap-6 md:grid-cols-2">
                <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
                  <div className="flex items-center gap-4 border-b border-slate-100 pb-4">
                    <div className="bg-primary-50 p-3 rounded-lg text-primary-600">
                      <User className="w-6 h-6" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-500 uppercase tracking-wider">Full Name</p>
                      <p className="text-lg font-semibold text-slate-900">{profile.full_name}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-4 pt-2">
                    <div className="bg-slate-50 p-3 rounded-lg text-slate-500">
                      <Mail className="w-6 h-6" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-500 uppercase tracking-wider">Email Address</p>
                      <p className="text-lg font-semibold text-slate-900">{profile.email}</p>
                    </div>
                  </div>
                </div>

                <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
                  <div className="flex items-center gap-4 border-b border-slate-100 pb-4">
                    <div className="bg-blue-50 p-3 rounded-lg text-blue-600">
                      <Building className="w-6 h-6" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-500 uppercase tracking-wider">Organization</p>
                      <p className="text-lg font-semibold text-slate-900">{profile.organization_name}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-4 pt-2">
                    <div className="bg-emerald-50 p-3 rounded-lg text-emerald-600">
                      <ShieldCheck className="w-6 h-6" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-500 uppercase tracking-wider">Role</p>
                      <p className="text-lg font-bold text-emerald-700 uppercase">{profile.role}</p>
                    </div>
                  </div>
                </div>
              </div>
            ) : null}
          </div>
        </div>
      </div>
    </PageTransition>
  )
}
