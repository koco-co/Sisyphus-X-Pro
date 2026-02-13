// 环境管理类型定义

export interface Environment {
  id: string
  project_id: string
  name: string
  base_url: string
  created_at: string
  updated_at: string
}

export interface EnvVariable {
  id: string
  environment_id: string
  name: string
  value: string
  description?: string
  created_at: string
  updated_at: string
}

export interface GlobalVariable {
  id: string
  project_id: string
  name: string
  value: string
  description?: string
  source: 'manual' | 'extracted'
  created_at: string
  updated_at: string
}
