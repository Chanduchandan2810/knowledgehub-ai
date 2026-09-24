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
