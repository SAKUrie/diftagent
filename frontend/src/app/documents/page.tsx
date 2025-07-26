'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'

type Document = {
  id: string
  title: string
  type: string
  updated_at: string
}

export default function DocumentsPage() {
  const [docs, setDocs] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ title: '', type: 'resume', content: '' })
  const [msg, setMsg] = useState('')
  const router = useRouter()

  // 获取所有文档
  useEffect(() => {
    fetch('/documents/', { credentials: 'include' })
      .then(res => res.json())
      .then(data => setDocs(data))
      .finally(() => setLoading(false))
  }, [showForm, msg])

  // 新建文档
  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    setMsg('')
    const res = await fetch('/documents/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ title, type, content, content_format: 'markdown' })
    })
    if (res.ok) {
      setMsg('新建成功')
      setShowForm(false)
      setForm({ title: '', type: 'resume', content: '' })
      // 自动刷新文档列表
      const data = await res.json()
      setDocs(docs => [data, ...docs])
    } else {
      setMsg('新建失败')
    }
  }

  return (
    <div className="max-w-3xl mx-auto p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">我的文档</h1>
        <button
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          onClick={() => setShowForm(v => !v)}
        >
          新建文档
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="mb-6 border p-4 rounded bg-gray-50">
          <div className="mb-2">
            <label className="block mb-1">标题</label>
            <input
              className="border rounded px-2 py-1 w-full"
              value={form.title}
              onChange={e => setForm(f => ({ ...f, title: e.target.value }))}
              required
            />
          </div>
          <div className="mb-2">
            <label className="block mb-1">类型</label>
            <select
              className="border rounded px-2 py-1 w-full"
              value={form.type}
              onChange={e => setForm(f => ({ ...f, type: e.target.value }))}
            >
              <option value="resume">简历</option>
              <option value="letter">推荐信</option>
              <option value="sop">SOP</option>
            </select>
          </div>
          <div className="mb-2">
            <label className="block mb-1">内容</label>
            <textarea
              className="border rounded px-2 py-1 w-full h-24"
              value={form.content}
              onChange={e => setForm(f => ({ ...f, content: e.target.value }))}
              required
            />
          </div>
          <button
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
            type="submit"
          >
            提交
          </button>
          {msg && <span className="ml-4 text-sm text-green-600">{msg}</span>}
        </form>
      )}

      {loading ? (
        <div>加载中...</div>
      ) : (
        <ul className="space-y-3">
          {docs.map(doc => (
            <li
              key={doc.id}
              className="border rounded p-4 flex justify-between items-center hover:bg-gray-50 cursor-pointer"
              onClick={() => router.push(`/documents/${doc.id}`)}
            >
              <div>
                <div className="font-bold">{doc.title}</div>
                <div className="text-xs text-gray-500">{doc.type}</div>
              </div>
              <div className="text-xs text-gray-400">{doc.updated_at?.slice(0, 16).replace('T', ' ')}</div>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}