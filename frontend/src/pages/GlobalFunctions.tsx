// 全局参数配置页面

import { useState, useEffect } from 'react'
import { globalParamAPI } from '@/lib/api'
import type { GlobalParam, GlobalParamGrouped } from '@/types/global-param'
import FunctionEditor from '@/components/FunctionEditor'

export default function GlobalFunctions() {
  const [functions, setFunctions] = useState<GlobalParamGrouped>({})
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedClass, setSelectedClass] = useState<string>('all')
  const [editingFunction, setEditingFunction] = useState<GlobalParam | undefined>()

  useEffect(() => {
    loadFunctions()
  }, [])

  const loadFunctions = async () => {
    try {
      setLoading(true)
      const response = await globalParamAPI.getGlobalParamsGrouped()
      setFunctions(response.params)
    } catch (error) {
      console.error('加载全局参数失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredFunctions = Object.entries(functions).reduce<
    GlobalParamGrouped
  >((acc, [className, funcs]) => {
    if (selectedClass !== 'all' && className !== selectedClass) {
      return acc
    }

    const filtered = funcs.filter(
      (func) =>
        func.method_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        func.description.toLowerCase().includes(searchTerm.toLowerCase())
    )

    if (filtered.length > 0) {
      acc[className] = filtered
    }

    return acc
  }, {})

  const classes = ['all', ...Object.keys(functions)]

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">全局参数配置</h1>
        <p className="text-gray-600 mt-2">
          管理内置工具函数和自定义函数,可在场景中使用 {{函数名()}} 引用
        </p>
      </div>

      {/* 搜索和筛选 */}
      <div className="mb-6 flex gap-4">
        <input
          type="text"
          placeholder="搜索函数名称或描述..."
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />

        <select
          className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={selectedClass}
          onChange={(e) => setSelectedClass(e.target.value)}
        >
          <option value="all">所有类</option>
          {Object.keys(functions).map((className) => (
            <option key={className} value={className}>
              {className}
            </option>
          ))}
        </select>

        <button
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          onClick={() => setEditingFunction(undefined)}
        >
          创建函数
        </button>
      </div>

      {/* 函数列表 */}
      {loading ? (
        <div className="text-center py-12 text-gray-500">加载中...</div>
      ) : Object.keys(filteredFunctions).length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          {searchTerm || selectedClass !== 'all' ? '未找到匹配的函数' : '暂无函数'}
        </div>
      ) : (
        <div className="space-y-6">
          {Object.entries(filteredFunctions).map(([className, funcs]) => (
            <div key={className} className="bg-white rounded-lg shadow overflow-hidden">
              <div className="bg-gray-50 px-6 py-3 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">{className}</h2>
              </div>
              <div className="divide-y divide-gray-200">
                {funcs.map((func) => (
                  <div
                    key={func.id}
                    className="px-6 py-4 hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <h3 className="text-base font-semibold text-gray-900">
                            {func.method_name}()
                          </h3>
                          {func.is_builtin && (
                            <span className="px-2 py-0.5 text-xs font-medium bg-blue-100 text-blue-800 rounded">
                              内置
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-gray-600 mt-1">
                          {func.description}
                        </p>

                        {/* 输入参数 */}
                        {func.params_in && func.params_in.length > 0 && (
                          <div className="mt-3">
                            <div className="text-xs font-medium text-gray-700 mb-1">
                              输入参数:
                            </div>
                            <div className="flex flex-wrap gap-2">
                              {func.params_in.map((param, idx) => (
                                <span
                                  key={idx}
                                  className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded"
                                >
                                  {param.name}: {param.type}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* 输出参数 */}
                        {func.params_out && func.params_out.length > 0 && (
                          <div className="mt-2">
                            <div className="text-xs font-medium text-gray-700 mb-1">
                              输出:
                            </div>
                            <div className="flex flex-wrap gap-2">
                              {func.params_out.map((param, idx) => (
                                <span
                                  key={idx}
                                  className="px-2 py-1 text-xs bg-green-100 text-green-700 rounded"
                                >
                                  {param.type}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>

                      {!func.is_builtin && (
                        <div className="flex gap-2 ml-4">
                          <button
                            className="text-blue-600 hover:text-blue-800 text-sm"
                            onClick={() => setEditingFunction(func)}
                          >
                            编辑
                          </button>
                          <button
                            className="text-red-600 hover:text-red-800 text-sm"
                            onClick={async () => {
                              if (confirm(`确定要删除函数 ${func.method_name} 吗?`)) {
                                try {
                                  await globalParamAPI.deleteGlobalParam(
                                    func.id
                                  )
                                  loadFunctions()
                                } catch (error) {
                                  console.error('删除失败:', error)
                                  alert('删除失败')
                                }
                              }
                            }}
                          >
                            删除
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* 函数编辑器 */}
      {editingFunction !== undefined && (
        <FunctionEditor
          function={editingFunction}
          onSave={() => {
            setEditingFunction(undefined)
            loadFunctions()
          }}
          onCancel={() => setEditingFunction(undefined)}
        />
      )}
    </div>
  )
}
