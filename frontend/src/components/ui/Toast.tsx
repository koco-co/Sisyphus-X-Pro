import { CheckCircle, XCircle, Info } from 'lucide-react'
import { cn } from '@/lib/utils'

interface ToastProps {
  message: string
  type: 'success' | 'error' | 'info'
}

export function Toast({ message, type }: ToastProps) {
  const icons = {
    success: <CheckCircle className="h-5 w-5 text-green-500" />,
    error: <XCircle className="h-5 w-5 text-destructive" />,
    info: <Info className="h-5 w-5 text-primary" />,
  }

  const colors = {
    success: 'border-green-500 bg-green-50 dark:bg-green-950',
    error: 'border-destructive bg-destructive/10',
    info: 'border-primary bg-primary/10',
  }

  return (
    <div
      className={cn(
        'fixed right-4 top-4 z-50 flex items-center gap-3 rounded-lg border p-4 shadow-lg',
        'animate-in slide-in-from-top-2 fade-in-0',
        colors[type]
      )}
    >
      {icons[type]}
      <span className="text-sm font-medium">{message}</span>
      <div className="absolute bottom-0 left-0 h-1 animate-progress-full bg-current opacity-20" />
    </div>
  )
}
