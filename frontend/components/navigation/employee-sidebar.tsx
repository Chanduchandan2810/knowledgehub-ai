"use client"
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { MessageSquare, Plus, BrainCircuit, Search, LogOut, Settings, User } from 'lucide-react'
import { Button, cn } from '../ui/button'
import { LogoutButton } from '../shared/logout-button'
import { useEffect, useState } from 'react'
import { createClient } from '@/utils/supabase/client'

export function EmployeeSidebar() {
  const pathname = usePathname()
  const [orgName, setOrgName] = useState<string>('')
  const [empName, setEmpName] = useState<string>('')
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
        const [orgRes, userRes] = await Promise.all([
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
          const orgData = await orgRes.json()
          setOrgName(orgData.name)
        } else {
          setOrgName('Organization info unavailable')
        }

        if (userRes.ok) {
          const userData = await userRes.json()
          setEmpName(userData.full_name || userData.email)
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
    <aside className="hidden md:flex flex-col w-[260px] flex-shrink-0 border-r border-slate-200 bg-slate-50/50 z-20">
      <div className="h-16 flex items-center px-4 border-b border-slate-200/60 bg-transparent">
        <Link href="/employee/chat" className="flex items-center gap-2 font-bold text-lg tracking-tight text-slate-900 group w-full">
          <div className="bg-primary-600 text-white p-1 rounded-md shadow-sm group-hover:bg-primary-700 transition-colors">
            <BrainCircuit className="w-4 h-4" />
          </div>
          KnowledgeHub AI
        </Link>
      </div>
      
      <div className="p-4">
        <Button className="w-full justify-start shadow-sm bg-primary-600 hover:bg-primary-700 text-white font-medium h-10 rounded-lg">
          <Plus className="mr-2 h-4 w-4" /> New Chat
        </Button>
      </div>

      <div className="flex-1 py-2 overflow-y-auto custom-scrollbar">
        <h3 className="px-5 text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2">History</h3>
        <nav className="space-y-0.5 px-3">
          {[
            { id: 1, title: 'Annual Leave Policy & Carryover', active: true },
            { id: 2, title: 'Hardware Request Process', active: false },
            { id: 3, title: 'Q3 Financial Summary Review', active: false },
          ].map(chat => (
            <Link key={chat.id} href="/employee/conversations" className={cn(
              "flex items-center px-3 py-2 text-sm font-medium rounded-md transition-all duration-200 group",
              chat.active ? "bg-white border border-slate-200 shadow-sm text-slate-900" : "text-slate-600 hover:bg-slate-100 hover:text-slate-900 border border-transparent"
            )}>
              <MessageSquare className={cn("mr-3 h-4 w-4", chat.active ? "text-primary-500" : "text-slate-400 group-hover:text-slate-500")} />
              <span className="truncate flex-1">{chat.title}</span>
            </Link>
          ))}
        </nav>
      </div>

      <div className="p-4 border-t border-slate-200/60 bg-white">
        <div className="flex items-center px-3 py-2 mb-3 text-sm rounded-md border border-slate-200 bg-slate-50 shadow-sm transition-colors">
          <div className="w-8 h-8 rounded bg-primary-100 text-primary-700 flex items-center justify-center font-bold text-xs mr-3 border border-primary-200">
            {loading ? '...' : (empName ? empName.charAt(0).toUpperCase() : 'U')}
          </div>
          <div className="flex-1 truncate">
            <p className="text-[10px] font-semibold text-slate-500 truncate mb-0.5 tracking-wide">
              {loading ? 'Loading...' : (orgName || 'Organization info unavailable')}
            </p>
            <p className="font-semibold text-slate-900 truncate text-sm leading-tight">
              {loading ? 'Loading...' : (empName || 'Employee')}
            </p>
            <p className="text-[10px] font-bold text-slate-400 tracking-widest mt-0.5 uppercase">EMPLOYEE</p>
          </div>
        </div>

        <div className="flex flex-col gap-1">
          <Link href="/employee/profile" className={cn(
            "flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors",
            pathname === "/employee/profile" ? "bg-slate-100 text-slate-900" : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
          )}>
            <User className="w-4 h-4 mr-3 text-slate-400" /> Profile
          </Link>
          <Link href="/employee/settings" className={cn(
            "flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors",
            pathname === "/employee/settings" || pathname === "/employee/change-password" ? "bg-slate-100 text-slate-900" : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
          )}>
            <Settings className="w-4 h-4 mr-3 text-slate-400" /> Settings
          </Link>
          <LogoutButton variant="full" />
        </div>
      </div>
    </aside>
  )
}
