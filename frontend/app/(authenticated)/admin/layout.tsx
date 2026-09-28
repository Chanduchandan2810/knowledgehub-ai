import { AdminSidebar } from '@/components/navigation/admin-sidebar'
import { createClient } from '@/utils/supabase/server'
import { redirect } from 'next/navigation'
import { cookies } from 'next/headers'

export default async function AdminLayout({ children }: { children: React.ReactNode }) {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()

  // No authenticated user → redirect to login
  if (!user) {
    redirect('/login')
  }

  const cookieStore = await cookies()
  const role = cookieStore.get('khub_role')?.value
  const activeOrgId = cookieStore.get('khub_org_id')?.value

  // Wrong role → redirect to correct portal
  if (role === 'EMPLOYEE') {
    redirect('/employee/chat')
  }

  // Note: activeOrgId is no longer strictly enforced here to prevent 307 loops.
  // The backend will enforce authorization strictly via the API endpoints.

  return (
    <div className="flex h-screen overflow-hidden bg-slate-50/50">
      <AdminSidebar />
      <div className="flex flex-col flex-1 w-0 overflow-hidden">
        {children}
      </div>
    </div>
  )
}
