// 接口管理相关类型定义

export interface InterfaceFolder {
  id: string
  project_id: string
  name: string
  parent_id: string | null
  sort_order: number
  created_at: string
  updated_at: string
  children?: InterfaceFolder[]
  interfaces?: InterfaceItem[]
}

export interface InterfaceItem {
  id: string
  project_id: string
  folder_id: string | null
  name: string
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH' | 'HEAD' | 'OPTIONS'
  url: string
  description: string
  headers: Record<string, string>
  params: Record<string, string>
  body_type: 'none' | 'form-data' | 'x-www-form-urlencoded' | 'raw' | 'binary'
  body_json?: string
  body_text?: string
  body_form_data?: Record<string, FormDataValue>
  body_form_urlencoded?: Record<string, string>
  created_at: string
  updated_at: string
}

export interface FormDataValue {
  type: 'text' | 'file'
  value: string
  description?: string
}

export interface CurlImportResult {
  method: string
  url: string
  headers: Record<string, string>
  params?: Record<string, string>
  body?: string
  body_type: InterfaceItem['body_type']
}

// 树节点类型 (用于目录树渲染)
export interface TreeNode {
  id: string
  name: string
  type: 'folder' | 'interface'
  method?: InterfaceItem['method']
  children?: TreeNode[]
  data: InterfaceFolder | InterfaceItem
}
