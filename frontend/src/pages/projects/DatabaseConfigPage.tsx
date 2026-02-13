import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Plus, Pencil, Trash2, Check, Loader2 } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { useToast } from '@/hooks/use-toast'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Label } from '@/components/ui/Label'
import { Select } from '@/components/ui/Select'
import { Switch } from '@/components/ui/Switch'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/Dialog'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'

interface DatabaseConfig {
  id: string
  project_id: string
  name: string
  variable: string
  db_type: 'mysql' | 'postgresql'
  host: string
  port: number
  database: string
  username: string
  enabled: boolean
  connection_status: 'connected' | 'failed' | 'testing'
  created_at: string
  updated_at: string
}

interface ProjectInfo {
  id: string
  name: string
}

export default function DatabaseConfigPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const navigate = useNavigate()
  const { token } = useAuth()
  const { toast } = useToast()

  const [configs, setConfigs] = useState<DatabaseConfig[]>([])
  const [projectInfo, setProjectInfo] = useState<ProjectInfo | null>(null)
  const [loading, setLoading] = useState(true)

  // 弹窗状态
  const [dialogOpen, setDialogOpen] = useState(false)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [editingConfig, setEditingConfig] = useState<DatabaseConfig | null>(null)
  const [deletingConfig, setDeletingConfig] = useState<DatabaseConfig | null>(null)
  const [testing, setTesting] = useState(false)
  const [testPassed, setTestPassed] = useState(false)

  // 表单数据
  const [formData, setFormData] = useState({
    name: '',
    variable: '',
    db_type: 'mysql' as 'mysql' | 'postgresql',
    host: '',
    port: 3306,
    database: '',
    username: '',
    password: '',
  })

  // 获取数据库配置列表
  const fetchConfigs = async () => {
    setLoading(true)
    try {
      const response = await fetch(`http://localhost:8000/api/v1/db-configs?project_id=${projectId}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (!response.ok) throw new Error('获取数据库配置失败')

      const data = await response.json()
      setConfigs(data.data)

      // 获取项目信息
      const projectRes = await fetch(`http://localhost:8000/api/v1/projects/${projectId}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (projectRes.ok) {
        const projectData = await projectRes.json()
        setProjectInfo(projectData)
      }
    } catch (error) {
      toast('获取数据库配置失败', 'error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchConfigs()

    // 设置定时刷新连接状态 (每10分钟)
    const interval = setInterval(() => {
      fetchConfigs()
    }, 10 * 60 * 1000)

    return () => clearInterval(interval)
  }, [projectId])

  // 打开新增弹窗
  const handleAdd = () => {
    setEditingConfig(null)
    setFormData({
      name: '',
      variable: '',
      db_type: 'mysql',
      host: '',
      port: 3306,
      database: '',
      username: '',
      password: '',
    })
    setTestPassed(false)
    setDialogOpen(true)
  }

  // 打开编辑弹窗
  const handleEdit = (config: DatabaseConfig) => {
    setEditingConfig(config)
    setFormData({
      name: config.name,
      variable: config.variable,
      db_type: config.db_type,
      host: config.host,
      port: config.port,
      database: config.database,
      username: config.username,
      password: '',
    })
    setTestPassed(false)
    setDialogOpen(true)
  }

  // 打开删除确认弹窗
  const handleDeleteClick = (config: DatabaseConfig) => {
    setDeletingConfig(config)
    setDeleteDialogOpen(true)
  }

  // 测试连接
  const handleTestConnection = async () => {
    setTesting(true)
    try {
      const response = await fetch('http://localhost:8000/api/v1/db-configs/test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      })

      if (!response.ok) throw new Error('连接测试失败')

      const data = await response.json()
      if (data.data.success) {
        toast('连接测试成功', 'success')
        setTestPassed(true)
      } else {
        toast(`连接测试失败: ${data.data.message}`, 'error')
        setTestPassed(false)
      }
    } catch (error) {
      toast('连接测试失败', 'error')
      setTestPassed(false)
    } finally {
      setTesting(false)
    }
  }

  // 提交表单
  const handleSubmit = async () => {
    if (!testPassed && !editingConfig) {
      toast('请先测试连接', 'error')
      return
    }

    try {
      const url = editingConfig
        ? `http://localhost:8000/api/v1/db-configs/${editingConfig.id}`
        : 'http://localhost:8000/api/v1/db-configs'

      const payload = editingConfig
        ? { ...formData, project_id: projectId }
        : { ...formData, project_id: projectId }

      const response = await fetch(url, {
        method: editingConfig ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) throw new Error(editingConfig ? '编辑失败' : '创建失败')

      toast(editingConfig ? '编辑成功' : '添加成功', 'success')
      setDialogOpen(false)
      fetchConfigs()
    } catch (error) {
      toast(editingConfig ? '编辑失败' : '添加失败', 'error')
    }
  }

  // 切换启用状态
  const handleToggleEnabled = async (config: DatabaseConfig) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/db-configs/${config.id}/toggle`, {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (!response.ok) throw new Error('切换状态失败')

      toast('切换状态成功', 'success')
      fetchConfigs()
    } catch (error) {
      toast('切换状态失败', 'error')
    }
  }

  // 删除配置
  const handleDelete = async () => {
    if (!deletingConfig) return

    try {
      const response = await fetch(`http://localhost:8000/api/v1/db-configs/${deletingConfig.id}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (!response.ok) throw new Error('删除失败')

      toast('删除成功', 'success')
      setDeleteDialogOpen(false)
      fetchConfigs()
    } catch (error) {
      toast('删除失败', 'error')
    }
  }

  // 获取连接状态徽章
  const getConnectionStatusBadge = (status: DatabaseConfig['connection_status']) => {
    const statusMap = {
      connected: { label: '已连接', className: 'bg-green-500 text-white' },
      failed: { label: '连接失败', className: 'bg-destructive text-destructive-foreground' },
      testing: { label: '测试中', className: 'bg-yellow-500 text-white' },
    }

    const { label, className } = statusMap[status]
    return <Badge className={className}>{label}</Badge>
  }

  return (
    <div className="min-h-screen bg-background">
      {/* 页面头部 */}
      <div className="border-b bg-card">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm" onClick={() => navigate('/projects')}>
              <ArrowLeft className="h-4 w-4" />
            </Button>
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <h1 className="text-3xl font-bold tracking-tight">数据库配置</h1>
                {projectInfo && (
                  <>
                    <span className="text-muted-foreground">/</span>
                    <span className="text-muted-foreground">{projectInfo.name}</span>
                  </>
                )}
              </div>
              <p className="text-muted-foreground mt-1">配置项目的数据库连接信息</p>
            </div>
            <Button onClick={handleAdd}>
              <Plus className="mr-2 h-4 w-4" />
              新增配置
            </Button>
          </div>
        </div>
      </div>

      {/* 配置列表 */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="bg-card rounded-lg border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>连接名称</TableHead>
                <TableHead>引用变量</TableHead>
                <TableHead>配置信息</TableHead>
                <TableHead>连接状态</TableHead>
                <TableHead>启用状态</TableHead>
                <TableHead className="text-right">操作</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell className="text-center text-muted-foreground" colSpan={6}>
                    加载中...
                  </TableCell>
                </TableRow>
              ) : configs.length === 0 ? (
                <TableRow>
                  <TableCell className="text-center text-muted-foreground" colSpan={6}>
                    暂无数据库配置
                  </TableCell>
                </TableRow>
              ) : (
                configs.map((config) => (
                  <TableRow key={config.id}>
                    <TableCell className="font-medium">{config.name}</TableCell>
                    <TableCell>
                      <code className="text-sm bg-muted px-2 py-1 rounded">
                        {'{{'}{config.variable}{'}}'}
                      </code>
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {config.host}:{config.port}/{config.database}
                    </TableCell>
                    <TableCell>{getConnectionStatusBadge(config.connection_status)}</TableCell>
                    <TableCell>
                      <Switch
                        checked={config.enabled}
                        onClick={() => handleToggleEnabled(config)}
                      />
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleEdit(config)}
                          title="编辑"
                        >
                          <Pencil className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDeleteClick(config)}
                          title="删除"
                        >
                          <Trash2 className="h-4 w-4 text-destructive" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </div>

      {/* 新增/编辑弹窗 */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent onClose={() => setDialogOpen(false)} className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>{editingConfig ? '编辑数据库配置' : '新增数据库配置'}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4 max-h-[60vh] overflow-y-auto">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="name">连接名称 *</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="例如: 生产数据库"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="variable">引用变量 *</Label>
                <Input
                  id="variable"
                  value={formData.variable}
                  onChange={(e) => setFormData({ ...formData, variable: e.target.value })}
                  placeholder="例如: prod_db"
                />
                <p className="text-xs text-muted-foreground">在 YAML 中通过 {'{{'}变量名{'}}'} 引用</p>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="db_type">数据库类型 *</Label>
              <Select
                id="db_type"
                value={formData.db_type}
                onChange={(e) => setFormData({ ...formData, db_type: e.target.value as 'mysql' | 'postgresql' })}
              >
                <option value="mysql">MySQL</option>
                <option value="postgresql">PostgreSQL</option>
              </Select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="host">主机 *</Label>
                <Input
                  id="host"
                  value={formData.host}
                  onChange={(e) => setFormData({ ...formData, host: e.target.value })}
                  placeholder="localhost"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="port">端口 *</Label>
                <Input
                  id="port"
                  type="number"
                  value={formData.port}
                  onChange={(e) => setFormData({ ...formData, port: parseInt(e.target.value) })}
                  placeholder={formData.db_type === 'mysql' ? '3306' : '5432'}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="database">初始数据库 *</Label>
              <Input
                id="database"
                value={formData.database}
                onChange={(e) => setFormData({ ...formData, database: e.target.value })}
                placeholder="数据库名称"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="username">用户名 *</Label>
                <Input
                  id="username"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  placeholder="数据库用户名"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">密码 *</Label>
                <Input
                  id="password"
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  placeholder={editingConfig ? '留空则不修改密码' : '数据库密码'}
                />
              </div>
            </div>

            {/* 测试连接按钮和状态 */}
            <div className="flex items-center gap-4 pt-4 border-t">
              <Button
                type="button"
                variant="outline"
                onClick={handleTestConnection}
                disabled={testing}
              >
                {testing ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    测试中
                  </>
                ) : (
                  <>
                    <Check className="mr-2 h-4 w-4" />
                    测试连接
                  </>
                )}
              </Button>
              {testPassed && (
                <div className="flex items-center gap-2 text-sm text-green-600">
                  <Check className="h-4 w-4" />
                  连接成功,可以保存
                </div>
              )}
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>
              取消
            </Button>
            <Button onClick={handleSubmit} disabled={!testPassed && !editingConfig}>
              {editingConfig ? '保存' : '创建'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 删除确认弹窗 */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent onClose={() => setDeleteDialogOpen(false)}>
          <DialogHeader>
            <DialogTitle>确认删除</DialogTitle>
          </DialogHeader>
          <div className="py-4">
            <p className="text-muted-foreground">
              确定要删除数据库配置 <span className="font-semibold text-foreground">{deletingConfig?.name}</span> 吗?
              <br />
              此操作不可撤销。
            </p>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteDialogOpen(false)}>
              取消
            </Button>
            <Button variant="destructive" onClick={handleDelete}>
              删除
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
