import { MessageSquare } from 'lucide-react'
import { EmptyState } from '@/components/shared/empty-state'

export default function EmployeeConversations() {
  return (
    <div className="flex-1 p-8">
      <h1 className="text-2xl font-bold text-slate-900 mb-6">Conversation History</h1>
      <div className="max-w-3xl">
        <EmptyState 
          icon={MessageSquare} 
          title="Select a conversation" 
          description="Choose a conversation from the sidebar or start a new chat." 
        />
      </div>
    </div>
  )
}
