"use client"
import { AdminTopbar } from '@/components/navigation/admin-topbar'
import { EmptyState } from '@/components/shared/empty-state'
import { Button } from '@/components/ui/button'
import { 
  FileUp, 
  X, 
  CheckCircle, 
  AlertCircle, 
  ShieldCheck, 
  Trash2, 
  Users, 
  Loader2, 
  UserCheck, 
  UserX,
  FileText,
  RefreshCw
} from 'lucide-react'
import { PageTransition } from '@/components/shared/page-transition'
import { useState, useEffect, useCallback } from 'react'
import { Card } from '@/components/ui/card'
import { createBrowserClient } from '@supabase/ssr'

interface DocumentData {
  id: string
  filename: string
  mime_type: string
  file_size: number
  status: string
  created_at: string
  chunk_count?: number
  error_message?: string
}

interface EmployeeData {
  id: string
  auth_user_id: string
  email: string
  full_name: string
  role: string
}

interface PermissionData {
  id: string
  document_id: string
  employee_id: string
  created_at: string
}

export default function AdminDocuments() {
  const [documents, setDocuments] = useState<DocumentData[]>([])
  const [loadingDocs, setLoadingDocs] = useState(true)
  
  // Upload modal state
  const [isUploading, setIsUploading] = useState(false)
  const [uploadState, setUploadState] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadError, setUploadError] = useState<string>('')
  
  // Deleting document state (stores document id currently being deleted)
  const [deletingId, setDeletingId] = useState<string | null>(null)
  
  // Permissions modal state
  const [permDoc, setPermDoc] = useState<DocumentData | null>(null)
  const [orgEmployees, setOrgEmployees] = useState<EmployeeData[]>([])
  const [docPermissions, setDocPermissions] = useState<PermissionData[]>([])
  const [loadingPerms, setLoadingPerms] = useState(false)
  const [permActionLoading, setPermActionLoading] = useState<string | null>(null)
  const [permError, setPermError] = useState<string | null>(null)

  const supabase = createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )

  const fetchDocuments = useCallback(async () => {
    try {
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
    } finally {
      setLoadingDocs(false)
    }
  }, [supabase])

  useEffect(() => {
    fetchDocuments()
  }, [fetchDocuments])

  // Polling for processing documents
  useEffect(() => {
    const hasProcessing = documents.some(d => d.status === 'PROCESSING' || d.status === 'UPLOADED')
    if (hasProcessing) {
      const interval = setInterval(() => {
        fetchDocuments()
      }, 3000)
      return () => clearInterval(interval)
    }
  }, [documents, fetchDocuments])

  const [reprocessingId, setReprocessingId] = useState<string | null>(null)

  const handleReprocess = async (documentId: string) => {
    if (reprocessingId) return
    setReprocessingId(documentId)
    
    try {
      const { data: { session } } = await supabase.auth.getSession()
      if (!session) return

      const res = await fetch(`/api/v1/documents/${documentId}/process`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`
        }
      })
      
      if (res.ok) {
        // Optimistically update
        setDocuments(prev => prev.map(d => d.id === documentId ? { ...d, status: 'PROCESSING' } : d))
      }
    } finally {
      setReprocessingId(null)
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0])
      setUploadError('')
      setUploadState('idle')
    }
  }

  const handleUpload = async () => {
    if (!selectedFile || uploadState === 'uploading') return
    setUploadState('uploading')
    setUploadError('')
    
    const { data: { session } } = await supabase.auth.getSession()
    if (!session) {
      setUploadError('Session expired. Please log in again.')
      setUploadState('error')
      return
    }

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
        const newDoc: DocumentData = await res.json()
        // Immediately update documents state without page reload
        setDocuments(prev => [newDoc, ...prev.filter(d => d.id !== newDoc.id)])
        setUploadState('success')
        setTimeout(() => {
          setIsUploading(false)
          setUploadState('idle')
          setSelectedFile(null)
        }, 1200)
      } else {
        const errorData = await res.json().catch(() => ({}))
        setUploadError(errorData.detail || 'Upload failed')
        setUploadState('error')
      }
    } catch {
      setUploadError('Network error during upload')
      setUploadState('error')
    }
  }

  const handleDelete = async (id: string) => {
    if (deletingId) return
    if (!confirm('Are you sure you want to delete this document? This will remove the file and associated permissions.')) return
    
    setDeletingId(id)
    try {
      const { data: { session } } = await supabase.auth.getSession()
      if (!session) return

      const res = await fetch(`/api/v1/documents/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${session.access_token}`
        }
      })
      
      if (res.ok || res.status === 204) {
        // Immediately remove document from local UI state
        setDocuments(prev => prev.filter(doc => doc.id !== id))
      } else {
        alert('Failed to delete document')
      }
    } catch {
      alert('Network error while deleting document')
    } finally {
      setDeletingId(null)
    }
  }

  // Open permissions modal
  const openPermissionsModal = async (doc: DocumentData) => {
    setPermDoc(doc)
    setLoadingPerms(true)
    setPermError(null)
    
    try {
      const { data: { session } } = await supabase.auth.getSession()
      if (!session) return

      // Parallel fetch permissions and organization employees
      const [permsRes, empsRes] = await Promise.all([
        fetch(`/api/v1/documents/${doc.id}/permissions`, {
          headers: { 'Authorization': `Bearer ${session.access_token}` }
        }),
        fetch('/api/v1/employees', {
          headers: { 'Authorization': `Bearer ${session.access_token}` }
        })
      ])

      if (permsRes.ok) {
        setDocPermissions(await permsRes.json())
      }
      if (empsRes.ok) {
        setOrgEmployees(await empsRes.json())
      }
    } catch {
      setPermError('Failed to load permissions and employee data')
    } finally {
      setLoadingPerms(false)
    }
  }

  const grantPermission = async (employeeId: string) => {
    if (!permDoc || permActionLoading) return
    setPermActionLoading(employeeId)
    setPermError(null)

    try {
      const { data: { session } } = await supabase.auth.getSession()
      if (!session) return

      const res = await fetch(`/api/v1/documents/${permDoc.id}/permissions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          document_id: permDoc.id,
          employee_id: employeeId
        })
      })

      if (res.ok) {
        const newPerm: PermissionData = await res.json()
        setDocPermissions(prev => [...prev.filter(p => p.employee_id !== employeeId), newPerm])
      } else {
        const err = await res.json().catch(() => ({}))
        setPermError(err.detail || 'Failed to grant permission')
      }
    } catch {
      setPermError('Network error while granting permission')
    } finally {
      setPermActionLoading(null)
    }
  }

  const revokePermission = async (employeeId: string) => {
    if (!permDoc || permActionLoading) return
    setPermActionLoading(employeeId)
    setPermError(null)

    try {
      const { data: { session } } = await supabase.auth.getSession()
      if (!session) return

      const res = await fetch(`/api/v1/documents/${permDoc.id}/permissions/${employeeId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${session.access_token}`
        }
      })

      if (res.ok || res.status === 204) {
        const emp = orgEmployees.find(e => e.id === employeeId || e.auth_user_id === employeeId)
        setDocPermissions(prev => prev.filter(p => p.employee_id !== employeeId && (!emp || (p.employee_id !== emp.id && p.employee_id !== emp.auth_user_id))))
      } else {
        const err = await res.json().catch(() => ({}))
        setPermError(err.detail || 'Failed to revoke permission')
      }
    } catch {
      setPermError('Network error while revoking permission')
    } finally {
      setPermActionLoading(null)
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
              <Button 
                className="shadow-sm flex-1 sm:flex-none" 
                onClick={() => {
                  setIsUploading(true)
                  setUploadState('idle')
                  setSelectedFile(null)
                  setUploadError('')
                }}
              >
                <FileUp className="mr-2 h-4 w-4" /> Upload
              </Button>
            </div>
          </div>
          
          <div className="bg-white border border-slate-200/80 rounded-xl shadow-sm flex flex-col flex-1 min-h-[400px]">
            <div className="p-4 border-b border-slate-200 bg-slate-50/50 flex justify-between items-center rounded-t-xl">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-slate-900">
                  {loadingDocs ? 'Loading documents...' : `${documents.length} Document${documents.length === 1 ? '' : 's'}`}
                </span>
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
            {documents.length === 0 && !loadingDocs ? (
              <div className="flex-1 flex items-center justify-center p-8 bg-slate-50/30 rounded-b-xl">
                <div className="max-w-md w-full">
                  <EmptyState 
                    icon={FileUp} 
                    title="Library is empty" 
                    description="Upload PDFs or Text files. They will be stored securely for your organization." 
                    actionLabel="Upload Document"
                    onAction={() => {
                      setIsUploading(true)
                      setUploadState('idle')
                      setSelectedFile(null)
                      setUploadError('')
                    }}
                  />
                </div>
              </div>
            ) : (
              <div className="flex-1 overflow-auto rounded-b-xl">
                {documents.map((doc) => (
                  <div key={doc.id} className="grid grid-cols-12 px-6 py-4 border-b border-slate-100 hover:bg-slate-50/50 items-center transition-colors">
                    <div className="col-span-6 md:col-span-5 font-medium text-sm text-slate-900 truncate pr-4 flex items-center gap-2">
                      <FileText className="w-4 h-4 text-slate-400 shrink-0" />
                      <span className="truncate">{doc.filename}</span>
                    </div>
                    <div className="col-span-3 hidden md:flex flex-col text-xs text-slate-500">
                      <span>{doc.mime_type}</span>
                      <span>{formatSize(doc.file_size)}</span>
                    </div>
                    <div className="col-span-2 hidden lg:flex items-center gap-1">
                      {doc.status === 'PROCESSED' ? (
                        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-50 text-green-700 border border-green-200/50" title={doc.chunk_count ? `${doc.chunk_count} chunks` : ''}>
                          Processed
                        </span>
                      ) : doc.status === 'PROCESSING' ? (
                        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-amber-50 text-amber-700 border border-amber-200/50">
                          <Loader2 className="w-3 h-3 animate-spin mr-1" /> Processing
                        </span>
                      ) : doc.status === 'FAILED' ? (
                        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-red-50 text-red-700 border border-red-200/50" title={doc.error_message || 'Failed'}>
                          <AlertCircle className="w-3 h-3 mr-1" /> Failed
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200/50">
                          Pending
                        </span>
                      )}
                    </div>
                    <div className="col-span-6 md:col-span-4 lg:col-span-2 flex items-center justify-end gap-1">
                      {(doc.status === 'FAILED' || doc.status === 'PROCESSED') && (
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8 text-slate-500 hover:text-amber-600 hover:bg-amber-50"
                          title="Reprocess Document"
                          disabled={reprocessingId === doc.id}
                          onClick={() => handleReprocess(doc.id)}
                        >
                          <RefreshCw className={`w-4 h-4 ${reprocessingId === doc.id ? 'animate-spin text-amber-500' : ''}`} />
                        </Button>
                      )}
                      <Button 
                        variant="ghost" 
                        size="icon" 
                        className="h-8 w-8 text-slate-500 hover:text-primary-600 hover:bg-primary-50" 
                        title="Manage Permissions"
                        onClick={() => openPermissionsModal(doc)}
                      >
                        <Users className="w-4 h-4" />
                      </Button>
                      <Button 
                        variant="ghost" 
                        size="icon" 
                        className="h-8 w-8 text-slate-500 hover:text-red-600 hover:bg-red-50" 
                        disabled={deletingId === doc.id}
                        onClick={() => handleDelete(doc.id)} 
                        title="Delete Document"
                      >
                        {deletingId === doc.id ? (
                          <Loader2 className="w-4 h-4 animate-spin text-red-500" />
                        ) : (
                          <Trash2 className="w-4 h-4" />
                        )}
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
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4">
          <Card className="w-full max-w-lg shadow-xl border-slate-200">
            <div className="flex items-center justify-between p-4 border-b border-slate-100">
              <h3 className="font-semibold text-slate-900">Upload Document</h3>
              <Button 
                variant="ghost" 
                size="icon" 
                disabled={uploadState === 'uploading'}
                onClick={() => { setIsUploading(false); setUploadState('idle'); setSelectedFile(null); }} 
                className="h-8 w-8 rounded-full"
              >
                <X className="w-4 h-4"/>
              </Button>
            </div>
            
            <div className="p-6">
              {uploadState === 'idle' && (
                <div className="flex flex-col gap-4">
                  <input 
                    type="file" 
                    accept=".pdf,.txt" 
                    onChange={handleFileChange} 
                    className="block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100 transition-colors" 
                  />
                  {selectedFile && (
                    <div className="flex flex-col gap-2">
                      <div className="text-xs text-slate-600 bg-slate-50 p-2.5 rounded border border-slate-200/80">
                        Selected: <span className="font-medium text-slate-800">{selectedFile.name}</span> ({formatSize(selectedFile.size)})
                      </div>
                      <Button data-testid="modal-upload-submit-btn" onClick={handleUpload} className="w-full">Upload Document</Button>
                    </div>
                  )}
                  <p className="text-[10px] text-slate-400 font-mono bg-slate-100 inline-block px-2 py-1 rounded w-max">Max size: 10MB per file (PDF, TXT)</p>
                </div>
              )}

              {uploadState === 'uploading' && (
                <div className="text-center py-10">
                  <div className="w-12 h-12 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin mx-auto mb-4"></div>
                  <h4 className="text-sm font-semibold text-slate-900">Uploading to Secure Storage...</h4>
                  <p className="text-xs text-slate-500 mt-1">Validating and saving metadata</p>
                </div>
              )}

              {uploadState === 'success' && (
                <div className="text-center py-10">
                  <div className="w-12 h-12 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <CheckCircle className="w-6 h-6 text-emerald-600" />
                  </div>
                  <h4 className="text-sm font-semibold text-slate-900">Upload Complete</h4>
                  <p className="text-xs text-slate-500 mt-1">Document is now available in your library</p>
                </div>
              )}

              {uploadState === 'error' && (
                <div className="text-center py-8">
                  <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <AlertCircle className="w-6 h-6 text-red-600" />
                  </div>
                  <h4 className="text-sm font-semibold text-slate-900">Upload Failed</h4>
                  <p className="text-xs text-red-600 mt-1 font-medium bg-red-50 p-2 rounded border border-red-100">{uploadError}</p>
                  <Button variant="outline" className="mt-4" onClick={() => { setUploadState('idle'); setUploadError(''); }}>Try Again</Button>
                </div>
              )}
            </div>
            
            <div className="bg-slate-50 p-4 border-t border-slate-100 flex justify-between items-center rounded-b-xl">
              <span className="text-xs text-slate-500 flex items-center gap-1.5"><ShieldCheck className="w-3.5 h-3.5"/> End-to-end tenant isolated</span>
            </div>
          </Card>
        </div>
      )}

      {/* Permissions Modal */}
      {permDoc && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4">
          <Card className="w-full max-w-xl shadow-xl border-slate-200">
            <div className="flex items-center justify-between p-4 border-b border-slate-100">
              <div>
                <h3 className="font-semibold text-slate-900">Document Permissions</h3>
                <p className="text-xs text-slate-500 truncate max-w-sm">{permDoc.filename}</p>
              </div>
              <Button 
                variant="ghost" 
                size="icon" 
                onClick={() => { setPermDoc(null); setPermError(null); }} 
                className="h-8 w-8 rounded-full"
              >
                <X className="w-4 h-4"/>
              </Button>
            </div>

            <div className="p-6">
              {permError && (
                <div className="mb-4 p-2.5 bg-red-50 border border-red-200 rounded-md text-xs text-red-700 font-medium">
                  {permError}
                </div>
              )}

              {loadingPerms ? (
                <div className="text-center py-8">
                  <Loader2 className="w-8 h-8 animate-spin text-primary-600 mx-auto mb-2" />
                  <p className="text-xs text-slate-500">Loading employees and permissions...</p>
                </div>
              ) : orgEmployees.length === 0 ? (
                <div className="text-center py-8">
                  <Users className="w-8 h-8 text-slate-300 mx-auto mb-2" />
                  <p className="text-sm font-medium text-slate-700">No employees found in organization</p>
                  <p className="text-xs text-slate-500 mt-1">Add employees in the Employees section first.</p>
                </div>
              ) : (
                <div className="divide-y divide-slate-100 max-h-80 overflow-y-auto pr-1">
                  {orgEmployees.map(emp => {
                    const hasAccess = docPermissions.some(p => p.employee_id === emp.id || (emp.auth_user_id && p.employee_id === emp.auth_user_id))
                    const isProcessing = permActionLoading === emp.id

                    return (
                      <div key={emp.id} className="py-3 flex items-center justify-between gap-4">
                        <div className="min-w-0">
                          <p className="text-sm font-medium text-slate-900 truncate">{emp.full_name}</p>
                          <p className="text-xs text-slate-500 truncate">{emp.email}</p>
                        </div>
                        <div className="flex items-center gap-3">
                          {hasAccess ? (
                            <Button 
                              size="sm" 
                              variant="outline" 
                              className="h-8 text-xs text-red-600 border-red-200 hover:bg-red-50 hover:text-red-700"
                              disabled={isProcessing}
                              onClick={() => revokePermission(emp.id)}
                            >
                              {isProcessing ? (
                                <Loader2 className="w-3.5 h-3.5 animate-spin mr-1.5" />
                              ) : (
                                <UserX className="w-3.5 h-3.5 mr-1.5" />
                              )}
                              Revoke
                            </Button>
                          ) : (
                            <Button 
                              size="sm" 
                              className="h-8 text-xs bg-primary-600 hover:bg-primary-700 text-white"
                              disabled={isProcessing}
                              onClick={() => grantPermission(emp.id)}
                            >
                              {isProcessing ? (
                                <Loader2 className="w-3.5 h-3.5 animate-spin mr-1.5" />
                              ) : (
                                <UserCheck className="w-3.5 h-3.5 mr-1.5" />
                              )}
                              Grant
                            </Button>
                          )}
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}
            </div>

            <div className="bg-slate-50 p-4 border-t border-slate-100 flex justify-between items-center rounded-b-xl">
              <span className="text-xs text-slate-500">
                {docPermissions.length} employee{docPermissions.length === 1 ? '' : 's'} with access
              </span>
              <Button variant="outline" size="sm" onClick={() => setPermDoc(null)}>Close</Button>
            </div>
          </Card>
        </div>
      )}
    </div>
  )
}
