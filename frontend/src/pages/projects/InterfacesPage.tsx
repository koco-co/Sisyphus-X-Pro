import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
} from '@dnd-kit/core'
import type { DragEndEvent } from '@dnd-kit/core'
import { arrayMove, SortableContext, sortableKeyboardCoordinates, useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { Plus, Folder, File, ChevronRight, ChevronDown, Play, Trash2, Terminal } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { useToast } from '@/hooks/use-toast'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/Dialog'
import { CurlImportDialog } from '@/components/CurlImportDialog'
import type { InterfaceFolder, InterfaceItem, TreeNode } from '@/types/interface'

export function InterfacesPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const { token } = useAuth()
  const { toast } = useToast()

  const [treeData, setTreeData] = useState<TreeNode[]>([])
  const [selectedNode, setSelectedNode] = useState<TreeNode | null>(null)
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set())
  const [newFolderDialogOpen, setNewFolderDialogOpen] = useState(false)
  const [newFolderName, setNewFolderName] = useState('')
  const [curlDialogOpen, setCurlDialogOpen] = useState(false)

  // 拖拽传感器
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  )

  // 获取目录树数据
  const fetchTreeData = async () => {
    if (!projectId) return

    try {
      const response = await fetch(`http://localhost:8000/api/v1/interface-folders?project_id=${projectId}`, {
        headers: { Authorization: `Bearer ${token}` },
      })

      if (!response.ok) throw new Error('获取目录树失败')

      const folders: InterfaceFolder[] = await response.json()

      // 获取接口列表
      const interfacesResponse = await fetch(`http://localhost:8000/api/v1/interfaces?project_id=${projectId}`, {
        headers: { Authorization: `Bearer ${token}` },
      })

      const interfaces: InterfaceItem[] = interfacesResponse.ok ? await interfacesResponse.json() : []

      // 构建树形结构
      const tree = buildTree(folders, interfaces)
      setTreeData(tree)
    } catch (error) {
      toast('获取接口列表失败', 'error')
    }
  }

  // 构建树形结构
  const buildTree = (folders: InterfaceFolder[], interfaces: InterfaceItem[]): TreeNode[] => {
    const folderMap = new Map<string, TreeNode>()
    const rootNodes: TreeNode[] = []

    // 先创建所有文件夹节点
    folders.forEach((folder) => {
      folderMap.set(folder.id, {
        id: folder.id,
        name: folder.name,
        type: 'folder',
        children: [],
        data: folder,
      })
    })

    // 构建文件夹层级关系
    folders.forEach((folder) => {
      const node = folderMap.get(folder.id)!
      if (folder.parent_id) {
        const parent = folderMap.get(folder.parent_id)
        if (parent) {
          parent.children = parent.children || []
          parent.children.push(node)
        }
      } else {
        rootNodes.push(node)
      }
    })

    // 添加接口到对应文件夹
    interfaces.forEach((iface) => {
      const interfaceNode: TreeNode = {
        id: iface.id,
        name: iface.name,
        type: 'interface',
        method: iface.method,
        data: iface,
      }

      if (iface.folder_id) {
        const folder = folderMap.get(iface.folder_id)
        if (folder) {
          folder.children = folder.children || []
          folder.children.push(interfaceNode)
        }
      } else {
        rootNodes.push(interfaceNode)
      }
    })

    return rootNodes
  }

  // 拖拽结束处理
  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event

    if (over && active.id !== over.id) {
      setTreeData((items) => {
        const oldIndex = items.findIndex((item) => item.id === active.id)
        const newIndex = items.findIndex((item) => item.id === over.id)

        return arrayMove(items, oldIndex, newIndex)
      })
    }
  }

  // 切换展开/折叠
  const toggleNode = (nodeId: string) => {
    setExpandedNodes((prev) => {
      const newSet = new Set(prev)
      if (newSet.has(nodeId)) {
        newSet.delete(nodeId)
      } else {
        newSet.add(nodeId)
      }
      return newSet
    })
  }

  // 创建文件夹
  const handleCreateFolder = async () => {
    if (!newFolderName.trim() || !projectId) return

    try {
      const response = await fetch('http://localhost:8000/api/v1/interface-folders', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          project_id: projectId,
          name: newFolderName,
          parent_id: null,
        }),
      })

      if (!response.ok) throw new Error('创建文件夹失败')

      toast('创建成功', 'success')
      setNewFolderDialogOpen(false)
      setNewFolderName('')
      fetchTreeData()
    } catch (error) {
      toast('创建失败', 'error')
    }
  }

  // 删除节点
  const handleDeleteNode = async (node: TreeNode) => {
    if (!confirm(`确定要删除 ${node.name} 吗?`)) return

    try {
      const endpoint = node.type === 'folder' ? 'interface-folders' : 'interfaces'
      const response = await fetch(`http://localhost:8000/api/v1/${endpoint}/${node.id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      })

      if (!response.ok) throw new Error('删除失败')

      toast('删除成功', 'success')
      fetchTreeData()
      setSelectedNode(null)
    } catch (error) {
      toast('删除失败', 'error')
    }
  }

  useEffect(() => {
    fetchTreeData()
  }, [projectId])

  return (
    <div className="flex h-screen bg-background">
      {/* 左侧目录树 */}
      <div className="w-80 border-r border-border flex flex-col">
        {/* 工具栏 */}
        <div className="p-4 border-b border-border flex items-center justify-between">
          <h2 className="text-lg font-semibold">接口定义</h2>
          <div className="flex gap-2">
            <Button size="sm" variant="ghost" onClick={() => setCurlDialogOpen(true)}>
              <Terminal className="h-4 w-4 mr-1" />
              导入 cURL
            </Button>
            <Button size="sm" variant="ghost" onClick={() => setNewFolderDialogOpen(true)}>
              <Folder className="h-4 w-4 mr-1" />
              新建目录
            </Button>
          </div>
        </div>

        {/* 目录树 */}
        <div className="flex-1 overflow-y-auto p-2">
          <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
            <SortableContext items={treeData.map((node) => node.id)}>
              {treeData.map((node) => (
                <TreeNodeItem
                  key={node.id}
                  node={node}
                  level={0}
                  isExpanded={expandedNodes.has(node.id)}
                  onToggle={() => toggleNode(node.id)}
                  onSelect={setSelectedNode}
                  isSelected={selectedNode?.id === node.id}
                  onDelete={handleDeleteNode}
                />
              ))}
            </SortableContext>
          </DndContext>
        </div>
      </div>

      {/* 右侧编辑器 */}
      <div className="flex-1 flex flex-col">
        {selectedNode ? (
          selectedNode.type === 'interface' ? (
            <InterfaceEditor
              interfaceData={selectedNode.data as InterfaceItem}
              onSave={fetchTreeData}
            />
          ) : (
            <div className="flex items-center justify-center h-full text-muted-foreground">
              请选择接口进行编辑
            </div>
          )
        ) : (
          <div className="flex items-center justify-center h-full text-muted-foreground">
            <div className="text-center">
              <File className="h-16 w-16 mx-auto mb-4 opacity-20" />
              <p>选择左侧目录或接口开始工作</p>
            </div>
          </div>
        )}
      </div>

      {/* 新建目录对话框 */}
      <Dialog open={newFolderDialogOpen} onOpenChange={setNewFolderDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>新建目录</DialogTitle>
          </DialogHeader>
          <div className="py-4">
            <Input
              placeholder="目录名称"
              value={newFolderName}
              onChange={(e) => setNewFolderName(e.target.value)}
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setNewFolderDialogOpen(false)}>
              取消
            </Button>
            <Button onClick={handleCreateFolder}>确定</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* cURL 导入对话框 */}
      {projectId && (
        <CurlImportDialog
          open={curlDialogOpen}
          onClose={() => setCurlDialogOpen(false)}
          projectId={projectId}
          folderId={selectedNode?.type === 'folder' ? selectedNode.id : null}
          onImportSuccess={() => {
            fetchTreeData()
          }}
        />
      )}
    </div>
  )
}

// 树节点项组件
interface TreeNodeItemProps {
  node: TreeNode
  level: number
  isExpanded: boolean
  onToggle: () => void
  onSelect: (node: TreeNode) => void
  isSelected: boolean
  onDelete: (node: TreeNode) => void
}

function TreeNodeItem({
  node,
  level,
  isExpanded,
  onToggle,
  onSelect,
  isSelected,
  onDelete,
}: TreeNodeItemProps) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: node.id,
  })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  }

  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    onSelect(node)
  }

  const handleToggle = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (node.type === 'folder') {
      onToggle()
    }
  }

  return (
    <div>
      <div
        ref={setNodeRef}
        className={`
          flex items-center gap-2 px-2 py-1.5 rounded-md cursor-pointer
          hover:bg-accent hover:text-accent-foreground
          ${isSelected ? 'bg-accent' : ''}
          ${isDragging ? 'opacity-50' : ''}
        `}
        style={{
          paddingLeft: `${level * 16 + 8}px`,
          ...style,
        }}
        onClick={handleClick}
        {...attributes}
        {...listeners}
      >
        {/* 展开/折叠图标 */}
        {node.type === 'folder' && (
          <button
            onClick={handleToggle}
            className="p-0.5 hover:bg-accent rounded"
          >
            {isExpanded ? (
              <ChevronDown className="h-4 w-4" />
            ) : (
              <ChevronRight className="h-4 w-4" />
            )}
          </button>
        )}

        {/* 文件夹/接口图标 */}
        {node.type === 'folder' ? (
          <Folder className="h-4 w-4 text-muted-foreground" />
        ) : (
          <MethodBadge method={node.method!} />
        )}

        {/* 名称 */}
        <span className="flex-1 truncate text-sm">{node.name}</span>

        {/* 删除按钮 */}
        <button
          onClick={(e) => {
            e.stopPropagation()
            onDelete(node)
          }}
          className="p-1 hover:bg-destructive hover:text-destructive-foreground rounded opacity-0 group-hover:opacity-100"
        >
          <Trash2 className="h-3 w-3" />
        </button>
      </div>

      {/* 子节点 */}
      {node.type === 'folder' && isExpanded && node.children && (
        <div>
          {node.children.map((child) => (
            <TreeNodeItem
              key={child.id}
              node={child}
              level={level + 1}
              isExpanded={false}
              onToggle={() => {}}
              onSelect={onSelect}
              isSelected={isSelected}
              onDelete={onDelete}
            />
          ))}
        </div>
      )}
    </div>
  )
}

// 方法标签组件
function MethodBadge({ method }: { method: InterfaceItem['method'] }) {
  const colors: Record<InterfaceItem['method'], string> = {
    GET: 'bg-green-500',
    POST: 'bg-blue-500',
    PUT: 'bg-yellow-500',
    DELETE: 'bg-red-500',
    PATCH: 'bg-orange-500',
    HEAD: 'bg-purple-500',
    OPTIONS: 'bg-pink-500',
  }

  return (
    <span className={`
      px-1.5 py-0.5 rounded text-xs font-medium text-white
      ${colors[method]}
    `}>
      {method}
    </span>
  )
}

// 接口编辑器组件
interface InterfaceEditorProps {
  interfaceData: InterfaceItem
  onSave: () => void
}

function InterfaceEditor({ interfaceData, onSave }: InterfaceEditorProps) {
  const { token } = useAuth()
  const { toast } = useToast()

  const [formData, setFormData] = useState<InterfaceItem>(interfaceData)
  const [activeTab, setActiveTab] = useState<
    'basic' | 'params' | 'headers' | 'body' | 'response'
  >('basic')

  const handleSave = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/interfaces/${formData.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      })

      if (!response.ok) throw new Error('保存失败')

      toast('保存成功', 'success')
      onSave()
    } catch (error) {
      toast('保存失败', 'error')
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* 工具栏 */}
      <div className="p-4 border-b border-border flex items-center justify-between">
        <div className="flex items-center gap-3">
          <MethodBadge method={formData.method} />
          <Input
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            className="border-none text-lg font-semibold focus-visible:ring-0 px-0"
          />
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <Play className="h-4 w-4 mr-2" />
            发送
          </Button>
          <Button size="sm" onClick={handleSave}>
            保存
          </Button>
        </div>
      </div>

      {/* Tab 切换 */}
      <div className="flex border-b border-border">
        {[
          { key: 'basic', label: '基础信息' },
          { key: 'params', label: '请求参数' },
          { key: 'headers', label: '请求头' },
          { key: 'body', label: '请求体' },
          { key: 'response', label: '响应结果' },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key as any)}
            className={`
              px-4 py-2 text-sm font-medium transition-colors
              ${activeTab === tab.key
                ? 'text-primary border-b-2 border-primary'
                : 'text-muted-foreground hover:text-foreground'
              }
            `}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab 内容 */}
      <div className="flex-1 overflow-y-auto p-4">
        {activeTab === 'basic' && (
          <div className="space-y-4 max-w-2xl">
            <div className="space-y-2">
              <label className="text-sm font-medium">接口名称</label>
              <Input
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">请求方法</label>
              <select
                value={formData.method}
                onChange={(e) => setFormData({ ...formData, method: e.target.value as any })}
                className="w-full px-3 py-2 bg-background border border-border rounded-md"
              >
                {['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'].map((method) => (
                  <option key={method} value={method}>
                    {method}
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">请求 URL</label>
              <Input
                value={formData.url}
                onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                placeholder="https://api.example.com/path"
              />
              <p className="text-xs text-muted-foreground">
                支持 {'{{变量名}}'} 引用环境变量或全局变量
              </p>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">接口描述</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="w-full min-h-[100px] px-3 py-2 bg-background border border-border rounded-md"
                placeholder="输入接口描述..."
              />
            </div>
          </div>
        )}

        {activeTab === 'params' && (
          <ParamsEditor
            params={formData.params}
            onChange={(params) => setFormData({ ...formData, params })}
          />
        )}

        {activeTab === 'headers' && (
          <HeadersEditor
            headers={formData.headers}
            onChange={(headers) => setFormData({ ...formData, headers })}
          />
        )}

        {activeTab === 'body' && (
          <BodyEditor
            bodyType={formData.body_type}
            bodyJson={formData.body_json}
            onChange={(updates) => setFormData({ ...formData, ...updates })}
          />
        )}

        {activeTab === 'response' && (
          <div className="text-center text-muted-foreground py-8">
            点击「发送」按钮查看响应结果
          </div>
        )}
      </div>
    </div>
  )
}

// 参数编辑器
function ParamsEditor({
  params,
  onChange,
}: {
  params: Record<string, string>
  onChange: (params: Record<string, string>) => void
}) {
  const entries = Object.entries(params)

  const handleAdd = () => {
    onChange({ ...params, '': '' })
  }

  const handleUpdate = (index: number, field: 'key' | 'value', value: string) => {
    const newEntries = [...entries]
    if (field === 'key') {
      newEntries[index][0] = value
    } else {
      newEntries[index][1] = value
    }
    onChange(Object.fromEntries(newEntries))
  }

  const handleDelete = (index: number) => {
    const newEntries = entries.filter((_, i) => i !== index)
    onChange(Object.fromEntries(newEntries))
  }

  return (
    <div className="space-y-2 max-w-4xl">
      {entries.map(([key, value], index) => (
        <div key={index} className="flex gap-2">
          <Input
            placeholder="参数名"
            value={key}
            onChange={(e) => handleUpdate(index, 'key', e.target.value)}
            className="flex-1"
          />
          <Input
            placeholder="参数值"
            value={value}
            onChange={(e) => handleUpdate(index, 'value', e.target.value)}
            className="flex-1"
          />
          <Button variant="ghost" size="sm" onClick={() => handleDelete(index)}>
            <Trash2 className="h-4 w-4 text-destructive" />
          </Button>
        </div>
      ))}
      <Button variant="outline" size="sm" onClick={handleAdd}>
        <Plus className="h-4 w-4 mr-2" />
        添加参数
      </Button>
    </div>
  )
}

// 请求头编辑器
function HeadersEditor({
  headers,
  onChange,
}: {
  headers: Record<string, string>
  onChange: (headers: Record<string, string>) => void
}) {
  const entries = Object.entries(headers)

  const handleAdd = () => {
    onChange({ ...headers, '': '' })
  }

  const handleUpdate = (index: number, field: 'key' | 'value', value: string) => {
    const newEntries = [...entries]
    if (field === 'key') {
      newEntries[index][0] = value
    } else {
      newEntries[index][1] = value
    }
    onChange(Object.fromEntries(newEntries))
  }

  const handleDelete = (index: number) => {
    const newEntries = entries.filter((_, i) => i !== index)
    onChange(Object.fromEntries(newEntries))
  }

  return (
    <div className="space-y-2 max-w-4xl">
      {entries.map(([key, value], index) => (
        <div key={index} className="flex gap-2">
          <Input
            placeholder="Header 名称"
            value={key}
            onChange={(e) => handleUpdate(index, 'key', e.target.value)}
            className="flex-1"
          />
          <Input
            placeholder="Header 值"
            value={value}
            onChange={(e) => handleUpdate(index, 'value', e.target.value)}
            className="flex-1"
          />
          <Button variant="ghost" size="sm" onClick={() => handleDelete(index)}>
            <Trash2 className="h-4 w-4 text-destructive" />
          </Button>
        </div>
      ))}
      <Button variant="outline" size="sm" onClick={handleAdd}>
        <Plus className="h-4 w-4 mr-2" />
        添加 Header
      </Button>
    </div>
  )
}

// 请求体编辑器
function BodyEditor({
  bodyType,
  bodyJson,
  onChange,
}: {
  bodyType: InterfaceItem['body_type']
  bodyJson?: string
  onChange: (updates: Partial<InterfaceItem>) => void
}) {
  return (
    <div className="space-y-4 max-w-4xl">
      <div className="space-y-2">
        <label className="text-sm font-medium">Body 类型</label>
        <select
          value={bodyType}
          onChange={(e) => onChange({ body_type: e.target.value as any })}
          className="w-full px-3 py-2 bg-background border border-border rounded-md"
        >
          <option value="none">none</option>
          <option value="form-data">form-data</option>
          <option value="x-www-form-urlencoded">x-www-form-urlencoded</option>
          <option value="raw">raw</option>
          <option value="binary">binary</option>
        </select>
      </div>

      {bodyType === 'raw' && (
        <div className="space-y-2">
          <label className="text-sm font-medium">JSON 数据</label>
          <textarea
            value={bodyJson || ''}
            onChange={(e) => onChange({ body_json: e.target.value })}
            className="w-full min-h-[300px] px-3 py-2 bg-background border border-border rounded-md font-mono text-sm"
            placeholder='{"key": "value"}'
          />
        </div>
      )}

      {bodyType === 'form-data' && <div className="text-muted-foreground">form-data 编辑器待实现</div>}

      {bodyType === 'x-www-form-urlencoded' && (
        <div className="text-muted-foreground">x-www-form-urlencoded 编辑器待实现</div>
      )}
    </div>
  )
}
