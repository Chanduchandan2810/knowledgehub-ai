import { RetrievalChat } from '@/components/chat/retrieval-chat'
import { AdminTopbar } from '@/components/navigation/admin-topbar'

export default function EmployeeChat() {
  return (
    <div className="flex flex-col h-full bg-slate-50/50 relative">
      <AdminTopbar title="AI Chat" description="Semantic retrieval and knowledge access." role="EMPLOYEE" />
      <div className="flex-1 overflow-hidden relative">
        <RetrievalChat role="Employee" />
      </div>
    </div>
  )
}
