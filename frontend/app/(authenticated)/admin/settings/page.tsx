"use client"
import { AdminTopbar } from '@/components/navigation/admin-topbar'
import { PageTransition } from '@/components/shared/page-transition'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Building2, Globe, Shield, CreditCard, Bell } from 'lucide-react'
import { useState } from 'react'

export default function AdminSettings() {
  const [activeTab, setActiveTab] = useState('org')
  
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
                    <Input defaultValue="Acme Corporation" className="max-w-md" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-700">Workspace URL</label>
                    <div className="flex items-center gap-2 max-w-md">
                      <Input defaultValue="acme" className="flex-1" />
                      <span className="text-slate-500 text-sm">.knowledgehub.ai</span>
                    </div>
                  </div>
                  <div className="pt-4 border-t border-slate-100">
                    <Button>Save Changes</Button>
                  </div>
                </CardContent>
              </Card>
            )}
            
            {activeTab !== 'org' && (
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
