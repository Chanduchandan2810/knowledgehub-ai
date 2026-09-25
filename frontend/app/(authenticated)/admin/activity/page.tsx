"use client"
import { AdminTopbar } from '@/components/navigation/admin-topbar'
import { PageTransition } from '@/components/shared/page-transition'
import { Card, CardContent } from '@/components/ui/card'
import { Activity, UserPlus, Database, Settings } from 'lucide-react'

export default function AdminActivity() {
  return (
    <div className="flex flex-col h-full bg-slate-50/50">
      <AdminTopbar title="Activity Log" description="Audit trail of organizational events." />
      <PageTransition className="flex-1 overflow-y-auto p-6 md:p-8">
        <div className="max-w-[1200px] mx-auto">
          <Card className="shadow-sm overflow-hidden">
            <div className="p-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
              <h2 className="text-sm font-semibold text-slate-900">System Audit Trail</h2>
              <span className="text-xs text-slate-500">Last 7 days</span>
            </div>
            <CardContent className="p-0">
              <div className="divide-y divide-slate-100">
                <div className="p-5 flex items-start gap-4 bg-white hover:bg-slate-50 transition-colors">
                  <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center mt-0.5">
                    <Database className="w-4 h-4 text-blue-600" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm text-slate-900 font-medium">Workspace Initialized</p>
                    <p className="text-xs text-slate-500 mt-1">System configured the initial organizational boundaries.</p>
                  </div>
                  <span className="text-xs text-slate-400">Just now</span>
                </div>
                
                <div className="p-5 flex items-start gap-4 bg-white hover:bg-slate-50 transition-colors">
                  <div className="w-8 h-8 rounded-full bg-emerald-100 flex items-center justify-center mt-0.5">
                    <UserPlus className="w-4 h-4 text-emerald-600" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm text-slate-900 font-medium">Owner Account Created</p>
                    <p className="text-xs text-slate-500 mt-1">Admin user provisioned with full workspace access.</p>
                  </div>
                  <span className="text-xs text-slate-400">Just now</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </PageTransition>
    </div>
  )
}
