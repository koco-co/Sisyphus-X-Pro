import Editor from '@monaco-editor/react'
import type { OnChange } from '@monaco-editor/react'
import { cn } from '@/lib/utils'

interface CodeEditorProps {
  value: string
  onChange?: (value: string | undefined) => void
  language?: string
  readOnly?: boolean
  height?: string
  className?: string
}

export function CodeEditor({
  value,
  onChange,
  language = 'python',
  readOnly = false,
  height = '400px',
  className,
}: CodeEditorProps) {
  const handleChange: OnChange = (newValue) => {
    if (onChange) {
      onChange(newValue)
    }
  }

  return (
    <div className={cn('border rounded-md overflow-hidden', className)}>
      <Editor
        height={height}
        language={language}
        value={value}
        onChange={handleChange}
        theme="vs-dark"
        options={{
          readOnly,
          minimap: { enabled: false },
          fontSize: 14,
          lineNumbers: 'on',
          scrollBeyondLastLine: false,
          automaticLayout: true,
          tabSize: 4,
          insertSpaces: true,
        }}
      />
    </div>
  )
}
