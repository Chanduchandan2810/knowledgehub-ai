"use client"
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { BrainCircuit, Search, Shield, FileText, Lock, CheckCircle2, ChevronRight, Zap, Database } from 'lucide-react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { PageTransition } from '@/components/shared/page-transition'

const staggerContainer = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
}
const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 }
}

export default function LandingPage() {
  return (
    <PageTransition className="flex flex-col overflow-hidden">
      
      {/* Dynamic Background */}
      <div className="absolute inset-0 -z-10 bg-[linear-gradient(to_right,#8080800a_1px,transparent_1px),linear-gradient(to_bottom,#8080800a_1px,transparent_1px)] bg-[size:14px_24px]">
        <div className="absolute left-0 right-0 top-0 -z-10 m-auto h-[310px] w-[310px] rounded-full bg-primary-400 opacity-20 blur-[100px]"></div>
      </div>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 px-4 text-center mx-auto w-full max-w-7xl">
        <motion.div initial="hidden" animate="show" variants={staggerContainer} className="max-w-4xl mx-auto">
          <motion.div variants={fadeUp} className="inline-flex items-center rounded-full border border-primary-200 bg-primary-50 px-3 py-1 text-sm text-primary-600 mb-8 font-medium">
            <span className="flex h-2 w-2 rounded-full bg-primary-600 mr-2 animate-pulse"></span>
            Enterprise AI Knowledge Platform
          </motion.div>
          <motion.h1 variants={fadeUp} className="text-5xl md:text-7xl font-extrabold tracking-tight text-slate-900 mb-8 leading-[1.1]">
            Your organization's knowledge, <br className="hidden md:block"/>
            <span className="text-gradient">intelligently connected.</span>
          </motion.h1>
          <motion.p variants={fadeUp} className="text-xl text-slate-600 mb-10 max-w-2xl mx-auto leading-relaxed">
            Turn internal documents into a secure AI knowledge assistant with grounded answers, explicit citations, and enterprise-grade permissions.
          </motion.p>
          <motion.div variants={fadeUp} className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-20">
            <Link href="/register"><Button size="lg" className="w-full sm:w-auto group">Get Started <ChevronRight className="ml-2 w-4 h-4 group-hover:translate-x-1 transition-transform" /></Button></Link>
            <Link href="/demo"><Button size="lg" variant="outline" className="w-full sm:w-auto bg-white/50 backdrop-blur-sm">View Platform Demo</Button></Link>
          </motion.div>
        </motion.div>

        {/* Hero Product Visualization */}
        <motion.div 
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.8, type: "spring", stiffness: 200, damping: 30 }}
          className="max-w-5xl mx-auto glass-card rounded-2xl overflow-hidden text-left flex flex-col md:flex-row relative z-10"
        >
          {/* Sidebar Mockup */}
          <div className="w-full md:w-64 bg-slate-50/80 border-r border-slate-200/50 p-6 hidden md:flex flex-col backdrop-blur-md">
            <div className="flex items-center gap-2 font-bold text-slate-900 mb-8"><BrainCircuit className="w-5 h-5 text-primary-600"/> Workspace</div>
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">Knowledge Base</div>
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-sm text-slate-700 bg-white p-2 rounded-md shadow-sm border border-slate-100"><FileText className="w-4 h-4 text-primary-500"/> Employee_Handbook.pdf</div>
              <div className="flex items-center gap-2 text-sm text-slate-600 p-2"><FileText className="w-4 h-4 text-slate-400"/> Q3_Financials_v2.pdf</div>
              <div className="flex items-center gap-2 text-sm text-slate-600 p-2"><FileText className="w-4 h-4 text-slate-400"/> Security_Policy.pdf</div>
            </div>
          </div>
          {/* Main Chat Mockup */}
          <div className="flex-1 p-6 md:p-10 bg-white/60 backdrop-blur-md">
            <div className="flex items-start gap-4 mb-8">
              <div className="w-8 h-8 rounded-full bg-slate-900 flex items-center justify-center flex-shrink-0 text-white text-xs font-bold">You</div>
              <div className="bg-slate-100/80 rounded-2xl rounded-tl-none px-5 py-3 text-slate-800 font-medium border border-slate-200/50 shadow-sm">
                What is our standard annual leave policy and how much carries over?
              </div>
            </div>
            
            <div className="flex items-start gap-4">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-primary-700 text-white flex items-center justify-center flex-shrink-0 shadow-md">
                <BrainCircuit className="w-4 h-4" />
              </div>
              <div className="space-y-4 w-full">
                <div className="text-slate-700 leading-relaxed bg-white rounded-2xl rounded-tl-none px-5 py-4 border border-slate-100 shadow-sm">
                  Employees are entitled to <strong>20 days of paid annual leave</strong> per year, accrued monthly. Carryover is limited to <strong>5 days</strong> into the next calendar year, which must be used by March 31st.
                </div>
                
                {/* Citations block */}
                <div className="pt-2">
                  <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1">
                    <Database className="w-3 h-3" /> Grounded in authorized sources
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-white border border-slate-200 shadow-sm text-xs font-medium text-slate-700 hover:border-primary-300 transition-colors cursor-pointer">
                      <FileText className="w-3.5 h-3.5 text-primary-500" /> Employee Handbook <span className="text-slate-400">Page 14</span>
                    </div>
                    <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-white border border-slate-200 shadow-sm text-xs font-medium text-slate-700 hover:border-primary-300 transition-colors cursor-pointer">
                      <FileText className="w-3.5 h-3.5 text-primary-500" /> HR Leave Policy v2 <span className="text-slate-400">Sec 3.2</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </section>

      {/* RAG Workflow Visualization */}
      <section className="py-24 bg-navy-900 text-white relative overflow-hidden">
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 brightness-100 contrast-150"></div>
        <div className="container mx-auto px-4 max-w-6xl relative z-10">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold mb-4">Enterprise AI Workflow</h2>
            <p className="text-slate-400 max-w-2xl mx-auto">Retrieval-Augmented Generation strictly governed by PostgreSQL Row-Level Security.</p>
          </div>
          
          <div className="flex flex-col md:flex-row items-center justify-between gap-4 md:gap-8">
            <div className="flex-1 bg-navy-800 p-6 rounded-xl border border-navy-700 text-center w-full">
              <Shield className="w-8 h-8 text-blue-400 mx-auto mb-3" />
              <h3 className="font-semibold text-white mb-2">1. Identity Auth</h3>
              <p className="text-sm text-slate-400">Verifies organization & RBAC role.</p>
            </div>
            <ChevronRight className="w-6 h-6 text-slate-600 hidden md:block" />
            <div className="flex-1 bg-navy-800 p-6 rounded-xl border border-navy-700 text-center w-full">
              <Database className="w-8 h-8 text-blue-400 mx-auto mb-3" />
              <h3 className="font-semibold text-white mb-2">2. Secure Retrieval</h3>
              <p className="text-sm text-slate-400">Vector search filtered by RLS policies.</p>
            </div>
            <ChevronRight className="w-6 h-6 text-slate-600 hidden md:block" />
            <div className="flex-1 bg-navy-800 p-6 rounded-xl border border-navy-700 text-center w-full">
              <Zap className="w-8 h-8 text-blue-400 mx-auto mb-3" />
              <h3 className="font-semibold text-white mb-2">3. LLM Generation</h3>
              <p className="text-sm text-slate-400">Synthesizes answer with exact citations.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-24 bg-slate-50 px-4">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-slate-900">Platform Capabilities</h2>
            <p className="mt-4 text-slate-600 max-w-2xl mx-auto">Built from the ground up for security, scale, and accuracy.</p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              { icon: BrainCircuit, title: "AI Knowledge Assistant", desc: "Natural-language answers grounded exclusively in authorized company knowledge." },
              { icon: FileText, title: "Document Intelligence", desc: "Turn raw organizational PDFs and text into searchable, structured knowledge graphs." },
              { icon: Search, title: "Hybrid Search", desc: "Combines semantic vector embeddings with PostgreSQL full-text search for optimal accuracy." },
              { icon: CheckCircle2, title: "Source Citations", desc: "Every generated answer shows the exact documents and chunks supporting the response." },
              { icon: Shield, title: "Multi-Tenant Security", desc: "Strict organization isolation using advanced PostgreSQL Row-Level Security (RLS)." },
              { icon: Lock, title: "Permission-Aware AI", desc: "AI retrieval respects document-level permissions and granular user roles." }
            ].map((f, i) => (
              <motion.div 
                key={i}
                whileHover={{ y: -5 }}
                transition={{ type: "spring", stiffness: 300 }}
              >
                <Card className="h-full border-slate-200 bg-white">
                  <CardHeader>
                    <div className="w-12 h-12 bg-primary-50 rounded-lg flex items-center justify-center mb-4 text-primary-600">
                      <f.icon className="w-6 h-6" />
                    </div>
                    <CardTitle className="text-xl">{f.title}</CardTitle>
                  </CardHeader>
                  <CardContent><p className="text-slate-600 leading-relaxed">{f.desc}</p></CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>
    </PageTransition>
  )
}
