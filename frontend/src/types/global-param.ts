// 全局参数类型定义

export interface ParamIn {
  name: string
  type: string
  description: string
}

export interface ParamOut {
  type: string
  description: string
}

export interface GlobalParam {
  id: number
  class_name: string
  method_name: string
  description: string
  code: string
  params_in: ParamIn[]
  params_out: ParamOut[]
  is_builtin: boolean
  created_at: string
}

export interface GlobalParamGrouped {
  [className: string]: GlobalParam[]
}
