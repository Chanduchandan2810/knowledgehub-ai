import { createBrowserClient } from '@supabase/ssr'

export function createClient() {
  const client = createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )

  if (typeof document !== 'undefined') {
    const isDemo = document.cookie.includes('demo_role=')
    if (isDemo) {
      // Provide a mock session so existing frontend components can bypass auth checks
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
      client.auth.getUser = async () => ({
        data: { user: { id: 'demo-user', aud: 'authenticated', role: 'authenticated', email: 'demo@knowledgehub.local', app_metadata: {}, user_metadata: {}, created_at: '', updated_at: '' } },
        error: null
      })
      client.auth.onAuthStateChange = ((callback: any) => {
        callback('SIGNED_IN', {
          access_token: 'demo-bypass-token',
          token_type: 'bearer',
          expires_in: 3600,
          refresh_token: 'demo-refresh',
          user: { id: 'demo-user', aud: 'authenticated', role: 'authenticated', email: 'demo@knowledgehub.local', app_metadata: {}, user_metadata: {}, created_at: '', updated_at: '' }
        })
        return { data: { subscription: { unsubscribe: () => {}, id: 'demo-sub', callback } } }
      }) as any
    }
  }

  return client
}
