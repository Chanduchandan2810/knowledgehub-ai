"use client"
import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Button } from '../ui/button'
import { BrainCircuit, Menu, X } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

export function PublicNavbar() {
  const [scrolled, setScrolled] = useState(false)
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <header className={`fixed top-0 w-full z-50 transition-all duration-300 ${scrolled ? 'bg-white/80 backdrop-blur-md border-b border-slate-200 shadow-sm' : 'bg-transparent'}`}>
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2 font-bold text-xl tracking-tight text-slate-900 group">
          <div className="bg-primary-600 text-white p-1.5 rounded-lg group-hover:bg-primary-700 transition-colors">
            <BrainCircuit className="w-5 h-5" />
          </div>
          KnowledgeHub AI
        </Link>
        
        {/* Desktop Nav */}
        <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-600">
          <Link href="#" className="hover:text-primary-600 transition-colors">Platform</Link>
          <Link href="#" className="hover:text-primary-600 transition-colors">Security</Link>
          <Link href="#" className="hover:text-primary-600 transition-colors">Architecture</Link>
        </nav>
        
        <div className="hidden md:flex items-center gap-4">
          <Link href="/login"><Button variant="ghost" className="font-semibold">Login</Button></Link>
          <Link href="/register"><Button className="font-semibold">Start Free Trial</Button></Link>
        </div>

        {/* Mobile Toggle */}
        <button className="md:hidden p-2 text-slate-600" onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}>
          {isMobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </button>
      </div>

      {/* Mobile Nav */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div 
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden border-t bg-white px-4 py-6 shadow-xl"
          >
            <nav className="flex flex-col space-y-4 text-base font-medium text-slate-600 mb-6">
              <Link href="#" onClick={() => setIsMobileMenuOpen(false)}>Platform</Link>
              <Link href="#" onClick={() => setIsMobileMenuOpen(false)}>Security</Link>
              <Link href="#" onClick={() => setIsMobileMenuOpen(false)}>Architecture</Link>
            </nav>
            <div className="flex flex-col gap-3">
              <Link href="/login" onClick={() => setIsMobileMenuOpen(false)}><Button variant="outline" className="w-full">Login</Button></Link>
              <Link href="/register" onClick={() => setIsMobileMenuOpen(false)}><Button className="w-full">Start Free Trial</Button></Link>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  )
}
