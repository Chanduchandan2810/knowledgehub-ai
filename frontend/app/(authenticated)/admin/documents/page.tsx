"use client"
import { AdminTopbar } from '@/components/navigation/admin-topbar'
import { EmptyState } from '@/components/shared/empty-state'
import { Button } from '@/components/ui/button'
import { FileUp, Filter, FolderKanban, X, CheckCircle, AlertCircle, FileText, ShieldCheck } from 'lucide-react'
import { PageTransition } from '@/components/shared/page-transition'
import { useState } from 'react'
import { Card } from '@/components/ui/card'

export default function AdminDocuments() {
  const [isUploading, setIsUploading] = useState(false)
  const [uploadState, setUploadState] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle')

  // Mock upload flow for UI demonstration (Phase 3 Prep)
  const handleMockUpload = () => {
    setUploadState('uploading')
    setTimeout(() => {
      setUploadState('success')
      setTimeout(() => {
        setIsUploading(false)
        setUploadState('idle')
      }, 2000)
    }, 1500)
  }

  return (
    <div className="flex flex-col h-full bg-slate-50/50 relative">
      <AdminTopbar title="Documents" description="Manage the knowledge base and AI retrieval sources." />
      <PageTransition className="flex-1 flex flex-col overflow-hidden p-6 md:p-8">
        <div className="flex flex-col h-full max-w-[1600px] w-full mx-auto">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
            <h2 className="text-xl font-bold text-slate-900 tracking-tight">Organization Library</h2>
            <div className="flex items-center gap-3 w-full sm:w-auto">
              <Button variant="outline" className="bg-white shadow-sm flex-1 sm:flex-none"><FolderKanban className="mr-2 h-4 w-4" /> Manage Folders</Button>
              <Button className="shadow-sm flex-1 sm:flex-none" onClick={() => setIsUploading(true)}><FileUp className="mr-2 h-4 w-4" /> Upload</Button>
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

      {/* Upload Modal (Design Prep) */}
      {isUploading && (
        <div className="absolute inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4">
          <Card className="w-full max-w-lg shadow-xl border-slate-200">
            <div className="flex items-center justify-between p-4 border-b border-slate-100">
              <h3 className="font-semibold text-slate-900">Document Upload Preview</h3>
              <Button variant="ghost" size="icon" onClick={() => setIsUploading(false)} className="h-8 w-8 rounded-full"><X className="w-4 h-4"/></Button>
            </div>
            
            <div className="p-6">
              {uploadState === 'idle' && (
                <div className="border-2 border-dashed border-slate-200 rounded-xl p-10 text-center hover:bg-slate-50 transition-colors cursor-pointer" onClick={handleMockUpload}>
                  <div className="w-12 h-12 bg-primary-50 rounded-full flex items-center justify-center mx-auto mb-4">
                    <FileUp className="w-6 h-6 text-primary-600" />
                  </div>
                  <h4 className="text-sm font-semibold text-slate-900 mb-1">Select file to preview upload flow</h4>
                  <p className="text-xs text-slate-500 mb-4">Document management will be connected in Phase 3.</p>
                  <p className="text-[10px] text-slate-400 font-mono bg-slate-100 inline-block px-2 py-1 rounded">Max size: 50MB per file</p>
                </div>
              )}

              {uploadState === 'uploading' && (
                <div className="text-center py-12">
                  <div className="w-12 h-12 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin mx-auto mb-4"></div>
                  <h4 className="text-sm font-semibold text-slate-900">Simulating upload preview...</h4>
                  <p className="text-xs text-slate-500 mt-1">This is a UI demonstration. No data is stored.</p>
                </div>
              )}

              {uploadState === 'success' && (
                <div className="text-center py-12">
                  <div className="w-12 h-12 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <CheckCircle className="w-6 h-6 text-emerald-600" />
                  </div>
                  <h4 className="text-sm font-semibold text-slate-900">Preview Flow Complete</h4>
                  <p className="text-xs text-slate-500 mt-1">Real document uploads and Phase 3 vectorization are not yet active.</p>
                </div>
              )}

              {uploadState === 'error' && (
                <div className="text-center py-12">
                  <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <AlertCircle className="w-6 h-6 text-red-600" />
                  </div>
                  <h4 className="text-sm font-semibold text-slate-900">Simulation Complete</h4>
                  <p className="text-xs text-red-500 mt-1">This mock flow finished.</p>
                </div>
              )}
            </div>
            
            <div className="bg-slate-50 p-4 border-t border-slate-100 flex justify-between items-center rounded-b-xl">
              <span className="text-xs text-slate-500 flex items-center gap-1.5"><ShieldCheck className="w-3.5 h-3.5"/> End-to-end encrypted</span>
              <Button variant="outline" size="sm" onClick={() => setIsUploading(false)}>Cancel</Button>
            </div>
          </Card>
        </div>
      )}
    </div>
  )
}
