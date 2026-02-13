import { useState, useEffect } from 'react';
import { ChevronDown } from 'lucide-react';
import { ApiClient } from '@/lib/api';
import type { Keyword } from '@/types/keyword';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { Badge } from '@/components/ui/Badge';

interface StepEditorProps {
  keywordId?: number;
  params: Record<string, any>;
  onChange: (keywordId: number, params: Record<string, any>) => void;
}

// 关键字类型映射
const KEYWORD_TYPES = {
  http_request: 'HTTP 请求',
  assertion: '断言',
  extract: '提取变量',
  db_query: '数据库查询',
  custom: '自定义',
} as const;

const KEYWORD_TYPE_OPTIONS = [
  { value: 'http_request', label: 'HTTP 请求' },
  { value: 'assertion', label: '断言' },
  { value: 'extract', label: '提取变量' },
  { value: 'db_query', label: '数据库查询' },
  { value: 'custom', label: '自定义' },
];

type KeywordType = keyof typeof KEYWORD_TYPES;

export default function StepEditor({ keywordId, params, onChange }: StepEditorProps) {
  const api = ApiClient.getInstance();
  
  const [keywordType, setKeywordType] = useState<KeywordType | null>(null);
  const [keywords, setKeywords] = useState<Keyword[]>([]);
  const [selectedKeywordId, setSelectedKeywordId] = useState<number | null>(null);
  const [keywordDetails, setKeywordDetails] = useState<Keyword | null>(null);
  const [editedParams, setEditedParams] = useState<Record<string, any>>({});

  // 当 keywordId 改变时，加载关键字详情
  useEffect(() => {
    if (keywordId) {
      loadKeywordDetails(keywordId);
    }
  }, [keywordId]);

  // 当类型改变时，加载该类型的所有关键字
  useEffect(() => {
    if (keywordType) {
      loadKeywords(keywordType);
    }
  }, [keywordType]);

  async function loadKeywordDetails(id: number) {
    try {
      const response = await api.get<Keyword>(\`/keywords/\${id}\`);
      if (response.success && response.data) {
        setKeywordDetails(response.data);
        setSelectedKeywordId(id);
        
        // 自动推断类型
        const inferredType = Object.keys(KEYWORD_TYPES).find(
          type => response.data.type === type
        ) as KeywordType | null;
        if (inferredType) {
          setKeywordType(inferredType);
          // 加载该类型的所有关键字
          loadKeywords(inferredType);
        }
        
        // 初始化参数
        setEditedParams(response.data.params || {});
      }
    } catch (error) {
      console.error('加载关键字详情失败:', error);
    }
  }

  async function loadKeywords(type: KeywordType) {
    try {
      const response = await api.get<Keyword[]>(\`/keywords?type=\${type}\`);
      if (response.success && response.data) {
        setKeywords(response.data);
      }
    } catch (error) {
      console.error('加载关键字列表失败:', error);
    }
  }

  function handleTypeChange(type: KeywordType) {
    setKeywordType(type);
    setSelectedKeywordId(null);
    setKeywordDetails(null);
    setEditedParams({});
  }

  function handleKeywordChange(keywordId: string) {
    const id = parseInt(keywordId);
    const keyword = keywords.find(k => k.id === id);
    if (keyword) {
      setSelectedKeywordId(id);
      setKeywordDetails(keyword);
      setEditedParams(keyword.params || {});
    }
  }

  function handleParamChange(key: string, value: any) {
    const newParams = { ...editedParams, [key]: value };
    setEditedParams(newParams);
    onChange(keywordDetails?.id || 0, newParams);
  }

  function handleApply() {
    if (keywordDetails?.id) {
      onChange(keywordDetails.id, editedParams);
    }
  }

  // 根据参数类型渲染输入框
  function renderParamInput(param: { name: string; description?: string; type?: string; required?: boolean; default?: any }) {
    const value = editedParams[param.name] !== undefined ? editedParams[param.name] : param.default;
    
    const inputId = \`param-\${param.name}\`;

    switch (param.type) {
      case 'boolean':
        return (
          <div className="flex items-center gap-2">
            <input
              id={inputId}
              type="checkbox"
              checked={value || false}
              onChange={(e) => handleParamChange(param.name, e.target.checked)}
              className="w-4 h-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor={inputId} className="text-sm text-gray-700">
              {param.description || param.name}
              {param.required && <span className="text-red-500 ml-1">*</span>}
            </label>
          </div>
        );

      case 'number':
        return (
          <div>
            <label htmlFor={inputId} className="block text-sm font-medium text-gray-700 mb-1">
              {param.description || param.name}
              {param.required && <span className="text-red-500 ml-1">*</span>}
            </label>
            <Input
              id={inputId}
              type="number"
              value={value?.toString() || ''}
              onChange={(e) => handleParamChange(param.name, e.target.value ? parseFloat(e.target.value) : null)}
              placeholder={\`请输入 \${param.description || param.name}\`}
              className="w-full"
            />
          </div>
        );

      case 'dict':
        return (
          <div>
            <label htmlFor={inputId} className="block text-sm font-medium text-gray-700 mb-1">
              {param.description || param.name}
              {param.required && <span className="text-red-500 ml-1">*</span>}
            </label>
            <textarea
              id={inputId}
              value={typeof value === 'string' ? value : JSON.stringify(value || {}, null, 2)}
              onChange={(e) => {
                try {
                  const parsed = JSON.parse(e.target.value);
                  handleParamChange(param.name, parsed);
                } catch {
                  // 忽略 JSON 解析错误
                }
              }}
              placeholder={\`请输入 JSON 格式的 \${param.description || param.name}\`}
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm font-mono"
            />
          </div>
        );

      case 'array':
        return (
          <div>
            <label htmlFor={inputId} className="block text-sm font-medium text-gray-700 mb-1">
              {param.description || param.name}
              {param.required && <span className="text-red-500 ml-1">*</span>}
            </label>
            <textarea
              id={inputId}
              value={typeof value === 'string' ? value : JSON.stringify(value || [], null, 2)}
              onChange={(e) => {
                try {
                  const parsed = JSON.parse(e.target.value);
                  handleParamChange(param.name, parsed);
                } catch {
                  // 忽略 JSON 解析错误
                }
              }}
              placeholder={\`请输入 JSON 数组格式的 \${param.description || param.name}\`}
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm font-mono"
            />
          </div>
        );

      case 'string':
      default:
        return (
          <div>
            <label htmlFor={inputId} className="block text-sm font-medium text-gray-700 mb-1">
              {param.description || param.name}
              {param.required && <span className="text-red-500 ml-1">*</span>}
            </label>
            <Input
              id={inputId}
              type="text"
              value={value?.toString() || ''}
              onChange={(e) => handleParamChange(param.name, e.target.value)}
              placeholder={\`请输入 \${param.description || param.name}\`}
              className="w-full"
            />
          </div>
        );
    }
  }

  return (
    <div className="space-y-6 bg-white rounded-lg p-6 border border-gray-200">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">步骤配置</h3>

      {/* 第一级：关键字类型 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          关键字类型 <span className="text-red-500">*</span>
        </label>
        <div className="grid grid-cols-2 gap-3">
          {KEYWORD_TYPE_OPTIONS.map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => handleTypeChange(option.value)}
              className={\`p-3 border rounded-lg text-left transition-colors \${keywordType === option.value
                ? 'border-blue-500 bg-blue-50 text-blue-700'
                : 'border-gray-300 hover:border-gray-400 text-gray-700'}\`}
            >
              <div className="flex items-center justify-between">
                <span className="font-medium">{option.label}</span>
                {keywordType === option.value && <ChevronDown size={16} />}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* 第二级：具体关键字 */}
      {keywordType && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            选择关键字 <span className="text-red-500">*</span>
          </label>
          {keywords.length === 0 ? (
            <div className="text-gray-500 text-sm">该类型下暂无关键字</div>
          ) : (
            <div className="grid grid-cols-2 gap-3">
              {keywords.map((keyword) => (
                <button
                  key={keyword.id}
                  type="button"
                  onClick={() => handleKeywordChange(keyword.id.toString())}
                  className={\`p-3 border rounded-lg text-left transition-colors \${selectedKeywordId === keyword.id
                    ? 'border-blue-500 bg-blue-50 text-blue-700'
                    : 'border-gray-300 hover:border-gray-400 text-gray-700'}\`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="font-medium">{keyword.name}</div>
                      <div className="text-xs text-gray-600 mt-1">{keyword.method_name}</div>
                    </div>
                    {selectedKeywordId === keyword.id && <ChevronDown size={16} />}
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {/* 第三级：参数表单 */}
      {keywordDetails && keywordDetails.params && keywordDetails.params.length > 0 && (
        <div className="space-y-4 pt-4 border-t border-gray-200">
          <h4 className="text-md font-semibold text-gray-900 mb-3">
            配置参数 - {keywordDetails.name}
          </h4>
          <div className="bg-gray-50 rounded-lg p-4 space-y-4">
            {keywordDetails.params.map((param) => (
              <div key={param.name}>
                {renderParamInput(param)}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 应用按钮 */}
      <div className="flex justify-end pt-4 border-t border-gray-200">
        <Button
          onClick={handleApply}
          disabled={!keywordDetails || Object.keys(editedParams).length === 0}
          className="w-full"
        >
          应用配置
        </Button>
      </div>

      {/* 参数提示 */}
      {Object.keys(editedParams).length > 0 && (
        <div className="mt-4 text-sm text-gray-600 bg-blue-50 rounded-lg p-4">
          <p className="font-medium mb-2">当前参数预览:</p>
          <pre className="text-xs bg-gray-800 text-green-400 p-3 rounded overflow-x-auto">
            {JSON.stringify(editedParams, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
