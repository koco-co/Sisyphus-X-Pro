import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { Plus, Trash2, Variable } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { useToast } from '@/hooks/use-toast'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/Dialog'
import type { GlobalVariable } from '@/types/environment'

export function GlobalVariablesPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const { token } = useAuth()
  const { toast } = useToast()

  const [variables, setVariables] = useState<GlobalVariable[]>([])
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [newVarName, setNewVarName] = useState('')
  const [newVarValue, setNewVarValue] = useState('')
  const [newVarDescription, setNewVarDescription] = useState('')

  // 获取全局变量列表
  const fetchVariables = async () => {
    if (!projectId) return

    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/environments/global/variables?project_id=${projectId}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      )

      if (!response.ok) throw new Error('获取全局变量失败')

      const data = await response.json()
      setVariables(data)
    } catch (error) {
      toast('获取全局变量失败', 'error')
    }
  }

  // 创建全局变量
  const handleCreateVariable = async () => {
    if (!newVarName.trim() || !newVarValue.trim() || !projectId) return

    try {
      const response = await fetch('http://localhost:8000/api/v1/environments/global/variables', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          project_id: projectId,
          name: newVarName,
          value: newVarValue,
          description: newVarDescription,
        }),
      })

      if (!response.ok) throw new Error('创建全局变量失败')

      toast('创建成功', 'success')
      setCreateDialogOpen(false)
      setNewVarName('')
      setNewVarValue('')
      setNewVarDescription('')
      fetchVariables()
    } catch (error) {
      toast('创建失败', 'error')
    }
  }

  // 删除全局变量
  const handleDeleteVariable = async (varId: string) => {
    if (!confirm('确定要删除这个全局变量吗?')) return

    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/environments/global/variables/${varId}`,
        {
          method: 'DELETE',
          headers: { Authorization: `Bearer ${token}` },
        }
      )

      if (!response.ok) throw new Error('删除失败')

      toast('删除成功', 'success')
      fetchVariables()
    } catch (error) {
      toast('删除失败', 'error')
    }
  }

  useEffect(() => {
    fetchVariables()
  }, [projectId])

  return (
    <div className="container mx-auto py-6">
      {/* 页面标题和操作 */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">全局变量</h1>
          <p className="text-muted-foreground">管理项目中所有场景共享的全局变量</p>
        </div>
        <Button onClick={() => setCreateDialogOpen(true)}>
          <Plus className="h-4 w-4 mr-2" />
          添加变量
        </Button>
      </div>

      {/* 变量列表 */}
      <div className="border border-border rounded-md">
        {variables.map((variable) => (
          <div
            key={variable.id}
            className="flex items-center justify-between p-4 border-b border-border last:border-b-0"
          >
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <span className="font-medium">{variable.name}</span>
                <span className="text-xs text-muted-foreground bg-muted px-2 py-0.5 rounded">
                  {variable.source}
                </span>
              </div>
              <div className="font-mono text-sm text-muted-foreground">{variable.value}</div>
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

        {variables.length === 0 && (
          <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
            <Variable className="h-16 w-16 mb-4 opacity-20" />
            <p className="mb-4">暂无全局变量</p>
            <Button variant="outline" onClick={() => setCreateDialogOpen(true)}>
              创建第一个变量
            </Button>
          </div>
        )}
      </div>

      {/* 使用说明 */}
      <div className="mt-6 p-4 bg-muted rounded-md">
        <h3 className="font-medium mb-2">使用说明</h3>
        <ul className="text-sm text-muted-foreground space-y-1 list-disc list-inside">
          <li>全局变量在项目中所有场景和接口中可用</li>
          <li>在接口定义中通过 {'{{变量名}}'} 引用全局变量</li>
          <li>变量按创建顺序依次替换,请确保变量名不冲突</li>
          <li>来源为 "extracted" 的变量是由系统自动提取的</li>
        </ul>
      </div>

      {/* 创建变量对话框 */}
      <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>添加全局变量</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">变量名</label>
              <Input
                placeholder="API_BASE_URL"
                value={newVarName}
                onChange={(e) => setNewVarName(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">变量值</label>
              <Input
                placeholder="https://api.example.com"
                value={newVarValue}
                onChange={(e) => setNewVarValue(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">描述</label>
              <Input
                placeholder="API 基础地址"
                value={newVarDescription}
                onChange={(e) => setNewVarDescription(e.target.value)}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCreateDialogOpen(false)}>
              取消
            </Button>
            <Button onClick={handleCreateVariable}>确定</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
