"use client"
import { AdminTopbar } from '@/components/navigation/admin-topbar'
import { PageTransition } from '@/components/shared/page-transition'
import { Card, CardContent } from '@/components/ui/card'
import { BarChart3, LineChart, PieChart } from 'lucide-react'

export default function AdminAnalytics() {
  return (
    <div className="flex flex-col h-full bg-slate-50/50">
      <AdminTopbar title="Analytics" description="Insights into knowledge utilization and AI performance." />
      <PageTransition className="flex-1 overflow-y-auto p-6 md:p-8">
        <div className="max-w-[1600px] mx-auto space-y-6">
          
          <div className="grid md:grid-cols-3 gap-6">
            <Card className="bg-white shadow-sm border-slate-200 overflow-hidden">
              <div className="p-4 border-b border-slate-100 bg-slate-50/50 flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-primary-500" /> <span className="text-sm font-semibold">Query Volume</span>
              </div>
              <CardContent className="h-48 flex items-center justify-center">
                <p className="text-sm text-slate-400 font-medium">Insufficient data for chart</p>
              </CardContent>
            </Card>

            <Card className="bg-white shadow-sm border-slate-200 overflow-hidden">
              <div className="p-4 border-b border-slate-100 bg-slate-50/50 flex items-center gap-2">
                <LineChart className="w-4 h-4 text-emerald-500" /> <span className="text-sm font-semibold">Retrieval Accuracy</span>
              </div>
              <CardContent className="h-48 flex items-center justify-center">
                <p className="text-sm text-slate-400 font-medium">Insufficient data for chart</p>
              </CardContent>
            </Card>
            
            <Card className="bg-white shadow-sm border-slate-200 overflow-hidden">
              <div className="p-4 border-b border-slate-100 bg-slate-50/50 flex items-center gap-2">
                <PieChart className="w-4 h-4 text-indigo-500" /> <span className="text-sm font-semibold">Document Types</span>
              </div>
              <CardContent className="h-48 flex items-center justify-center">
                <p className="text-sm text-slate-400 font-medium">Insufficient data for chart</p>
              </CardContent>
            </Card>
          </div>

          <Card className="shadow-sm border-slate-200">
             <div className="p-6 text-center h-[300px] flex flex-col items-center justify-center">
               <h3 className="text-lg font-semibold text-slate-900 mb-2">Platform Metrics</h3>
               <p className="text-sm text-slate-500 max-w-md mx-auto">Analytics will automatically populate once your team begins uploading documents and interacting with the AI knowledge assistant.</p>
             </div>
          </Card>
          
        </div>
      </PageTransition>
    </div>
  )
}
