import { EmployeeSidebar } from '@/components/navigation/employee-sidebar'

export default function EmployeeLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-white">
      <EmployeeSidebar />
      <div className="ml-72 flex-1 h-screen flex flex-col">
        {children}
      </div>
    </div>
  )
}
