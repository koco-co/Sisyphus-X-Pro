// Dashboard 相关类型定义

export interface CoreStats {
  total_projects: number
  total_interfaces: number
  total_scenarios: number
  total_plans: number
}

export interface TrendDataPoint {
  date: string
  count: number
}

export interface TrendData {
  trend: TrendDataPoint[]
}

export interface CoverageData {
  tested_projects: number
  untested_projects: number
  coverage_percentage: number
}
