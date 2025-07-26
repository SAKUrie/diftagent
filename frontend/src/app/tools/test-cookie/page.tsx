'use client'

import { useEffect, useState } from 'react'

export default function TestCookiePage() {
  const [authStatus, setAuthStatus] = useState<'pending' | 'ok' | 'forbidden' | 'unauth' | 'error'>('pending')
  const [message, setMessage] = useState('')

  useEffect(() => {
    // 假设跳转时带了 ?tool=xxx，或你可以根据业务写死一个 toolKey
    const params = new URLSearchParams(window.location.search)
    const tool = params.get('tool') || 'tool_essay' // 默认测试 tool_essay

    fetch('http://localhost:8000/authz', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ tool })
    })
      .then(async res => {
        if (res.ok) {
          setAuthStatus('ok')
          setMessage('您有权限访问本工具')
        } else if (res.status === 403) {
          const data = await res.json()
          setAuthStatus('forbidden')
          setMessage(data.detail || '无权限访问本工具')
        } else if (res.status === 401) {
          setAuthStatus('unauth')
          setMessage('未登录或登录已过期')
        } else {
          setAuthStatus('error')
          setMessage('服务异常，请稍后重试')
        }
      })
      .catch(() => {
        setAuthStatus('error')
        setMessage('网络错误，请稍后重试')
      })
  }, [])

  return (
    <div className="min-h-screen flex flex-col items-center justify-center">
      <h1 className="text-2xl font-bold mb-4">工具访问权限测试</h1>
      <div className="mb-2">
        {authStatus === 'pending' && '正在检测权限...'}
        {authStatus !== 'pending' && message}
      </div>
      <div className="text-muted-foreground text-sm mt-4">
        本页用于测试当前用户是否有权限访问本工具即cookies是否正确携带跳转信息。
      </div>
    </div>
  )
}