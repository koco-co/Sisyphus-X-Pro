// 环境管理类型定义

export interface Environment {
  id: string
  project_id: string
  name: string
  base_url: string
  is_default: boolean
  created_at: string
  updated_at: string
}

export interface EnvironmentVariable {
  id: string
  env_id: string
  key: string
  value: string
  description?: string
}

export interface GlobalVariable {
  id: string
  project_id: string
  key: string
  value: string
  description?: string
  created_at: string
  updated_at: string
}
