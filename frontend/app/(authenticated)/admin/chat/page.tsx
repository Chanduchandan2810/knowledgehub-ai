import { ChatInterface } from '@/components/chat/chat-interface'
import { AdminTopbar } from '@/components/navigation/admin-topbar'

export default function AdminChat() {
  return (
    <div className="flex flex-col h-full bg-slate-50/50 relative">
      <AdminTopbar title="AI Chat" description="KnowledgeHub semantic search and chat." role="ADMIN" />
      <div className="flex-1 overflow-hidden relative">
        <ChatInterface role="Admin" />
      </div>
    </div>
  )
}
