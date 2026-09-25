"use client"
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { LayoutDashboard, FileText, Users, Shield, BarChart3, Activity, Settings, BrainCircuit } from 'lucide-react'
import { cn } from '../ui/button'

const workspaceNav = [
  { name: 'Dashboard', href: '/admin/dashboard', icon: LayoutDashboard },
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

  return (
    <aside className="hidden md:flex flex-col w-[260px] flex-shrink-0 border-r border-slate-200/80 bg-white z-20">
      <div className="h-16 flex items-center px-6 border-b border-slate-100">
        <Link href="/" className="flex items-center gap-2.5 font-bold text-lg tracking-tight text-slate-900 group">
          <div className="bg-primary-600 text-white p-1 rounded-md shadow-sm group-hover:bg-primary-700 transition-colors">
            <BrainCircuit className="w-4 h-4" />
          </div>
          KnowledgeHub
        </Link>
      </div>
      
      <div className="flex-1 py-6 overflow-y-auto custom-scrollbar">
        <NavGroup label="Workspace" items={workspaceNav} />
        <NavGroup label="Insights" items={insightsNav} />
        <NavGroup label="Configuration" items={configNav} />
      </div>
      
      <div className="p-4 border-t border-slate-100 bg-slate-50/50">
        <div className="flex items-center px-3 py-2 text-sm rounded-md border border-slate-200 bg-white shadow-sm cursor-pointer hover:bg-slate-50 transition-colors">
          <div className="w-7 h-7 rounded bg-primary-100 text-primary-700 flex items-center justify-center font-bold text-xs mr-3">A</div>
          <div className="flex-1 truncate">
            <p className="font-semibold text-slate-900 truncate text-xs">Acme Corp</p>
            <p className="text-[10px] text-slate-500 truncate">Enterprise Plan</p>
          </div>
        </div>
      </div>
    </aside>
  )
}
