// 函数编辑器组件

import { useState, useEffect, useRef } from 'react'
import type { GlobalParam } from '@/types/global-param'
import { globalParamAPI } from '@/lib/api'

interface FunctionEditorProps {
  function?: GlobalParam
  onSave: () => void
  onCancel: () => void
}

export default function FunctionEditor({
  function: func,
  onSave,
  onCancel,
}: FunctionEditorProps) {
  const [className, setClassName] = useState(func?.class_name || 'CustomUtils')
  const [methodName, setMethodName] = useState(func?.method_name || '')
  const [description, setDescription] = useState(func?.description || '')
  const [code, setCode] = useState(
    func?.code ||
      `def ${methodName || 'custom_function'}():
    """自定义函数描述.

    Returns:
        返回值描述
    """
    # TODO: 实现函数逻辑
    pass
`
  )
  const [saving, setSaving] = useState(false)
  const editorRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (editorRef.current) {
      editorRef.current.focus()
    }
  }, [])

  const handleSave = async () => {
    if (!methodName.trim()) {
      alert('请输入方法名')
      return
    }

    if (!description.trim()) {
      alert('请输入描述')
      return
    }

    if (!code.trim()) {
      alert('请输入代码')
      return
    }

    try {
      setSaving(true)

      if (func) {
        // 更新现有函数
        await globalParamAPI.updateGlobalParam(func.id, {
          class_name: className,
          method_name: methodName,
          description,
          code,
        })
      } else {
        // 创建新函数
        await globalParamAPI.createGlobalParam({
          class_name: className,
          method_name: methodName,
          description,
          code,
          params_in: [],
          params_out: [],
        })
      }

      onSave()
    } catch (error) {
      console.error('保存失败:', error)
      alert(`保存失败: ${error instanceof Error ? error.message : '未知错误'}`)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">
            {func ? '编辑函数' : '创建函数'}
          </h2>
        </div>

        <div className="px-6 py-4 space-y-4">
          {/* 类名 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              类名 (分组)
            </label>
            <input
              type="text"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="CustomUtils"
              value={className}
              onChange={(e) => setClassName(e.target.value)}
              disabled={!!func} // 编辑时不允许修改类名
            />
            <p className="text-xs text-gray-500 mt-1">
              函数分组类别,如 StringUtils, TimeUtils, CustomUtils
            </p>
          </div>

          {/* 方法名 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              方法名
            </label>
            <input
              type="text"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="custom_function"
              value={methodName}
              onChange={(e) => setMethodName(e.target.value)}
              disabled={!!func} // 编辑时不允许修改方法名
              pattern="[a-zA-Z_][a-zA-Z0-9_]*"
            />
            <p className="text-xs text-gray-500 mt-1">
              字母开头,仅含字母、数字、下划线
            </p>
          </div>

          {/* 描述 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              功能描述
            </label>
            <textarea
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={2}
              placeholder="描述这个函数的功能..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>

          {/* 代码编辑器 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Python 代码
            </label>
            <div className="border border-gray-300 rounded-lg overflow-hidden">
              <textarea
                ref={editorRef}
                className="w-full px-3 py-2 font-mono text-sm focus:outline-none"
                rows={20}
                value={code}
                onChange={(e) => setCode(e.target.value)}
                style={{
                  backgroundColor: '#1e1e1e',
                  color: '#d4d4d4',
                  lineHeight: '1.5',
                }}
                spellCheck={false}
              />
            </div>
            <p className="text-xs text-gray-500 mt-1">
              支持 docstring 自动解析参数说明
            </p>
          </div>
        </div>

        {/* 按钮 */}
        <div className="px-6 py-4 border-t border-gray-200 flex justify-end gap-3">
          <button
            className="px-4 py-2 text-gray-700 hover:text-gray-900 transition-colors"
            onClick={onCancel}
            disabled={saving}
          >
            取消
          </button>
          <button
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400"
            onClick={handleSave}
            disabled={saving}
          >
            {saving ? '保存中...' : '保存'}
          </button>
        </div>
      </div>
    </div>
  )
}
