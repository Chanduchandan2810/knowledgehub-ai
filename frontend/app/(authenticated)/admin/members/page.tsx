"use client"
import { AdminTopbar } from '@/components/navigation/admin-topbar'
import { EmptyState } from '@/components/shared/empty-state'
import { Button } from '@/components/ui/button'
import { UserPlus, Search, ShieldCheck, Users } from 'lucide-react'
import { PageTransition } from '@/components/shared/page-transition'
import { Input } from '@/components/ui/input'

export default function AdminMembers() {
  return (
    <div className="flex flex-col h-full bg-slate-50/50">
      <AdminTopbar title="Members" description="Manage user access and organizational roles." />
      <PageTransition className="flex-1 overflow-y-auto p-6 md:p-8">
        <div className="max-w-[1600px] mx-auto space-y-6">
          
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div className="relative w-full sm:max-w-md">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
              <Input placeholder="Search members by name or email..." className="pl-9 bg-white shadow-sm" />
            </div>
            <Button className="w-full sm:w-auto shadow-sm"><UserPlus className="mr-2 h-4 w-4" /> Invite Member</Button>
          </div>
          
          <div className="bg-white border border-slate-200/80 rounded-xl shadow-sm overflow-hidden">
            <div className="grid grid-cols-12 px-6 py-4 border-b border-slate-200 bg-slate-50/80 text-xs font-semibold text-slate-500 uppercase tracking-wider">
              <div className="col-span-6 md:col-span-5">User</div>
              <div className="col-span-3 md:col-span-3 hidden sm:block">Role</div>
              <div className="col-span-3 md:col-span-3 hidden md:block">Status</div>
              <div className="col-span-6 sm:col-span-3 md:col-span-1 text-right">Joined</div>
            </div>
            
            <div className="divide-y divide-slate-100">
              {/* Dummy row for layout composition */}
              <div className="grid grid-cols-12 px-6 py-4 items-center hover:bg-slate-50/50 transition-colors">
                <div className="col-span-6 md:col-span-5 flex items-center gap-3">
                  <div className="w-9 h-9 rounded-full bg-primary-100 text-primary-700 flex items-center justify-center font-bold text-xs border border-primary-200 shadow-sm">A</div>
                  <div>
                    <p className="text-sm font-semibold text-slate-900">Admin User</p>
                    <p className="text-xs text-slate-500">admin@company.com</p>
                  </div>
                </div>
                <div className="col-span-3 md:col-span-3 hidden sm:block">
                  <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-purple-50 text-purple-700 text-xs font-medium border border-purple-100">
                    <ShieldCheck className="w-3 h-3" /> ADMIN
                  </span>
                </div>
                <div className="col-span-3 md:col-span-3 hidden md:block">
                  <span className="inline-flex items-center px-2 py-1 rounded-full bg-emerald-50 text-emerald-700 text-[11px] font-semibold">Active</span>
                </div>
                <div className="col-span-6 sm:col-span-3 md:col-span-1 text-right text-sm text-slate-500">
                  Today
                </div>
              </div>
            </div>
            
            {/* Example of empty state if no other users */}
            <div className="p-12 border-t border-slate-100 bg-slate-50/30">
              <div className="max-w-sm mx-auto text-center">
                <div className="w-12 h-12 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4 border border-slate-200">
                  <Users className="w-5 h-5 text-slate-400" />
                </div>
                <h3 className="text-sm font-semibold text-slate-900 mb-1">No other members</h3>
                <p className="text-xs text-slate-500 mb-4">Invite colleagues to your organization to grant them access to the knowledge base.</p>
              </div>
            </div>
          </div>
          
        </div>
      </PageTransition>
    </div>
  )
}
