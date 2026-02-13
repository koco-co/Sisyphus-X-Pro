import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  FileText,
  Download,
  ExternalLink,
  Search,
  Filter,
  Trash2,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
} from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { useToast } from '@/hooks/use-toast'
import { reportAPI, type TestReport } from '@/lib/api'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Label } from '@/components/ui/Label'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/Dialog'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table'
import { Badge, BadgeSecondary } from '@/components/ui/Badge'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/DropdownMenu'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/Select'

export default function ReportsPage() {
  const navigate = useNavigate()
  const { token } = useAuth()
  const { toast } = useToast()

  const [reports, setReports] = useState<TestReport[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [selectedPlan, setSelectedPlan] = useState<string>('all')

  // 分页状态
  const [page, setPage] = useState(1)
  const [limit] = useState(10)
  const [total, setTotal] = useState(0)

  // 详情弹窗状态
  const [detailDialogOpen, setDetailDialogOpen] = useState(false)
  const [selectedReport, setSelectedReport] = useState<TestReport | null>(null)

  // 删除确认弹窗状态
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [deletingReport, setDeletingReport] = useState<TestReport | null>(null)

  // 获取报告列表
  const fetchReports = async () => {
    setLoading(true)
    try {
      const params: {
        page: number
        limit: number
        plan_id?: number
        status?: string
      } = {
        page,
        limit,
      }

      if (statusFilter !== 'all') {
        params.status = statusFilter
      }

      if (selectedPlan !== 'all') {
        params.plan_id = parseInt(selectedPlan)
      }

      const data = await reportAPI.getReports(params)
      setReports(data.reports)
      setTotal(data.total)
    } catch (error) {
      toast(error instanceof Error ? error.message : '获取报告列表失败', 'error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchReports()
  }, [page, limit, statusFilter, selectedPlan])

  // 获取报告详情
  const fetchReportDetail = async (reportId: number) => {
    try {
      const report = await reportAPI.getReport(reportId)
      setSelectedReport(report)
      setDetailDialogOpen(true)
    } catch (error) {
      toast(error instanceof Error ? error.message : '获取报告详情失败', 'error')
    }
  }

  // 打开删除确认弹窗
  const handleDeleteClick = (report: TestReport) => {
    setDeletingReport(report)
    setDeleteDialogOpen(true)
  }

  // 删除报告
  const handleDelete = async () => {
    if (!deletingReport) return

    try {
      await reportAPI.deleteReport(deletingReport.id)
      toast('删除成功', 'success')
      setDeleteDialogOpen(false)
      fetchReports()
    } catch (error) {
      toast(error instanceof Error ? error.message : '删除失败', 'error')
    }
  }

  // 打开 Allure 报告
  const handleOpenAllure = async () => {
    if (!selectedReport) return

    try {
      const allureData = await reportAPI.getAllureReport(selectedReport.id)
      window.open(allureData.url, '_blank')
    } catch (error) {
      toast(error instanceof Error ? error.message : '打开 Allure 报告失败', 'error')
    }
  }

  // 导出报告
  const handleExport = async (format: 'pdf' | 'excel' | 'html') => {
    if (!selectedReport) return

    try {
      toast('导出功能即将推出', 'info')
      // TODO: 实现导出功能
      // const blob = await reportAPI.exportReport(selectedReport.id, {
      //   format,
      //   include_details: true,
      // })
      // const url = window.URL.createObjectURL(blob)
      // const a = document.createElement('a')
      // a.href = url
      // a.download = `report_${selectedReport.id}.${format === 'excel' ? 'xlsx' : format}`
      // a.click()
      // window.URL.revokeObjectURL(url)
    } catch (error) {
      toast(error instanceof Error ? error.message : '导出失败', 'error')
    }
  }

  // 计算通过率
  const calculatePassRate = (report: TestReport) => {
    if (report.total_scenarios === 0) return 0
    return Math.round((report.passed / report.total_scenarios) * 100)
  }

  // 获取状态图标
  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'passed':
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />
      case 'running':
        return <Clock className="h-4 w-4 text-blue-500" />
      default:
        return <AlertCircle className="h-4 w-4 text-yellow-500" />
    }
  }

  // 获取状态徽章样式
  const getStatusBadgeClass = (status: string) => {
    switch (status.toLowerCase()) {
      case 'passed':
      case 'completed':
        return 'bg-green-500/10 text-green-500 border-green-500/20'
      case 'failed':
        return 'bg-red-500/10 text-red-500 border-red-500/20'
      case 'running':
        return 'bg-blue-500/10 text-blue-500 border-blue-500/20'
      default:
        return 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20'
    }
  }

  // 格式化时长
  const formatDuration = (seconds: number | null) => {
    if (!seconds) return '-'
    const minutes = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${minutes}m ${secs}s`
  }

  return (
    <div className="min-h-screen bg-background">
      {/* 页面头部 */}
      <div className="border-b bg-card">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">测试报告</h1>
              <p className="text-muted-foreground mt-1">查看和管理测试执行报告</p>
            </div>
          </div>
        </div>
      </div>

      {/* 搜索栏和筛选器 */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex flex-1 gap-2">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="搜索报告..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[140px]">
                <Filter className="mr-2 h-4 w-4" />
                <SelectValue placeholder="状态筛选" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">全部状态</SelectItem>
                <SelectItem value="passed">通过</SelectItem>
                <SelectItem value="failed">失败</SelectItem>
                <SelectItem value="running">运行中</SelectItem>
              </SelectContent>
            </Select>
            <Select value={selectedPlan} onValueChange={setSelectedPlan}>
              <SelectTrigger className="w-[140px]">
                <SelectValue placeholder="测试计划" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">全部计划</SelectItem>
                {/* TODO: 从 API 获取测试计划列表 */}
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      {/* 报告列表 */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-6">
        <div className="bg-card rounded-lg border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>执行 ID</TableHead>
                <TableHead>测试计划</TableHead>
                <TableHead>环境</TableHead>
                <TableHead>状态</TableHead>
                <TableHead>通过率</TableHead>
                <TableHead>时长</TableHead>
                <TableHead>开始时间</TableHead>
                <TableHead className="text-right">操作</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell className="text-center text-muted-foreground" colSpan={8}>
                    加载中...
                  </TableCell>
                </TableRow>
              ) : reports.length === 0 ? (
                <TableRow>
                  <TableCell className="text-center text-muted-foreground" colSpan={8}>
                    暂无测试报告
                  </TableCell>
                </TableRow>
              ) : (
                reports.map((report) => (
                  <TableRow
                    key={report.id}
                    className="cursor-pointer hover:bg-muted/50"
                    onClick={() => fetchReportDetail(report.id)}
                  >
                    <TableCell className="font-medium">
                      <div className="flex items-center gap-2">
                        <FileText className="h-4 w-4 text-muted-foreground" />
                        <span className="text-xs">{report.execution_id}</span>
                      </div>
                    </TableCell>
                    <TableCell className="text-muted-foreground">#{report.plan_id}</TableCell>
                    <TableCell>
                      <BadgeSecondary>{report.environment_name}</BadgeSecondary>
                    </TableCell>
                    <TableCell>
                      <Badge className={getStatusBadgeClass(report.status)}>
                        <div className="flex items-center gap-1">
                          {getStatusIcon(report.status)}
                          <span>{report.status}</span>
                        </div>
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <span
                        className={`font-medium ${
                          calculatePassRate(report) >= 80
                            ? 'text-green-500'
                            : calculatePassRate(report) >= 50
                              ? 'text-yellow-500'
                              : 'text-red-500'
                        }`}
                      >
                        {calculatePassRate(report)}%
                      </span>
                      <span className="text-muted-foreground text-xs ml-1">
                        ({report.passed}/{report.total_scenarios})
                      </span>
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {formatDuration(report.duration_seconds)}
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {new Date(report.started_at).toLocaleString('zh-CN')}
                    </TableCell>
                    <TableCell className="text-right">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={(e) => e.stopPropagation()}
                          >
                            操作
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem
                            onClick={(e) => {
                              e.stopPropagation()
                              fetchReportDetail(report.id)
                            }}
                          >
                            <FileText className="mr-2 h-4 w-4" />
                            查看详情
                          </DropdownMenuItem>
                          <DropdownMenuItem
                            onClick={(e) => {
                              e.stopPropagation()
                              setSelectedReport(report)
                              handleOpenAllure()
                            }}
                            disabled={!report.allure_path}
                          >
                            <ExternalLink className="mr-2 h-4 w-4" />
                            Allure 报告
                          </DropdownMenuItem>
                          <DropdownMenuItem
                            onClick={(e) => {
                              e.stopPropagation()
                              setSelectedReport(report)
                              handleExport('pdf')
                            }}
                          >
                            <Download className="mr-2 h-4 w-4" />
                            导出 PDF
                          </DropdownMenuItem>
                          <DropdownMenuItem
                            onClick={(e) => {
                              e.stopPropagation()
                              handleDeleteClick(report)
                            }}
                            className="text-destructive focus:text-destructive"
                          >
                            <Trash2 className="mr-2 h-4 w-4" />
                            删除
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>

          {/* 分页 */}
          {total > limit && (
            <div className="flex items-center justify-between px-6 py-4 border-t">
              <div className="text-sm text-muted-foreground">
                共 {total} 条记录
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                >
                  上一页
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage((p) => p + 1)}
                  disabled={page * limit >= total}
                >
                  下一页
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 报告详情弹窗 */}
      <Dialog open={detailDialogOpen} onOpenChange={setDetailDialogOpen}>
        <DialogContent
          onClose={() => setDetailDialogOpen(false)}
          className="max-w-4xl max-h-[80vh] overflow-y-auto"
        >
          <DialogHeader>
            <DialogTitle>测试报告详情</DialogTitle>
          </DialogHeader>
          {selectedReport && (
            <div className="space-y-4">
              {/* 基本信息 */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-muted-foreground">执行 ID</Label>
                  <p className="font-medium">{selectedReport.execution_id}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground">测试计划</Label>
                  <p className="font-medium">#{selectedReport.plan_id}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground">执行环境</Label>
                  <p className="font-medium">{selectedReport.environment_name}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground">状态</Label>
                  <p className="font-medium">{selectedReport.status}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground">开始时间</Label>
                  <p className="font-medium">
                    {new Date(selectedReport.started_at).toLocaleString('zh-CN')}
                  </p>
                </div>
                <div>
                  <Label className="text-muted-foreground">结束时间</Label>
                  <p className="font-medium">
                    {selectedReport.finished_at
                      ? new Date(selectedReport.finished_at).toLocaleString('zh-CN')
                      : '-'}
                  </p>
                </div>
              </div>

              {/* 统计信息 */}
              <div className="grid grid-cols-4 gap-4">
                <div className="bg-muted/50 rounded-lg p-4 text-center">
                  <p className="text-2xl font-bold">{selectedReport.total_scenarios}</p>
                  <p className="text-sm text-muted-foreground">总场景数</p>
                </div>
                <div className="bg-green-500/10 rounded-lg p-4 text-center">
                  <p className="text-2xl font-bold text-green-500">{selectedReport.passed}</p>
                  <p className="text-sm text-muted-foreground">通过</p>
                </div>
                <div className="bg-red-500/10 rounded-lg p-4 text-center">
                  <p className="text-2xl font-bold text-red-500">{selectedReport.failed}</p>
                  <p className="text-sm text-muted-foreground">失败</p>
                </div>
                <div className="bg-yellow-500/10 rounded-lg p-4 text-center">
                  <p className="text-2xl font-bold text-yellow-500">{selectedReport.skipped}</p>
                  <p className="text-sm text-muted-foreground">跳过</p>
                </div>
              </div>

              {/* 通过率 */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <Label>通过率</Label>
                  <span className="text-2xl font-bold">{calculatePassRate(selectedReport)}%</span>
                </div>
                <div className="w-full bg-muted rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${
                      calculatePassRate(selectedReport) >= 80
                        ? 'bg-green-500'
                        : calculatePassRate(selectedReport) >= 50
                          ? 'bg-yellow-500'
                          : 'bg-red-500'
                    }`}
                    style={{ width: `${calculatePassRate(selectedReport)}%` }}
                  />
                </div>
              </div>
            </div>
          )}
          <DialogFooter>
            {selectedReport?.allure_path && (
              <Button variant="outline" onClick={handleOpenAllure}>
                <ExternalLink className="mr-2 h-4 w-4" />
                Allure 报告
              </Button>
            )}
            <Button onClick={() => setDetailDialogOpen(false)}>关闭</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 删除确认弹窗 */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent onClose={() => setDeleteDialogOpen(false)}>
          <DialogHeader>
            <DialogTitle>确认删除</DialogTitle>
          </DialogHeader>
          <div className="py-4">
            <p className="text-muted-foreground">
              确定要删除报告 <span className="font-semibold text-foreground">{deletingReport?.execution_id}</span>{' '}
              吗？
              <br />
              此操作不可撤销。
            </p>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteDialogOpen(false)}>
              取消
            </Button>
            <Button variant="destructive" onClick={handleDelete}>
              删除
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
