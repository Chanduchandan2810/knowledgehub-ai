import * as React from "react"
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "outline" | "ghost" | "link" | "danger"
  size?: "default" | "sm" | "lg"
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "default", size = "default", ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(
          "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none disabled:pointer-events-none disabled:opacity-50",
          {
            "bg-blue-600 text-white hover:bg-blue-700": variant === "default",
            "border border-slate-200 bg-white hover:bg-slate-100 text-slate-900": variant === "outline",
            "hover:bg-slate-100 text-slate-900": variant === "ghost",
            "text-blue-600 underline-offset-4 hover:underline": variant === "link",
            "bg-red-600 text-white hover:bg-red-700": variant === "danger",
            "h-10 px-4 py-2": size === "default",
            "h-9 rounded-md px-3": size === "sm",
            "h-11 rounded-md px-8": size === "lg",
          },
          className
        )}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"
