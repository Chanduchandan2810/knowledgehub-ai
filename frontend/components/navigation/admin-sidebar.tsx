"use client"

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { LayoutDashboard, FileText, Users, Shield, BarChart3, Activity, Settings, HelpCircle, LogOut } from 'lucide-react'
import { cn } from '../ui/button'

const workspaceNav = [
  { name: 'Overview', href: '/admin/dashboard', icon: LayoutDashboard },
  { name: 'Documents', href: '/admin/documents', icon: FileText },
  { name: 'Members', href: '/admin/members', icon: Users },
  { name: 'Permissions', href: '/admin/permissions', icon: Shield },
]

const insightsNav = [
  { name: 'Analytics', href: '/admin/analytics', icon: BarChart3 },
  { name: 'Activity', href: '/admin/activity', icon: Activity },
]

const configNav = [
  { name: 'Settings', href: '/admin/settings', icon: Settings },
]

export function AdminSidebar() {
  const pathname = usePathname()

  const NavGroup = ({ items, label }: { items: any[], label: string }) => (
    <div className="mb-6">
      <h3 className="px-4 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">{label}</h3>
      <nav className="space-y-1 px-2">
        {items.map((item) => (
          <Link
            key={item.name}
            href={item.href}
            className={cn(
              "flex items-center px-3 py-2 text-sm font-medium rounded-md group transition-colors",
              pathname === item.href ? "bg-blue-600/10 text-blue-600" : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
            )}
          >
            <item.icon className={cn("mr-3 h-5 w-5 flex-shrink-0", pathname === item.href ? "text-blue-600" : "text-slate-400 group-hover:text-slate-600")} />
            {item.name}
          </Link>
        ))}
      </nav>
    </div>
  )

  return (
    <div className="flex flex-col w-64 bg-slate-50 border-r border-slate-200 h-screen fixed left-0 top-0">
      <div className="h-16 flex items-center px-6 text-slate-900 font-bold text-lg border-b border-slate-200 bg-white">
        KnowledgeHub AI
      </div>
      <div className="flex-1 py-6 overflow-y-auto">
        <NavGroup label="Workspace" items={workspaceNav} />
        <NavGroup label="Insights" items={insightsNav} />
        <NavGroup label="Configuration" items={configNav} />
      </div>
      <div className="p-4 border-t border-slate-200 space-y-1 bg-white">
        <Link href="#" className="flex items-center px-3 py-2 text-sm font-medium rounded-md text-slate-600 hover:bg-slate-100 hover:text-slate-900 group">
          <HelpCircle className="mr-3 h-5 w-5 text-slate-400 group-hover:text-slate-600" /> Help
        </Link>
        <Link href="#" className="flex items-center px-3 py-2 text-sm font-medium rounded-md text-red-600 hover:bg-red-50 hover:text-red-700 group">
          <LogOut className="mr-3 h-5 w-5 text-red-400 group-hover:text-red-500" /> Sign Out
        </Link>
      </div>
    </div>
  )
}
