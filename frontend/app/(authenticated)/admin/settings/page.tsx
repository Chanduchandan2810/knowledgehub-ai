"use client"
import { AdminTopbar } from '@/components/navigation/admin-topbar'
import { PageTransition } from '@/components/shared/page-transition'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Building2, Globe, Shield, CreditCard, Bell, KeyRound } from 'lucide-react'
import { useState, useEffect } from 'react'
import { createClient } from '@/utils/supabase/client'
import Link from 'next/link'

export default function AdminSettings() {
  const [activeTab, setActiveTab] = useState('org')
  const [org, setOrg] = useState<Record<string, string> | null>(null)
  const [currentUserEmail, setCurrentUserEmail] = useState('')
  const supabase = createClient()

  useEffect(() => {
    async function loadOrg() {
      const { data: { session } } = await supabase.auth.getSession()
      if (!session) return
      if (session.user?.email) setCurrentUserEmail(session.user.email)

      // Read org ID from cookie
      const match = document.cookie.match(new RegExp('(^| )khub_org_id=([^;]+)'))
      const orgId = match ? match[2] : null

      if (!orgId) return

      try {
        const res = await fetch('/api/v1/organizations/current', {
          headers: {
            'Authorization': `Bearer ${session.access_token}`,
            'x-organization-id': orgId
          }
        })
        if (res.ok) {
          const contentType = res.headers.get("content-type");
          if (!contentType || !contentType.includes("application/json")) {
             throw new Error("Invalid content type from server.");
          }
          const orgData = await res.json()
          setOrg(orgData)
        }
      } catch (err) {
        console.error("Failed to load org", err)
      }
    }
    loadOrg()
  }, [supabase])
  
  return (
    <div className="flex flex-col h-full bg-slate-50/50">
      <AdminTopbar title="Settings" description="Configure organization-wide preferences." />
      <PageTransition className="flex-1 overflow-y-auto p-6 md:p-8">
        <div className="max-w-[1200px] mx-auto flex flex-col md:flex-row gap-8">
          
          <aside className="w-full md:w-64 flex-shrink-0">
            <nav className="space-y-1">
              {[
                { id: 'org', label: 'Organization Profile', icon: Building2 },
                { id: 'security', label: 'Security & Access', icon: Shield },
                { id: 'domain', label: 'Domain & SSO', icon: Globe },
                { id: 'billing', label: 'Billing & Plan', icon: CreditCard },
                { id: 'notifications', label: 'Notifications', icon: Bell },
              ].map(tab => (
                <button 
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg transition-colors ${activeTab === tab.id ? 'bg-white shadow-sm border border-slate-200 text-primary-700' : 'text-slate-600 hover:bg-slate-100 border border-transparent'}`}
                >
                  <tab.icon className={`w-4 h-4 ${activeTab === tab.id ? 'text-primary-600' : 'text-slate-400'}`} />
                  {tab.label}
                </button>
              ))}
            </nav>
          </aside>

          <main className="flex-1">
            {activeTab === 'org' && (
              <Card className="shadow-sm border-slate-200">
                <div className="p-6 border-b border-slate-100">
                  <h2 className="text-lg font-semibold text-slate-900">Organization Profile</h2>
                  <p className="text-sm text-slate-500">Manage your company details and brand identity.</p>
                </div>
                <CardContent className="p-6 space-y-6">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-700">Organization Name</label>
                    <Input value={(org?.name as string) || ''} readOnly className="max-w-md bg-slate-50" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-700">Organization ID (UUID)</label>
                    <Input value={(org?.id as string) || ''} readOnly className="max-w-md bg-slate-50 font-mono text-xs" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-700">Created At</label>
                    <Input value={org?.created_at ? new Date(org.created_at as string).toLocaleDateString() : ''} readOnly className="max-w-md bg-slate-50" />
                  </div>
                  <div className="pt-4 border-t border-slate-100">
                    <Button disabled>Save Changes</Button>
                    <p className="text-xs text-slate-400 mt-2">Editing organization details is restricted in this environment.</p>
                  </div>
                </CardContent>
              </Card>
            )}

            {activeTab === 'security' && (
              <Card className="shadow-sm border-slate-200">
                <div className="p-6 border-b border-slate-100">
                  <h2 className="text-lg font-semibold text-slate-900">Security & Access</h2>
                  <p className="text-sm text-slate-500">Manage your personal security credentials.</p>
                </div>
                <CardContent className="p-6">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 border border-slate-200 rounded-lg bg-slate-50">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-white border border-slate-200 rounded-full flex items-center justify-center text-slate-600">
                        <KeyRound className="w-5 h-5" />
                      </div>
                      <div>
                        <h3 className="text-sm font-semibold text-slate-900">Password</h3>
                        <p className="text-xs text-slate-500">Change your administrative account password.</p>
                      </div>
                    </div>
                    {currentUserEmail !== 'admin@demo.knowledgehub.local' ? (
                      <Link href="/admin/change-password">
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
                </CardContent>
              </Card>
            )}
            
            {activeTab !== 'org' && activeTab !== 'security' && (
              <Card className="shadow-sm border-slate-200">
                <div className="p-12 text-center text-slate-500">
                  Settings panel for {activeTab} will be available in future releases.
                </div>
              </Card>
            )}
          </main>
          
        </div>
      </PageTransition>
    </div>
  )
}
