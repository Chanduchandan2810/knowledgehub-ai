import { AdminTopbar } from '@/components/navigation/admin-topbar'
import { Card, CardContent } from '@/components/ui/card'

export default function AdminActivity() {
  return (
    <div className="bg-slate-50 min-h-full">
      <AdminTopbar title="Activity Log" />
      <main className="p-8 max-w-5xl mx-auto">
        <Card className="overflow-hidden">
          <CardContent className="p-0">
            <div className="divide-y divide-slate-100 text-sm">
              <div className="p-4 hover:bg-slate-50 transition-colors">
                <div className="flex justify-between items-start">
                  <div className="flex gap-3 items-start">
                    <div className="w-2 h-2 rounded-full bg-blue-500 mt-1.5"></div>
                    <div>
                      <p><span className="font-medium text-slate-900">Chandan</span> uploaded <span className="font-medium text-slate-700">Employee Handbook.pdf</span></p>
                      <p className="text-xs text-slate-500 mt-0.5">Knowledge Base</p>
                    </div>
                  </div>
                  <span className="text-slate-400 text-xs">2 mins ago</span>
                </div>
              </div>
              <div className="p-4 hover:bg-slate-50 transition-colors">
                <div className="flex justify-between items-start">
                  <div className="flex gap-3 items-start">
                    <div className="w-2 h-2 rounded-full bg-slate-300 mt-1.5"></div>
                    <div>
                      <p><span className="font-medium text-slate-900">Admin</span> changed document permissions for <span className="font-medium text-slate-700">Q3 Financials.pdf</span></p>
                      <p className="text-xs text-slate-500 mt-0.5">Permissions</p>
                    </div>
                  </div>
                  <span className="text-slate-400 text-xs">18 mins ago</span>
                </div>
              </div>
              <div className="p-4 hover:bg-slate-50 transition-colors">
                <div className="flex justify-between items-start">
                  <div className="flex gap-3 items-start">
                    <div className="w-2 h-2 rounded-full bg-green-500 mt-1.5"></div>
                    <div>
                      <p><span className="font-medium text-slate-900">New member</span> joined organization</p>
                      <p className="text-xs text-slate-500 mt-0.5">Members</p>
                    </div>
                  </div>
                  <span className="text-slate-400 text-xs">1 hour ago</span>
                </div>
              </div>
              <div className="p-4 hover:bg-slate-50 transition-colors">
                <div className="flex justify-between items-start">
                  <div className="flex gap-3 items-start">
                    <div className="w-2 h-2 rounded-full bg-red-400 mt-1.5"></div>
                    <div>
                      <p><span className="font-medium text-slate-900">Document deleted</span></p>
                      <p className="text-xs text-slate-500 mt-0.5">System</p>
                    </div>
                  </div>
                  <span className="text-slate-400 text-xs">Yesterday</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  )
}
