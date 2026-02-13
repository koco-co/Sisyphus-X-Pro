import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { Plus, Trash2, Edit2, Globe, Server } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { useToast } from '@/hooks/use-toast'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/Dialog'
import type { Environment, EnvVariable } from '@/types/environment'

export function EnvironmentsPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const { token } = useAuth()
  const { toast } = useToast()

  const [environments, setEnvironments] = useState<Environment[]>([])
  const [selectedEnv, setSelectedEnv] = useState<Environment | null>(null)
  const [envVariables, setEnvVariables] = useState<EnvVariable[]>([])
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [newEnvName, setNewEnvName] = useState('')
  const [newEnvBaseUrl, setNewEnvBaseUrl] = useState('')
  const [varDialogOpen, setVarDialogOpen] = useState(false)
  const [editingVar, setEditingVar] = useState<EnvVariable | null>(null)

  // 获取环境列表
  const fetchEnvironments = async () => {
    if (!projectId) return

    try {
      const response = await fetch(`http://localhost:8000/api/v1/environments?project_id=${projectId}`, {
        headers: { Authorization: `Bearer ${token}` },
      })

      if (!response.ok) throw new Error('获取环境列表失败')

      const data = await response.json()
      setEnvironments(data)
    } catch (error) {
      toast('获取环境列表失败', 'error')
    }
  }

  // 获取环境变量
  const fetchEnvVariables = async (envId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/environments/${envId}/variables`, {
        headers: { Authorization: `Bearer ${token}` },
      })

      if (!response.ok) throw new Error('获取环境变量失败')

      const data = await response.json()
      setEnvVariables(data)
    } catch (error) {
      toast('获取环境变量失败', 'error')
    }
  }

  // 创建环境
  const handleCreateEnvironment = async () => {
    if (!newEnvName.trim() || !newEnvBaseUrl.trim() || !projectId) return

    try {
      const response = await fetch('http://localhost:8000/api/v1/environments', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          project_id: projectId,
          name: newEnvName,
          base_url: newEnvBaseUrl,
        }),
      })

      if (!response.ok) throw new Error('创建环境失败')

      toast('创建成功', 'success')
      setCreateDialogOpen(false)
      setNewEnvName('')
      setNewEnvBaseUrl('')
      fetchEnvironments()
    } catch (error) {
      toast('创建失败', 'error')
    }
  }

  // 删除环境
  const handleDeleteEnvironment = async (envId: string) => {
    if (!confirm('确定要删除这个环境吗?')) return

    try {
      const response = await fetch(`http://localhost:8000/api/v1/environments/${envId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      })

      if (!response.ok) throw new Error('删除失败')

      toast('删除成功', 'success')
      if (selectedEnv?.id === envId) {
        setSelectedEnv(null)
        setEnvVariables([])
      }
      fetchEnvironments()
    } catch (error) {
      toast('删除失败', 'error')
    }
  }

  // 创建环境变量
  const handleCreateVariable = async () => {
    if (!editingVar || !selectedEnv) return

    try {
      const response = await fetch(`http://localhost:8000/api/v1/environments/${selectedEnv.id}/variables`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          name: editingVar.name,
          value: editingVar.value,
          description: editingVar.description,
        }),
      })

      if (!response.ok) throw new Error('创建变量失败')

      toast('创建成功', 'success')
      setVarDialogOpen(false)
      setEditingVar(null)
      fetchEnvVariables(selectedEnv.id)
    } catch (error) {
      toast('创建失败', 'error')
    }
  }

  // 删除环境变量
  const handleDeleteVariable = async (varId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/environments/variables/${varId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      })

      if (!response.ok) throw new Error('删除失败')

      toast('删除成功', 'success')
      if (selectedEnv) fetchEnvVariables(selectedEnv.id)
    } catch (error) {
      toast('删除失败', 'error')
    }
  }

  // 选择环境
  const handleSelectEnvironment = (env: Environment) => {
    setSelectedEnv(env)
    fetchEnvVariables(env.id)
  }

  useEffect(() => {
    fetchEnvironments()
  }, [projectId])

  return (
    <div className="flex h-screen bg-background">
      {/* 左侧环境列表 */}
      <div className="w-80 border-r border-border flex flex-col">
        {/* 工具栏 */}
        <div className="p-4 border-b border-border flex items-center justify-between">
          <h2 className="text-lg font-semibold">环境配置</h2>
          <Button size="sm" variant="ghost" onClick={() => setCreateDialogOpen(true)}>
            <Plus className="h-4 w-4 mr-1" />
            新建环境
          </Button>
        </div>

        {/* 环境列表 */}
        <div className="flex-1 overflow-y-auto">
          {environments.map((env) => (
            <div
              key={env.id}
              className={`
                flex items-center justify-between px-4 py-3 cursor-pointer
                hover:bg-accent hover:text-accent-foreground
                ${selectedEnv?.id === env.id ? 'bg-accent' : ''}
              `}
              onClick={() => handleSelectEnvironment(env)}
            >
              <div className="flex items-center gap-2">
                <Globe className="h-4 w-4 text-muted-foreground" />
                <span className="font-medium">{env.name}</span>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={(e) => {
                  e.stopPropagation()
                  handleDeleteEnvironment(env.id)
                }}
              >
                <Trash2 className="h-4 w-4 text-destructive" />
              </Button>
            </div>
          ))}

          {environments.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
              <Server className="h-16 w-16 mb-4 opacity-20" />
              <p>暂无环境配置</p>
              <Button variant="outline" size="sm" className="mt-4" onClick={() => setCreateDialogOpen(true)}>
                创建第一个环境
              </Button>
            </div>
          )}
        </div>
      </div>

      {/* 右侧环境详情 */}
      <div className="flex-1 flex flex-col">
        {selectedEnv ? (
          <>
            {/* 环境基本信息 */}
            <div className="p-6 border-b border-border">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-semibold">{selectedEnv.name}</h3>
                <Button variant="outline" size="sm">
                  <Edit2 className="h-4 w-4 mr-2" />
                  编辑
                </Button>
              </div>
              <div className="space-y-2">
                <div>
                  <span className="text-sm text-muted-foreground">Base URL:</span>
                  <p className="font-mono text-sm">{selectedEnv.base_url}</p>
                </div>
              </div>
            </div>

            {/* 环境变量列表 */}
            <div className="flex-1 overflow-y-auto p-6">
              <div className="flex items-center justify-between mb-4">
                <h4 className="text-lg font-semibold">环境变量</h4>
                <Button size="sm" onClick={() => setVarDialogOpen(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  添加变量
                </Button>
              </div>

              <div className="space-y-2">
                {envVariables.map((variable) => (
                  <div
                    key={variable.id}
                    className="flex items-center gap-4 p-4 border border-border rounded-md"
                  >
                    <div className="flex-1">
                      <div className="font-medium">{variable.name}</div>
                      <div className="text-sm text-muted-foreground font-mono">{variable.value}</div>
                      {variable.description && (
                        <div className="text-xs text-muted-foreground mt-1">{variable.description}</div>
                      )}
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDeleteVariable(variable.id)}
                    >
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  </div>
                ))}

                {envVariables.length === 0 && (
                  <div className="text-center text-muted-foreground py-8">
                    暂无环境变量
                  </div>
                )}
              </div>
            </div>
          </>
        ) : (
          <div className="flex items-center justify-center h-full text-muted-foreground">
            <div className="text-center">
              <Globe className="h-16 w-16 mx-auto mb-4 opacity-20" />
              <p>选择左侧环境查看详情</p>
            </div>
          </div>
        )}
      </div>

      {/* 创建环境对话框 */}
      <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>新建环境</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">环境名称</label>
              <Input
                placeholder="开发/测试/生产"
                value={newEnvName}
                onChange={(e) => setNewEnvName(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Base URL</label>
              <Input
                placeholder="https://api.example.com"
                value={newEnvBaseUrl}
                onChange={(e) => setNewEnvBaseUrl(e.target.value)}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCreateDialogOpen(false)}>
              取消
            </Button>
            <Button onClick={handleCreateEnvironment}>确定</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 添加变量对话框 */}
      <Dialog open={varDialogOpen} onOpenChange={setVarDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>添加环境变量</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">变量名</label>
              <Input
                placeholder="API_KEY"
                value={editingVar?.name || ''}
                onChange={(e) => setEditingVar({ ...editingVar!, name: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">变量值</label>
              <Input
                placeholder="your-api-key-value"
                value={editingVar?.value || ''}
                onChange={(e) => setEditingVar({ ...editingVar!, value: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">描述</label>
              <Input
                placeholder="可选的描述信息"
                value={editingVar?.description || ''}
                onChange={(e) => setEditingVar({ ...editingVar!, description: e.target.value })}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setVarDialogOpen(false)}>
              取消
            </Button>
            <Button onClick={handleCreateVariable}>确定</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
