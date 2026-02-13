// Dashboard - 首页仪表盘组件

import { useEffect, useState } from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { dashboardAPI } from '@/lib/api'
import type { CoreStats, TrendDataPoint, CoverageData } from '@/lib/api'

// 统计卡片组件
interface StatCardProps {
  title: string
  value: number
  icon: string
  color: string
}

function StatCard({ title, value, icon, color }: StatCardProps) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm transition-all hover:shadow-md">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="mt-2 text-3xl font-bold text-gray-900">{value}</p>
        </div>
        <div
          className={`flex h-12 w-12 items-center justify-center rounded-full ${color} bg-opacity-10`}
        >
          <span className="text-2xl">{icon}</span>
        </div>
      </div>
    </div>
  )
}

export default function Dashboard() {
  const [stats, setStats] = useState<CoreStats | null>(null)
  const [trend, setTrend] = useState<TrendDataPoint[]>([])
  const [coverage, setCoverage] = useState<CoverageData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true)
        setError(null)

        // 并行获取所有数据
        const [statsData, trendData, coverageData] = await Promise.all([
          dashboardAPI.getCoreStats(),
          dashboardAPI.getExecutionTrend(30),
          dashboardAPI.getProjectCoverage(),
        ])

        setStats(statsData)
        setTrend(trendData.trend)
        setCoverage(coverageData)
      } catch (err) {
        console.error('获取仪表盘数据失败:', err)
        setError('加载数据失败，请稍后重试')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-center">
          <div className="mb-4 h-12 w-12 animate-spin rounded-full border-b-2 border-t-2 border-blue-600" />
          <p className="text-gray-600">加载中...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="rounded-lg border border-red-200 bg-red-50 p-8 text-center">
          <p className="text-lg font-medium text-red-800">{error}</p>
        </div>
      </div>
    )
  }

  // 准备覆盖率图表数据
  const coverageChartData = coverage
    ? [
        { name: '已测试', value: coverage.tested_projects, color: '#10b981' },
        { name: '未测试', value: coverage.untested_projects, color: '#f59e0b' },
      ]
    : []

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="mx-auto max-w-7xl">
        {/* 页面标题 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">仪表盘</h1>
          <p className="mt-2 text-gray-600">测试项目概览与统计信息</p>
        </div>

        {/* DASH-001: 核心指标卡片 */}
        {stats && (
          <div className="mb-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard
              title="项目总数"
              value={stats.total_projects}
              icon="📁"
              color="text-blue-600"
            />
            <StatCard
              title="接口总数"
              value={stats.total_interfaces}
              icon="🔌"
              color="text-green-600"
            />
            <StatCard
              title="场景总数"
              value={stats.total_scenarios}
              icon="🎯"
              color="text-purple-600"
            />
            <StatCard
              title="计划总数"
              value={stats.total_plans}
              icon="📋"
              color="text-orange-600"
            />
          </div>
        )}

        <div className="grid gap-6 lg:grid-cols-2">
          {/* DASH-002: 测试执行趋势图 */}
          <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
            <h2 className="mb-6 text-xl font-semibold text-gray-900">
              测试执行趋势 (最近30天)
            </h2>
            {trend.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={trend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="date"
                    tick={{ fontSize: 12 }}
                    tickFormatter={(value) => {
                      const date = new Date(value)
                      return `${date.getMonth() + 1}/${date.getDate()}`
                    }}
                  />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'white',
                      border: '1px solid #ccc',
                      borderRadius: '4px',
                    }}
                    labelFormatter={(value) => `日期: ${value}`}
                    formatter={(value: number | undefined) => [
                      `执行 ${value ?? 0} 次`,
                      '执行次数',
                    ]}
                  />
                  <Legend />
                  <Bar dataKey="count" fill="#3b82f6" name="执行次数" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex h-64 items-center justify-center text-gray-500">
                暂无数据
              </div>
            )}
          </div>

          {/* DASH-003: 项目覆盖率概览 */}
          <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
            <h2 className="mb-6 text-xl font-semibold text-gray-900">项目覆盖率概览</h2>
            {coverage && coverage.tested_projects + coverage.untested_projects > 0 ? (
              <div>
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={coverageChartData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) =>
                        `${name} ${((percent ?? 0) * 100).toFixed(1)}%`
                      }
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {coverageChartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
                <div className="mt-4 text-center">
                  <p className="text-sm text-gray-600">
                    已测试项目: <span className="font-semibold text-green-600">{coverage?.tested_projects}</span>
                    {' | '}
                    未测试项目: <span className="font-semibold text-orange-600">{coverage?.untested_projects}</span>
                  </p>
                  <p className="mt-2 text-2xl font-bold text-gray-900">
                    覆盖率: {coverage?.coverage_percentage}%
                  </p>
                </div>
              </div>
            ) : (
              <div className="flex h-64 items-center justify-center text-gray-500">
                暂无项目数据
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
