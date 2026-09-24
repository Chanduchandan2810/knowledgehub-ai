import { AdminTopbar } from '@/components/navigation/admin-topbar'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { FileText, Users, Search, BrainCircuit, Activity } from 'lucide-react'

export default function AdminDashboard() {
  return (
    <div className="bg-slate-50 min-h-full">
      <AdminTopbar title="Organization Overview" />
      <main className="p-8 max-w-7xl mx-auto">
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-500">Total Documents</CardTitle>
              <FileText className="h-4 w-4 text-slate-400" />
            </CardHeader>
            <CardContent><div className="text-3xl font-bold text-slate-900">0</div></CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-500">Active Members</CardTitle>
              <Users className="h-4 w-4 text-slate-400" />
            </CardHeader>
            <CardContent><div className="text-3xl font-bold text-slate-900">1</div></CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-500">Knowledge Queries</CardTitle>
              <Search className="h-4 w-4 text-slate-400" />
            </CardHeader>
            <CardContent><div className="text-3xl font-bold text-slate-900">0</div></CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-500">AI Usage</CardTitle>
              <BrainCircuit className="h-4 w-4 text-slate-400" />
            </CardHeader>
            <CardContent><div className="text-sm font-medium text-slate-500 mt-2">No data yet</div></CardContent>
          </Card>
        </div>
        
        <div className="grid gap-6 md:grid-cols-2">
          <Card className="h-[400px]">
            <CardHeader><CardTitle>Recent Documents</CardTitle></CardHeader>
            <CardContent className="flex items-center justify-center h-64">
              <div className="text-center text-slate-500">
                <FileText className="w-8 h-8 mx-auto mb-3 opacity-20" />
                <p className="text-sm">No documents uploaded yet</p>
              </div>
            </CardContent>
          </Card>
          <Card className="h-[400px]">
            <CardHeader><CardTitle>Recent Activity</CardTitle></CardHeader>
            <CardContent>
              <div className="flex items-center gap-4 py-3">
                <div className="w-2 h-2 rounded-full bg-blue-500"></div>
                <p className="text-sm text-slate-600"><span className="font-medium text-slate-900">You</span> created the organization</p>
                <span className="ml-auto text-xs text-slate-400">Just now</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}
