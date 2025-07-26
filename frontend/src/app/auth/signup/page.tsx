'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { FloatingInput } from '@/components/FloatingInput'
import Link from 'next/link'
import Image from 'next/image'
import { useRouter } from 'next/navigation'

export default function SignupPage() {
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    confirmPassword: ''
  })
  const router = useRouter()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // 模拟注册成功，跳转到登录页面
    router.push('/auth/login')
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

        {/* 右侧注册表单 */}
        <Card className="w-full max-w-sm shadow-none border-none">
          <CardHeader className="space-y-1 pb-3">
            <h1 className="text-xl font-semibold">注册</h1>
            <p className="text-sm text-muted-foreground">创建您的EduPro账户</p>
          </CardHeader>

          <CardContent className="space-y-4">
            <form onSubmit={handleSubmit} className="space-y-4">
              <FloatingInput
                type="email"
                label="邮箱"
                placeholder="输入您的邮箱地址"
                value={formData.email}
                onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                required
              />

              <FloatingInput
                type="text"
                label="用户名"
                placeholder="输入用户名"
                value={formData.username}
                onChange={(e) => setFormData(prev => ({ ...prev, username: e.target.value }))}
                required
              />

              <FloatingInput
                type="password"
                label="密码"
                placeholder="输入密码"
                value={formData.password}
                onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
                required
              />

              <FloatingInput
                type="password"
                label="确认密码"
                placeholder="再次输入密码"
                value={formData.confirmPassword}
                onChange={(e) => setFormData(prev => ({ ...prev, confirmPassword: e.target.value }))}
                required
              />

              <Button type="submit" className="w-full h-10 bg-primary hover:bg-primary/90 text-primary-foreground">
                注册
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
              使用 Google 账号注册
            </Button>

            <Separator className="my-2" />

            <p className="text-xs text-muted-foreground text-center">
              注册即表示您同意我们的服务条款和隐私政策
            </p>
          </CardContent>

          <CardFooter>
            <div className="flex justify-center items-center w-full text-sm">
              <div>
                已有账号? <Link href="/auth/login" className="text-primary hover:brightness-110 font-bold">
                  去登录
                </Link>
              </div>
            </div>
          </CardFooter>
        </Card>
      </div>
    </div>
  )
}
