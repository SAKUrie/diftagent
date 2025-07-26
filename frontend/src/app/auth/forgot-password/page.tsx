'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { FloatingInput } from '@/components/FloatingInput'
import Link from 'next/link'
import Image from 'next/image'

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [isSubmitted, setIsSubmitted] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // 模拟发送重置邮件
    setIsSubmitted(true)
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

        {/* 右侧忘记密码表单 */}
        <Card className="w-full max-w-sm shadow-none border-none">
          <CardHeader className="space-y-1 pb-3">
            <h1 className="text-xl font-semibold">忘记密码</h1>
            <p className="text-sm text-muted-foreground">
              {isSubmitted ? '重置链接已发送' : '输入您的邮箱地址，我们将发送重置链接'}
            </p>
          </CardHeader>

          <CardContent className="space-y-4">
            {!isSubmitted ? (
              <form onSubmit={handleSubmit} className="space-y-4">
                <FloatingInput
                  type="email"
                  label="邮箱"
                  placeholder="输入您的邮箱地址"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />

                <Button type="submit" className="w-full h-10 bg-primary hover:bg-primary/90 text-primary-foreground">
                  发送重置链接
                </Button>
              </form>
            ) : (
              <div className="space-y-4">
                <div className="text-center space-y-2">
                  <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto">
                    <svg className="w-8 h-8 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    我们已向 <span className="font-medium text-foreground">{email}</span> 发送了密码重置链接。
                  </p>
                  <p className="text-xs text-muted-foreground">
                    请检查您的邮箱（包括垃圾邮件文件夹）并点击链接重置密码。
                  </p>
                </div>

                <Button
                  onClick={() => setIsSubmitted(false)}
                  variant="outline"
                  className="w-full h-10"
                >
                  重新发送
                </Button>
              </div>
            )}

            <Separator className="my-4" />

            <p className="text-xs text-muted-foreground text-center">
              链接将在24小时后失效
            </p>
          </CardContent>

          <CardFooter>
            <div className="flex justify-center items-center w-full text-sm">
              <div>
                记起密码了? <Link href="/auth/login" className="text-primary hover:brightness-110 font-bold">
                  返回登录
                </Link>
              </div>
            </div>
          </CardFooter>
        </Card>
      </div>
    </div>
  )
}
