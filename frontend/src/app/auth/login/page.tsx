'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { FloatingInput } from '@/components/FloatingInput'
import Link from 'next/link'
import Image from 'next/image'
import { useRouter } from 'next/navigation'

export default function LoginPage() {
  const [credentials, setCredentials] = useState({ username: '', password: '' })
  const [error, setError] = useState<string | null>(null)
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    try {
      const res = await fetch('http://localhost:8000/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
          username: credentials.username,
          password: credentials.password,
        }),
        credentials: 'include', // 允许后端设置cookie
      })
      if (!res.ok) {
        const data = await res.json()
        setError(data.detail || '登录失败')
        return
      }
      // 登录成功，跳转到 dashboard
      router.push('/dashboard')
    } catch (err) {
      setError('网络错误，请稍后重试')
    }
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      <div className="flex flex-col md:flex-row items-center justify-center gap-6 md:gap-16 w-full max-w-4xl px-4">

        {/* 左侧 Logo 和标语 */}
        <div className="flex flex-col items-center justify-center">
          <div className="w-40 h-auto mb-2">
            <Image
              src="https://ext.same-assets.com/1518271320/2578780032.svg"
              alt="EduPro AI · 留学行业的AI工具箱"
              width={160}
              height={51}
              className="w-full h-full object-contain"
            />
          </div>
          <p className="text-muted-foreground text-sm">留学行业的AI工具箱</p>
        </div>

        {/* 分割线 */}
        <div className="hidden lg:block">
          <Separator orientation="vertical" className="h-12 bg-border" />
        </div>

        {/* 右侧登录表单 */}
        <Card className="w-full max-w-sm shadow-none border-none">
          <CardHeader className="space-y-1 pb-3">
            <h1 className="text-xl font-semibold">登录</h1>
            <p className="text-sm text-muted-foreground">享受属于AI时代的工作效率</p>
          </CardHeader>

          <CardContent className="space-y-4">
            <form onSubmit={handleSubmit} className="space-y-4">
              <FloatingInput
                type="text"
                label="账号"
                placeholder="输入邮箱或用户名"
                value={credentials.username}
                onChange={(e) => setCredentials(prev => ({ ...prev, username: e.target.value }))}
              />

              <FloatingInput
                type="password"
                label="密码"
                placeholder="输入密码"
                value={credentials.password}
                onChange={(e) => setCredentials(prev => ({ ...prev, password: e.target.value }))}
              />

              {error && <div className="text-red-500 text-sm">{error}</div>}

              <Button type="submit" className="w-full h-10 bg-primary hover:bg-primary/90 text-primary-foreground">
                登录
              </Button>
            </form>

            <Separator className="my-4" />

            <Button variant="outline" className="w-full h-10 bg-foreground text-background hover:bg-foreground/90">
              <Image
                src="https://ext.same-assets.com/1518271320/1073860064.svg"
                alt=""
                width={14}
                height={14}
                className="mr-2"
              />
              使用 Google 账号登录
            </Button>

            <Separator className="my-2" />

            <p className="text-xs text-muted-foreground text-center">
              *使用Gmail邮箱注册的账号可直接使用Google登录原账号
            </p>
          </CardContent>

          <CardFooter>
            <div className="flex justify-between items-center w-full text-sm">
              <div>
                没有账号? <Link href="/auth/signup" className="text-primary hover:brightness-110 font-bold inline-flex items-center gap-1">
                  去注册
                  <Image
                    src="https://ext.same-assets.com/1518271320/704268976.svg"
                    alt=""
                    width={14}
                    height={14}
                  />
                </Link>
              </div>
              <Link href="/auth/forgot-password" className="text-primary hover:brightness-110">
                忘记密码?
              </Link>
            </div>
          </CardFooter>
        </Card>
      </div>
    </div>
  )
}
