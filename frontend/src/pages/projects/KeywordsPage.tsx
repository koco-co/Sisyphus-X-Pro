import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Plus, Pencil, Trash2, Eye, Code, Database } from 'lucide-react'
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
import { CodeEditor } from '@/components/editor/CodeEditor'
import type { Keyword, KeywordType } from '@/types/keyword'
import { BUILTIN_KEYWORDS } from '@/types/keyword'

const KEYWORD_TYPE_LABELS: Record<KeywordType, string> = {
  http_request: 'HTTP 请求',
  assertion: '断言类型',
  extract: '提取变量',
  database: '数据库操作',
  custom: '自定义操作',
}

export default function KeywordsPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const navigate = useNavigate()
  const { token } = useAuth()
  const { toast } = useToast()

  const [keywords, setKeywords] = useState<Keyword[]>([])
  const [loading, setLoading] = useState(true)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [editingKeyword, setEditingKeyword] = useState<Keyword | null>(null)
  const [deletingKeyword, setDeletingKeyword] = useState<Keyword | null>(null)
  const [viewingKeyword, setViewingKeyword] = useState<Keyword | null>(null)

  const [formData, setFormData] = useState({
    type: 'custom' as KeywordType,
    name: '',
    method_name: '',
    code: '',
  })

  const fetchKeywords = async () => {
    setLoading(true)
    try {
      const response = await fetch('http://localhost:8000/api/v1/keywords?project_id=' + projectId + '&is_builtin=false', {
        headers: { Authorization: 'Bearer ' + token },
      })

      if (!response.ok) throw new Error('获取关键字列表失败')

      const data = await response.json()
      setKeywords(data)
    } catch (error) {
      toast('获取关键字列表失败', 'error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchKeywords()
  }, [projectId])

  const handleAdd = () => {
    setEditingKeyword(null)
    setFormData({ type: 'custom', name: '', method_name: '', code: '' })
    setDialogOpen(true)
  }

  const handleView = (keyword: Keyword) => {
    setViewingKeyword(keyword)
  }

  const handleEdit = (keyword: Keyword) => {
    if (keyword.is_builtin) {
      toast('内置关键字不可编辑', 'error')
      return
    }
    setEditingKeyword(keyword)
    setFormData({
      type: keyword.type,
      name: keyword.name,
      method_name: keyword.method_name,
      code: keyword.code,
    })
    setDialogOpen(true)
  }

  const handleDeleteClick = (keyword: Keyword) => {
    if (keyword.is_builtin) {
      toast('内置关键字不可删除', 'error')
      return
    }
    setDeletingKeyword(keyword)
    setDeleteDialogOpen(true)
  }

  const handleSubmit = async () => {
    try {
      const url = editingKeyword
        ? 'http://localhost:8000/api/v1/keywords/' + editingKeyword.id
        : 'http://localhost:8000/api/v1/keywords'

      const response = await fetch(url, {
        method: editingKeyword ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Bearer ' + token,
        },
        body: JSON.stringify({ ...formData, project_id: projectId }),
      })

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: '保存失败' }))
        throw new Error(error.detail || '保存失败')
      }

      toast(editingKeyword ? '编辑成功' : '添加成功', 'success')
      setDialogOpen(false)
      fetchKeywords()
    } catch (error) {
      toast(error instanceof Error ? error.message : '保存失败', 'error')
    }
  }

  const handleDelete = async () => {
    if (!deletingKeyword) return

    try {
      const response = await fetch('http://localhost:8000/api/v1/keywords/' + deletingKeyword.id, {
        method: 'DELETE',
        headers: { Authorization: 'Bearer ' + token },
      })

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: '删除失败' }))
        throw new Error(error.detail || '删除失败')
      }

      toast('删除成功', 'success')
      setDeleteDialogOpen(false)
      fetchKeywords()
    } catch (error) {
      toast(error instanceof Error ? error.message : '删除失败', 'error')
    }
  }

  const handleToggleEnabled = async (keyword: Keyword) => {
    try {
      const newEnabled = !keyword.enabled
      const response = await fetch(`http://localhost:8000/api/v1/keywords/${keyword.id}/toggle?is_enabled=${newEnabled}`, {
        method: 'PATCH',
        headers: { Authorization: `Bearer ${token}` },
      })

      if (!response.ok) throw new Error('切换状态失败')

      toast('切换状态成功', 'success')
      fetchKeywords()
    } catch (error) {
      toast('切换状态失败', 'error')
    }
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="border-b bg-card">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm" onClick={() => navigate('/projects/' + projectId)}>
              <ArrowLeft className="h-4 w-4" />
            </Button>
            <div className="flex-1">
              <h1 className="text-3xl font-bold tracking-tight">关键字配置</h1>
              <p className="text-muted-foreground mt-1">配置可扩展的关键字函数</p>
            </div>
            <Button onClick={handleAdd}>
              <Plus className="mr-2 h-4 w-4" />
              新建关键字
            </Button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-8">
        <div>
          <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2">
            <Code className="h-6 w-6" />
            内置关键字
            <Badge className="text-xs">系统预置</Badge>
          </h2>
          <p className="text-muted-foreground mb-4">内置关键字由系统提供,不可编辑或删除</p>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {BUILTIN_KEYWORDS.map((keyword) => (
              <div key={keyword.id} className="bg-card border rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold">{keyword.name}</h3>
                      <Badge className="text-xs">内置</Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">{keyword.method_name}</p>
                  </div>
                  <Button variant="ghost" size="sm" onClick={() => handleView(keyword as Keyword)}>
                    <Eye className="h-4 w-4" />
                  </Button>
                </div>
                {keyword.params && keyword.params.length > 0 && (
                  <div className="space-y-1">
                    <div className="text-xs text-muted-foreground">入参:</div>
                    {keyword.params.map((param, idx) => (
                      <div key={idx} className="text-xs bg-muted/50 px-2 py-1 rounded">
                        <span className="font-medium">{param.name}</span>: {param.description}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        <div>
          <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2">
            <Database className="h-6 w-6" />
            自定义关键字
          </h2>

          <div className="bg-card rounded-lg border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>关键字名称</TableHead>
                  <TableHead>类型</TableHead>
                  <TableHead>方法名</TableHead>
                  <TableHead>状态</TableHead>
                  <TableHead className="text-right">操作</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell className="text-center text-muted-foreground" colSpan={5}>
                      加载中...
                    </TableCell>
                  </TableRow>
                ) : keywords.length === 0 ? (
                  <TableRow>
                    <TableCell className="text-center text-muted-foreground" colSpan={5}>
                      暂无自定义关键字
                    </TableCell>
                  </TableRow>
                ) : (
                  keywords.map((keyword) => (
                    <TableRow key={keyword.id}>
                      <TableCell className="font-medium">{keyword.name}</TableCell>
                      <TableCell>
                        <Badge>{KEYWORD_TYPE_LABELS[keyword.type]}</Badge>
                      </TableCell>
                      <TableCell className="text-muted-foreground">{keyword.method_name}</TableCell>
                      <TableCell>
                        <Switch
                          checked={keyword.enabled}
                          onClick={() => handleToggleEnabled(keyword)}
                        />
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button variant="ghost" size="sm" onClick={() => handleView(keyword)} title="查看">
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="sm" onClick={() => handleEdit(keyword)} title="编辑">
                            <Pencil className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="sm" onClick={() => handleDeleteClick(keyword)} title="删除">
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
      </div>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="max-w-4xl">
          <DialogHeader>
            <DialogTitle>{editingKeyword ? '编辑关键字' : '新建关键字'}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="type">关键字类型 *</Label>
                <Select
                  id="type"
                  value={formData.type}
                  onChange={(e) => setFormData({ ...formData, type: e.target.value as KeywordType })}
                >
                  <option value="http_request">HTTP 请求</option>
                  <option value="assertion">断言类型</option>
                  <option value="extract">提取变量</option>
                  <option value="database">数据库操作</option>
                  <option value="custom">自定义操作</option>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="name">关键字名称 *</Label>
                <Input
                  id="name"
                  placeholder="例如: 自定义断言"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="method_name">方法名 *</Label>
              <Input
                id="method_name"
                placeholder="custom_assertion"
                value={formData.method_name}
                onChange={(e) => setFormData({ ...formData, method_name: e.target.value })}
              />
              <p className="text-xs text-muted-foreground">Python 函数名,使用蛇形命名法</p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="code">代码块 *</Label>
              <CodeEditor
                value={formData.code}
                onChange={(value) => setFormData({ ...formData, code: value || '' })}
                language="python"
                height="300px"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>
              取消
            </Button>
            <Button onClick={handleSubmit}>
              {editingKeyword ? '保存' : '创建'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={!!viewingKeyword} onOpenChange={() => setViewingKeyword(null)}>
        <DialogContent className="max-w-4xl">
          <DialogHeader>
            <DialogTitle>
              {viewingKeyword?.name}
              {viewingKeyword?.is_builtin && <Badge className="ml-2">内置</Badge>}
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-muted-foreground">类型:</span>
                <span className="ml-2">{KEYWORD_TYPE_LABELS[viewingKeyword?.type || 'custom']}</span>
              </div>
              <div>
                <span className="text-muted-foreground">方法名:</span>
                <span className="ml-2">{viewingKeyword?.method_name}</span>
              </div>
            </div>

            {viewingKeyword?.params && viewingKeyword.params.length > 0 && (
              <div className="space-y-2">
                <Label>入参释义</Label>
                <div className="space-y-1">
                  {viewingKeyword.params.map((param, idx) => (
                    <div key={idx} className="text-sm bg-muted/50 px-3 py-2 rounded">
                      <span className="font-medium">{param.name}</span>: {param.description}
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="space-y-2">
              <Label>代码</Label>
              <CodeEditor
                value={viewingKeyword?.code || ''}
                language="python"
                readOnly
                height="400px"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setViewingKeyword(null)}>
              关闭
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>确认删除</DialogTitle>
          </DialogHeader>
          <div className="py-4">
            <p className="text-muted-foreground">
              确定要删除关键字 <span className="font-semibold text-foreground">{deletingKeyword?.name}</span> 吗?
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
