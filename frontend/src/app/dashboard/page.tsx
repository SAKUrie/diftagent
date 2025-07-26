'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import Image from 'next/image'
import Link from 'next/link'

export default function DashboardPage() {
  const [user] = useState({ name: '用户', email: 'user@example.com' })

  const tools = [
    {
      title: '文书生成器',
      description: '快速生成个人陈述、推荐信等留学文书',
      icon: '📝',
      color: 'bg-blue-50 hover:bg-blue-100',
      textColor: 'text-blue-600'
    },
    {
      title: '申请表分析',
      description: '智能识别和解析各类申请表格',
      icon: '📋',
      color: 'bg-green-50 hover:bg-green-100',
      textColor: 'text-green-600'
    },
    {
      title: 'AI润色助手',
      description: '移除AI痕迹，让文书更加自然',
      icon: '✨',
      color: 'bg-purple-50 hover:bg-purple-100',
      textColor: 'text-purple-600'
    },
    {
      title: '院校匹配',
      description: '根据个人条件推荐合适的院校',
      icon: '🎓',
      color: 'bg-yellow-50 hover:bg-yellow-100',
      textColor: 'text-yellow-600'
    },
    {
      title: '时间规划',
      description: '制定个性化的申请时间表',
      icon: '📅',
      color: 'bg-red-50 hover:bg-red-100',
      textColor: 'text-red-600'
    },
    {
      title: '材料清单',
      description: '智能生成申请材料清单',
      icon: '📄',
      color: 'bg-indigo-50 hover:bg-indigo-100',
      textColor: 'text-indigo-600'
    }
  ]

  const recentProjects = [
    { name: '哈佛大学申请文书', status: '进行中', date: '2025-01-20' },
    { name: '斯坦福推荐信', status: '已完成', date: '2025-01-18' },
    { name: 'MIT个人陈述', status: '待审核', date: '2025-01-15' }
  ]

  return (
    <div className="min-h-screen bg-background">
      {/* 顶部导航栏 */}
      <nav className="bg-white border-b border-border p-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <Image
              src="https://ext.same-assets.com/1518271320/2578780032.svg"
              alt="EduPro"
              width={120}
              height={38}
              className="object-contain"
            />
            <span className="text-sm text-muted-foreground">工具平台</span>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-muted-foreground">欢迎回来，{user.name}</span>
            <Button variant="outline" size="sm">
              <Link href="/auth/login">退出登录</Link>
            </Button>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto p-6">
        {/* 欢迎区域 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-foreground mb-2">
            欢迎使用 EduPro AI 工具平台
          </h1>
          <p className="text-muted-foreground">
            享受属于AI时代的工作效率，快至5分钟搞定全套留学文案
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 主要工具区域 */}
          <div className="lg:col-span-2">
            <h2 className="text-xl font-semibold mb-4">AI 工具箱</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {tools.map((tool, index) => (
                <Card key={index} className={`cursor-pointer transition-all duration-200 ${tool.color} border-transparent hover:shadow-md`}>
                  <CardHeader className="pb-3">
                    <div className="flex items-center space-x-3">
                      <span className="text-2xl">{tool.icon}</span>
                      <CardTitle className={`text-lg ${tool.textColor}`}>
                        {tool.title}
                      </CardTitle>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <p className={`text-sm ${tool.textColor} opacity-80`}>
                      {tool.description}
                    </p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* 侧边栏 */}
          <div className="space-y-6">
            {/* 最近项目 */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">最近项目</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {recentProjects.map((project, index) => (
                  <div key={index} className="flex justify-between items-start">
                    <div className="flex-1">
                      <p className="text-sm font-medium">{project.name}</p>
                      <p className="text-xs text-muted-foreground">{project.date}</p>
                    </div>
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      project.status === '已完成' ? 'bg-green-100 text-green-700' :
                      project.status === '进行中' ? 'bg-blue-100 text-blue-700' :
                      'bg-yellow-100 text-yellow-700'
                    }`}>
                      {project.status}
                    </span>
                  </div>
                ))}
                <Separator className="my-3" />
                <Button variant="outline" size="sm" className="w-full">
                  查看全部项目
                </Button>
              </CardContent>
            </Card>

            {/* 快速操作 */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">快速操作</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button className="w-full bg-primary hover:bg-primary/90">
                  🚀 新建文书项目
                </Button>
                <Button variant="outline" className="w-full">
                  📤 上传申请表
                </Button>
                <Button variant="outline" className="w-full">
                  💡 获取AI建议
                </Button>
              </CardContent>
            </Card>

            {/* 统计信息 */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">使用统计</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">已生成文书</span>
                  <span className="text-sm font-medium">12 份</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">节省时间</span>
                  <span className="text-sm font-medium">24 小时</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">成功申请</span>
                  <span className="text-sm font-medium">5 所院校</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
