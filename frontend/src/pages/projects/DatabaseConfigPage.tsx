import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Plus, Pencil, Trash2, Check, Loader2 } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { useToast } from '@/hooks/use-toast'
import { apiClient, type PaginatedResponse } from '@/lib/api'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Label } from '@/components/ui/Label'
import { Select } from '@/components/ui/Select'
import { Switch } from '@/components/ui/Switch'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/Dialog'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'

interface DatabaseConfig {
  id: number
  project_id: number
  name: string
  variable_name: string
  db_type: 'mysql' | 'postgresql'
  host: string
  port: number
  database: string
  username: string
  config_display: string
  is_connected: boolean
  is_enabled: boolean
  created_at: string
  last_check_at: string | null
}

interface ProjectInfo {
  id: number
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
    variable_name: '',
    db_type: 'mysql' as 'mysql' | 'postgresql',
    host: '',
    port: 3306,
    database: '',
    username: '',
    password: '',
  })

  // 获取数据库配置列表
  const fetchConfigs = async () => {
    if (!projectId) return

    setLoading(true)
    try {
      const data: PaginatedResponse<DatabaseConfig> = await apiClient.get(
        `/projects/${projectId}/db-configs?page=1&pageSize=100`
      )
      setConfigs(data.items)

      // 获取项目信息
      try {
        const project = await apiClient.get<ProjectInfo>(`/projects/${projectId}`)
        setProjectInfo(project)
      } catch (error) {
        console.error('Failed to fetch project info:', error)
      }
    } catch (error) {
      toast(error instanceof Error ? error.message : '获取数据库配置失败', 'error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchConfigs()
  }, [projectId])

  // 打开新增弹窗
  const handleAdd = () => {
    setEditingConfig(null)
    setFormData({
      name: '',
      variable_name: '',
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
      variable_name: config.variable_name,
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
      const result = await apiClient.post<{ connected: boolean; message: string }>(
        `/projects/${projectId}/db-configs/test-connection`,
        formData
      )

      if (result.connected) {
        toast('连接测试成功', 'success')
        setTestPassed(true)
      } else {
        toast(`连接测试失败: ${result.message}`, 'error')
        setTestPassed(false)
      }
    } catch (error) {
      toast(error instanceof Error ? error.message : '连接测试失败', 'error')
      setTestPassed(false)
    } finally {
      setTesting(false)
    }
  }

  // 提交表单
  const handleSubmit = async () => {
    if (!projectId) return

    if (!testPassed && !editingConfig) {
      toast('请先测试连接', 'error')
      return
    }

    try {
      const payload = editingConfig
        ? formData
        : { ...formData, project_id: parseInt(projectId) }

      if (editingConfig) {
        await apiClient.put(`/projects/${projectId}/db-configs/${editingConfig.id}`, payload)
        toast('编辑成功', 'success')
      } else {
        await apiClient.post(`/projects/${projectId}/db-configs`, payload)
        toast('添加成功', 'success')
      }

      setDialogOpen(false)
      fetchConfigs()
    } catch (error) {
      toast(error instanceof Error ? error.message : (editingConfig ? '编辑失败' : '添加失败'), 'error')
    }
  }

  // 切换启用状态
  const handleToggleEnabled = async (config: DatabaseConfig) => {
    if (!projectId) return

    try {
      await apiClient.patch<DatabaseConfig>(
        `/projects/${projectId}/db-configs/${config.id}/toggle`,
        { is_enabled: !config.is_enabled }
      )
      toast('切换状态成功', 'success')
      fetchConfigs()
    } catch (error) {
      toast(error instanceof Error ? error.message : '切换状态失败', 'error')
    }
  }

  // 删除配置
  const handleDelete = async () => {
    if (!deletingConfig || !projectId) return

    try {
      await apiClient.delete(`/projects/${projectId}/db-configs/${deletingConfig.id}`)
      toast('删除成功', 'success')
      setDeleteDialogOpen(false)
      fetchConfigs()
    } catch (error) {
      toast(error instanceof Error ? error.message : '删除失败', 'error')
    }
  }

  // 获取连接状态徽章
  const getConnectionStatusBadge = (connected: boolean) => {
    if (connected) {
      return <Badge className="bg-green-500 text-white">已连接</Badge>
    }
    return <Badge className="bg-destructive text-destructive-foreground">连接失败</Badge>
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
                        {'{{'}{config.variable_name}{'}}'}
                      </code>
                    </TableCell>
                    <TableCell className="text-muted-foreground">{config.config_display}</TableCell>
                    <TableCell>{getConnectionStatusBadge(config.is_connected)}</TableCell>
                    <TableCell>
                      <Switch
                        checked={config.is_enabled}
                        onCheckedChange={() => handleToggleEnabled(config)}
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
        <DialogContent onClose={() => setDialogOpen(false)} className="max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
          <DialogHeader>
            <DialogTitle>{editingConfig ? '编辑数据库配置' : '新增数据库配置'}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4 overflow-y-auto flex-1">
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
                <Label htmlFor="variable_name">引用变量 *</Label>
                <Input
                  id="variable_name"
                  value={formData.variable_name}
                  onChange={(e) => setFormData({ ...formData, variable_name: e.target.value })}
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
                onChange={(e) =>
                  setFormData({ ...formData, db_type: e.target.value as 'mysql' | 'postgresql' })
                }
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
              确定要删除数据库配置 <span className="font-semibold text-foreground">{deletingConfig?.name}</span>
              吗?
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
