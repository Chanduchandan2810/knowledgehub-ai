import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import Link from 'next/link'

export default function LoginPage() {
  return (
    <div className="flex items-center justify-center min-h-[calc(100vh-16rem)] py-12 px-4 sm:px-6 lg:px-8">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold">Sign in to your account</CardTitle>
          <p className="text-sm text-slate-500 mt-2">Enter your email and password to access your workspace.</p>
        </CardHeader>
        <CardContent>
          <form className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Email address</label>
              <Input type="email" placeholder="name@company.com" required />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Password</label>
              <Input type="password" required />
            </div>
            <Button className="w-full" type="button">Sign In</Button>
          </form>
          <div className="mt-6 text-center text-sm">
            <span className="text-slate-500">Don't have an account? </span>
            <Link href="/register" className="font-medium text-blue-600 hover:text-blue-500">Register</Link>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
