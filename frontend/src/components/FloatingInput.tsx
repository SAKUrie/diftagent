'use client'

import { useState, forwardRef } from 'react'
import { cn } from '@/lib/utils'

interface FloatingInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string
}

const FloatingInput = forwardRef<HTMLInputElement, FloatingInputProps>(
  ({ label, className, type, ...props }, ref) => {
    const [isFocused, setIsFocused] = useState(false)
    const [hasValue, setHasValue] = useState(false)

    const handleFocus = () => setIsFocused(true)
    const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
      setIsFocused(false)
      setHasValue(e.target.value.length > 0)
    }
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      setHasValue(e.target.value.length > 0)
      props.onChange?.(e)
    }

    return (
      <div className="relative">
        <input
          ref={ref}
          type={type}
          className={cn(
            "w-full h-14 px-3 pt-6 pb-2 bg-input border-transparent rounded-lg",
            "focus:ring-2 focus:ring-primary focus:border-transparent focus:outline-none",
            "transition-all duration-200",
            className
          )}
          onFocus={handleFocus}
          onBlur={handleBlur}
          onChange={handleChange}
          {...props}
        />
        <label
          className={cn(
            "absolute left-3 text-muted-foreground transition-all duration-200 pointer-events-none",
            "origin-top-left",
            (isFocused || hasValue || props.value)
              ? "top-2 text-xs scale-85 text-primary"
              : "top-4 text-sm"
          )}
        >
          {label}
        </label>
      </div>
    )
  }
)

FloatingInput.displayName = "FloatingInput"

export { FloatingInput }
