import { useState, useEffect } from 'react'
import { ChevronDown, Settings } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { useToast } from '@/hooks/use-toast'
import { useEnvironment } from '@/contexts/EnvironmentContext'
import { EnvironmentManager } from './EnvironmentManager'
import { Button } from '@/components/ui/Button'
import type { Environment } from '@/types/environment'

interface EnvironmentSelectorProps {
  projectId: string
}

export function EnvironmentSelector({ projectId }: EnvironmentSelectorProps) {
  const { token } = useAuth()
  const { toast } = useToast()
  const { currentEnv, setCurrentEnv, environments, setEnvironments } = useEnvironment()

  const [isOpen, setIsOpen] = useState(false)
  const [managerOpen, setManagerOpen] = useState(false)

  // 获取环境列表
  const fetchEnvironments = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/environments?project_id=${projectId}`, {
        headers: { Authorization: `Bearer ${token}` },
      })

      if (!response.ok) throw new Error('获取环境列表失败')

      const data = await response.json()
      setEnvironments(data)

      // 自动选择默认环境
      if (!currentEnv && data.length > 0) {
        const defaultEnv = data.find((env: Environment) => env.is_default) || data[0]
        setCurrentEnv(defaultEnv)
      }
    } catch (error) {
      toast('获取环境列表失败', 'error')
    }
  }

  useEffect(() => {
    fetchEnvironments()
  }, [projectId])

  const handleSelectEnv = (env: Environment) => {
    setCurrentEnv(env)
    setIsOpen(false)
  }

  return (
    <>
      {/* 环境选择器 */}
      <div className="flex items-center gap-2">
        <div className="relative">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsOpen(!isOpen)}
            className="min-w-[150px] justify-between"
          >
            {currentEnv ? currentEnv.name : '选择环境'}
            <ChevronDown className="ml-2 h-4 w-4" />
          </Button>

          {isOpen && (
            <div className="absolute right-0 mt-2 w-56 bg-popover border rounded-md shadow-lg z-50">
              <div className="p-1">
                {environments.map((env) => (
                  <button
                    key={env.id}
                    onClick={() => handleSelectEnv(env)}
                    className={`w-full text-left px-3 py-2 text-sm rounded-md transition-colors ${
                      currentEnv?.id === env.id
                        ? 'bg-accent text-accent-foreground'
                        : 'hover:bg-muted'
                    }`}
                  >
                    <div className="font-medium">{env.name}</div>
                    <div className="text-xs text-muted-foreground">{env.base_url}</div>
                  </button>
                ))}
                {environments.length === 0 && (
                  <div className="px-3 py-2 text-sm text-muted-foreground">暂无环境</div>
                )}
              </div>
            </div>
          )}
        </div>

        <Button variant="ghost" size="sm" onClick={() => setManagerOpen(true)}>
          <Settings className="h-4 w-4" />
        </Button>
      </div>

      {/* 环境管理弹窗 */}
      <EnvironmentManager
        projectId={projectId}
        open={managerOpen}
        onOpenChange={setManagerOpen}
      />
    </>
  )
}
