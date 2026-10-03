"use client"
import { Bell, Search, Menu, HelpCircle } from 'lucide-react'
import { Input } from '../ui/input'
import { Button } from '../ui/button'
import { LogoutButton } from '../shared/logout-button'
import { useEffect, useState } from 'react'
import { createClient } from '@/utils/supabase/client'

export function AdminTopbar({ title, description, role = "ADMIN" }: { title: string, description?: string, role?: "ADMIN" | "EMPLOYEE" }) {
  const [orgName, setOrgName] = useState<string>('')
  const [userName, setUserName] = useState<string>('')
  const [userEmail, setUserEmail] = useState<string>('')
  const [loading, setLoading] = useState(true)
  const supabase = createClient()

  useEffect(() => {
    const fetchData = async () => {
      const match = document.cookie.match(/(^|;)\s*khub_org_id\s*=\s*([^;]+)/);
      const orgId = match ? (match.pop() as string) : '';

      const { data: { session } } = await supabase.auth.getSession()
      if (!session) {
        setLoading(false)
        return
      }

      try {
        const [orgRes, authRes] = await Promise.all([
          orgId ? fetch('/api/v1/organizations/current', {
            headers: {
              'Authorization': `Bearer ${session.access_token}`,
              'X-Organization-Id': orgId
            }
          }) : Promise.resolve(null),
          fetch('/api/v1/auth/me', {
            headers: {
              'Authorization': `Bearer ${session.access_token}`
            }
          })
        ])

        if (orgRes && orgRes.ok) {
          const data = await orgRes.json()
          setOrgName(data.name)
        } else {
          setOrgName('Organization info unavailable')
        }

        if (authRes.ok) {
          const authData = await authRes.json()
          const isDemoAdmin = session.user?.email === 'admin@demo.knowledgehub.local'
          const isDemoEmployee = session.user?.email === 'employee@demo.knowledgehub.local'
          
          let display = authData.full_name
          if (isDemoAdmin) display = 'Demo Admin'
          else if (isDemoEmployee) display = 'Demo Employee'
          
          setUserName(display)
          setUserEmail(session.user?.email || authData.email)
        }
      } catch (err) {
        setOrgName('Organization info unavailable')
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  return (
    <header className="h-16 flex-shrink-0 bg-white/80 backdrop-blur-md border-b border-slate-200/60 flex items-center justify-between px-4 sm:px-6 z-10">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" className="md:hidden text-slate-500">
          <Menu className="h-5 w-5" />
        </Button>
        <div>
          <h1 className="text-lg font-semibold text-slate-900 tracking-tight leading-tight">{title}</h1>
          {description && <p className="text-xs text-slate-500 hidden sm:block">{description}</p>}
        </div>
      </div>
      
      <div className="flex items-center gap-3 sm:gap-4">
        <div className="hidden lg:flex items-center mr-4 border-r border-slate-200 pr-4">
          <div className="text-right">
            <p className="text-sm font-bold text-slate-900 max-w-[160px] truncate">
              {loading ? 'Loading...' : (userName || 'User')}
            </p>
            <p className={`text-[10px] font-bold tracking-wider ${role === 'ADMIN' ? 'text-purple-600' : 'text-blue-600'}`}>
              {role}
            </p>
          </div>
        </div>
        
        <div className="relative hidden xl:block w-64">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-400" />
          <Input type="search" placeholder="Search knowledge base..." className="w-full pl-9 bg-slate-50 border-slate-200 text-sm h-9 rounded-md shadow-inner transition-all focus:bg-white" />
        </div>
        
        <div className="flex items-center gap-1 sm:gap-2 pl-2">
          <Button variant="ghost" size="icon" className="text-slate-400 hover:text-slate-600 rounded-full h-8 w-8 relative">
            <Bell className="h-4 w-4" />
          </Button>
          <LogoutButton />
          <div className={`ml-2 w-8 h-8 rounded-full border flex items-center justify-center text-xs font-bold cursor-default shadow-sm hidden sm:flex ${
            role === 'ADMIN' 
              ? 'bg-purple-100 text-purple-700 border-purple-200' 
              : 'bg-blue-100 text-blue-700 border-blue-200'
          }`}>
            {loading ? '...' : (userName ? userName.charAt(0).toUpperCase() : (role === 'ADMIN' ? 'A' : 'E'))}
          </div>
        </div>
      </div>
    </header>
  )
}
