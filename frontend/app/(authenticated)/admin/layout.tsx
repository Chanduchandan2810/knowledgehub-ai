import { AdminSidebar } from '@/components/navigation/admin-sidebar'

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen overflow-hidden bg-slate-50/50">
      <AdminSidebar />
      <div className="flex flex-col flex-1 w-0 overflow-hidden">
        {children}
      </div>
    </div>
  )
}
