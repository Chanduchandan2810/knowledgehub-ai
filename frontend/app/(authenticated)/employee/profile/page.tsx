import { Button } from '@/components/ui/button'

export default function EmployeeProfile() {
  return (
    <div className="flex-1 p-8 bg-slate-50 min-h-full">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold text-slate-900 mb-8">Profile & Account</h1>
        
        <div className="bg-white border rounded-xl overflow-hidden shadow-sm">
          <div className="px-6 py-4 border-b bg-slate-50/50">
            <h2 className="text-sm font-semibold text-slate-900 uppercase tracking-wider">Personal Information</h2>
          </div>
          <div className="divide-y divide-slate-100">
            <div className="px-6 py-5 flex flex-col md:flex-row md:items-center">
              <span className="text-sm font-medium text-slate-500 md:w-48 mb-1 md:mb-0">Name</span>
              <span className="text-sm font-medium text-slate-900">Chandan</span>
            </div>
            <div className="px-6 py-5 flex flex-col md:flex-row md:items-center">
              <span className="text-sm font-medium text-slate-500 md:w-48 mb-1 md:mb-0">Email</span>
              <span className="text-sm font-medium text-slate-900">employee@company.com</span>
            </div>
            <div className="px-6 py-5 flex flex-col md:flex-row md:items-center">
              <span className="text-sm font-medium text-slate-500 md:w-48 mb-1 md:mb-0">Organization</span>
              <span className="text-sm font-medium text-slate-900">Acme Corporation</span>
            </div>
            <div className="px-6 py-5 flex flex-col md:flex-row md:items-center">
              <span className="text-sm font-medium text-slate-500 md:w-48 mb-1 md:mb-0">Role</span>
              <span className="inline-flex items-center rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-semibold text-slate-800">
                MEMBER
              </span>
            </div>
          </div>
        </div>

        <div className="mt-8 bg-white border rounded-xl overflow-hidden shadow-sm">
          <div className="px-6 py-4 border-b bg-slate-50/50">
            <h2 className="text-sm font-semibold text-slate-900 uppercase tracking-wider">Account Actions</h2>
          </div>
          <div className="p-6">
            <Button variant="outline" className="text-red-600 hover:text-red-700 hover:bg-red-50 border-red-200">
              Sign Out
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
