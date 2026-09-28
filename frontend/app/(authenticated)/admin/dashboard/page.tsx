import { AdminTopbar } from "@/components/navigation/admin-topbar"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { 
  FileText, 
  Users, 
  MessageSquare, 
  Activity, 
  Plus, 
  ShieldCheck, 
  Settings,
  BrainCircuit,
  Search,
  ArrowRight
} from "lucide-react"
import Link from "next/link"

export const metadata = {
  title: "Dashboard - Admin Portal",
}

export default function AdminDashboardPage() {
  return (
    <div className="flex flex-col h-full bg-slate-50/50 relative">
      <AdminTopbar title="Dashboard" description="Overview of your organization's AI knowledge hub." />
      <div className="flex-1 flex flex-col overflow-auto p-6 md:p-8 custom-scrollbar">
        <div className="max-w-6xl mx-auto space-y-8 w-full">

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Documents</CardTitle>
            <FileText className="h-4 w-4 text-slate-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">12</div>
            <p className="text-xs text-slate-500 mt-1">Processed and indexed</p>
          </CardContent>
        </Card>
        
        <Card className="shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Employees</CardTitle>
            <Users className="h-4 w-4 text-slate-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">4</div>
            <p className="text-xs text-slate-500 mt-1">Granted access</p>
          </CardContent>
        </Card>
        
        <Card className="shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Queries</CardTitle>
            <MessageSquare className="h-4 w-4 text-slate-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">148</div>
            <p className="text-xs text-slate-500 mt-1">+12% from last week</p>
          </CardContent>
        </Card>
        
        <Card className="shadow-sm border-primary-200 bg-primary-50/30">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-primary-900">AI Status</CardTitle>
            <BrainCircuit className="h-4 w-4 text-primary-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-primary-700">Online</div>
            <p className="text-xs text-primary-600 mt-1">Retrieval system active</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card className="shadow-sm col-span-1">
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <p className="text-sm text-slate-500">Frequently used administrative tools</p>
          </CardHeader>
          <CardContent className="grid gap-4">
            <Link href="/admin/documents">
              <Button variant="outline" className="w-full justify-start h-12 hover:bg-primary-50 hover:text-primary-700 hover:border-primary-200 transition-colors">
                <Plus className="mr-3 h-4 w-4" />
                Add Knowledge Document
              </Button>
            </Link>
            <Link href="/admin/employees">
              <Button variant="outline" className="w-full justify-start h-12 hover:bg-primary-50 hover:text-primary-700 hover:border-primary-200 transition-colors">
                <Users className="mr-3 h-4 w-4" />
                Add Team Members
              </Button>
            </Link>
            <Link href="/admin/permissions">
              <Button variant="outline" className="w-full justify-start h-12 hover:bg-primary-50 hover:text-primary-700 hover:border-primary-200 transition-colors">
                <ShieldCheck className="mr-3 h-4 w-4" />
                Configure Access & Permissions
              </Button>
            </Link>
            <Link href="/admin/settings">
              <Button variant="outline" className="w-full justify-start h-12 hover:bg-primary-50 hover:text-primary-700 hover:border-primary-200 transition-colors">
                <Settings className="mr-3 h-4 w-4" />
                Organization Settings
              </Button>
            </Link>
          </CardContent>
        </Card>

        <Card className="shadow-sm col-span-1">
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <p className="text-sm text-slate-500">Latest events in your workspace</p>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {[
                { icon: FileText, title: "Employee Handbook.pdf", desc: "Successfully processed and indexed", time: "2 hours ago", color: "text-blue-600", bg: "bg-blue-100" },
                { icon: Users, title: "New Employee Added", desc: "chan@gmail.com granted access", time: "5 hours ago", color: "text-green-600", bg: "bg-green-100" },
                { icon: Search, title: "Query Spike Detected", desc: "45 queries processed in 1 hour", time: "Yesterday", color: "text-orange-600", bg: "bg-orange-100" },
                { icon: Settings, title: "Settings Updated", desc: "Organization details modified", time: "2 days ago", color: "text-slate-600", bg: "bg-slate-100" },
              ].map((activity, i) => (
                <div key={i} className="flex items-start gap-4">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${activity.bg} ${activity.color}`}>
                    <activity.icon className="w-4 h-4" />
                  </div>
                  <div className="flex-1 space-y-1">
                    <p className="text-sm font-medium leading-none">{activity.title}</p>
                    <p className="text-sm text-slate-500">{activity.desc}</p>
                  </div>
                  <div className="text-xs text-slate-400 font-medium whitespace-nowrap">
                    {activity.time}
                  </div>
                </div>
              ))}
            </div>
            
            <div className="mt-6 pt-4 border-t border-slate-100">
              <Link href="/admin/activity" className="text-sm text-primary-600 font-medium hover:text-primary-700 flex items-center">
                View all activity <ArrowRight className="ml-1 w-4 h-4" />
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
    </div>
    </div>
  )
}
