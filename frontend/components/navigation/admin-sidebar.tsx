"use client"
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { LayoutDashboard, FileText, Users, Shield, BarChart3, Activity, Settings, BrainCircuit } from 'lucide-react'
import { cn } from '../ui/button'
import React, { useEffect, useState } from 'react'
import { createClient } from '@/utils/supabase/client'

const workspaceNav = [
  // Dashboard item requested by user to be at the TOP of the WORKSPACE section
  { name: 'Dashboard', href: '/admin/dashboard', icon: LayoutDashboard },
  { name: 'AI Chat', href: '/admin/chat', icon: BrainCircuit },
  { name: 'Documents', href: '/admin/documents', icon: FileText },
  { name: 'Employees', href: '/admin/employees', icon: Users },
  { name: 'Permissions', href: '/admin/permissions', icon: Shield },
]

const insightsNav = [
  { name: 'Analytics', href: '/admin/analytics', icon: BarChart3 },
  { name: 'Activity', href: '/admin/activity', icon: Activity },
]

const configNav = [
  { name: 'Settings', href: '/admin/settings', icon: Settings },
]

type NavItem = { name: string, href: string, icon: React.ElementType }

function NavGroup({ items, label }: { items: NavItem[], label: string }) {
  const pathname = usePathname()
  return (
    <div className="mb-6">
      <h3 className="px-4 text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-2">{label}</h3>
      <nav className="space-y-0.5 px-2">
        {items.map((item) => {
          const isActive = pathname === item.href
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center px-3 py-2 text-sm font-medium rounded-md transition-all duration-200 group",
                isActive ? "bg-primary-50 text-primary-700" : "text-slate-600 hover:bg-slate-100/80 hover:text-slate-900"
              )}
            >
              <item.icon className={cn(
                "mr-3 h-4 w-4 transition-colors",
                isActive ? "text-primary-600" : "text-slate-400 group-hover:text-slate-600"
              )} />
              {item.name}
            </Link>
          )
        })}
      </nav>
    </div>
  )
}

export function AdminSidebar() {
  const pathname = usePathname()
  const [orgName, setOrgName] = useState<string>('')
  const [adminName, setAdminName] = useState<string>('')
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
          const isDemo = session.user?.email === 'admin@demo.knowledgehub.local'
          setAdminName(isDemo ? 'Demo Admin' : authData.full_name)
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

  const [isMobileOpen, setIsMobileOpen] = useState(false)
  useEffect(() => {
    const handleToggle = () => setIsMobileOpen(prev => !prev)
    window.addEventListener('toggle-mobile-sidebar', handleToggle)
    return () => window.removeEventListener('toggle-mobile-sidebar', handleToggle)
  }, [])

  // Close sidebar on navigation on mobile
  useEffect(() => {
    const t = setTimeout(() => setIsMobileOpen(false), 0)
    return () => clearTimeout(t)
  }, [pathname])

  return (
    <>
      {isMobileOpen && (
        <div
          className="fixed inset-0 bg-slate-900/50 z-40 md:hidden"
          onClick={() => setIsMobileOpen(false)}
        />
      )}
      <aside className={cn(
        "flex-col w-[260px] flex-shrink-0 border-r border-slate-200/80 bg-white z-50 md:z-20 transition-transform",
        isMobileOpen ? "fixed inset-y-0 left-0 flex" : "hidden md:flex"
      )}>
        <div className="h-16 flex items-center justify-between px-6 border-b border-slate-100">
          <Link href="/admin/dashboard" className="flex items-center gap-2.5 font-bold text-lg tracking-tight text-slate-900 group">
          <div className="bg-primary-600 text-white p-1 rounded-md shadow-sm group-hover:bg-primary-700 transition-colors">
            <BrainCircuit className="w-4 h-4" />
          </div>
          KnowledgeHub AI
        </Link>
      </div>

      <div className="flex-1 py-6 overflow-y-auto custom-scrollbar">
        <NavGroup label="Workspace" items={workspaceNav} />
        <NavGroup label="Insights" items={insightsNav} />
        <NavGroup label="Configuration" items={configNav} />
      </div>

      <div className="p-4 border-t border-slate-100 bg-slate-50/50 space-y-2">
        {userEmail === 'admin@demo.knowledgehub.local' && (
          <button
            onClick={async () => {
              await supabase.auth.signOut()
              window.location.href = '/demo'
            }}
            className="w-full flex items-center justify-center px-3 py-2 text-xs font-semibold rounded-md border border-amber-200 bg-amber-50 text-amber-700 shadow-sm hover:bg-amber-100 transition-colors"
          >
            Exit Demo Environment
          </button>
        )}
        <div className="flex items-center px-3 py-2 text-sm rounded-md border border-slate-200 bg-white shadow-sm cursor-pointer hover:bg-slate-50 transition-colors">
          <div className="w-7 h-7 rounded bg-purple-100 text-purple-700 flex items-center justify-center font-bold text-xs mr-3 border border-purple-200">
            {loading ? '...' : (adminName ? adminName.charAt(0).toUpperCase() : 'A')}
          </div>
          <div className="flex-1 truncate">
            <p className="font-semibold text-slate-900 truncate text-xs">
              {loading ? 'Loading...' : (adminName || 'Admin')}
            </p>
            <p className="text-[10px] font-bold text-purple-600 truncate tracking-wide uppercase">
              ADMIN PORTAL &bull; {orgName || 'N/A'}
            </p>
          </div>
        </div>
      </div>
    </aside>
    </>
  )
}
