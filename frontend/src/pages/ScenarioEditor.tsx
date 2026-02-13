import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, Plus, Trash2, Save, Play, Database, FileText } from 'lucide-react';
import { ApiClient } from '@/lib/api';
import type { Scenario, ScenarioStep, ScenarioUpdateRequest } from '@/types/scenario';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Dialog } from '@/components/ui/Dialog';
import CodeEditor from '@/components/editor/CodeEditor';

export default function ScenarioEditor() {
  const { projectId, scenarioId } = useParams<{ projectId: string; scenarioId: string }>();
  const navigate = useNavigate();
  const api = ApiClient.getInstance();

  const [scenario, setScenario] = useState<Scenario | null>(null);
  const [steps, setSteps] = useState<ScenarioStep[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [activeTab, setActiveTab] = useState<'steps' | 'pre-sql' | 'post-sql' | 'dataset'>('steps');
  const [isAddStepOpen, setIsAddStepOpen] = useState(false);
  const [editedStep, setEditedStep] = useState<ScenarioStep | null>(null);

  useEffect(() => {
    loadScenario();
  }, [scenarioId]);

  async function loadScenario() {
    try {
      setLoading(true);
      const response = await api.get<Scenario>(`/scenarios/\${scenarioId}`);
      if (response.success && response.data) {
        setScenario(response.data);
        setSteps(response.data.steps || []);
      }
    } catch (error) {
      console.error('加载场景失败:', error);
    } finally {
      setLoading(false);
    }
  }

  async function handleSave() {
    if (!scenario) return;

    try {
      setSaving(true);
      const updateData: ScenarioUpdateRequest = {
        name: scenario.name,
        description: scenario.description,
        priority: scenario.priority,
        tags: scenario.tags,
        variables: scenario.variables,
        environment_id: scenario.environment_id,
      };
      const response = await api.put(`/scenarios/\${scenarioId}`, updateData);
      if (response.success) {
        alert('保存成功');
        await loadScenario();
      }
    } catch (error) {
      console.error('保存失败:', error);
      alert('保存失败');
    } finally {
      setSaving(false);
    }
  }

  async function handleDeleteStep(stepId: number) {
    try {
      const response = await api.delete(`/scenarios/\${scenarioId}/steps/\${stepId}`);
      if (response.success) {
        setSteps(steps.filter(s => s.id !== stepId));
      }
    } catch (error) {
      console.error('删除步骤失败:', error);
    }
  }

  async function handleDebug() {
    if (!scenario) return;
    try {
      const response = await api.post(`/scenarios/\${scenarioId}/debug`, {});
      if (response.success) {
        alert('调试已启动，请查看 Allure 报告');
      }
    } catch (error) {
      console.error('调试失败:', error);
      alert('调试失败');
    }
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

  if (!scenario) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-gray-600">场景不存在</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* 页面头部 */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate(`/projects/\${projectId}/scenarios`)}
            className="flex items-center gap-2"
          >
            <ArrowLeft size={20} />
            返回
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{scenario.name}</h1>
            {scenario.description && (
              <p className="text-gray-600 mt-1">{scenario.description}</p>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button
            onClick={handleDebug}
            className="flex items-center gap-2"
          >
            <Play size={20} />
            调试
          </Button>
          <Button
            onClick={handleSave}
            disabled={saving}
            className="flex items-center gap-2"
          >
            <Save size={20} />
            {saving ? '保存中...' : '保存'}
          </Button>
        </div>
      </div>

      {/* 标签页切换 */}
      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8" aria-label="Tabs">
            {[
              { key: 'steps', label: '测试步骤', icon: FileText },
              { key: 'pre-sql', label: '前置 SQL', icon: Database },
              { key: 'post-sql', label: '后置 SQL', icon: Database },
              { key: 'dataset', label: '数据集', icon: Database },
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as any)}
                className={`\${activeTab === tab.key ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'} group inline-flex items-center gap-2 border-b-2 py-4 px-1 text-sm font-medium`}
              >
                <tab.icon size={18} />
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* 测试步骤标签页 */}
      {activeTab === 'steps' && (
        <div className="space-y-6">
          {/* 步骤列表 */}
          <div className="bg-white rounded-lg shadow-md border border-gray-200">
            <div className="p-4 border-b border-gray-200 flex items-center justify-between">
              <h2 className="text-xl font-semibold text-gray-900">测试步骤</h2>
              <Button
                size="sm"
                onClick={() => setIsAddStepOpen(true)}
                className="flex items-center gap-2"
              >
                <Plus size={18} />
                添加步骤
              </Button>
            </div>

            {steps.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                暂无测试步骤，点击"添加步骤"开始创建
              </div>
            ) : (
              <div className="divide-y divide-gray-200">
                {steps.map((step, index) => (
                  <div
                    key={step.id}
                    className="p-4 flex items-start gap-4 hover:bg-gray-50 group"
                  >
                    <div className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center font-semibold">
                      {index + 1}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-start justify-between">
                        <div>
                          <h3 className="text-lg font-medium text-gray-900">{step.description}</h3>
                          <p className="text-sm text-gray-600 mt-1">
                            关键字 ID: {step.keyword_id}
                          </p>
                          {Object.keys(step.params).length > 0 && (
                            <div className="mt-2 text-sm bg-gray-50 rounded p-2">
                              <p className="font-medium text-gray-700 mb-1">参数:</p>
                              <pre className="text-xs text-gray-600">
                                {JSON.stringify(step.params, null, 2)}
                              </pre>
                            </div>
                          )}
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setEditedStep(step)}
                          className="flex items-center gap-2"
                        >
                          编辑
                        </Button>
                      </div>
                      <Button
                        variant="danger"
                        size="sm"
                        onClick={() => handleDeleteStep(step.id)}
                        className="flex items-center gap-2"
                      >
                        <Trash2 size={18} />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* 编辑步骤对话框 */}
          <Dialog
            isOpen={isAddStepOpen || editedStep !== null}
            onClose={() => {
              setIsAddStepOpen(false);
              setEditedStep(null);
            }}
            title={editedStep ? '编辑步骤' : '添加步骤'}
          >
            <form className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  步骤描述
                </label>
                <Input
                  type="text"
                  required
                  defaultValue={editedStep?.description || ''}
                  placeholder="描述此步骤的作用"
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  关键字 ID
                </label>
                <Input
                  type="number"
                  required
                  defaultValue={editedStep?.keyword_id || 1}
                  placeholder="输入关键字 ID"
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  参数（JSON 格式）
                </label>
                <textarea
                  defaultValue={editedStep ? JSON.stringify(editedStep.params, null, 2) : '{\n  }'}
                  placeholder='输入参数，如: {\n  "url": "https://api.example.com"\n}'
                  rows={6}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-mono text-sm"
                />
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t">
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => {
                    setIsAddStepOpen(false);
                    setEditedStep(null);
                  }}
                >
                  取消
                </Button>
                <Button type="submit">
                  {editedStep ? '更新' : '添加'}
                </Button>
              </div>
            </form>
          </Dialog>
        </div>
      )}

      {/* 前置 SQL 标签页 */}
      {activeTab === 'pre-sql' && (
        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">前置 SQL</h2>
          <p className="text-sm text-gray-600 mb-4">
            在执行场景前运行的 SQL 语句，用于准备测试数据
          </p>
          <CodeEditor
            value={scenario.pre_sql || ''}
            onChange={(value) => setScenario({ ...scenario, pre_sql: value })}
            language="sql"
            height="300px"
            placeholder="-- 在此编写前置 SQL..."
          />
          <div className="mt-4 flex justify-end">
            <Button
              onClick={handleSave}
              disabled={saving}
            >
              {saving ? '保存中...' : '保存前置 SQL'}
            </Button>
          </div>
        </div>
      )}

      {/* 后置 SQL 标签页 */}
      {activeTab === 'post-sql' && (
        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">后置 SQL</h2>
          <p className="text-sm text-gray-600 mb-4">
            在执行场景后运行的 SQL 语句，用于清理测试数据
          </p>
          <CodeEditor
            value={scenario.post_sql || ''}
            onChange={(value) => setScenario({ ...scenario, post_sql: value })}
            language="sql"
            height="300px"
            placeholder="-- 在此编写后置 SQL..."
          />
          <div className="mt-4 flex justify-end">
            <Button
              onClick={handleSave}
              disabled={saving}
            >
              {saving ? '保存中...' : '保存后置 SQL'}
            </Button>
          </div>
        </div>
      )}

      {/* 数据集标签页 */}
      {activeTab === 'dataset' && (
        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">CSV 数据集</h2>
          <p className="text-sm text-gray-600 mb-4">
            上传 CSV 文件进行数据驱动测试
          </p>
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
            <Database className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <p className="text-sm text-gray-600 mb-4">
              点击或拖拽 CSV 文件到此处上传
            </p>
            <input
              type="file"
              accept=".csv"
              className="hidden"
              id="csv-upload"
            />
            <label
              htmlFor="csv-upload"
              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 cursor-pointer"
            >
              <Database size={20} />
              选择 CSV 文件
            </label>
          </div>
        </div>
      )}
    </div>
  );
}
