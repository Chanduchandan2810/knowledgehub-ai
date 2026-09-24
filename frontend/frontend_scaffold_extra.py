import os

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

create_file("app/(authenticated)/admin/permissions/page.tsx", """
import { AdminTopbar } from '@/components/navigation/admin-topbar'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Shield } from 'lucide-react'

export default function AdminPermissions() {
  return (
    <div>
      <AdminTopbar title="Permissions" />
      <main className="p-8">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center"><Shield className="mr-2 h-5 w-5 text-blue-600"/> Document Access Control</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-slate-500 mb-6">Manage default access rules for newly uploaded documents.</p>
            <div className="space-y-4 border rounded-md p-4">
              <div className="flex justify-between items-center pb-4 border-b">
                <div>
                  <h4 className="text-sm font-medium text-slate-900">Organization Wide</h4>
                  <p className="text-xs text-slate-500">All members can view</p>
                </div>
                <input type="checkbox" defaultChecked className="h-4 w-4 text-blue-600 rounded border-slate-300" />
              </div>
              <div className="flex justify-between items-center pb-4 border-b">
                <div>
                  <h4 className="text-sm font-medium text-slate-900">Role-Based Access</h4>
                  <p className="text-xs text-slate-500">Restrict to specific roles (e.g. KNOWLEDGE_MANAGER only)</p>
                </div>
                <input type="checkbox" className="h-4 w-4 text-blue-600 rounded border-slate-300" />
              </div>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  )
}
""")

create_file("app/(authenticated)/admin/analytics/page.tsx", """
import { AdminTopbar } from '@/components/navigation/admin-topbar'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { BarChart3 } from 'lucide-react'

export default function AdminAnalytics() {
  return (
    <div>
      <AdminTopbar title="Analytics" />
      <main className="p-8">
        <div className="grid gap-6 md:grid-cols-2">
          <Card>
            <CardHeader><CardTitle className="flex items-center"><BarChart3 className="mr-2 h-5 w-5 text-blue-600"/> Query Volume</CardTitle></CardHeader>
            <CardContent>
              <div className="h-64 flex items-center justify-center border border-dashed rounded bg-slate-50">
                <span className="text-slate-400 text-sm">Chart Placeholder (Queries over time)</span>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Top Documents</CardTitle></CardHeader>
            <CardContent>
              <div className="space-y-4">
                {['Employee Handbook', 'Q3 Report', 'Security Policy'].map((doc, i) => (
                  <div key={doc} className="flex justify-between items-center text-sm">
                    <span className="text-slate-900">{doc}</span>
                    <span className="text-slate-500">{100 - (i*20)} references</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}
""")

create_file("app/(authenticated)/admin/activity/page.tsx", """
import { AdminTopbar } from '@/components/navigation/admin-topbar'
import { Card, CardContent } from '@/components/ui/card'

export default function AdminActivity() {
  return (
    <div>
      <AdminTopbar title="Activity Log" />
      <main className="p-8">
        <Card>
          <CardContent className="p-0">
            <div className="divide-y text-sm">
              <div className="p-4"><span className="font-medium text-slate-900">Alice Admin</span> uploaded "Employee Handbook.pdf" <span className="text-slate-500 float-right">2 mins ago</span></div>
              <div className="p-4"><span className="font-medium text-slate-900">System</span> processed embeddings for "Q3 Report.pdf" <span className="text-slate-500 float-right">1 hour ago</span></div>
              <div className="p-4"><span className="font-medium text-slate-900">Bob Manager</span> joined the organization <span className="text-slate-500 float-right">Yesterday</span></div>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  )
}
""")

create_file("app/(authenticated)/admin/settings/page.tsx", """
import { AdminTopbar } from '@/components/navigation/admin-topbar'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

export default function AdminSettings() {
  return (
    <div>
      <AdminTopbar title="Settings" />
      <main className="p-8">
        <Card className="max-w-2xl">
          <CardHeader><CardTitle>Organization Settings</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Organization Name</label>
              <Input defaultValue="Acme Corp" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Domain Restriction</label>
              <Input placeholder="acme.com" />
            </div>
            <Button>Save Changes</Button>
          </CardContent>
        </Card>
      </main>
    </div>
  )
}
""")

create_file("app/(authenticated)/employee/conversations/page.tsx", """
import { MessageSquare } from 'lucide-react'
import { EmptyState } from '@/components/shared/empty-state'

export default function EmployeeConversations() {
  return (
    <div className="flex-1 p-8">
      <h1 className="text-2xl font-bold text-slate-900 mb-6">Conversation History</h1>
      <div className="max-w-3xl">
        <EmptyState 
          icon={MessageSquare} 
          title="Select a conversation" 
          description="Choose a conversation from the sidebar or start a new chat." 
        />
      </div>
    </div>
  )
}
""")

create_file("app/(authenticated)/employee/profile/page.tsx", """
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'

export default function EmployeeProfile() {
  return (
    <div className="flex-1 p-8">
      <h1 className="text-2xl font-bold text-slate-900 mb-6">Profile & Settings</h1>
      <Card className="max-w-2xl">
        <CardHeader><CardTitle>Personal Information</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Full Name</label>
            <Input defaultValue="Employee Name" disabled />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Email</label>
            <Input defaultValue="employee@company.com" disabled />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Role</label>
            <Input defaultValue="MEMBER" disabled />
          </div>
          <Button variant="outline">Sign Out</Button>
        </CardContent>
      </Card>
    </div>
  )
}
""")

print("Finished scaffolding all remaining pages.")
