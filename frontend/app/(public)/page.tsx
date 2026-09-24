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
