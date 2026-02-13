/** 场景编排页面 */

import { For, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Plus, Search, MoreHorizontal } from "lucide-react";
import { apiClient } from "@/lib/api";

export default function ScenariosPage() {
  const navigate = useNavigate();
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedProject, setSelectedProject] = useState<number | null>(null);

  useEffect(() => {
    loadScenarios();
  }, [selectedProject]);

  const loadScenarios = async () => {
    try {
      setLoading(true);
      const response = await apiClient.request<{
        items: Scenario[];
        total: number;
      }>(`/scenarios?project_id=${selectedProject || ""}`);

      if (response.success && response.data) {
        setScenarios(response.data.items);
      }
    } catch (error) {
      console.error("Failed to load scenarios:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateScenario = () => {
    navigate("/scenarios/new");
  };

  const handleEditScenario = (id: number) => {
    navigate(`/scenarios/${id}/edit`);
  };

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">场景编排</h1>
        <p className="text-gray-600 mt-1">管理测试场景,编排测试步骤</p>
      </div>

      {/* Toolbar */}
      <div className="mb-6 flex items-center justify-between">
        <div className="flex items-center gap-4">
          {/* Project Filter */}
          <select
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            value={selectedProject || ""}
            onChange={(e) => setSelectedProject(Number(e.target.value) || null)}
          >
            <option value="">所有项目</option>
            {/* TODO: Load from API */}
            <option value="1">项目 1</option>
          </select>

          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="搜索场景..."
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>

        <button
          onClick={handleCreateScenario}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Plus size={20} />
          <span>创建场景</span>
        </button>
      </div>

      {/* Scenarios List */}
      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-600"></div>
        </div>
      ) : scenarios.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500">暂无场景</p>
          <button
            onClick={handleCreateScenario}
            className="mt-4 text-blue-600 hover:underline"
          >
            创建第一个场景
          </button>
        </div>
      ) : (
        <div className="grid gap-4">
          {scenarios.map((scenario) => (
            <div
              key={scenario.id}
              className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{scenario.name}</h3>
                  <p className="text-sm text-gray-600 mt-1">{scenario.description || "暂无描述"}</p>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleEditScenario(scenario.id)}
                    className="p-2 text-blue-600 hover:bg-blue-50 rounded"
                  >
                    编辑
                  </button>
                  <button className="p-2 text-gray-600 hover:bg-gray-50 rounded">
                    <MoreHorizontal size={20} />
                  </button>
                </div>
              </div>

              <div className="flex items-center gap-4 text-sm text-gray-600">
                <span>优先级: P{scenario.priority || "1"}</span>
                {Object.keys(scenario.tags || {}).length > 0 && (
                  <span>标签: {Object.keys(scenario.tags || {}).length}</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
