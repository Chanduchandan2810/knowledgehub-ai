"use client"
import { AdminTopbar } from '@/components/navigation/admin-topbar'
import { EmptyState } from '@/components/shared/empty-state'
import { Button } from '@/components/ui/button'
import { FileUp, Filter, FolderKanban } from 'lucide-react'
import { PageTransition } from '@/components/shared/page-transition'

export default function AdminDocuments() {
  return (
    <div className="flex flex-col h-full bg-slate-50/50">
      <AdminTopbar title="Documents" description="Manage the knowledge base and AI retrieval sources." />
      <PageTransition className="flex-1 flex flex-col overflow-hidden p-6 md:p-8">
        <div className="flex flex-col h-full max-w-[1600px] w-full mx-auto">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
            <h2 className="text-xl font-bold text-slate-900 tracking-tight">Organization Library</h2>
            <div className="flex items-center gap-3 w-full sm:w-auto">
              <Button variant="outline" className="bg-white shadow-sm flex-1 sm:flex-none"><FolderKanban className="mr-2 h-4 w-4" /> Manage Folders</Button>
              <Button className="shadow-sm flex-1 sm:flex-none"><FileUp className="mr-2 h-4 w-4" /> Upload</Button>
            </div>
          </div>
          
          <div className="bg-white border border-slate-200/80 rounded-xl shadow-sm flex flex-col flex-1 min-h-[400px]">
            <div className="p-4 border-b border-slate-200 bg-slate-50/50 flex justify-between items-center rounded-t-xl">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-slate-900">0 Documents</span>
                <span className="text-slate-300">|</span>
                <span className="text-xs text-slate-500">0 Bytes used</span>
              </div>
              <Button variant="outline" size="sm" className="h-8 text-xs bg-white"><Filter className="w-3.5 h-3.5 mr-1.5"/> Filter</Button>
            </div>
            
            {/* Table Header */}
            <div className="grid grid-cols-12 px-6 py-3 border-b border-slate-200 bg-slate-50/80 text-xs font-semibold text-slate-500 uppercase tracking-wider">
              <div className="col-span-6 md:col-span-5">Name</div>
              <div className="col-span-3 hidden md:block">Type / Size</div>
              <div className="col-span-3 hidden lg:block">Visibility</div>
              <div className="col-span-6 md:col-span-4 lg:col-span-1 text-right">Updated</div>
            </div>
            
            {/* Table Body / Empty State */}
            <div className="flex-1 flex items-center justify-center p-8 bg-slate-50/30 rounded-b-xl">
              <div className="max-w-md w-full">
                <EmptyState 
                  icon={FileUp} 
                  title="Library is empty" 
                  description="Upload PDFs, Word docs, or Text files. They will be automatically processed and vectorized for AI search." 
                  actionLabel="Upload Document" 
                />
              </div>
            </div>
          </div>
        </div>
      </PageTransition>
    </div>
  )
}
