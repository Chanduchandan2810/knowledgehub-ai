"use client"
import { AdminTopbar } from '@/components/navigation/admin-topbar'
import { PageTransition } from '@/components/shared/page-transition'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Shield, Lock, FileText, CheckCircle2 } from 'lucide-react'
import { Button } from '@/components/ui/button'

export default function AdminPermissions() {
  return (
    <div className="flex flex-col h-full bg-slate-50/50">
      <AdminTopbar title="Permissions & Access" description="Control document-level visibility and AI retrieval rules." />
      <PageTransition className="flex-1 overflow-y-auto p-6 md:p-8">
        <div className="max-w-[1200px] mx-auto">
          
          <div className="mb-8 p-6 bg-indigo-50 border border-indigo-100 rounded-xl flex items-start gap-4">
            <div className="p-2 bg-indigo-100 text-indigo-700 rounded-lg"><Shield className="w-6 h-6" /></div>
            <div>
              <h2 className="text-lg font-bold text-indigo-900 mb-1">Enterprise Grade Security (RLS)</h2>
              <p className="text-sm text-indigo-700 leading-relaxed">
                KnowledgeHub uses PostgreSQL Row-Level Security. AI can only retrieve documents that a user has explicit permission to read. Modifying rules here directly updates the database security policies.
              </p>
            </div>
          </div>
          
          <div className="grid md:grid-cols-3 gap-6">
            <div className="md:col-span-1 space-y-6">
              <Card className="shadow-sm">
                <CardHeader className="bg-slate-50/50 border-b border-slate-100 py-4">
                  <CardTitle className="text-sm font-semibold">Access Hierarchy</CardTitle>
                </CardHeader>
                <CardContent className="p-4 space-y-3">
                  <div className="flex items-start gap-3 p-3 rounded-lg border border-slate-200 bg-white">
                    <Shield className="w-4 h-4 text-purple-600 mt-0.5" />
                    <div>
                      <h4 className="text-xs font-bold text-slate-900">ADMIN</h4>
                      <p className="text-[11px] text-slate-500">Full control over workspace and billing.</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3 p-3 rounded-lg border border-slate-200 bg-white">
                    <FileText className="w-4 h-4 text-emerald-600 mt-0.5" />
                    <div>
                      <h4 className="text-xs font-bold text-slate-900">EMPLOYEE</h4>
                      <p className="text-[11px] text-slate-500">Read and chat with authorized docs.</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
            
            <div className="md:col-span-2">
              <Card className="shadow-sm h-full">
                <CardHeader className="bg-slate-50/50 border-b border-slate-100 py-4 flex flex-row items-center justify-between">
                  <CardTitle className="text-sm font-semibold">Document Groups & Rules</CardTitle>
                  <Button variant="outline" size="sm" className="h-8 text-xs">New Rule</Button>
                </CardHeader>
                <CardContent className="flex flex-col items-center justify-center p-12 text-center h-[300px]">
                  <div className="w-12 h-12 bg-slate-50 rounded-full border border-slate-100 flex items-center justify-center mb-4">
                    <CheckCircle2 className="w-5 h-5 text-slate-400" />
                  </div>
                  <h3 className="text-sm font-semibold text-slate-900 mb-1">Global Organization Access</h3>
                  <p className="text-xs text-slate-500 max-w-sm mb-4">Currently, all processed documents inherit the &quot;Organization-Wide&quot; visibility policy.</p>
                </CardContent>
              </Card>
            </div>
          </div>

        </div>
      </PageTransition>
    </div>
  )
}
