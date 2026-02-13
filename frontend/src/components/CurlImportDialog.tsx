import { useState } from 'react'
import { Terminal } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { useToast } from '@/hooks/use-toast'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/Dialog'
import { Button } from '@/components/ui/Button'
import { Textarea } from '@/components/ui/Textarea'
import type { InterfaceItem } from '@/types/interface'

interface CurlImportDialogProps {
  open: boolean
  onClose: () => void
  projectId: string
  folderId: string | null
  onImportSuccess: (interfaceData: InterfaceItem) => void
}

export function CurlImportDialog({
  open,
  onClose,
  projectId,
  folderId,
  onImportSuccess,
}: CurlImportDialogProps) {
  const { token } = useAuth()
  const { toast } = useToast()

  const [curlCommand, setCurlCommand] = useState('')
  const [parsedData, setParsedData] = useState<Partial<InterfaceItem> | null>(null)
  const [isParsing, setIsParsing] = useState(false)

  const handleParse = async () => {
    if (!curlCommand.trim()) return

    setIsParsing(true)
    try {
      const response = await fetch('http://localhost:8000/api/v1/interfaces/parse-curl', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          curl: curlCommand,
          project_id: projectId,
          folder_id: folderId,
        }),
      })

      if (!response.ok) throw new Error('解析 cURL 失败')

      const data = await response.json()
      setParsedData(data)
    } catch (error) {
      toast('解析 cURL 失败', 'error')
    } finally {
      setIsParsing(false)
    }
  }

  const handleImport = async () => {
    if (!parsedData) return

    try {
      const response = await fetch('http://localhost:8000/api/v1/interfaces/import/curl', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          curl: curlCommand,
          project_id: projectId,
          folder_id: folderId,
        }),
      })

      if (!response.ok) throw new Error('导入失败')

      const interfaceData = await response.json()
      toast('导入成功', 'success')
      onImportSuccess(interfaceData)
      handleClose()
    } catch (error) {
      toast('导入失败', 'error')
    }
  }

  const handleClose = () => {
    setCurlCommand('')
    setParsedData(null)
    onClose()
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>从 cURL 导入接口</DialogTitle>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* cURL 输入 */}
          <div className="space-y-2">
            <label className="text-sm font-medium">cURL 命令</label>
            <Textarea
              value={curlCommand}
              onChange={(e) => setCurlCommand(e.target.value)}
              placeholder="curl -X POST https://api.example.com/users ..."
              className="min-h-[150px] font-mono text-sm"
            />
            <p className="text-xs text-muted-foreground">
              粘贴从浏览器 DevTools 或其他工具复制的 cURL 命令
            </p>
          </div>

          {/* 解析按钮 */}
          <div className="flex justify-end">
            <Button
              onClick={handleParse}
              disabled={!curlCommand.trim() || isParsing}
              variant="outline"
            >
              <Terminal className="h-4 w-4 mr-2" />
              {isParsing ? '解析中...' : '解析 cURL'}
            </Button>
          </div>

          {/* 解析结果 */}
          {parsedData && (
            <div className="space-y-3 p-4 bg-muted rounded-md">
              <h4 className="font-medium text-sm">解析结果</h4>

              <div className="grid grid-cols-[100px_1fr] gap-2 text-sm">
                <span className="text-muted-foreground">请求方法:</span>
                <span className="font-medium">{parsedData.method}</span>

                <span className="text-muted-foreground">请求路径:</span>
                <span className="font-mono">{parsedData.url}</span>

                {parsedData.headers && Object.keys(parsedData.headers).length > 0 && (
                  <>
                    <span className="text-muted-foreground">请求头:</span>
                    <span className="font-mono text-xs">
                      {JSON.stringify(parsedData.headers, null, 2)}
                    </span>
                  </>
                )}

                {parsedData.params && Object.keys(parsedData.params).length > 0 && (
                  <>
                    <span className="text-muted-foreground">查询参数:</span>
                    <span className="font-mono text-xs">
                      {JSON.stringify(parsedData.params, null, 2)}
                    </span>
                  </>
                )}

                {parsedData.body && (
                  <>
                    <span className="text-muted-foreground">请求体:</span>
                    <span className="font-mono text-xs">
                      {typeof parsedData.body === 'string'
                        ? parsedData.body
                        : JSON.stringify(parsedData.body, null, 2)}
                    </span>
                  </>
                )}
              </div>
            </div>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={handleClose}>
            取消
          </Button>
          <Button onClick={handleImport} disabled={!parsedData}>
            导入
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
