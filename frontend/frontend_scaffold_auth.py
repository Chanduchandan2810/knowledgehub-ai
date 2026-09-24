import os

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

# Admin Routes
create_file("app/(authenticated)/admin/layout.tsx", """
import { AdminSidebar } from '@/components/navigation/admin-sidebar'

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-slate-50">
      <AdminSidebar />
      <div className="ml-64 flex-1">
        {children}
      </div>
    </div>
  )
}
""")

create_file("app/(authenticated)/admin/dashboard/page.tsx", """
import { AdminTopbar } from '@/components/navigation/admin-topbar'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { FileText, Users, Search, BrainCircuit } from 'lucide-react'

export default function AdminDashboard() {
  return (
    <div>
      <AdminTopbar title="Organization Overview" />
      <main className="p-8">
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Documents</CardTitle>
              <FileText className="h-4 w-4 text-slate-500" />
            </CardHeader>
            <CardContent><div className="text-2xl font-bold">142</div></CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Members</CardTitle>
              <Users className="h-4 w-4 text-slate-500" />
            </CardHeader>
            <CardContent><div className="text-2xl font-bold">12</div></CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Knowledge Queries</CardTitle>
              <Search className="h-4 w-4 text-slate-500" />
            </CardHeader>
            <CardContent><div className="text-2xl font-bold">1,204</div></CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">AI Processing</CardTitle>
              <BrainCircuit className="h-4 w-4 text-slate-500" />
            </CardHeader>
            <CardContent><div className="text-2xl font-bold">99.8%</div></CardContent>
          </Card>
        </div>
        
        <div className="grid gap-6 md:grid-cols-2">
          <Card>
            <CardHeader><CardTitle>Recent Documents</CardTitle></CardHeader>
            <CardContent>
              <div className="space-y-4">
                {['Q3 Financial Report.pdf', 'Employee Handbook 2026.pdf', 'Engineering Onboarding.md'].map(doc => (
                  <div key={doc} className="flex items-center">
                    <FileText className="mr-2 h-4 w-4 text-slate-400" />
                    <span className="text-sm font-medium text-slate-900">{doc}</span>
                    <span className="ml-auto text-xs text-slate-500">Processed</span>
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

create_file("app/(authenticated)/admin/documents/page.tsx", """
import { AdminTopbar } from '@/components/navigation/admin-topbar'
import { EmptyState } from '@/components/shared/empty-state'
import { Button } from '@/components/ui/button'
import { FileUp, Search } from 'lucide-react'
import { Input } from '@/components/ui/input'

export default function AdminDocuments() {
  return (
    <div>
      <AdminTopbar title="Documents" />
      <main className="p-8">
        <div className="flex justify-between items-center mb-6">
          <div className="relative w-72">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-400" />
            <Input type="search" placeholder="Search documents..." className="pl-9 bg-white" />
          </div>
          <Button><FileUp className="mr-2 h-4 w-4" /> Upload Document</Button>
        </div>
        
        <div className="bg-white border rounded-lg overflow-hidden">
          {/* Table Header Placeholder */}
          <div className="grid grid-cols-5 bg-slate-50 p-4 border-b text-sm font-medium text-slate-500">
            <div className="col-span-2">Name</div>
            <div>Type</div>
            <div>Status</div>
            <div>Uploaded</div>
          </div>
          <div className="p-12">
            <EmptyState 
              icon={FileUp} 
              title="No documents yet" 
              description="Upload your organization's first document to build your knowledge base." 
              actionLabel="Upload Document" 
            />
          </div>
        </div>
      </main>
    </div>
  )
}
""")

create_file("app/(authenticated)/admin/members/page.tsx", """
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
""")

# Employee Routes
create_file("app/(authenticated)/employee/layout.tsx", """
import { EmployeeSidebar } from '@/components/navigation/employee-sidebar'

export default function EmployeeLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-white">
      <EmployeeSidebar />
      <div className="ml-72 flex-1 h-screen flex flex-col">
        {children}
      </div>
    </div>
  )
}
""")

create_file("app/(authenticated)/employee/chat/page.tsx", """
import { BrainCircuit, Send } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

export default function EmployeeChat() {
  return (
    <div className="flex-1 flex flex-col h-full relative">
      <div className="flex-1 overflow-y-auto p-8 flex flex-col items-center justify-center">
        <div className="max-w-2xl w-full text-center space-y-6">
          <div className="mx-auto w-16 h-16 bg-blue-100 text-blue-600 rounded-2xl flex items-center justify-center mb-6">
            <BrainCircuit className="w-8 h-8" />
          </div>
          <h1 className="text-2xl font-semibold text-slate-900">Ask anything about your organization's knowledge.</h1>
          <p className="text-slate-500">The AI assistant securely searches company documents to give you grounded answers.</p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-8 text-left">
            <div className="p-4 border rounded-xl hover:bg-slate-50 cursor-pointer transition-colors">
              <p className="text-sm font-medium text-slate-900">What is our annual leave policy?</p>
            </div>
            <div className="p-4 border rounded-xl hover:bg-slate-50 cursor-pointer transition-colors">
              <p className="text-sm font-medium text-slate-900">What is the reimbursement process?</p>
            </div>
            <div className="p-4 border rounded-xl hover:bg-slate-50 cursor-pointer transition-colors">
              <p className="text-sm font-medium text-slate-900">Where can I find the employee handbook?</p>
            </div>
            <div className="p-4 border rounded-xl hover:bg-slate-50 cursor-pointer transition-colors">
              <p className="text-sm font-medium text-slate-900">How do I request a new laptop?</p>
            </div>
          </div>
        </div>
      </div>
      
      <div className="p-6 bg-white border-t">
        <div className="max-w-3xl mx-auto relative">
          <Input 
            className="w-full h-14 pl-6 pr-14 text-base rounded-full shadow-sm border-slate-300" 
            placeholder="Ask a question..."
          />
          <Button size="sm" className="absolute right-2 top-2 h-10 w-10 rounded-full p-0">
            <Send className="h-4 w-4" />
          </Button>
        </div>
        <div className="text-center mt-3">
          <span className="text-xs text-slate-400">AI can make mistakes. Check important information.</span>
        </div>
      </div>
    </div>
  )
}
""")
