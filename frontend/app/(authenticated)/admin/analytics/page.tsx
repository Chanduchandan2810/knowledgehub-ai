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
