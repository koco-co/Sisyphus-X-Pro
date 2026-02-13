import { useState, useEffect } from 'react'

interface Toast {
  id: string
  message: string
  type: 'success' | 'error' | 'info'
}

let toastListeners: ((toast: Toast) => void)[] = []
let toasts: Toast[] = []

export function toast(message: string, type: 'success' | 'error' | 'info' = 'info') {
  const id = Math.random().toString(36).substring(7)
  const newToast: Toast = { id, message, type }
  toasts.push(newToast)
  toastListeners.forEach((listener) => listener(newToast))

  setTimeout(() => {
    toasts = toasts.filter((t) => t.id !== id)
  }, 3000)
}

export function useToast() {
  const [toastList, setToastList] = useState<Toast[]>([])

  useEffect(() => {
    toastListeners.push((newToast) => {
      setToastList((prev) => [...prev, newToast])
      setTimeout(() => {
        setToastList((current) => current.filter((t) => t.id !== newToast.id))
      }, 3000)
    })

    return () => {
      toastListeners = []
    }
  }, [])

  return { toastList, toast }
}
