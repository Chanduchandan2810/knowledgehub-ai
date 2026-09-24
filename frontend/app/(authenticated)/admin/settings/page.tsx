import { AdminTopbar } from '@/components/navigation/admin-topbar'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

export default function AdminSettings() {
  return (
    <div className="bg-slate-50 min-h-full">
      <AdminTopbar title="Settings" />
      <main className="p-8 max-w-4xl mx-auto space-y-8">
        
        <Card>
          <div className="px-6 py-4 border-b bg-slate-50/50">
            <h2 className="text-sm font-semibold text-slate-900 uppercase tracking-wider">General</h2>
          </div>
          <CardContent className="space-y-4 pt-6">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Organization Name</label>
              <Input defaultValue="Acme Corp" className="max-w-md" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Organization Logo</label>
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 rounded bg-slate-100 border border-dashed flex items-center justify-center text-xs text-slate-400">Logo</div>
                <Button variant="outline" size="sm">Upload new</Button>
              </div>
            </div>
            <Button>Save General Settings</Button>
          </CardContent>
        </Card>

        <Card>
          <div className="px-6 py-4 border-b bg-slate-50/50">
            <h2 className="text-sm font-semibold text-slate-900 uppercase tracking-wider">Security</h2>
          </div>
          <CardContent className="space-y-4 pt-6">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Domain Restrictions</label>
              <Input placeholder="e.g. acme.com" className="max-w-md" />
              <p className="text-xs text-slate-500 mt-1">Only users with these email domains can join the organization.</p>
            </div>
            <Button variant="outline">Save Security Settings</Button>
          </CardContent>
        </Card>

        <Card>
          <div className="px-6 py-4 border-b bg-slate-50/50">
            <h2 className="text-sm font-semibold text-slate-900 uppercase tracking-wider">Knowledge Base</h2>
          </div>
          <CardContent className="space-y-4 pt-6">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Default Document Access</label>
              <select className="flex h-10 w-full max-w-md rounded-md border border-slate-300 bg-white px-3 py-2 text-sm">
                <option>All Organization Members</option>
                <option>Private (Only Uploader & Admins)</option>
              </select>
            </div>
            <Button variant="outline">Save Knowledge Settings</Button>
          </CardContent>
        </Card>

        <Card className="border-red-200">
          <div className="px-6 py-4 border-b border-red-100 bg-red-50/50">
            <h2 className="text-sm font-semibold text-red-800 uppercase tracking-wider">Danger Zone</h2>
          </div>
          <CardContent className="space-y-4 pt-6">
            <p className="text-sm text-slate-600">Irreversible actions regarding your organization data.</p>
            <Button variant="danger">Delete Organization</Button>
          </CardContent>
        </Card>

      </main>
    </div>
  )
}
