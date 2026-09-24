import { AdminTopbar } from '@/components/navigation/admin-topbar'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Shield, FileText, Users, User, Plus } from 'lucide-react'
import { Button } from '@/components/ui/button'

export default function AdminPermissions() {
  return (
    <div className="bg-slate-50 min-h-full">
      <AdminTopbar title="Document Access & Permissions" />
      <main className="p-8 max-w-5xl mx-auto space-y-6">
        <p className="text-sm text-slate-600">Permissions are strictly enforced at the database level during vector retrieval.</p>
        
        <Card className="border-blue-100 shadow-sm">
          <CardHeader className="bg-blue-50/50 border-b border-blue-100 pb-4">
            <CardTitle className="flex items-center text-lg"><FileText className="mr-2 h-5 w-5 text-blue-600"/> Employee Handbook.pdf</CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            <h3 className="text-sm font-semibold text-slate-900 mb-4 uppercase tracking-wider">Access Control</h3>
            
            <div className="space-y-4">
              <label className="flex items-start gap-3 p-4 border rounded-lg cursor-pointer hover:bg-slate-50 transition-colors">
                <input type="checkbox" defaultChecked className="mt-1 h-4 w-4 text-blue-600 rounded border-slate-300" />
                <div>
                  <div className="flex items-center font-medium text-slate-900"><Users className="w-4 h-4 mr-2 text-slate-500"/> All Organization Members</div>
                  <p className="text-sm text-slate-500 mt-1">Anyone in the organization can search and retrieve this document.</p>
                </div>
              </label>

              <div className="border rounded-lg overflow-hidden">
                <div className="p-4 bg-slate-50 border-b flex justify-between items-center">
                  <div className="font-medium text-slate-900 text-sm">Restrict to Specific Roles</div>
                </div>
                <div className="p-4 space-y-3">
                  <label className="flex items-center gap-3 cursor-pointer">
                    <input type="checkbox" defaultChecked className="h-4 w-4 text-blue-600 rounded border-slate-300" />
                    <span className="text-sm font-medium text-slate-700">KNOWLEDGE_MANAGER</span>
                  </label>
                  <label className="flex items-center gap-3 cursor-pointer">
                    <input type="checkbox" defaultChecked className="h-4 w-4 text-blue-600 rounded border-slate-300" />
                    <span className="text-sm font-medium text-slate-700">MEMBER</span>
                  </label>
                </div>
              </div>

              <div className="border rounded-lg overflow-hidden">
                <div className="p-4 bg-slate-50 border-b flex justify-between items-center">
                  <div className="font-medium text-slate-900 text-sm">Specific Users</div>
                  <Button variant="outline" size="sm"><Plus className="w-4 h-4 mr-1"/> Add User</Button>
                </div>
                <div className="p-4 text-sm text-slate-500">
                  No individual users have been granted specific exceptions.
                </div>
              </div>

            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  )
}
