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
