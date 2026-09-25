import { EmployeeSidebar } from '@/components/navigation/employee-sidebar'

export default function EmployeeLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen overflow-hidden bg-white">
      <EmployeeSidebar />
      <div className="flex flex-col flex-1 w-0 overflow-hidden relative">
        {children}
      </div>
    </div>
  )
}
