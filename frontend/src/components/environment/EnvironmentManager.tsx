import { useState, useEffect } from 'react'
import { Plus, Trash2, Edit2, Globe } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { useToast } from '@/hooks/use-toast'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Label } from '@/components/ui/Label'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/Dialog'
import { Switch } from '@/components/ui/Switch'
import type { Environment, EnvironmentVariable, GlobalVariable } from '@/types/environment'

interface EnvironmentManagerProps {
  projectId: string
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function EnvironmentManager({ projectId, open, onOpenChange }: EnvironmentManagerProps) {
  const { token } = useAuth()
  const { toast } = useToast()

  const [environments, setEnvironments] = useState<Environment[]>([])
  const [envVars, setEnvVars] = useState<Record<string, EnvironmentVariable[]>>({})
  const [globalVars, setGlobalVars] = useState<GlobalVariable[]>([])

  const [activeTab, setActiveTab] = useState<'env' | 'global'>('env')
  const [editingEnv, setEditingEnv] = useState<Environment | null>(null)
  const [envDialogOpen, setEnvDialogOpen] = useState(false)

  // 表单状态
  const [envForm, setEnvForm] = useState({
    name: '',
    base_url: '',
    is_default: false,
  })

  const [varForm, setVarForm] = useState({
    key: '',
    value: '',
    description: '',
    env_id: '',
  })

  // 获取环境列表
  const fetchEnvironments = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/environments?project_id=${projectId}`, {
        headers: { Authorization: `Bearer ${token}` },
      })

      if (!response.ok) throw new Error('获取环境列表失败')

      const data = await response.json()
      setEnvironments(data)

      // 获取每个环境的变量
      for (const env of data) {
        fetchEnvVars(env.id)
      }
    } catch (error) {
      toast('获取环境列表失败', 'error')
    }
  }

  // 获取环境变量
  const fetchEnvVars = async (envId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/env-vars?env_id=${envId}`, {
        headers: { Authorization: `Bearer ${token}` },
      })

      if (!response.ok) return

      const data = await response.json()
      setEnvVars((prev) => ({ ...prev, [envId]: data }))
    } catch (error) {
      console.error('获取环境变量失败', error)
    }
  }

  // 获取全局变量
  const fetchGlobalVars = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/global-vars?project_id=${projectId}`, {
        headers: { Authorization: `Bearer ${token}` },
      })

      if (!response.ok) return

      const data = await response.json()
      setGlobalVars(data)
    } catch (error) {
      console.error('获取全局变量失败', error)
    }
  }

  useEffect(() => {
    if (open) {
      fetchEnvironments()
      fetchGlobalVars()
    }
  }, [open, projectId])

  // 新增/编辑环境
  const handleSaveEnv = async () => {
    try {
      const url = editingEnv
        ? `http://localhost:8000/api/v1/environments/${editingEnv.id}`
        : 'http://localhost:8000/api/v1/environments'

      const response = await fetch(url, {
        method: editingEnv ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          ...envForm,
          project_id: projectId,
        }),
      })

      if (!response.ok) throw new Error('保存环境失败')

      toast('保存成功', 'success')
      setEnvDialogOpen(false)
      setEditingEnv(null)
      setEnvForm({ name: '', base_url: '', is_default: false })
      fetchEnvironments()
    } catch (error) {
      toast('保存失败', 'error')
    }
  }

  // 删除环境
  const handleDeleteEnv = async (envId: string) => {
    if (!confirm('确定要删除这个环境吗?')) return

    try {
      const response = await fetch(`http://localhost:8000/api/v1/environments/${envId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      })

      if (!response.ok) throw new Error('删除环境失败')

      toast('删除成功', 'success')
      fetchEnvironments()
    } catch (error) {
      toast('删除失败', 'error')
    }
  }

  // 新增环境变量
  const handleAddEnvVar = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/env-vars', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(varForm),
      })

      if (!response.ok) throw new Error('添加变量失败')

      toast('添加成功', 'success')
      setVarForm({ key: '', value: '', description: '', env_id: '' })
      fetchEnvVars(varForm.env_id)
    } catch (error) {
      toast('添加失败', 'error')
    }
  }

  // 删除环境变量
  const handleDeleteEnvVar = async (varId: string, envId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/env-vars/${varId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      })

      if (!response.ok) throw new Error('删除变量失败')

      toast('删除成功', 'success')
      fetchEnvVars(envId)
    } catch (error) {
      toast('删除失败', 'error')
    }
  }

  // 新增全局变量
  const handleAddGlobalVar = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/global-vars', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          ...varForm,
          project_id: projectId,
        }),
      })

      if (!response.ok) throw new Error('添加变量失败')

      toast('添加成功', 'success')
      setVarForm({ key: '', value: '', description: '', env_id: '' })
      fetchGlobalVars()
    } catch (error) {
      toast('添加失败', 'error')
    }
  }

  // 删除全局变量
  const handleDeleteGlobalVar = async (varId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/global-vars/${varId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      })

      if (!response.ok) throw new Error('删除变量失败')

      toast('删除成功', 'success')
      fetchGlobalVars()
    } catch (error) {
      toast('删除失败', 'error')
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>环境管理</DialogTitle>
        </DialogHeader>

        {/* Tab 切换 */}
        <div className="flex gap-4 border-b">
          <button
            onClick={() => setActiveTab('env')}
            className={`flex-1 pb-3 text-sm font-medium transition-colors ${
              activeTab === 'env' ? 'text-primary border-b-2 border-primary' : 'text-muted-foreground'
            }`}
          >
            环境变量
          </button>
          <button
            onClick={() => setActiveTab('global')}
            className={`flex-1 pb-3 text-sm font-medium transition-colors ${
              activeTab === 'global' ? 'text-primary border-b-2 border-primary' : 'text-muted-foreground'
            }`}
          >
            全局变量
          </button>
        </div>

        {activeTab === 'env' ? (
          <div className="space-y-6 py-4">
            {/* 环境列表 */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">环境列表</h3>
                <Button size="sm" onClick={() => { setEnvDialogOpen(true); setEditingEnv(null) }}>
                  <Plus className="mr-2 h-4 w-4" />
                  新建环境
                </Button>
              </div>

              <div className="space-y-3">
                {environments.map((env) => (
                  <div key={env.id} className="border rounded-lg p-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Globe className="h-5 w-5 text-muted-foreground" />
                        <div>
                          <div className="font-medium">{env.name}</div>
                          <div className="text-sm text-muted-foreground">{env.base_url}</div>
                        </div>
                        {env.is_default && (
                          <span className="text-xs bg-primary/10 text-primary px-2 py-1 rounded">
                            默认
                          </span>
                        )}
                      </div>
                      <div className="flex gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => { setEditingEnv(env); setEnvForm({ name: env.name, base_url: env.base_url, is_default: env.is_default }); setEnvDialogOpen(true) }}
                        >
                          <Edit2 className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="sm" onClick={() => handleDeleteEnv(env.id)}>
                          <Trash2 className="h-4 w-4 text-destructive" />
                        </Button>
                      </div>
                    </div>

                    {/* 环境变量列表 */}
                    <div className="pl-8 space-y-2">
                      <div className="text-sm text-muted-foreground">环境变量</div>
                      {envVars[env.id]?.map((envVar) => (
                        <div key={envVar.id} className="flex items-center justify-between text-sm bg-muted/50 p-2 rounded">
                          <div className="flex-1">
                            <span className="font-medium">{envVar.key}</span>
                            <span className="text-muted-foreground mx-2">=</span>
                            <span className="text-muted-foreground">{envVar.value}</span>
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDeleteEnvVar(envVar.id, env.id)}
                          >
                            <Trash2 className="h-3 w-3 text-destructive" />
                          </Button>
                        </div>
                      )) || <div className="text-sm text-muted-foreground">暂无变量</div>}

                      {/* 添加环境变量 */}
                      <div className="flex gap-2">
                        <Input
                          placeholder="变量名"
                          value={varForm.env_id === env.id ? varForm.key : ''}
                          onChange={(e) => setVarForm({ ...varForm, key: e.target.value, env_id: env.id })}
                          className="flex-1"
                        />
                        <Input
                          placeholder="变量值"
                          value={varForm.env_id === env.id ? varForm.value : ''}
                          onChange={(e) => setVarForm({ ...varForm, value: e.target.value, env_id: env.id })}
                          className="flex-1"
                        />
                        <Button size="sm" onClick={handleAddEnvVar}>
                          <Plus className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-4 py-4">
            <h3 className="text-lg font-semibold">全局变量</h3>
            <p className="text-sm text-muted-foreground">全局变量在所有环境中可用</p>

            <div className="space-y-2">
              {globalVars.map((globalVar) => (
                <div key={globalVar.id} className="flex items-center justify-between text-sm bg-muted/50 p-3 rounded">
                  <div className="flex-1">
                    <div className="font-medium">{globalVar.key}</div>
                    <div className="text-muted-foreground">{globalVar.value}</div>
                    {globalVar.description && (
                      <div className="text-xs text-muted-foreground mt-1">{globalVar.description}</div>
                    )}
                  </div>
                  <Button variant="ghost" size="sm" onClick={() => handleDeleteGlobalVar(globalVar.id)}>
                    <Trash2 className="h-4 w-4 text-destructive" />
                  </Button>
                </div>
              ))}
            </div>

            {/* 添加全局变量表单 */}
            <div className="space-y-2 pt-4 border-t">
              <div className="grid grid-cols-2 gap-2">
                <Input
                  placeholder="变量名"
                  value={varForm.key}
                  onChange={(e) => setVarForm({ ...varForm, key: e.target.value })}
                />
                <Input
                  placeholder="变量值"
                  value={varForm.value}
                  onChange={(e) => setVarForm({ ...varForm, value: e.target.value })}
                />
              </div>
              <Input
                placeholder="描述 (可选)"
                value={varForm.description}
                onChange={(e) => setVarForm({ ...varForm, description: e.target.value })}
              />
              <Button onClick={handleAddGlobalVar} className="w-full">
                <Plus className="mr-2 h-4 w-4" />
                添加全局变量
              </Button>
            </div>
          </div>
        )}

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            关闭
          </Button>
        </DialogFooter>
      </DialogContent>

      {/* 新增/编辑环境弹窗 */}
      <Dialog open={envDialogOpen} onOpenChange={setEnvDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editingEnv ? '编辑环境' : '新建环境'}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="env-name">环境名称 *</Label>
              <Input
                id="env-name"
                placeholder="例如: 生产环境"
                value={envForm.name}
                onChange={(e) => setEnvForm({ ...envForm, name: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="env-base-url">前置 URL *</Label>
              <Input
                id="env-base-url"
                placeholder="https://api.example.com"
                value={envForm.base_url}
                onChange={(e) => setEnvForm({ ...envForm, base_url: e.target.value })}
              />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="env-default">设为默认环境</Label>
              <Switch
                id="env-default"
                checked={envForm.is_default}
                onClick={() => setEnvForm({ ...envForm, is_default: !envForm.is_default })}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setEnvDialogOpen(false)}>
              取消
            </Button>
            <Button onClick={handleSaveEnv}>
              保存
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </Dialog>
  )
}
