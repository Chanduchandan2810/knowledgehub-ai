"use client"
import { Bell, Search, Menu, HelpCircle } from 'lucide-react'
import { Input } from '../ui/input'
import { Button } from '../ui/button'

export function AdminTopbar({ title, description }: { title: string, description?: string }) {
  return (
    <header className="h-16 flex-shrink-0 bg-white/80 backdrop-blur-md border-b border-slate-200/60 flex items-center justify-between px-4 sm:px-6 z-10">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" className="md:hidden text-slate-500">
          <Menu className="h-5 w-5" />
        </Button>
        <div>
          <h1 className="text-lg font-semibold text-slate-900 tracking-tight leading-tight">{title}</h1>
          {description && <p className="text-xs text-slate-500 hidden sm:block">{description}</p>}
        </div>
      </div>
      
      <div className="flex items-center gap-3 sm:gap-4">
        <div className="relative hidden lg:block w-64 xl:w-80">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-400" />
          <Input type="search" placeholder="Search knowledge base..." className="w-full pl-9 bg-slate-50 border-slate-200 text-sm h-9 rounded-md shadow-inner transition-all focus:bg-white" />
        </div>
        
        <div className="flex items-center gap-1 sm:gap-2 border-l border-slate-200 pl-3 sm:pl-4">
          <Button variant="ghost" size="icon" className="text-slate-400 hover:text-slate-600 rounded-full h-8 w-8"><HelpCircle className="h-4 w-4" /></Button>
          <Button variant="ghost" size="icon" className="text-slate-400 hover:text-slate-600 rounded-full h-8 w-8 relative">
            <Bell className="h-4 w-4" />
            <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 bg-red-500 rounded-full border border-white"></span>
          </Button>
          <div className="ml-2 w-8 h-8 rounded-full bg-slate-800 text-white flex items-center justify-center text-xs font-bold cursor-pointer ring-2 ring-transparent hover:ring-slate-200 transition-all">
            AD
          </div>
        </div>
      </div>
    </header>
  )
}
