import { useState } from 'react'
import { FilePlus } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { useToast } from '@/hooks/use-toast'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/Dialog'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Textarea } from '@/components/ui/Textarea'
import type { InterfaceItem } from '@/types/interface'

interface InterfaceCreateDialogProps {
  open: boolean
  onClose: () => void
  projectId: string
  folderId: string | null
  onCreateSuccess: () => void
}

export function InterfaceCreateDialog({
  open,
  onClose,
  projectId,
  folderId,
  onCreateSuccess,
}: InterfaceCreateDialogProps) {
  const { token } = useAuth()
  const { toast } = useToast()

  const [name, setName] = useState('')
  const [method, setMethod] = useState<InterfaceItem['method']>('GET')
  const [path, setPath] = useState('')
  const [description, setDescription] = useState('')

  const handleCreate = async () => {
    if (!name.trim() || !path.trim()) {
      toast('请填写完整信息', 'error')
      return
    }

    try {
      const response = await fetch('http://localhost:8000/api/v1/interfaces', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          project_id: projectId,
          folder_id: folderId,
          name,
          method,
          path,
          description,
          headers: {},
          params: {},
          body: {},
          body_type: 'none',
        }),
      })

      if (!response.ok) throw new Error('创建失败')

      toast('创建成功', 'success')
      handleClose()
      onCreateSuccess()
    } catch (error) {
      toast('创建失败', 'error')
    }
  }

  const handleClose = () => {
    setName('')
    setMethod('GET')
    setPath('')
    setDescription('')
    onClose()
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>新建接口</DialogTitle>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* 接口名称 */}
          <div className="space-y-2">
            <label className="text-sm font-medium">接口名称</label>
            <Input
              placeholder="获取用户信息"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>

          {/* 请求方法和路径 */}
          <div className="flex gap-2">
            <div className="w-32 space-y-2">
              <label className="text-sm font-medium">请求方法</label>
              <select
                value={method}
                onChange={(e) => setMethod(e.target.value as InterfaceItem['method'])}
                className="w-full px-3 py-2 bg-background border border-border rounded-md"
              >
                {['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'].map((m) => (
                  <option key={m} value={m}>
                    {m}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex-1 space-y-2">
              <label className="text-sm font-medium">请求路径</label>
              <Input
                placeholder="/api/users"
                value={path}
                onChange={(e) => setPath(e.target.value)}
              />
            </div>
          </div>

          {/* 接口描述 */}
          <div className="space-y-2">
            <label className="text-sm font-medium">接口描述</label>
            <Textarea
              placeholder="简要描述这个接口的作用..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="min-h-[80px]"
            />
          </div>

          {/* 提示信息 */}
          <div className="text-xs text-muted-foreground bg-muted p-3 rounded-md">
            <p>创建后可以在右侧编辑器中配置请求头、参数、请求体等详细信息</p>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={handleClose}>
            取消
          </Button>
          <Button onClick={handleCreate} disabled={!name.trim() || !path.trim()}>
            <FilePlus className="h-4 w-4 mr-2" />
            创建
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
