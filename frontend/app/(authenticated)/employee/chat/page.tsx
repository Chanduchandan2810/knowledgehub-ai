import { BrainCircuit, Send, FileText } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

export default function EmployeeChat() {
  return (
    <div className="flex-1 flex flex-col h-full relative">
      <div className="flex-1 overflow-y-auto p-8 flex flex-col items-center justify-center">
        <div className="max-w-2xl w-full text-center space-y-6">
          <div className="mx-auto w-16 h-16 bg-blue-100 text-blue-600 rounded-2xl flex items-center justify-center mb-6 shadow-sm border border-blue-200">
            <BrainCircuit className="w-8 h-8" />
          </div>
          <h1 className="text-2xl font-semibold text-slate-900">Ask questions about your organization's authorized knowledge.</h1>
          <p className="text-slate-500">Answers are grounded in company documents and include source citations.</p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-8 text-left">
            <div className="p-4 border rounded-xl hover:bg-slate-50 cursor-pointer transition-colors shadow-sm">
              <p className="text-sm font-medium text-slate-900">What is our annual leave policy?</p>
            </div>
            <div className="p-4 border rounded-xl hover:bg-slate-50 cursor-pointer transition-colors shadow-sm">
              <p className="text-sm font-medium text-slate-900">What is the reimbursement process?</p>
            </div>
            <div className="p-4 border rounded-xl hover:bg-slate-50 cursor-pointer transition-colors shadow-sm">
              <p className="text-sm font-medium text-slate-900">Where can I find the employee handbook?</p>
            </div>
            <div className="p-4 border rounded-xl hover:bg-slate-50 cursor-pointer transition-colors shadow-sm">
              <p className="text-sm font-medium text-slate-900">How do I request a new laptop?</p>
            </div>
          </div>
        </div>
      </div>
      
      <div className="p-6 bg-white border-t">
        <div className="max-w-3xl mx-auto relative">
          <Input 
            className="w-full h-14 pl-6 pr-14 text-base rounded-full shadow-sm border-slate-300 focus-visible:ring-blue-500" 
            placeholder="Ask a question..."
          />
          <Button size="sm" className="absolute right-2 top-2 h-10 w-10 rounded-full p-0 bg-blue-600 hover:bg-blue-700">
            <Send className="h-4 w-4" />
          </Button>
        </div>
        <div className="text-center mt-3">
          <span className="text-xs text-slate-400">AI can make mistakes. Always check important information against primary sources.</span>
        </div>
      </div>
    </div>
  )
}
