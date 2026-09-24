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
