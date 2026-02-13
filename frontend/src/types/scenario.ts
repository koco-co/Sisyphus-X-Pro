/** 场景相关类型定义 */

export interface Scenario {
  id: number;
  project_id: number;
  name: string;
  description: string | null;
  priority: 'P0' | 'P1' | 'P2' | 'P3';
  tags: Record<string, any>;
  pre_sql: string | null;
  post_sql: string | null;
  variables: Record<string, any>;
  environment_id: number | null;
  creator_id: number;
  created_at: string;
  updated_at: string;
  step_count?: number;
}

export interface ScenarioStep {
  id: number;
  scenario_id: number;
  sort_order: number;
  description: string;
  keyword_id: number;
  params: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface ScenarioCreateRequest {
  name: string;
  description?: string;
  priority?: 'P0' | 'P1' | 'P2' | 'P3';
  tags?: Record<string, any>;
  pre_sql?: string;
  post_sql?: string;
  variables?: Record<string, any>;
  environment_id?: number;
}

export interface ScenarioUpdateRequest {
  name?: string;
  description?: string;
  priority?: 'P0' | 'P1' | 'P2' | 'P3';
  tags?: Record<string, any>;
  pre_sql?: string;
  post_sql?: string;
  variables?: Record<string, any>;
  environment_id?: number;
}

export interface Dataset {
  id: number;
  scenario_id: number;
  name: string;
  headers: string[];
  rows: string[][];
  created_at: string;
  updated_at: string;
}

export interface StepReorderRequest {
  step_ids: number[];
}
