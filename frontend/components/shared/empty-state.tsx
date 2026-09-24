import { LucideIcon } from "lucide-react"
import { Button } from "../ui/button"

export function EmptyState({ icon: Icon, title, description, actionLabel }: { icon: LucideIcon, title: string, description: string, actionLabel?: string }) {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center border rounded-lg bg-slate-50 border-dashed">
      <div className="flex items-center justify-center w-12 h-12 rounded-full bg-slate-100 mb-4">
        <Icon className="w-6 h-6 text-slate-500" />
      </div>
      <h3 className="text-lg font-medium text-slate-900">{title}</h3>
      <p className="mt-1 text-sm text-slate-500 max-w-sm">{description}</p>
      {actionLabel && (
        <div className="mt-6">
          <Button>{actionLabel}</Button>
        </div>
      )}
    </div>
  )
}
