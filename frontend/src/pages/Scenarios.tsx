import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Plus, Pencil, Trash2, Play } from 'lucide-react';
import { ApiClient } from '@/lib/api';
import type { Scenario } from '@/types/scenario';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/Dialog';
import { Input } from '@/components/ui/Input';

export default function Scenarios() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const api = new ApiClient();

  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [scenarioToDelete, setScenarioToDelete] = useState<Scenario | null>(null);
  const [newScenario, setNewScenario] = useState({
    name: '',
    description: '',
    priority: 'P2',
  });

  // 加载场景列表
  useEffect(() => {
    loadScenarios();
  }, [projectId]);

  async function loadScenarios() {
    try {
      setLoading(true);
      const response = await api.get<Scenario[]>(`/scenarios?project_id=\${projectId}`);
      if (response.success && response.data) {
        setScenarios(response.data);
      }
    } catch (error) {
      console.error('加载场景失败:', error);
    } finally {
      setLoading(false);
    }
  }

  // 创建场景
  async function handleCreateScenario() {
    try {
      const response = await api.post<Scenario>('/scenarios', {
        ...newScenario,
        project_id: parseInt(projectId!),
      });

      if (response.success) {
        setIsCreateDialogOpen(false);
        setNewScenario({ name: '', description: '', priority: 'P2' });
        await loadScenarios();
      }
    } catch (error) {
      console.error('创建场景失败:', error);
    }
  }

  // 删除场景
  async function handleDeleteScenario() {
    if (!scenarioToDelete) return;

    try {
      const response = await api.delete(`/scenarios/\${scenarioToDelete.id}`);
      if (response.success) {
        setIsDeleteDialogOpen(false);
        setScenarioToDelete(null);
        await loadScenarios();
      }
    } catch (error) {
      console.error('删除场景失败:', error);
    }
  }

  // 过滤场景
  const filteredScenarios = scenarios.filter(
    (scenario) =>
      scenario.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      scenario.description?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // 获取优先级颜色
  function getPriorityColor(priority: Scenario['priority']) {
    const colors = {
      P0: 'bg-red-100 text-red-800',
      P1: 'bg-orange-100 text-orange-800',
      P2: 'bg-yellow-100 text-yellow-800',
      P3: 'bg-blue-100 text-blue-800',
    };
    return colors[priority];
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-t-transparent"></div>
          <p className="mt-4 text-gray-600">加载中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* 页面标题和操作 */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">测试场景</h1>
          <p className="text-gray-600 mt-1">管理和组织测试场景</p>
        </div>
        <Button onClick={() => setIsCreateDialogOpen(true)} className="flex items-center gap-2">
          <Plus size={20} />
          创建场景
        </Button>
      </div>

      {/* 搜索框 */}
      <div className="mb-6">
        <Input
          type="search"
          placeholder="搜索场景..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full"
        />
      </div>

      {/* 场景列表 */}
      {filteredScenarios.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">
            {searchQuery ? '未找到匹配的场景' : '暂无场景'}
          </p>
          {!searchQuery && (
            <Button
              onClick={() => setIsCreateDialogOpen(true)}
              className="mt-4"
            >
              创建第一个场景
            </Button>
          )}
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {filteredScenarios.map((scenario) => (
            <div
              key={scenario.id}
              className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow p-6 border border-gray-200"
            >
              {/* 场景头部 */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    {scenario.name}
                  </h3>
                  {scenario.description && (
                    <p className="text-gray-600 text-sm line-clamp-2">
                      {scenario.description}
                    </p>
                  )}
                </div>
                <Badge className={getPriorityColor(scenario.priority)}>
                  {scenario.priority}
                </Badge>
              </div>

              {/* 场景信息 */}
              <div className="space-y-2 text-sm text-gray-600 mb-4">
                <div className="flex items-center gap-2">
                  <span className="font-medium">步骤数:</span>
                  <span>{scenario.step_count || 0} 个</span>
                </div>
                {scenario.tags && Object.keys(scenario.tags).length > 0 && (
                  <div className="flex items-center gap-2">
                    <span className="font-medium">标签:</span>
                    <div className="flex gap-1 flex-wrap">
                      {Object.entries(scenario.tags).slice(0, 3).map(([key, value]) => (
                        <Badge key={key} className="bg-gray-100 text-gray-700 text-xs">
                          {key}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
                <div className="flex items-center gap-2">
                  <span className="font-medium">创建时间:</span>
                  <span>{new Date(scenario.created_at).toLocaleDateString('zh-CN')}</span>
                </div>
              </div>

              {/* 操作按钮 */}
              <div className="flex items-center gap-2 pt-4 border-t border-gray-200">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => navigate(`/projects/${projectId}/scenarios/${scenario.id}`)}
                  className="flex items-center gap-2"
                >
                  <Pencil size={16} />
                  编辑
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => navigate(`/projects/${projectId}/scenarios/${scenario.id}/debug`)}
                  className="flex items-center gap-2"
                >
                  <Play size={16} />
                  调试
                </Button>
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => {
                    setScenarioToDelete(scenario);
                    setIsDeleteDialogOpen(true);
                  }}
                  className="flex items-center gap-2"
                >
                  <Trash2 size={16} />
                  删除
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* 创建场景对话框 */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
      <DialogContent onClose={() => setIsCreateDialogOpen(false)}>
        <DialogHeader>
          <DialogTitle>创建新场景</DialogTitle>
        </DialogHeader>
        <form onSubmit={(e) => { e.preventDefault(); handleCreateScenario(); }} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              场景名称 <span className="text-red-500">*</span>
            </label>
            <Input
              type="text"
              required
              value={newScenario.name}
              onChange={(e) => setNewScenario({ ...newScenario, name: e.target.value })}
              placeholder="输入场景名称"
              className="w-full"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              场景描述
            </label>
            <textarea
              value={newScenario.description}
              onChange={(e) => setNewScenario({ ...newScenario, description: e.target.value })}
              placeholder="输入场景描述（可选）"
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              优先级
            </label>
            <select
              value={newScenario.priority}
              onChange={(e) => setNewScenario({ ...newScenario, priority: e.target.value as Scenario['priority'] })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="P0">P0 - 最高</option>
              <option value="P1">P1 - 高</option>
              <option value="P2">P2 - 中</option>
              <option value="P3">P3 - 低</option>
            </select>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="ghost"
              onClick={() => setIsCreateDialogOpen(false)}
            >
              取消
            </Button>
            <Button
              type="submit"
              disabled={!newScenario.name.trim()}
            >
              创建
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>

    {/* 删除确认对话框 */}
    <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
      <DialogContent onClose={() => setIsDeleteDialogOpen(false)}>
        <DialogHeader>
          <DialogTitle>确认删除</DialogTitle>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <p className="text-gray-700">
            确定要删除场景 <strong>{scenarioToDelete?.name}</strong> 吗？
          </p>
          <p className="text-sm text-gray-600">
            此操作无法撤销，删除后需要重新创建。
          </p>
          <DialogFooter>
            <Button
              variant="ghost"
              onClick={() => setIsDeleteDialogOpen(false)}
            >
              取消
            </Button>
            <Button
              variant="destructive"
              onClick={handleDeleteScenario}
            >
              确认删除
            </Button>
          </DialogFooter>
        </div>
      </DialogContent>
    </Dialog>
  </div>
  );
}
