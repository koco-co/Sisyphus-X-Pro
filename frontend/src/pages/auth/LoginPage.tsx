import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Github, Chrome } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { useToast } from '@/hooks/use-toast'
import { authService } from '@/lib/auth'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Label } from '@/components/ui/Label'
import { cn } from '@/lib/utils'

type TabType = 'login' | 'register'

export default function LoginPage() {
  const [activeTab, setActiveTab] = useState<TabType>('login')
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    nickname: '',
    confirmPassword: '',
  })
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(false)
  const { login, register } = useAuth()
  const { toast } = useToast()
  const navigate = useNavigate()

  const typewriterText = '打破命运循环,解放测试生产力'

  const validateForm = () => {
    const newErrors: Record<string, string> = {}

    if (!formData.email) {
      newErrors.email = '请输入邮箱'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = '邮箱格式不正确'
    }

    if (!formData.password) {
      newErrors.password = '请输入密码'
    } else if (formData.password.length < 6) {
      newErrors.password = '密码至少6位'
    }

    if (activeTab === 'register') {
      if (!formData.nickname) {
        newErrors.nickname = '请输入昵称'
      }
      if (formData.password !== formData.confirmPassword) {
        newErrors.confirmPassword = '两次密码不一致'
      }
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) return

    setLoading(true)
    try {
      if (activeTab === 'login') {
        await login(formData.email, formData.password)
        toast('登录成功', 'success')
        navigate('/')
      } else {
        await register(formData.email, formData.password, formData.nickname)
        toast('注册成功', 'success')
        navigate('/')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : (activeTab === 'login' ? '登录失败' : '注册失败')
      toast(errorMessage, 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleSocialLogin = async (provider: 'github' | 'google') => {
    try {
      const authUrl = provider === 'github'
        ? await authService.getGitHubAuthUrl()
        : await authService.getGoogleAuthUrl()

      // 跳转到 OAuth 提供商的授权页面
      window.location.href = authUrl
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '获取授权链接失败'
      toast(errorMessage, 'error')
    }
  }

  return (
    <div className="min-h-screen flex flex-col lg:flex-row">
      {/* 左半屏 - 品牌展示 */}
      <div className="lg:w-1/2 bg-gradient-to-br from-primary/10 via-primary/5 to-background p-8 lg:p-16 flex items-center justify-center relative overflow-hidden">
        {/* 动态背景装饰 */}
        <div className="absolute inset-0 opacity-20">
          <div className="absolute top-20 left-20 w-72 h-72 bg-primary rounded-full mix-blend-multiply filter blur-3xl animate-blob" />
          <div className="absolute top-40 right-20 w-72 h-72 bg-accent rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-2000" />
          <div className="absolute bottom-20 left-1/2 w-72 h-72 bg-secondary rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-4000" />
        </div>

        <div className="relative z-10 text-center max-w-lg">
          {/* Logo + 品牌名 */}
          <div className="mb-8">
            <h1 className="text-5xl lg:text-7xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-primary/60 mb-4">
              Sisyphus-X-Pro
            </h1>
            <div className="h-1 w-32 bg-primary mx-auto rounded-full" />
          </div>

          {/* 打字机效果 */}
          <p className="text-xl lg:text-2xl text-muted-foreground font-light">
            {typewriterText}
          </p>

          {/* 装饰性描述 */}
          <div className="mt-12 space-y-4 text-sm text-muted-foreground">
            <div className="flex items-center justify-center gap-2">
              <div className="h-px w-12 bg-border" />
              <span>企业级自动化测试管理平台</span>
              <div className="h-px w-12 bg-border" />
            </div>
            <p className="italic">"将重复的回归测试交给自动化,让测试工程师从推巨石中解放出来"</p>
          </div>
        </div>
      </div>

      {/* 右半屏 - 登录/注册表单 */}
      <div className="lg:w-1/2 flex items-center justify-center p-8 lg:p-16">
        <div className="w-full max-w-md space-y-8">
          {/* Tab 切换 */}
          <div className="flex gap-4 border-b border-border">
            <button
              onClick={() => setActiveTab('login')}
              className={cn(
                'flex-1 pb-4 text-sm font-medium transition-colors relative',
                activeTab === 'login'
                  ? 'text-primary'
                  : 'text-muted-foreground hover:text-foreground'
              )}
            >
              登录
              {activeTab === 'login' && (
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary rounded-full" />
              )}
            </button>
            <button
              onClick={() => setActiveTab('register')}
              className={cn(
                'flex-1 pb-4 text-sm font-medium transition-colors relative',
                activeTab === 'register'
                  ? 'text-primary'
                  : 'text-muted-foreground hover:text-foreground'
              )}
            >
              注册
              {activeTab === 'register' && (
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary rounded-full" />
              )}
            </button>
          </div>

          {/* 表单 */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {activeTab === 'register' && (
              <div className="space-y-2">
                <Label htmlFor="nickname">昵称</Label>
                <Input
                  id="nickname"
                  type="text"
                  placeholder="请输入昵称"
                  value={formData.nickname}
                  onChange={(e) => setFormData({ ...formData, nickname: e.target.value })}
                />
                {errors.nickname && <p className="text-sm text-destructive">{errors.nickname}</p>}
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="email">邮箱</Label>
              <Input
                id="email"
                type="email"
                placeholder="your@email.com"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              />
              {errors.email && <p className="text-sm text-destructive">{errors.email}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">密码</Label>
              <Input
                id="password"
                type="password"
                placeholder="至少6位密码"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              />
              {errors.password && <p className="text-sm text-destructive">{errors.password}</p>}
            </div>

            {activeTab === 'register' && (
              <div className="space-y-2">
                <Label htmlFor="confirmPassword">确认密码</Label>
                <Input
                  id="confirmPassword"
                  type="password"
                  placeholder="再次输入密码"
                  value={formData.confirmPassword}
                  onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                />
                {errors.confirmPassword && (
                  <p className="text-sm text-destructive">{errors.confirmPassword}</p>
                )}
              </div>
            )}

            <Button type="submit" className="w-full" size="lg" disabled={loading}>
              {loading ? '处理中...' : (activeTab === 'login' ? '登录' : '注册')}
            </Button>
          </form>

          {/* 分隔线 */}
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-border" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="bg-background px-2 text-muted-foreground">或</span>
            </div>
          </div>

          {/* OAuth 登录 */}
          <div className="grid grid-cols-2 gap-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => handleSocialLogin('github')}
              className="w-full"
            >
              <Github className="mr-2 h-4 w-4" />
              GitHub
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => handleSocialLogin('google')}
              className="w-full"
            >
              <Chrome className="mr-2 h-4 w-4" />
              Google
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
