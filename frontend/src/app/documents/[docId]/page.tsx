'use client'

import { useEffect, useState, ChangeEvent } from 'react'
import { useParams, useRouter } from 'next/navigation'

type Version = {
  id: string
  version_number: number
  content: string
  content_format: string
  created_at: string
}

type Document = {
  id: string
  title: string
  type: string
  current_version_id: string
  versions: Version[]
}

export default function DocumentPage() {
  const { docId } = useParams<{ docId: string }>()
  const router = useRouter()
  const [doc, setDoc] = useState<Document | null>(null)
  const [content, setContent] = useState('')
  const [selectedVersion, setSelectedVersion] = useState<number | null>(null)
  const [loading, setLoading] = useState(false)
  const [msg, setMsg] = useState('')

  // 获取文档详情
  useEffect(() => {
    if (!docId) return
    fetch(`/documents/${docId}`, { credentials: 'include' })
      .then(res => res.json())
      .then(data => {
        setDoc(data)
        const cur = data.versions.find((v: Version) => v.id === data.current_version_id)
        setContent(cur?.content || '')
        setSelectedVersion(cur?.version_number || null)
      })
  }, [docId])

  // 上传文件
  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = ev => setContent(ev.target?.result as string)
    reader.readAsText(file)
  }

  // 保存为新版本
  const handleSave = async () => {
    if (!doc) return
    setLoading(true)
    setMsg('')
    const res = await fetch(`/documents/${doc.id}/new_version`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ content, content_format: 'markdown' })
    })
    if (res.ok) {
      setMsg('保存成功')
      const updated = await res.json()
      setDoc(updated)
      setSelectedVersion(updated.versions[updated.versions.length - 1].version_number)
    } else {
      setMsg('保存失败')
    }
    setLoading(false)
  }

  // 回退到指定版本
  const handleRevert = async (version_number: number) => {
    if (!doc) return
    setLoading(true)
    setMsg('')
    const res = await fetch(`/documents/${doc.id}/revert/${version_number}`, {
      method: 'POST',
      credentials: 'include'
    })
    if (res.ok) {
      setMsg('已回退')
      const updated = await res.json()
      setDoc(updated)
      const cur = updated.versions.find((v: Version) => v.id === updated.current_version_id)
      setContent(cur?.content || '')
      setSelectedVersion(cur?.version_number || null)
    } else {
      setMsg('回退失败')
    }
    setLoading(false)
  }

  // 切换历史版本预览
  const handlePreview = async (version_number: number) => {
    if (!doc) return
    setLoading(true)
    setMsg('')
    const res = await fetch(`/documents/${doc.id}/version/${version_number}`, {
      credentials: 'include'
    })
    if (res.ok) {
      const v = await res.json()
      setContent(v.content)
      setSelectedVersion(v.version_number)
      setMsg(`已切换到版本${v.version_number}`)
    } else {
      setMsg('切换失败')
    }
    setLoading(false)
  }

  if (!doc) return <div className="p-8">加载中...</div>

  return (
    <div className="flex min-h-screen">
      {/* 侧边栏：历史版本 */}
      <aside className="w-64 border-r p-4 bg-gray-50">
        <h2 className="font-bold mb-2">历史版本</h2>
        <ul>
          {doc.versions
            .sort((a, b) => b.version_number - a.version_number)
            .map(v => (
              <li key={v.id} className="mb-2">
                <button
                  className={`block w-full text-left px-2 py-1 rounded ${selectedVersion === v.version_number ? 'bg-blue-100 font-bold' : 'hover:bg-gray-100'}`}
                  onClick={() => handlePreview(v.version_number)}
                >
                  版本{v.version_number} {v.id === doc.current_version_id && <span className="text-xs text-green-600">(当前)</span>}
                </button>
                <button
                  className="ml-2 text-xs text-blue-600 underline"
                  onClick={() => handleRevert(v.version_number)}
                  disabled={v.id === doc.current_version_id}
                >
                  回退
                </button>
              </li>
            ))}
        </ul>
      </aside>
      {/* 主体 */}
      <main className="flex-1 p-8">
        <div className="mb-4 flex items-center gap-4">
          <h1 className="text-2xl font-bold">{doc.title}</h1>
          <span className="text-sm text-gray-500">{doc.type}</span>
        </div>
        <div className="mb-4 flex items-center gap-4">
          <input type="file" accept=".md,.txt" onChange={handleFileChange} />
          <button
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            onClick={handleSave}
            disabled={loading}
          >
            保存为新版本
          </button>
          {msg && <span className="text-sm text-green-600">{msg}</span>}
        </div>
        <textarea
          className="w-full h-96 border rounded p-2 font-mono"
          value={content}
          onChange={e => setContent(e.target.value)}
        />
      </main>
    </div>
  )
}