"use client"
import { AdminTopbar } from '@/components/navigation/admin-topbar'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { FileText, Users, Search, BrainCircuit, Activity, Settings, ArrowUpRight, Shield } from 'lucide-react'
import { PageTransition } from '@/components/shared/page-transition'
import { Button } from '@/components/ui/button'

export default function AdminDashboard() {
  return (
    <div className="flex flex-col h-full bg-slate-50/50">
      <AdminTopbar title="Dashboard" description="Overview of your organization's knowledge base." />
      <PageTransition className="flex-1 overflow-y-auto p-6 md:p-8">
        <div className="max-w-[1600px] mx-auto space-y-8">
          
          {/* Welcome Section */}
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm relative overflow-hidden">
            <div className="absolute right-0 top-0 w-64 h-full bg-gradient-to-l from-primary-50 to-transparent pointer-events-none"></div>
            <div className="relative z-10">
              <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Welcome to KnowledgeHub</h2>
              <p className="text-sm text-slate-500 mt-1 max-w-xl leading-relaxed">
                Your workspace is ready. You can now invite members and upload organizational knowledge to enable AI-powered secure retrieval.
              </p>
            </div>
            <div className="flex gap-3 relative z-10 w-full sm:w-auto">
              <Button variant="outline" className="w-full sm:w-auto shadow-sm">View Guide</Button>
              <Button className="w-full sm:w-auto shadow-sm"><FileText className="w-4 h-4 mr-2" /> Add Knowledge</Button>
            </div>
          </div>

          {/* Core Metrics */}
          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 md:gap-6">
            <Card className="bg-white shadow-sm hover:shadow-md transition-all">
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-10 h-10 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center"><FileText className="w-5 h-5" /></div>
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Indexed Docs</span>
                </div>
                <div className="text-3xl font-bold text-slate-900 mb-1">0</div>
                <p className="text-xs text-slate-500 font-medium">Ready for retrieval</p>
              </CardContent>
            </Card>
            
            <Card className="bg-white shadow-sm hover:shadow-md transition-all">
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-10 h-10 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center"><Users className="w-5 h-5" /></div>
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Active Users</span>
                </div>
                <div className="text-3xl font-bold text-slate-900 mb-1">1</div>
                <p className="text-xs text-slate-500 font-medium">Organization members</p>
              </CardContent>
            </Card>

            <Card className="bg-white shadow-sm hover:shadow-md transition-all">
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-10 h-10 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center"><Search className="w-5 h-5" /></div>
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Queries</span>
                </div>
                <div className="text-3xl font-bold text-slate-900 mb-1">0</div>
                <p className="text-xs text-slate-500 font-medium">Last 30 days</p>
              </CardContent>
            </Card>

            <Card className="bg-white shadow-sm hover:shadow-md transition-all">
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-10 h-10 rounded-lg bg-purple-50 text-purple-600 flex items-center justify-center"><BrainCircuit className="w-5 h-5" /></div>
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">AI Accuracy</span>
                </div>
                <div className="text-3xl font-bold text-slate-900 mb-1">—</div>
                <p className="text-xs text-slate-500 font-medium">Awaiting first interactions</p>
              </CardContent>
            </Card>
          </div>
          
          {/* Main Content Area */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 lg:gap-8">
            <Card className="lg:col-span-2 flex flex-col shadow-sm">
              <CardHeader className="border-b border-slate-100 py-5 px-6 bg-slate-50/50">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base font-semibold text-slate-900">Recent Knowledge Activity</CardTitle>
                  <Button variant="ghost" size="sm" className="h-8 text-xs text-primary-600 hover:text-primary-700">View All</Button>
                </div>
              </CardHeader>
              <CardContent className="flex-1 flex flex-col items-center justify-center min-h-[300px] p-6 text-center">
                <div className="w-16 h-16 bg-slate-50 rounded-full border border-slate-100 flex items-center justify-center mb-4">
                  <Activity className="w-6 h-6 text-slate-300" />
                </div>
                <h3 className="text-sm font-semibold text-slate-900 mb-1">No recent activity</h3>
                <p className="text-xs text-slate-500 max-w-[250px] mx-auto mb-6">Activity will appear here once users start querying the knowledge base.</p>
                <Button variant="outline" size="sm" className="shadow-sm">Go to Documents</Button>
              </CardContent>
            </Card>

            <div className="space-y-6">
              <Card className="shadow-sm">
                <CardHeader className="py-4 px-6 border-b border-slate-100 bg-slate-50/50">
                  <CardTitle className="text-sm font-semibold text-slate-900 uppercase tracking-wider">Quick Actions</CardTitle>
                </CardHeader>
                <CardContent className="p-4 space-y-2">
                  <button className="w-full flex items-center justify-between p-3 text-sm font-medium text-slate-700 hover:bg-slate-50 rounded-lg transition-colors border border-transparent hover:border-slate-200">
                    <span className="flex items-center"><Users className="w-4 h-4 mr-3 text-slate-400" /> Invite Team Members</span>
                    <ArrowUpRight className="w-3.5 h-3.5 text-slate-400" />
                  </button>
                  <button className="w-full flex items-center justify-between p-3 text-sm font-medium text-slate-700 hover:bg-slate-50 rounded-lg transition-colors border border-transparent hover:border-slate-200">
                    <span className="flex items-center"><Shield className="w-4 h-4 mr-3 text-slate-400" /> Configure Access</span>
                    <ArrowUpRight className="w-3.5 h-3.5 text-slate-400" />
                  </button>
                  <button className="w-full flex items-center justify-between p-3 text-sm font-medium text-slate-700 hover:bg-slate-50 rounded-lg transition-colors border border-transparent hover:border-slate-200">
                    <span className="flex items-center"><Settings className="w-4 h-4 mr-3 text-slate-400" /> Organization Settings</span>
                    <ArrowUpRight className="w-3.5 h-3.5 text-slate-400" />
                  </button>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-br from-primary-900 to-navy-900 text-white shadow-md border-0">
                <CardContent className="p-6">
                  <BrainCircuit className="w-8 h-8 text-primary-400 mb-4" />
                  <h3 className="font-semibold mb-2">Need Help Getting Started?</h3>
                  <p className="text-sm text-primary-200 mb-4 leading-relaxed">
                    Read our enterprise setup guide to learn how to structure your documents for optimal AI retrieval.
                  </p>
                  <Button className="w-full bg-white text-navy-900 hover:bg-slate-100 shadow-sm">Read the Guide</Button>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </PageTransition>
    </div>
  )
}
