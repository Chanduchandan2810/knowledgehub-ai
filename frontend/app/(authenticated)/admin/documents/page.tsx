"use client"
import { AdminTopbar } from '@/components/navigation/admin-topbar'
import { EmptyState } from '@/components/shared/empty-state'
import { Button } from '@/components/ui/button'
import { FileUp, Filter, FolderKanban, X, CheckCircle, AlertCircle, ShieldCheck, Trash2, Users } from 'lucide-react'
import { PageTransition } from '@/components/shared/page-transition'
import { useState, useEffect } from 'react'
import { Card } from '@/components/ui/card'
import { createBrowserClient } from '@supabase/ssr'

interface DocumentData {
  id: string
  filename: string
  mime_type: string
  file_size: number
  status: string
  created_at: string
}

export default function AdminDocuments() {
  const [documents, setDocuments] = useState<DocumentData[]>([])
  const [isUploading, setIsUploading] = useState(false)
  const [uploadState, setUploadState] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadError, setUploadError] = useState<string>('')
  
  const supabase = createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )

  const fetchDocuments = async () => {
    const { data: { session } } = await supabase.auth.getSession()
    if (!session) return

    const res = await fetch('/api/v1/documents', {
      headers: {
        'Authorization': `Bearer ${session.access_token}`
      }
    })
    if (res.ok) {
      const data = await res.json()
      setDocuments(data)
    }
  }

  useEffect(() => {
    fetchDocuments()
  }, [])

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0])
      setUploadError('')
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) return
    setUploadState('uploading')
    setUploadError('')
    
    const { data: { session } } = await supabase.auth.getSession()
    if (!session) return

    const formData = new FormData()
    formData.append('file', selectedFile)

    try {
      const res = await fetch('/api/v1/documents', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`
        },
        body: formData
      })
      
      if (res.ok) {
        setUploadState('success')
        fetchDocuments()
        setTimeout(() => {
          setIsUploading(false)
          setUploadState('idle')
          setSelectedFile(null)
        }, 2000)
      } else {
        const errorData = await res.json()
        setUploadError(errorData.detail || 'Upload failed')
        setUploadState('error')
      }
    } catch (e) {
      setUploadError('Network error during upload')
      setUploadState('error')
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this document? This will permanently remove the file and all associated permissions.')) return
    
    const { data: { session } } = await supabase.auth.getSession()
    if (!session) return

    const res = await fetch(`/api/v1/documents/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${session.access_token}`
      }
    })
    
    if (res.ok) {
      fetchDocuments()
    } else {
      alert('Failed to delete document')
    }
  }

  const formatSize = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
  }

  return (
    <div className="flex flex-col h-full bg-slate-50/50 relative">
      <AdminTopbar title="Documents" description="Manage the knowledge base and AI retrieval sources." />
      <PageTransition className="flex-1 flex flex-col overflow-hidden p-6 md:p-8">
        <div className="flex flex-col h-full max-w-[1600px] w-full mx-auto">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
            <h2 className="text-xl font-bold text-slate-900 tracking-tight">Organization Library</h2>
            <div className="flex items-center gap-3 w-full sm:w-auto">
              <Button className="shadow-sm flex-1 sm:flex-none" onClick={() => setIsUploading(true)}><FileUp className="mr-2 h-4 w-4" /> Upload</Button>
            </div>
          </div>
          
          <div className="bg-white border border-slate-200/80 rounded-xl shadow-sm flex flex-col flex-1 min-h-[400px]">
            <div className="p-4 border-b border-slate-200 bg-slate-50/50 flex justify-between items-center rounded-t-xl">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-slate-900">{documents.length} Documents</span>
              </div>
            </div>
            
            {/* Table Header */}
            <div className="grid grid-cols-12 px-6 py-3 border-b border-slate-200 bg-slate-50/80 text-xs font-semibold text-slate-500 uppercase tracking-wider">
              <div className="col-span-6 md:col-span-5">Name</div>
              <div className="col-span-3 hidden md:block">Type / Size</div>
              <div className="col-span-2 hidden lg:block">Status</div>
              <div className="col-span-6 md:col-span-4 lg:col-span-2 text-right">Actions</div>
            </div>
            
            {/* Table Body / Empty State */}
            {documents.length === 0 ? (
              <div className="flex-1 flex items-center justify-center p-8 bg-slate-50/30 rounded-b-xl">
                <div className="max-w-md w-full">
                  <EmptyState 
                    icon={FileUp} 
                    title="Library is empty" 
                    description="Upload PDFs or Text files. They will be stored securely for your organization." 
                    actionLabel="Upload Document"
                    onAction={() => setIsUploading(true)}
                  />
                </div>
              </div>
            ) : (
              <div className="flex-1 overflow-auto rounded-b-xl">
                {documents.map((doc) => (
                  <div key={doc.id} className="grid grid-cols-12 px-6 py-4 border-b border-slate-100 hover:bg-slate-50/50 items-center transition-colors">
                    <div className="col-span-6 md:col-span-5 font-medium text-sm text-slate-900 truncate pr-4">
                      {doc.filename}
                    </div>
                    <div className="col-span-3 hidden md:flex flex-col text-xs text-slate-500">
                      <span>{doc.mime_type}</span>
                      <span>{formatSize(doc.file_size)}</span>
                    </div>
                    <div className="col-span-2 hidden lg:block">
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-50 text-blue-700 border border-blue-200/50">
                        {doc.status}
                      </span>
                    </div>
                    <div className="col-span-6 md:col-span-4 lg:col-span-2 flex items-center justify-end gap-2">
                      <Button variant="ghost" size="icon" className="h-8 w-8 text-slate-400 hover:text-slate-600" title="Permissions (Phase 3 Backend Integrated, UI Extension Planned)">
                        <Users className="w-4 h-4" />
                      </Button>
                      <Button variant="ghost" size="icon" className="h-8 w-8 text-slate-400 hover:text-red-600 hover:bg-red-50" onClick={() => handleDelete(doc.id)} title="Delete Document">
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </PageTransition>

      {/* Upload Modal */}
      {isUploading && (
        <div className="absolute inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4">
          <Card className="w-full max-w-lg shadow-xl border-slate-200">
            <div className="flex items-center justify-between p-4 border-b border-slate-100">
              <h3 className="font-semibold text-slate-900">Upload Document</h3>
              <Button variant="ghost" size="icon" onClick={() => { setIsUploading(false); setUploadState('idle'); setSelectedFile(null); }} className="h-8 w-8 rounded-full"><X className="w-4 h-4"/></Button>
            </div>
            
            <div className="p-6">
              {uploadState === 'idle' && (
                <div className="flex flex-col gap-4">
                  <input type="file" accept=".pdf,.txt" onChange={handleFileChange} className="block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100 transition-colors" />
                  {selectedFile && (
                    <Button onClick={handleUpload} className="w-full">Upload {selectedFile.name}</Button>
                  )}
                  <p className="text-[10px] text-slate-400 font-mono bg-slate-100 inline-block px-2 py-1 rounded w-max">Max size: 10MB per file (PDF, TXT)</p>
                </div>
              )}

              {uploadState === 'uploading' && (
                <div className="text-center py-12">
                  <div className="w-12 h-12 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin mx-auto mb-4"></div>
                  <h4 className="text-sm font-semibold text-slate-900">Uploading to Secure Storage...</h4>
                </div>
              )}

              {uploadState === 'success' && (
                <div className="text-center py-12">
                  <div className="w-12 h-12 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <CheckCircle className="w-6 h-6 text-emerald-600" />
                  </div>
                  <h4 className="text-sm font-semibold text-slate-900">Upload Complete</h4>
                </div>
              )}

              {uploadState === 'error' && (
                <div className="text-center py-12">
                  <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <AlertCircle className="w-6 h-6 text-red-600" />
                  </div>
                  <h4 className="text-sm font-semibold text-slate-900">Upload Failed</h4>
                  <p className="text-xs text-red-500 mt-1">{uploadError}</p>
                  <Button variant="outline" className="mt-4" onClick={() => { setUploadState('idle'); setUploadError(''); }}>Try Again</Button>
                </div>
              )}
            </div>
            
            <div className="bg-slate-50 p-4 border-t border-slate-100 flex justify-between items-center rounded-b-xl">
              <span className="text-xs text-slate-500 flex items-center gap-1.5"><ShieldCheck className="w-3.5 h-3.5"/> End-to-end encrypted</span>
            </div>
          </Card>
        </div>
      )}
    </div>
  )
}
