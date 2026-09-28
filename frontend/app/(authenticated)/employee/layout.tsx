import { EmployeeSidebar } from '@/components/navigation/employee-sidebar'
import { createClient } from '@/utils/supabase/server'
import { redirect } from 'next/navigation'
import { cookies } from 'next/headers'

export default async function EmployeeLayout({ children }: { children: React.ReactNode }) {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()

  // No authenticated user → redirect to login
  if (!user) {
    redirect('/login')
  }

  const cookieStore = await cookies()
  const role = cookieStore.get('khub_role')?.value

  // Wrong role → redirect to correct portal
  if (role === 'ADMIN') {
    redirect('/admin/documents')
  }

  return (
    <div className="flex h-screen overflow-hidden bg-white">
      <EmployeeSidebar />
      <div className="flex flex-col flex-1 w-0 overflow-hidden relative">
        {children}
      </div>
    </div>
  )
}
