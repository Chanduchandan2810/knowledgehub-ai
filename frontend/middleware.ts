import { type NextRequest, NextResponse } from 'next/server'
import { updateSession } from '@/utils/supabase/middleware'
import { createServerClient } from '@supabase/ssr'

export async function middleware(request: NextRequest) {
  // First update session (this refreshes tokens if needed)
  const response = await updateSession(request)

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll()
        },
        setAll(cookiesToSet) {
          // handled by updateSession
        },
      },
    }
  )

  const { data: { user } } = await supabase.auth.getUser()

  const isAdminRoute = request.nextUrl.pathname.startsWith('/admin')
  const isEmployeeRoute = request.nextUrl.pathname.startsWith('/employee')
  const role = request.cookies.get('khub_role')?.value
  
  // 1. Unauthenticated users cannot access protected routes
  if ((isAdminRoute || isEmployeeRoute) && !user) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  // 2. Role-based protection
  if (user) {
    // EMPLOYEE attempting to access Admin route
    if (isAdminRoute && role === 'EMPLOYEE') {
      return NextResponse.redirect(new URL('/employee/chat', request.url))
    }
    
    // ADMIN attempting to access Employee route
    if (isEmployeeRoute && role === 'ADMIN') {
      return NextResponse.redirect(new URL('/admin/documents', request.url))
    }
  }

  // 3. (Removed) Allow authenticated users to visit auth routes if they explicitly navigate there, as requested.

  return response
}

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
}
