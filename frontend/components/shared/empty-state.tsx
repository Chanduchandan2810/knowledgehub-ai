"use client"
import { LucideIcon } from 'lucide-react'
import { Button } from '../ui/button'
import { motion } from 'framer-motion'

interface EmptyStateProps {
  icon: LucideIcon
  title: string
  description: string
  actionLabel?: string
  onAction?: () => void
}

export function EmptyState({ icon: Icon, title, description, actionLabel, onAction }: EmptyStateProps) {
  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4 }}
      className="flex flex-col items-center justify-center p-12 text-center rounded-xl border border-dashed border-slate-200 bg-slate-50/50"
    >
      <div className="w-16 h-16 bg-white rounded-full shadow-sm border flex items-center justify-center mb-6">
        <Icon className="w-8 h-8 text-primary-500" />
      </div>
      <h3 className="text-lg font-semibold text-slate-900 mb-2">{title}</h3>
      <p className="text-sm text-slate-500 max-w-sm mb-6 leading-relaxed">{description}</p>
      {actionLabel && (
        <Button onClick={onAction} className="shadow-sm">{actionLabel}</Button>
      )}
    </motion.div>
  )
}
