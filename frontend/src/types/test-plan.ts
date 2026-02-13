/** 测试计划相关类型定义 */

export interface TestPlan {
  id: number;
  name: string;
  description?: string;
  project_id: number;
  creator_id: number;
  status: "pending" | "running" | "paused" | "completed" | "failed";
  scenario_count: number;
  created_at: string;
  updated_at: string;
}

export interface TestPlanCreate {
  name: string;
  description?: string;
  project_id: number;
  scenario_ids: number[];
  scheduled_at?: string;
}

export interface TestPlanUpdate {
  name?: string;
  description?: string;
  scenario_ids?: number[];
  scheduled_at?: string;
}

export interface TestExecution {
  id: string;
  plan_id: number;
  environment_id: number;
  executor_id: number;
  status: "pending" | "running" | "paused" | "completed" | "failed";
  total_scenarios: number;
  passed_scenarios: number;
  failed_scenarios: number;
  skipped_scenarios: number;
  started_at?: string;
  finished_at?: string;
  created_at: string;
}
