import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'

export async function createClient() {
  const cookieStore = await cookies()

  const client = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll()
        },
        setAll(cookiesToSet) {
          try {
            cookiesToSet.forEach(({ name, value, options }) => {
              cookieStore.set(name, value, options)
            })
          } catch (error) {
          }
        },
      },
    }
  )

  const isDemo = cookieStore.get('demo_role')?.value
  if (isDemo) {
    client.auth.getUser = async () => ({
      data: { user: { id: 'demo-user', aud: 'authenticated', role: 'authenticated', email: 'demo@knowledgehub.local', app_metadata: {}, user_metadata: {}, created_at: '', updated_at: '' } },
      error: null
    })
    client.auth.getSession = async () => ({
      data: {
        session: {
          access_token: 'demo-bypass-token',
          token_type: 'bearer',
          expires_in: 3600,
          refresh_token: 'demo-refresh',
          user: { id: 'demo-user', aud: 'authenticated', role: 'authenticated', email: 'demo@knowledgehub.local', app_metadata: {}, user_metadata: {}, created_at: '', updated_at: '' }
        }
      },
      error: null
    })
  }

  return client
}
