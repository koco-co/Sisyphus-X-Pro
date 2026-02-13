import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import { authService } from '@/lib/auth'
import { Button } from '@/components/ui/Button'
import { AlertCircle } from 'lucide-react'

/**
 * OAuth 回调处理页面
 * 处理 GitHub/Google OAuth 登录回调
 */
export default function OAuthCallback() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { login } = useAuth()
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [errorMessage, setErrorMessage] = useState('')

  useEffect(() => {
    const handleCallback = async () => {
      const code = searchParams.get('code')
      const state = searchParams.get('state')

      // 检查 URL 路径确定是哪个 provider
      const pathname = window.location.pathname
      const provider = pathname.includes('github') ? 'github' : pathname.includes('google') ? 'google' : null

      if (!code || !state || !provider) {
        setStatus('error')
        setErrorMessage('缺少必要的 OAuth 参数')
        return
      }

      try {
        // 调用后端 callback 接口
        const data = await authService.handleOAuthCallback(provider, code, state)

        // 存储 token 和用户信息
        localStorage.setItem('token', data.access_token)
        localStorage.setItem('user', JSON.stringify(data.user))

        setStatus('success')

        // 延迟跳转到首页,让用户看到成功提示
        setTimeout(() => {
          navigate('/', { replace: true })
        }, 1000)
      } catch (error) {
        setStatus('error')
        setErrorMessage(error instanceof Error ? error.message : 'OAuth 登录失败')
      }
    }

    handleCallback()
  }, [searchParams, navigate, login])

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center space-y-4">
        {status === 'loading' && (
          <div className="space-y-4">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto" />
            <p className="text-muted-foreground">正在登录...</p>
          </div>
        )}

        {status === 'success' && (
          <div className="space-y-4">
            <div className="rounded-full bg-green-100 dark:bg-green-900/20 p-3 w-fit mx-auto">
              <svg className="h-8 w-8 text-green-600 dark:text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <p className="text-lg font-medium">登录成功</p>
            <p className="text-sm text-muted-foreground">即将跳转到首页...</p>
          </div>
        )}

        {status === 'error' && (
          <div className="space-y-4">
            <div className="rounded-full bg-destructive/10 p-3 w-fit mx-auto">
              <AlertCircle className="h-8 w-8 text-destructive" />
            </div>
            <p className="text-lg font-medium text-destructive">登录失败</p>
            <p className="text-sm text-muted-foreground">{errorMessage}</p>
            <Button onClick={() => navigate('/login', { replace: true })}>
              返回登录页
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}
