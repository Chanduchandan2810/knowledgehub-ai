import os

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

# Utility Components
create_file("components/ui/button.tsx", """
import * as React from "react"
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "outline" | "ghost" | "link" | "danger"
  size?: "default" | "sm" | "lg"
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "default", size = "default", ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(
          "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none disabled:pointer-events-none disabled:opacity-50",
          {
            "bg-blue-600 text-white hover:bg-blue-700": variant === "default",
            "border border-slate-200 bg-white hover:bg-slate-100 text-slate-900": variant === "outline",
            "hover:bg-slate-100 text-slate-900": variant === "ghost",
            "text-blue-600 underline-offset-4 hover:underline": variant === "link",
            "bg-red-600 text-white hover:bg-red-700": variant === "danger",
            "h-10 px-4 py-2": size === "default",
            "h-9 rounded-md px-3": size === "sm",
            "h-11 rounded-md px-8": size === "lg",
          },
          className
        )}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"
""")

create_file("components/ui/card.tsx", """
import * as React from "react"
import { cn } from "./button"

export function Card({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("rounded-lg border bg-card text-card-foreground shadow-sm bg-white", className)} {...props} />
}
export function CardHeader({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("flex flex-col space-y-1.5 p-6", className)} {...props} />
}
export function CardTitle({ className, ...props }: React.HTMLAttributes<HTMLHeadingElement>) {
  return <h3 className={cn("text-lg font-semibold leading-none tracking-tight text-slate-900", className)} {...props} />
}
export function CardContent({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("p-6 pt-0", className)} {...props} />
}
""")

create_file("components/ui/input.tsx", """
import * as React from "react"
import { cn } from "./button"

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          "flex h-10 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent disabled:cursor-not-allowed disabled:opacity-50",
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Input.displayName = "Input"
""")

create_file("components/ui/badge.tsx", """
import * as React from "react"
import { cn } from "./button"

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "secondary" | "destructive" | "outline"
}

export function Badge({ className, variant = "default", ...props }: BadgeProps) {
  return (
    <div
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
        {
          "border-transparent bg-blue-100 text-blue-800 hover:bg-blue-200": variant === "default",
          "border-transparent bg-slate-100 text-slate-900 hover:bg-slate-200": variant === "secondary",
          "border-transparent bg-red-100 text-red-800 hover:bg-red-200": variant === "destructive",
          "text-slate-900": variant === "outline",
        },
        className
      )}
      {...props}
    />
  )
}
""")

create_file("components/shared/empty-state.tsx", """
import { LucideIcon } from "lucide-react"
import { Button } from "../ui/button"

export function EmptyState({ icon: Icon, title, description, actionLabel }: { icon: LucideIcon, title: string, description: string, actionLabel?: string }) {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center border rounded-lg bg-slate-50 border-dashed">
      <div className="flex items-center justify-center w-12 h-12 rounded-full bg-slate-100 mb-4">
        <Icon className="w-6 h-6 text-slate-500" />
      </div>
      <h3 className="text-lg font-medium text-slate-900">{title}</h3>
      <p className="mt-1 text-sm text-slate-500 max-w-sm">{description}</p>
      {actionLabel && (
        <div className="mt-6">
          <Button>{actionLabel}</Button>
        </div>
      )}
    </div>
  )
}
""")

# Public Navbar
create_file("components/navigation/public-navbar.tsx", """
import Link from 'next/link'
import { Button } from '../ui/button'
import { BrainCircuit } from 'lucide-react'

export function PublicNavbar() {
  return (
    <header className="border-b bg-white sticky top-0 z-50">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2 font-bold text-xl tracking-tight text-slate-900">
          <BrainCircuit className="w-6 h-6 text-blue-600" />
          KnowledgeHub AI
        </Link>
        <nav className="hidden md:flex items-center gap-6 text-sm font-medium text-slate-600">
          <Link href="/features" className="hover:text-slate-900 transition-colors">Features</Link>
          <Link href="/how-it-works" className="hover:text-slate-900 transition-colors">How It Works</Link>
          <Link href="/security" className="hover:text-slate-900 transition-colors">Security</Link>
          <Link href="/architecture" className="hover:text-slate-900 transition-colors">Architecture</Link>
          <Link href="/demo" className="hover:text-slate-900 transition-colors">Demo</Link>
        </nav>
        <div className="flex items-center gap-4">
          <Link href="/login">
            <Button variant="ghost">Login</Button>
          </Link>
          <Link href="/register">
            <Button>Get Started</Button>
          </Link>
        </div>
      </div>
    </header>
  )
}
""")

# Admin Sidebar
create_file("components/navigation/admin-sidebar.tsx", """
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { LayoutDashboard, FileText, Users, Shield, BarChart3, Activity, Settings, HelpCircle, LogOut } from 'lucide-react'
import { cn } from '../ui/button'

const navItems = [
  { name: 'Overview', href: '/admin/dashboard', icon: LayoutDashboard },
  { name: 'Documents', href: '/admin/documents', icon: FileText },
  { name: 'Members', href: '/admin/members', icon: Users },
  { name: 'Permissions', href: '/admin/permissions', icon: Shield },
  { name: 'Analytics', href: '/admin/analytics', icon: BarChart3 },
  { name: 'Activity', href: '/admin/activity', icon: Activity },
  { name: 'Settings', href: '/admin/settings', icon: Settings },
]

export function AdminSidebar() {
  const pathname = usePathname()

  return (
    <div className="flex flex-col w-64 bg-slate-900 text-slate-300 h-screen fixed left-0 top-0">
      <div className="h-16 flex items-center px-6 text-white font-bold text-lg border-b border-slate-800">
        KnowledgeHub AI
      </div>
      <div className="flex-1 py-6 overflow-y-auto">
        <nav className="space-y-1 px-3">
          {navItems.map((item) => (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center px-3 py-2 text-sm font-medium rounded-md group transition-colors",
                pathname === item.href ? "bg-slate-800 text-white" : "hover:bg-slate-800 hover:text-white"
              )}
            >
              <item.icon className={cn("mr-3 h-5 w-5 flex-shrink-0", pathname === item.href ? "text-blue-500" : "text-slate-400 group-hover:text-blue-500")} />
              {item.name}
            </Link>
          ))}
        </nav>
      </div>
      <div className="p-4 border-t border-slate-800 space-y-1">
        <Link href="#" className="flex items-center px-3 py-2 text-sm font-medium rounded-md hover:bg-slate-800 hover:text-white group">
          <HelpCircle className="mr-3 h-5 w-5 text-slate-400 group-hover:text-slate-300" /> Help
        </Link>
        <Link href="#" className="flex items-center px-3 py-2 text-sm font-medium rounded-md hover:bg-slate-800 hover:text-white group text-red-400">
          <LogOut className="mr-3 h-5 w-5 text-red-400" /> Sign Out
        </Link>
      </div>
    </div>
  )
}
""")

# Admin Topbar
create_file("components/navigation/admin-topbar.tsx", """
import { Bell, Search, User } from 'lucide-react'
import { Input } from '../ui/input'
import { Button } from '../ui/button'

export function AdminTopbar({ title }: { title: string }) {
  return (
    <header className="h-16 bg-white border-b flex items-center justify-between px-8 sticky top-0 z-40 ml-64">
      <h1 className="text-xl font-semibold text-slate-900">{title}</h1>
      <div className="flex items-center gap-6">
        <div className="relative w-64">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-400" />
          <Input type="search" placeholder="Search organization..." className="pl-9 h-9 bg-slate-50" />
        </div>
        <div className="flex items-center gap-2 border-l pl-6">
          <Button variant="ghost" size="sm" className="w-9 px-0 rounded-full"><Bell className="h-5 w-5 text-slate-500" /></Button>
          <Button variant="ghost" size="sm" className="w-9 px-0 rounded-full bg-slate-100"><User className="h-5 w-5 text-slate-600" /></Button>
        </div>
      </div>
    </header>
  )
}
""")

# Employee Sidebar
create_file("components/navigation/employee-sidebar.tsx", """
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { MessageSquare, Clock, User, Plus } from 'lucide-react'
import { Button, cn } from '../ui/button'

const recentChats = [
  "Annual leave policy",
  "Travel reimbursement",
  "Security policy",
  "Employee onboarding"
]

export function EmployeeSidebar() {
  const pathname = usePathname()

  return (
    <div className="flex flex-col w-72 bg-slate-50 h-screen fixed left-0 top-0 border-r">
      <div className="p-4 border-b">
        <Link href="/employee/chat">
          <Button className="w-full justify-start shadow-sm" variant="outline">
            <Plus className="mr-2 h-4 w-4" /> New Chat
          </Button>
        </Link>
      </div>
      <div className="flex-1 overflow-y-auto py-4">
        <div className="px-3">
          <h3 className="px-4 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Recent</h3>
          <nav className="space-y-1">
            {recentChats.map((chat) => (
              <Link key={chat} href="/employee/conversations" className="flex items-center px-4 py-2 text-sm text-slate-700 rounded-md hover:bg-slate-200 truncate">
                <MessageSquare className="mr-3 h-4 w-4 text-slate-400 shrink-0" />
                <span className="truncate">{chat}</span>
              </Link>
            ))}
          </nav>
        </div>
      </div>
      <div className="p-4 border-t">
        <nav className="space-y-1">
          <Link href="/employee/profile" className={cn("flex items-center px-4 py-2 text-sm font-medium rounded-md", pathname === '/employee/profile' ? "bg-slate-200 text-slate-900" : "text-slate-700 hover:bg-slate-200")}>
            <User className="mr-3 h-4 w-4 text-slate-500" /> Profile & Settings
          </Link>
        </nav>
      </div>
    </div>
  )
}
""")

print("Components scaffolded successfully.")
