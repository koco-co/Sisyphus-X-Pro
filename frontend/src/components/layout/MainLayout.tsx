import type { ReactNode } from 'react'
import Header from './Header'

interface MainLayoutProps {
  children: ReactNode
}

/**
 * 主布局组件
 * 包含 Header 和内容区域
 */
export default function MainLayout({ children }: MainLayoutProps) {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container py-6">
        {children}
      </main>
    </div>
  )
}
