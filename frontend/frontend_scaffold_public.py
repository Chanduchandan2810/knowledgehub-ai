import os

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

# Public Routes
create_file("app/(public)/layout.tsx", """
import { PublicNavbar } from '@/components/navigation/public-navbar'

export default function PublicLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <PublicNavbar />
      <main className="flex-1">{children}</main>
      <footer className="bg-slate-900 py-12 text-slate-400 text-sm">
        <div className="container mx-auto px-4 grid grid-cols-2 md:grid-cols-4 gap-8">
          <div><h4 className="text-white font-semibold mb-4">Product</h4><ul className="space-y-2"><li>Features</li><li>Security</li></ul></div>
          <div><h4 className="text-white font-semibold mb-4">Resources</h4><ul className="space-y-2"><li>Documentation</li><li>API</li></ul></div>
          <div><h4 className="text-white font-semibold mb-4">Company</h4><ul className="space-y-2"><li>About</li><li>Blog</li></ul></div>
          <div><h4 className="text-white font-semibold mb-4">Legal</h4><ul className="space-y-2"><li>Privacy</li><li>Terms</li></ul></div>
        </div>
      </footer>
    </div>
  )
}
""")

create_file("app/(public)/page.tsx", """
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { BrainCircuit, Search, Shield, Database } from 'lucide-react'
import Link from 'next/link'

export default function LandingPage() {
  return (
    <div className="flex flex-col">
      {/* Hero */}
      <section className="py-24 px-4 text-center max-w-4xl mx-auto">
        <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight text-slate-900 mb-6">
          Your company's knowledge, <span className="text-blue-600">intelligently connected.</span>
        </h1>
        <p className="text-xl text-slate-600 mb-10 max-w-2xl mx-auto">
          Turn internal documents and organizational knowledge into an AI-powered knowledge assistant that provides grounded answers with source citations.
        </p>
        <div className="flex items-center justify-center gap-4">
          <Link href="/register"><Button size="lg">Get Started</Button></Link>
          <Link href="/demo"><Button size="lg" variant="outline">View Demo</Button></Link>
        </div>
      </section>

      {/* Features */}
      <section className="py-24 bg-white px-4 border-t">
        <div className="container mx-auto max-w-5xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-slate-900">Enterprise AI Features</h2>
            <p className="mt-4 text-slate-600">Secure, scalable, and permission-aware architecture.</p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <Card>
              <CardHeader><BrainCircuit className="w-10 h-10 text-blue-600 mb-4"/><CardTitle>AI Knowledge Assistant</CardTitle></CardHeader>
              <CardContent><p className="text-slate-600">Natural language answers grounded securely in your company's proprietary data.</p></CardContent>
            </Card>
            <Card>
              <CardHeader><Search className="w-10 h-10 text-blue-600 mb-4"/><CardTitle>Hybrid Search</CardTitle></CardHeader>
              <CardContent><p className="text-slate-600">Combines semantic vector search with keyword matching for unparalleled accuracy.</p></CardContent>
            </Card>
            <Card>
              <CardHeader><Shield className="w-10 h-10 text-blue-600 mb-4"/><CardTitle>Multi-Tenant Security</CardTitle></CardHeader>
              <CardContent><p className="text-slate-600">PostgreSQL RLS and strict tenant isolation ensures data never crosses boundaries.</p></CardContent>
            </Card>
          </div>
        </div>
      </section>
    </div>
  )
}
""")

create_file("app/(public)/login/page.tsx", """
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import Link from 'next/link'

export default function LoginPage() {
  return (
    <div className="flex items-center justify-center min-h-[calc(100vh-16rem)] py-12 px-4 sm:px-6 lg:px-8">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold">Sign in to your account</CardTitle>
          <p className="text-sm text-slate-500 mt-2">Enter your email and password to access your workspace.</p>
        </CardHeader>
        <CardContent>
          <form className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Email address</label>
              <Input type="email" placeholder="name@company.com" required />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Password</label>
              <Input type="password" required />
            </div>
            <Button className="w-full" type="button">Sign In</Button>
          </form>
          <div className="mt-6 text-center text-sm">
            <span className="text-slate-500">Don't have an account? </span>
            <Link href="/register" className="font-medium text-blue-600 hover:text-blue-500">Register</Link>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
""")

create_file("app/(public)/register/page.tsx", """
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import Link from 'next/link'

export default function RegisterPage() {
  return (
    <div className="flex items-center justify-center min-h-[calc(100vh-16rem)] py-12 px-4 sm:px-6 lg:px-8">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold">Create your account</CardTitle>
          <p className="text-sm text-slate-500 mt-2">Start building your secure enterprise knowledge base.</p>
        </CardHeader>
        <CardContent>
          <form className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Full Name</label>
              <Input type="text" placeholder="John Doe" required />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Email address</label>
              <Input type="email" placeholder="name@company.com" required />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Password</label>
              <Input type="password" required />
            </div>
            <Button className="w-full" type="button">Create Account</Button>
          </form>
          <div className="mt-6 text-center text-sm">
            <span className="text-slate-500">Already have an account? </span>
            <Link href="/login" className="font-medium text-blue-600 hover:text-blue-500">Sign in</Link>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
""")
