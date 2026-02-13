/** 测试计划页面 */

import { For, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Plus, Play, Pause, Square } from "lucide-react";
import { apiClient } from "@/lib/api";
import type { TestPlan } from "@/types/test-plan";

export default function TestPlansPage() {
  const navigate = useNavigate();
  const [plans, setPlans] = useState<TestPlan[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedProject, setSelectedProject] = useState<number | null>(null);

  useEffect(() => {
    loadTestPlans();
  }, [selectedProject]);

  const loadTestPlans = async () => {
    try {
      setLoading(true);
      const response = await apiClient.request<{
        items: TestPlan[];
        total: number;
      }>(`/test-plans?project_id=${selectedProject || ""}`);

      if (response.success && response.data) {
        setPlans(response.data.items);
      }
    } catch (error) {
      console.error("Failed to load test plans:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePlan = () => {
    navigate("/test-plans/new");
  };

  const handleRunPlan = async (id: number) => {
    try {
      await apiClient.request(`/test-plans/${id}/execute`, {
        method: "POST",
      });
      // Navigate to execution page
      navigate(`/test-plans/${id}/executions`);
    } catch (error) {
      console.error("Failed to run test plan:", error);
      alert("执行失败,请稍后重试");
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "pending":
        return "text-gray-600";
      case "running":
        return "text-blue-600";
      case "paused":
        return "text-yellow-600";
      case "completed":
        return "text-green-600";
      case "failed":
        return "text-red-600";
      default:
        return "text-gray-600";
    }
  };

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">测试计划</h1>
        <p className="text-gray-600 mt-1">管理测试计划,批量执行测试场景</p>
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
        </div>

        <button
          onClick={handleCreatePlan}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Plus size={20} />
          <span>创建测试计划</span>
        </button>
      </div>

      {/* Test Plans List */}
      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-600"></div>
        </div>
      ) : plans.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500">暂无测试计划</p>
          <button
            onClick={handleCreatePlan}
            className="mt-4 text-blue-600 hover:underline"
          >
            创建第一个测试计划
          </button>
        </div>
      ) : (
        <div className="grid gap-4">
          {plans.map((plan) => (
            <div
              key={plan.id}
              className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{plan.name}</h3>
                  <p className="text-sm text-gray-600 mt-1">{plan.description || "暂无描述"}</p>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => navigate(`/test-plans/${plan.id}/edit`)}
                    className="p-2 text-blue-600 hover:bg-blue-50 rounded"
                  >
                    编辑
                  </button>
                  <button
                    onClick={() => handleRunPlan(plan.id)}
                    className="flex items-center gap-1 p-2 bg-green-600 text-white rounded hover:bg-green-700"
                    disabled={plan.status === "running"}
                  >
                    <Play size={16} />
                    <span>执行</span>
                  </button>
                  {plan.status === "running" && (
                    <button className="p-2 bg-yellow-600 text-white rounded hover:bg-yellow-700">
                      <Pause size={16} />
                      <span>暂停</span>
                    </button>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4 text-sm text-gray-600 mb-3">
                <div>
                  <span className="font-semibold">状态:</span>
                  <span className={getStatusColor(plan.status)}>
                    {plan.status === "pending" && "等待执行"}
                    {plan.status === "running" && "执行中"}
                    {plan.status === "paused" && "已暂停"}
                    {plan.status === "completed" && "已完成"}
                    {plan.status === "failed" && "执行失败"}
                  </span>
                </div>
                <div>
                  <span className="font-semibold">场景数:</span>
                  <span>{plan.scenario_count || 0}</span>
                </div>
                <div>
                  <span className="font-semibold">创建时间:</span>
                  <span>{new Date(plan.created_at).toLocaleString("zh-CN")}</span>
                </div>
              </div>

              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Square size={16} />
                <span>最后更新: {new Date(plan.updated_at).toLocaleString("zh-CN")}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
