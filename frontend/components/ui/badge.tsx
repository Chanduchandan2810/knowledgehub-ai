import * as React from "react"
import { cn } from "./button"

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "secondary" | "destructive" | "outline"
}

export function Badge({ className, variant = "default", ...props }: BadgeProps) {
  return (
    <div
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
        {
          "border-transparent bg-blue-100 text-blue-800 hover:bg-blue-200": variant === "default",
          "border-transparent bg-slate-100 text-slate-900 hover:bg-slate-200": variant === "secondary",
          "border-transparent bg-red-100 text-red-800 hover:bg-red-200": variant === "destructive",
          "text-slate-900": variant === "outline",
        },
        className
      )}
      {...props}
    />
  )
}
