import os

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

# ==========================================
# PUBLIC PORTAL
# ==========================================
write_file("app/(public)/layout.tsx", """
import { PublicNavbar } from '@/components/navigation/public-navbar'
import Link from 'next/link'

export default function PublicLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <PublicNavbar />
      <main className="flex-1">{children}</main>
      <footer className="bg-slate-900 py-12 text-slate-400 text-sm">
        <div className="container mx-auto px-4 grid grid-cols-2 md:grid-cols-4 gap-8">
          <div>
            <h4 className="text-white font-semibold mb-4 text-lg">KnowledgeHub AI</h4>
            <p className="mb-4">Your company's knowledge, intelligently connected.</p>
          </div>
          <div>
            <h4 className="text-white font-semibold mb-4">Product</h4>
            <ul className="space-y-2">
              <li><Link href="/features" className="hover:text-white transition-colors">Features</Link></li>
              <li><Link href="/how-it-works" className="hover:text-white transition-colors">How It Works</Link></li>
              <li><Link href="/demo" className="hover:text-white transition-colors">Demo</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="text-white font-semibold mb-4">Technology</h4>
            <ul className="space-y-2">
              <li><Link href="/architecture" className="hover:text-white transition-colors">Architecture</Link></li>
              <li><Link href="/security" className="hover:text-white transition-colors">Security</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="text-white font-semibold mb-4">Resources & Account</h4>
            <ul className="space-y-2">
              <li><Link href="#" className="hover:text-white transition-colors">GitHub</Link></li>
              <li><Link href="#" className="hover:text-white transition-colors">Documentation</Link></li>
              <li className="pt-2"><Link href="/login" className="hover:text-white transition-colors">Login</Link></li>
              <li><Link href="/register" className="hover:text-white transition-colors">Register</Link></li>
            </ul>
          </div>
        </div>
        <div className="container mx-auto px-4 mt-12 pt-8 border-t border-slate-800 text-center">
          <p>&copy; 2026 KnowledgeHub AI</p>
        </div>
      </footer>
    </div>
  )
}
""")

write_file("components/navigation/public-navbar.tsx", """
"use client"

import { useState } from 'react'
import Link from 'next/link'
import { Button } from '../ui/button'
import { BrainCircuit, Menu, X } from 'lucide-react'

export function PublicNavbar() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  return (
    <header className="border-b bg-white sticky top-0 z-50">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2 font-bold text-xl tracking-tight text-slate-900">
          <BrainCircuit className="w-6 h-6 text-blue-600" />
          KnowledgeHub AI
        </Link>
        
        {/* Desktop Nav */}
        <nav className="hidden md:flex items-center gap-6 text-sm font-medium text-slate-600">
          <Link href="/features" className="hover:text-slate-900 transition-colors">Features</Link>
          <Link href="/how-it-works" className="hover:text-slate-900 transition-colors">How It Works</Link>
          <Link href="/security" className="hover:text-slate-900 transition-colors">Security</Link>
          <Link href="/architecture" className="hover:text-slate-900 transition-colors">Architecture</Link>
          <Link href="/demo" className="hover:text-slate-900 transition-colors">Demo</Link>
        </nav>
        
        <div className="hidden md:flex items-center gap-4">
          <Link href="/login"><Button variant="ghost">Login</Button></Link>
          <Link href="/register"><Button>Get Started</Button></Link>
        </div>

        {/* Mobile Toggle */}
        <button 
          className="md:hidden p-2 text-slate-600"
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
        >
          {isMobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </button>
      </div>

      {/* Mobile Nav */}
      {isMobileMenuOpen && (
        <div className="md:hidden border-t bg-white px-4 py-4 space-y-4">
          <nav className="flex flex-col space-y-3 text-sm font-medium text-slate-600">
            <Link href="/features" onClick={() => setIsMobileMenuOpen(false)}>Features</Link>
            <Link href="/how-it-works" onClick={() => setIsMobileMenuOpen(false)}>How It Works</Link>
            <Link href="/security" onClick={() => setIsMobileMenuOpen(false)}>Security</Link>
            <Link href="/architecture" onClick={() => setIsMobileMenuOpen(false)}>Architecture</Link>
            <Link href="/demo" onClick={() => setIsMobileMenuOpen(false)}>Demo</Link>
          </nav>
          <div className="flex flex-col gap-2 pt-4 border-t">
            <Link href="/login" onClick={() => setIsMobileMenuOpen(false)}>
              <Button variant="outline" className="w-full">Login</Button>
            </Link>
            <Link href="/register" onClick={() => setIsMobileMenuOpen(false)}>
              <Button className="w-full">Get Started</Button>
            </Link>
          </div>
        </div>
      )}
    </header>
  )
}
""")

write_file("app/(public)/page.tsx", """
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { BrainCircuit, Search, Shield, FileText, Lock, CheckCircle2 } from 'lucide-react'
import Link from 'next/link'

export default function LandingPage() {
  return (
    <div className="flex flex-col">
      {/* Hero */}
      <section className="py-24 px-4 text-center mx-auto w-full max-w-6xl">
        <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight text-slate-900 mb-6">
          Your company's knowledge, <br className="hidden md:block"/>
          <span className="text-blue-600">intelligently connected.</span>
        </h1>
        <p className="text-xl text-slate-600 mb-10 max-w-2xl mx-auto">
          Turn internal documents into a secure AI knowledge assistant with grounded answers.
        </p>
        <div className="flex items-center justify-center gap-4 mb-16">
          <Link href="/register"><Button size="lg">Get Started</Button></Link>
          <Link href="/demo"><Button size="lg" variant="outline">View Demo</Button></Link>
        </div>

        {/* Hero Product Visualization */}
        <div className="max-w-4xl mx-auto bg-white rounded-2xl shadow-xl border border-slate-200 overflow-hidden text-left flex flex-col md:flex-row">
          <div className="w-full md:w-1/3 bg-slate-50 border-r p-6 hidden md:block">
            <div className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-4">Knowledge Base</div>
            <div className="space-y-3">
              <div className="h-8 bg-slate-200 rounded animate-pulse w-full"></div>
              <div className="h-8 bg-slate-200 rounded animate-pulse w-5/6"></div>
              <div className="h-8 bg-slate-200 rounded animate-pulse w-4/6"></div>
            </div>
          </div>
          <div className="flex-1 p-6 md:p-10">
            <div className="flex items-start gap-4 mb-8">
              <div className="w-8 h-8 rounded-full bg-slate-200 flex-shrink-0"></div>
              <div className="bg-slate-100 rounded-2xl rounded-tl-none px-5 py-3 text-slate-800 font-medium">
                What is our standard annual leave policy?
              </div>
            </div>
            <div className="flex items-start gap-4">
              <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center flex-shrink-0">
                <BrainCircuit className="w-5 h-5" />
              </div>
              <div className="space-y-4">
                <div className="text-slate-700 leading-relaxed">
                  Employees are entitled to 20 days of paid annual leave per year, accrued monthly. Carryover is limited to 5 days into the next calendar year.
                </div>
                <div className="border-t pt-4">
                  <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Sources</div>
                  <div className="flex gap-2">
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-blue-50 text-blue-700 text-xs font-medium border border-blue-100">
                      <FileText className="w-3 h-3" /> Employee Handbook (Page 14)
                    </span>
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-blue-50 text-blue-700 text-xs font-medium border border-blue-100">
                      <FileText className="w-3 h-3" /> Leave Policy v2.1
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-24 bg-white px-4 border-t">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-slate-900">Enterprise AI Features</h2>
            <p className="mt-4 text-slate-600">Secure, scalable, and permission-aware architecture.</p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <Card>
              <CardHeader><BrainCircuit className="w-10 h-10 text-blue-600 mb-4"/><CardTitle>AI Knowledge Assistant</CardTitle></CardHeader>
              <CardContent><p className="text-slate-600">Natural-language answers grounded in authorized company knowledge.</p></CardContent>
            </Card>
            <Card>
              <CardHeader><FileText className="w-10 h-10 text-blue-600 mb-4"/><CardTitle>Document Intelligence</CardTitle></CardHeader>
              <CardContent><p className="text-slate-600">Turn organizational documents into searchable, intelligent knowledge.</p></CardContent>
            </Card>
            <Card>
              <CardHeader><Search className="w-10 h-10 text-blue-600 mb-4"/><CardTitle>Hybrid Search</CardTitle></CardHeader>
              <CardContent><p className="text-slate-600">Semantic vector search + PostgreSQL full-text search for optimal accuracy.</p></CardContent>
            </Card>
            <Card>
              <CardHeader><CheckCircle2 className="w-10 h-10 text-blue-600 mb-4"/><CardTitle>Source Citations</CardTitle></CardHeader>
              <CardContent><p className="text-slate-600">Answers show the exact documents and chunks supporting the response.</p></CardContent>
            </Card>
            <Card>
              <CardHeader><Shield className="w-10 h-10 text-blue-600 mb-4"/><CardTitle>Multi-Tenant Security</CardTitle></CardHeader>
              <CardContent><p className="text-slate-600">Organization isolation with strict authorization and PostgreSQL RLS.</p></CardContent>
            </Card>
            <Card>
              <CardHeader><Lock className="w-10 h-10 text-blue-600 mb-4"/><CardTitle>Permission-Aware AI</CardTitle></CardHeader>
              <CardContent><p className="text-slate-600">AI retrieval respects document-level permissions and RBAC.</p></CardContent>
            </Card>
          </div>
        </div>
      </section>
    </div>
  )
}
""")

# ==========================================
# EMPLOYEE PORTAL
# ==========================================
write_file("app/(authenticated)/employee/chat/page.tsx", """
import { BrainCircuit, Send, FileText } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

export default function EmployeeChat() {
  return (
    <div className="flex-1 flex flex-col h-full relative">
      <div className="flex-1 overflow-y-auto p-8 flex flex-col items-center justify-center">
        <div className="max-w-2xl w-full text-center space-y-6">
          <div className="mx-auto w-16 h-16 bg-blue-100 text-blue-600 rounded-2xl flex items-center justify-center mb-6 shadow-sm border border-blue-200">
            <BrainCircuit className="w-8 h-8" />
          </div>
          <h1 className="text-2xl font-semibold text-slate-900">Ask questions about your organization's authorized knowledge.</h1>
          <p className="text-slate-500">Answers are grounded in company documents and include source citations.</p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-8 text-left">
            <div className="p-4 border rounded-xl hover:bg-slate-50 cursor-pointer transition-colors shadow-sm">
              <p className="text-sm font-medium text-slate-900">What is our annual leave policy?</p>
            </div>
            <div className="p-4 border rounded-xl hover:bg-slate-50 cursor-pointer transition-colors shadow-sm">
              <p className="text-sm font-medium text-slate-900">What is the reimbursement process?</p>
            </div>
            <div className="p-4 border rounded-xl hover:bg-slate-50 cursor-pointer transition-colors shadow-sm">
              <p className="text-sm font-medium text-slate-900">Where can I find the employee handbook?</p>
            </div>
            <div className="p-4 border rounded-xl hover:bg-slate-50 cursor-pointer transition-colors shadow-sm">
              <p className="text-sm font-medium text-slate-900">How do I request a new laptop?</p>
            </div>
          </div>
        </div>
      </div>
      
      <div className="p-6 bg-white border-t">
        <div className="max-w-3xl mx-auto relative">
          <Input 
            className="w-full h-14 pl-6 pr-14 text-base rounded-full shadow-sm border-slate-300 focus-visible:ring-blue-500" 
            placeholder="Ask a question..."
          />
          <Button size="sm" className="absolute right-2 top-2 h-10 w-10 rounded-full p-0 bg-blue-600 hover:bg-blue-700">
            <Send className="h-4 w-4" />
          </Button>
        </div>
        <div className="text-center mt-3">
          <span className="text-xs text-slate-400">AI can make mistakes. Always check important information against primary sources.</span>
        </div>
      </div>
    </div>
  )
}
""")

write_file("app/(authenticated)/employee/profile/page.tsx", """
import { Button } from '@/components/ui/button'

export default function EmployeeProfile() {
  return (
    <div className="flex-1 p-8 bg-slate-50 min-h-full">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold text-slate-900 mb-8">Profile & Account</h1>
        
        <div className="bg-white border rounded-xl overflow-hidden shadow-sm">
          <div className="px-6 py-4 border-b bg-slate-50/50">
            <h2 className="text-sm font-semibold text-slate-900 uppercase tracking-wider">Personal Information</h2>
          </div>
          <div className="divide-y divide-slate-100">
            <div className="px-6 py-5 flex flex-col md:flex-row md:items-center">
              <span className="text-sm font-medium text-slate-500 md:w-48 mb-1 md:mb-0">Name</span>
              <span className="text-sm font-medium text-slate-900">Chandan</span>
            </div>
            <div className="px-6 py-5 flex flex-col md:flex-row md:items-center">
              <span className="text-sm font-medium text-slate-500 md:w-48 mb-1 md:mb-0">Email</span>
              <span className="text-sm font-medium text-slate-900">employee@company.com</span>
            </div>
            <div className="px-6 py-5 flex flex-col md:flex-row md:items-center">
              <span className="text-sm font-medium text-slate-500 md:w-48 mb-1 md:mb-0">Organization</span>
              <span className="text-sm font-medium text-slate-900">Acme Corporation</span>
            </div>
            <div className="px-6 py-5 flex flex-col md:flex-row md:items-center">
              <span className="text-sm font-medium text-slate-500 md:w-48 mb-1 md:mb-0">Role</span>
              <span className="inline-flex items-center rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-semibold text-slate-800">
                MEMBER
              </span>
            </div>
          </div>
        </div>

        <div className="mt-8 bg-white border rounded-xl overflow-hidden shadow-sm">
          <div className="px-6 py-4 border-b bg-slate-50/50">
            <h2 className="text-sm font-semibold text-slate-900 uppercase tracking-wider">Account Actions</h2>
          </div>
          <div className="p-6">
            <Button variant="outline" className="text-red-600 hover:text-red-700 hover:bg-red-50 border-red-200">
              Sign Out
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
""")

# ==========================================
# ADMIN PORTAL
# ==========================================
write_file("components/navigation/admin-sidebar.tsx", """
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
""")

write_file("components/navigation/admin-topbar.tsx", """
import { Bell, Search, User, ChevronDown } from 'lucide-react'
import { Input } from '../ui/input'
import { Button } from '../ui/button'

export function AdminTopbar({ title }: { title: string }) {
  return (
    <header className="h-16 bg-white border-b flex items-center justify-between px-8 sticky top-0 z-40 ml-64">
      <h1 className="text-xl font-semibold text-slate-900">{title}</h1>
      <div className="flex items-center gap-6">
        
        {/* Organization Selector Mockup */}
        <div className="flex items-center border rounded-md px-3 py-1.5 bg-slate-50 cursor-pointer hover:bg-slate-100 transition-colors">
          <span className="text-sm font-medium text-slate-800">Acme Corporation</span>
          <ChevronDown className="ml-2 h-4 w-4 text-slate-500" />
        </div>

        <div className="flex items-center gap-2 border-l pl-6">
          <Button variant="ghost" size="sm" className="w-9 px-0 rounded-full"><Search className="h-5 w-5 text-slate-500" /></Button>
          <Button variant="ghost" size="sm" className="w-9 px-0 rounded-full"><Bell className="h-5 w-5 text-slate-500" /></Button>
          <Button variant="ghost" size="sm" className="w-9 px-0 rounded-full bg-slate-100"><User className="h-5 w-5 text-slate-600" /></Button>
        </div>
      </div>
    </header>
  )
}
""")

write_file("app/(authenticated)/admin/dashboard/page.tsx", """
import { AdminTopbar } from '@/components/navigation/admin-topbar'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { FileText, Users, Search, BrainCircuit, Activity } from 'lucide-react'

export default function AdminDashboard() {
  return (
    <div className="bg-slate-50 min-h-full">
      <AdminTopbar title="Organization Overview" />
      <main className="p-8 max-w-7xl mx-auto">
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-500">Total Documents</CardTitle>
              <FileText className="h-4 w-4 text-slate-400" />
            </CardHeader>
            <CardContent><div className="text-3xl font-bold text-slate-900">0</div></CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-500">Active Members</CardTitle>
              <Users className="h-4 w-4 text-slate-400" />
            </CardHeader>
            <CardContent><div className="text-3xl font-bold text-slate-900">1</div></CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-500">Knowledge Queries</CardTitle>
              <Search className="h-4 w-4 text-slate-400" />
            </CardHeader>
            <CardContent><div className="text-3xl font-bold text-slate-900">0</div></CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-500">AI Usage</CardTitle>
              <BrainCircuit className="h-4 w-4 text-slate-400" />
            </CardHeader>
            <CardContent><div className="text-sm font-medium text-slate-500 mt-2">No data yet</div></CardContent>
          </Card>
        </div>
        
        <div className="grid gap-6 md:grid-cols-2">
          <Card className="h-[400px]">
            <CardHeader><CardTitle>Recent Documents</CardTitle></CardHeader>
            <CardContent className="flex items-center justify-center h-64">
              <div className="text-center text-slate-500">
                <FileText className="w-8 h-8 mx-auto mb-3 opacity-20" />
                <p className="text-sm">No documents uploaded yet</p>
              </div>
            </CardContent>
          </Card>
          <Card className="h-[400px]">
            <CardHeader><CardTitle>Recent Activity</CardTitle></CardHeader>
            <CardContent>
              <div className="flex items-center gap-4 py-3">
                <div className="w-2 h-2 rounded-full bg-blue-500"></div>
                <p className="text-sm text-slate-600"><span className="font-medium text-slate-900">You</span> created the organization</p>
                <span className="ml-auto text-xs text-slate-400">Just now</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}
""")

write_file("app/(authenticated)/admin/documents/page.tsx", """
import { AdminTopbar } from '@/components/navigation/admin-topbar'
import { EmptyState } from '@/components/shared/empty-state'
import { Button } from '@/components/ui/button'
import { FileUp, Search, Filter } from 'lucide-react'
import { Input } from '@/components/ui/input'

export default function AdminDocuments() {
  return (
    <div className="bg-slate-50 min-h-full">
      <AdminTopbar title="Documents" />
      <main className="p-8 max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <div className="flex gap-4">
            <div className="relative w-72">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-400" />
              <Input type="search" placeholder="Search documents..." className="pl-9 bg-white" />
            </div>
            <Button variant="outline" className="bg-white"><Filter className="mr-2 h-4 w-4"/> Filter</Button>
          </div>
          <Button><FileUp className="mr-2 h-4 w-4" /> Upload Document</Button>
        </div>
        
        <div className="bg-white border rounded-xl overflow-hidden shadow-sm">
          {/* Table Header Placeholder */}
          <div className="grid grid-cols-12 bg-slate-50/80 p-4 border-b text-xs font-semibold text-slate-500 uppercase tracking-wider">
            <div className="col-span-4">Name</div>
            <div className="col-span-1">Type</div>
            <div className="col-span-1">Size</div>
            <div className="col-span-2">Status</div>
            <div className="col-span-2">Visibility</div>
            <div className="col-span-2 text-right">Updated</div>
          </div>
          <div className="p-16">
            <EmptyState 
              icon={FileUp} 
              title="Your knowledge base is empty" 
              description="Upload company documents such as policies, handbooks, manuals, and internal documentation." 
              actionLabel="Upload Document" 
            />
          </div>
        </div>
      </main>
    </div>
  )
}
""")

write_file("app/(authenticated)/admin/settings/page.tsx", """
import { AdminTopbar } from '@/components/navigation/admin-topbar'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

export default function AdminSettings() {
  return (
    <div className="bg-slate-50 min-h-full">
      <AdminTopbar title="Settings" />
      <main className="p-8 max-w-4xl mx-auto space-y-8">
        
        <Card>
          <div className="px-6 py-4 border-b bg-slate-50/50">
            <h2 className="text-sm font-semibold text-slate-900 uppercase tracking-wider">General</h2>
          </div>
          <CardContent className="space-y-4 pt-6">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Organization Name</label>
              <Input defaultValue="Acme Corp" className="max-w-md" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Organization Logo</label>
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 rounded bg-slate-100 border border-dashed flex items-center justify-center text-xs text-slate-400">Logo</div>
                <Button variant="outline" size="sm">Upload new</Button>
              </div>
            </div>
            <Button>Save General Settings</Button>
          </CardContent>
        </Card>

        <Card>
          <div className="px-6 py-4 border-b bg-slate-50/50">
            <h2 className="text-sm font-semibold text-slate-900 uppercase tracking-wider">Security</h2>
          </div>
          <CardContent className="space-y-4 pt-6">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Domain Restrictions</label>
              <Input placeholder="e.g. acme.com" className="max-w-md" />
              <p className="text-xs text-slate-500 mt-1">Only users with these email domains can join the organization.</p>
            </div>
            <Button variant="outline">Save Security Settings</Button>
          </CardContent>
        </Card>

        <Card>
          <div className="px-6 py-4 border-b bg-slate-50/50">
            <h2 className="text-sm font-semibold text-slate-900 uppercase tracking-wider">Knowledge Base</h2>
          </div>
          <CardContent className="space-y-4 pt-6">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Default Document Access</label>
              <select className="flex h-10 w-full max-w-md rounded-md border border-slate-300 bg-white px-3 py-2 text-sm">
                <option>All Organization Members</option>
                <option>Private (Only Uploader & Admins)</option>
              </select>
            </div>
            <Button variant="outline">Save Knowledge Settings</Button>
          </CardContent>
        </Card>

        <Card className="border-red-200">
          <div className="px-6 py-4 border-b border-red-100 bg-red-50/50">
            <h2 className="text-sm font-semibold text-red-800 uppercase tracking-wider">Danger Zone</h2>
          </div>
          <CardContent className="space-y-4 pt-6">
            <p className="text-sm text-slate-600">Irreversible actions regarding your organization data.</p>
            <Button variant="danger">Delete Organization</Button>
          </CardContent>
        </Card>

      </main>
    </div>
  )
}
""")

write_file("app/(authenticated)/admin/activity/page.tsx", """
import { AdminTopbar } from '@/components/navigation/admin-topbar'
import { Card, CardContent } from '@/components/ui/card'

export default function AdminActivity() {
  return (
    <div className="bg-slate-50 min-h-full">
      <AdminTopbar title="Activity Log" />
      <main className="p-8 max-w-5xl mx-auto">
        <Card className="overflow-hidden">
          <CardContent className="p-0">
            <div className="divide-y divide-slate-100 text-sm">
              <div className="p-4 hover:bg-slate-50 transition-colors">
                <div className="flex justify-between items-start">
                  <div className="flex gap-3 items-start">
                    <div className="w-2 h-2 rounded-full bg-blue-500 mt-1.5"></div>
                    <div>
                      <p><span className="font-medium text-slate-900">Chandan</span> uploaded <span className="font-medium text-slate-700">Employee Handbook.pdf</span></p>
                      <p className="text-xs text-slate-500 mt-0.5">Knowledge Base</p>
                    </div>
                  </div>
                  <span className="text-slate-400 text-xs">2 mins ago</span>
                </div>
              </div>
              <div className="p-4 hover:bg-slate-50 transition-colors">
                <div className="flex justify-between items-start">
                  <div className="flex gap-3 items-start">
                    <div className="w-2 h-2 rounded-full bg-slate-300 mt-1.5"></div>
                    <div>
                      <p><span className="font-medium text-slate-900">Admin</span> changed document permissions for <span className="font-medium text-slate-700">Q3 Financials.pdf</span></p>
                      <p className="text-xs text-slate-500 mt-0.5">Permissions</p>
                    </div>
                  </div>
                  <span className="text-slate-400 text-xs">18 mins ago</span>
                </div>
              </div>
              <div className="p-4 hover:bg-slate-50 transition-colors">
                <div className="flex justify-between items-start">
                  <div className="flex gap-3 items-start">
                    <div className="w-2 h-2 rounded-full bg-green-500 mt-1.5"></div>
                    <div>
                      <p><span className="font-medium text-slate-900">New member</span> joined organization</p>
                      <p className="text-xs text-slate-500 mt-0.5">Members</p>
                    </div>
                  </div>
                  <span className="text-slate-400 text-xs">1 hour ago</span>
                </div>
              </div>
              <div className="p-4 hover:bg-slate-50 transition-colors">
                <div className="flex justify-between items-start">
                  <div className="flex gap-3 items-start">
                    <div className="w-2 h-2 rounded-full bg-red-400 mt-1.5"></div>
                    <div>
                      <p><span className="font-medium text-slate-900">Document deleted</span></p>
                      <p className="text-xs text-slate-500 mt-0.5">System</p>
                    </div>
                  </div>
                  <span className="text-slate-400 text-xs">Yesterday</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  )
}
""")

write_file("app/(authenticated)/admin/permissions/page.tsx", """
import { AdminTopbar } from '@/components/navigation/admin-topbar'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Shield, FileText, Users, User, Plus } from 'lucide-react'
import { Button } from '@/components/ui/button'

export default function AdminPermissions() {
  return (
    <div className="bg-slate-50 min-h-full">
      <AdminTopbar title="Document Access & Permissions" />
      <main className="p-8 max-w-5xl mx-auto space-y-6">
        <p className="text-sm text-slate-600">Permissions are strictly enforced at the database level during vector retrieval.</p>
        
        <Card className="border-blue-100 shadow-sm">
          <CardHeader className="bg-blue-50/50 border-b border-blue-100 pb-4">
            <CardTitle className="flex items-center text-lg"><FileText className="mr-2 h-5 w-5 text-blue-600"/> Employee Handbook.pdf</CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            <h3 className="text-sm font-semibold text-slate-900 mb-4 uppercase tracking-wider">Access Control</h3>
            
            <div className="space-y-4">
              <label className="flex items-start gap-3 p-4 border rounded-lg cursor-pointer hover:bg-slate-50 transition-colors">
                <input type="checkbox" defaultChecked className="mt-1 h-4 w-4 text-blue-600 rounded border-slate-300" />
                <div>
                  <div className="flex items-center font-medium text-slate-900"><Users className="w-4 h-4 mr-2 text-slate-500"/> All Organization Members</div>
                  <p className="text-sm text-slate-500 mt-1">Anyone in the organization can search and retrieve this document.</p>
                </div>
              </label>

              <div className="border rounded-lg overflow-hidden">
                <div className="p-4 bg-slate-50 border-b flex justify-between items-center">
                  <div className="font-medium text-slate-900 text-sm">Restrict to Specific Roles</div>
                </div>
                <div className="p-4 space-y-3">
                  <label className="flex items-center gap-3 cursor-pointer">
                    <input type="checkbox" defaultChecked className="h-4 w-4 text-blue-600 rounded border-slate-300" />
                    <span className="text-sm font-medium text-slate-700">KNOWLEDGE_MANAGER</span>
                  </label>
                  <label className="flex items-center gap-3 cursor-pointer">
                    <input type="checkbox" defaultChecked className="h-4 w-4 text-blue-600 rounded border-slate-300" />
                    <span className="text-sm font-medium text-slate-700">MEMBER</span>
                  </label>
                </div>
              </div>

              <div className="border rounded-lg overflow-hidden">
                <div className="p-4 bg-slate-50 border-b flex justify-between items-center">
                  <div className="font-medium text-slate-900 text-sm">Specific Users</div>
                  <Button variant="outline" size="sm"><Plus className="w-4 h-4 mr-1"/> Add User</Button>
                </div>
                <div className="p-4 text-sm text-slate-500">
                  No individual users have been granted specific exceptions.
                </div>
              </div>

            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  )
}
""")

print("Refinement script applied!")
