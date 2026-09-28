"use client"
import { LogOut } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { createClient } from '@/utils/supabase/client'
import { useState } from 'react'

export function LogoutButton({ className, variant = 'icon' }: { className?: string, variant?: 'icon' | 'full' }) {
  const router = useRouter()
  const supabase = createClient()
  const [loading, setLoading] = useState(false)

  const handleLogout = async () => {
    setLoading(true)
    await supabase.auth.signOut()
    // Clear custom cookies
    document.cookie = 'khub_org_id=; path=/; max-age=0'
    document.cookie = 'khub_role=; path=/; max-age=0'
    router.push('/login')
    router.refresh()
  }

  if (variant === 'full') {
    return (
      <button 
        onClick={handleLogout}
        disabled={loading}
        className={`flex items-center px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-200/50 hover:text-slate-900 rounded-md transition-colors w-full ${className}`}
      >
        <LogOut className="w-4 h-4 mr-3 text-slate-400" /> 
        {loading ? 'Signing Out...' : 'Sign Out'}
      </button>
    )
  }

  return (
    <button 
      onClick={handleLogout}
      disabled={loading}
      className={`text-slate-400 hover:text-slate-600 rounded-full h-8 w-8 flex items-center justify-center ${className}`}
      title="Sign Out"
    >
      <LogOut className="h-4 w-4" />
    </button>
  )
}
