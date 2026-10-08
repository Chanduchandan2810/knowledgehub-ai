"use client"
import { AdminTopbar } from '@/components/navigation/admin-topbar'
import { Button } from '@/components/ui/button'
import { UserPlus, Search, ShieldCheck, Users, Mail } from 'lucide-react'
import { PageTransition } from '@/components/shared/page-transition'
import { Input } from '@/components/ui/input'
import { useEffect, useState } from 'react'
import { createClient } from '@/utils/supabase/client'

type Employee = {
  id: string
  email: string
  full_name: string
  role: string
  joined_at: string
}

export default function AdminEmployees() {
  const [employees, setEmployees] = useState<Employee[]>([])
  const [loading, setLoading] = useState(true)
  const [isAdding, setisAdding] = useState(false)
  const [employeeEmail, setemployeeEmail] = useState('')
  const [employeeName, setemployeeName] = useState('')
  const [currentUserEmail, setCurrentUserEmail] = useState('')
  const [addResult, setaddResult] = useState<{success?: boolean, message?: string, link?: string} | null>(null)
  const supabase = createClient()
  const isValidUUID = (uuid: string) => {
    return /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(uuid);
  }

  const getActiveOrganizationId = async (session: { access_token: string }) => {
    const match = document.cookie.match(/(^|;)\s*khub_org_id\s*=\s*([^;]+)/);
    let orgId = match ? (match.pop() as string) : '';
    
    if (orgId && isValidUUID(orgId)) {
      return orgId;
    }

    // Recover organization from backend identity
    const res = await fetch('/api/v1/auth/me', {
      headers: { 'Authorization': `Bearer ${session.access_token}` }
    });
    
    if (res.ok) {
      const userContext = await res.json();
      if (userContext && userContext.organization_id) {
        orgId = userContext.organization_id;
        
        document.cookie = `khub_org_id=${orgId}; path=/; max-age=86400; SameSite=Lax`;
        document.cookie = `khub_role=${userContext.role}; path=/; max-age=86400; SameSite=Lax`;
        
        if (isValidUUID(orgId)) {
          return orgId;
        }
      }
    }
    
    throw new Error("No organization is associated with this account.");
  }

  const fetchEmployees = async () => {
    const { data: { session } } = await supabase.auth.getSession()
    if (!session) return

    try {
      const orgId = await getActiveOrganizationId(session)
      
      const [res, meRes] = await Promise.all([
        fetch('/api/v1/employees', {
          headers: { 'Authorization': `Bearer ${session.access_token}`, 'X-Organization-Id': orgId }
        }),
        fetch('/api/v1/auth/me', {
          headers: { 'Authorization': `Bearer ${session.access_token}` }
        })
      ])
      
      if (meRes.ok) {
        // me.email is not used to override session email anymore
      }

      if (res.ok) {
        setEmployees(await res.json())
      }
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    const init = async () => {
      const { data: { session } } = await supabase.auth.getSession()
      if (session?.user?.email) {
        setCurrentUserEmail(session.user.email)
      }
      fetchEmployees()
    }
    init()
  }, [])


  const handleAddEmployee = async (e: React.FormEvent) => {
    e.preventDefault()
    setisAdding(true)
    setaddResult(null)

    const { data: { session } } = await supabase.auth.getSession()
    if (!session) return

    try {
      const res = await fetch('/api/v1/employees', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`, 'X-Organization-Id': await getActiveOrganizationId(session)
        },
        body: JSON.stringify({ email: employeeEmail, full_name: employeeName })
      })
      
      let data: Record<string, unknown> = {};
        try {
          const contentType = res.headers.get('content-type');
          if (contentType && contentType.indexOf('application/json') !== -1) {
            data = await res.json();
          } else {
            const text = await res.text();
            data = { detail: text || res.statusText };
          }
        } catch (parseErr) {
          data = { detail: 'Failed to parse server response' };
        }
      
      if (res.ok) {
        setaddResult({ success: true, message: `Employee created successfully. Temporary password: ${data?.temporary_password || 'Unknown'}`  })
        setemployeeEmail('')
        setemployeeName('')
        fetchEmployees()
      } else {
        let errorMsg = 'Failed to add employee';
          if (typeof data.detail === 'string') { errorMsg = data.detail; }
          else if (Array.isArray(data.detail)) { errorMsg = data.detail.map((err: { msg: string }) => err.msg).join(', '); }
          setaddResult({ success: false, message: errorMsg })
      }
    } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Unknown error';
        setaddResult({ success: false, message: errorMessage })
      // replaced
    } finally {
      setisAdding(false)
    }
  }

  return (
    <div className="flex flex-col h-full bg-slate-50/50">
      <AdminTopbar title="Employees" description="Manage user access and organizational roles." />
      <PageTransition className="flex-1 overflow-y-auto p-6 md:p-8">
        <div className="max-w-[1600px] mx-auto space-y-6">
          
          <div className="bg-white p-6 border border-slate-200/80 rounded-xl shadow-sm mb-6">
            <h3 className="text-lg font-semibold text-slate-900 mb-4">Add Employee</h3>
            <form onSubmit={handleAddEmployee} className="flex flex-col sm:flex-row gap-4 items-start">
              <div className="w-full sm:max-w-xs space-y-1.5">
                <label className="text-xs font-semibold text-slate-600 uppercase tracking-wider">Full Name</label>
                <Input required placeholder="Jane Doe" value={employeeName} onChange={e => setemployeeName(e.target.value)} />
              </div>
              <div className="w-full sm:max-w-xs space-y-1.5">
                <label className="text-xs font-semibold text-slate-600 uppercase tracking-wider">Work Email</label>
                <Input required type="email" placeholder="jane@company.com" value={employeeEmail} onChange={e => setemployeeEmail(e.target.value)} />
              </div>
              <div className="pt-6 relative group">
                <Button 
                  type="submit" 
                  disabled={isAdding || currentUserEmail === 'admin@demo.knowledgehub.local'} 
                  className="shadow-sm w-full"
                >
                  <UserPlus className="mr-2 h-4 w-4" /> {isAdding ? 'Adding...' : 'Create Employee'}
                </Button>
                {currentUserEmail === 'admin@demo.knowledgehub.local' && (
                  <div className="absolute top-full left-0 mt-2 p-2 bg-slate-800 text-white text-xs rounded shadow-lg opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity whitespace-nowrap z-50">
                    Employee management is disabled in the public demo.
                  </div>
                )}
              </div>
            </form>
            {addResult && (
              <div className={`mt-4 p-3 rounded-md text-sm border ${addResult.success ? 'bg-emerald-50 text-emerald-800 border-emerald-200' : 'bg-red-50 text-red-800 border-red-200'}`}>
                {addResult.message}
                
              </div>
            )}
          </div>

          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div className="relative w-full sm:max-w-md">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
              <Input placeholder="Search employees by name or email..." className="pl-9 bg-white shadow-sm" />
            </div>
          </div>
          
          <div className="bg-white border border-slate-200/80 rounded-xl shadow-sm overflow-hidden">
            <div className="grid grid-cols-12 px-6 py-4 border-b border-slate-200 bg-slate-50/80 text-xs font-semibold text-slate-500 uppercase tracking-wider">
              <div className="col-span-6 md:col-span-5">User</div>
              <div className="col-span-3 md:col-span-3 hidden sm:block">Role</div>
              <div className="col-span-6 sm:col-span-3 md:col-span-4 text-right">Joined</div>
            </div>
            
            <div className="divide-y divide-slate-100">
              {loading ? (
                <div className="px-6 py-8 text-center text-sm text-slate-500">Loading employees...</div>
              ) : employees.length === 0 ? (
                <div className="p-12 border-t border-slate-100 bg-slate-50/30">
                  <div className="max-w-sm mx-auto text-center">
                    <div className="w-12 h-12 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4 border border-slate-200">
                      <Users className="w-5 h-5 text-slate-400" />
                    </div>
                    <h3 className="text-sm font-semibold text-slate-900 mb-1">No other employees</h3>
                    <p className="text-xs text-slate-500 mb-4">Add employees to your organization to grant them access to the knowledge base.</p>
                  </div>
                </div>
              ) : (
                employees.map(employee => (
                  <div key={employee.id} className="grid grid-cols-12 px-6 py-4 items-center hover:bg-slate-50/50 transition-colors">
                    <div className="col-span-6 md:col-span-5 flex items-center gap-3">
                      <div className="w-9 h-9 rounded-full bg-primary-100 text-primary-700 flex items-center justify-center font-bold text-xs border border-primary-200 shadow-sm">
                        {employee.full_name ? employee.full_name[0].toUpperCase() : employee.email[0].toUpperCase()}
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-slate-900">{employee.full_name || 'Pending Name'}</p>
                        <p className="text-xs text-slate-500">{employee.email}</p>
                      </div>
                    </div>
                    <div className="col-span-3 md:col-span-3 hidden sm:block">
                      {employee.role === 'ADMIN' ? (
                        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-purple-50 text-purple-700 text-xs font-medium border border-purple-100">
                          <ShieldCheck className="w-3 h-3" /> ADMIN
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-slate-100 text-slate-700 text-xs font-medium border border-slate-200">
                          <Users className="w-3 h-3" /> EMPLOYEE
                        </span>
                      )}
                    </div>
                    <div className="col-span-6 sm:col-span-3 md:col-span-4 text-right text-sm text-slate-500">
                      {new Date(employee.joined_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                    </div>
                  </div>
                ))
              )}
            </div>
            
          </div>
          
        </div>
      </PageTransition>
    </div>
  )
}









