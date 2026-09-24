import { AdminTopbar } from '@/components/navigation/admin-topbar'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { UserPlus } from 'lucide-react'

export default function AdminMembers() {
  return (
    <div>
      <AdminTopbar title="Members" />
      <main className="p-8">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-lg font-medium text-slate-900">Organization Members</h2>
          <Button><UserPlus className="mr-2 h-4 w-4" /> Invite Member</Button>
        </div>
        
        <div className="bg-white border rounded-lg overflow-hidden">
          <div className="grid grid-cols-4 bg-slate-50 p-4 border-b text-sm font-medium text-slate-500">
            <div className="col-span-2">User</div>
            <div>Role</div>
            <div>Joined</div>
          </div>
          <div className="divide-y">
            <div className="grid grid-cols-4 p-4 items-center">
              <div className="col-span-2 flex flex-col">
                <span className="text-sm font-medium text-slate-900">Alice Admin</span>
                <span className="text-sm text-slate-500">alice@company.com</span>
              </div>
              <div><Badge variant="default">ADMIN</Badge></div>
              <div className="text-sm text-slate-500">Sep 24, 2026</div>
            </div>
            <div className="grid grid-cols-4 p-4 items-center">
              <div className="col-span-2 flex flex-col">
                <span className="text-sm font-medium text-slate-900">Bob Manager</span>
                <span className="text-sm text-slate-500">bob@company.com</span>
              </div>
              <div><Badge variant="secondary">KNOWLEDGE_MANAGER</Badge></div>
              <div className="text-sm text-slate-500">Sep 24, 2026</div>
            </div>
            <div className="grid grid-cols-4 p-4 items-center">
              <div className="col-span-2 flex flex-col">
                <span className="text-sm font-medium text-slate-900">Charlie Employee</span>
                <span className="text-sm text-slate-500">charlie@company.com</span>
              </div>
              <div><Badge variant="outline">MEMBER</Badge></div>
              <div className="text-sm text-slate-500">Sep 24, 2026</div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
