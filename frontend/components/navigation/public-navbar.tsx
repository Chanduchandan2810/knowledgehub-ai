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
