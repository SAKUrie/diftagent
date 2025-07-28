# 对话日志API文档

## 概述

对话日志API提供了用户对话会话和消息的完整管理功能，支持存储和读取用户的对话历史记录。

## 数据库设计

### 表结构

#### conversation_sessions (对话会话表)
- `id`: UUID主键
- `user_id`: 用户ID (外键)
- `session_name`: 会话名称 (255字符)
- `session_type`: 会话类型 (50字符，默认'general')
- `created_at`: 创建时间
- `updated_at`: 更新时间
- `deleted_at`: 删除时间 (软删除)
- `session_metadata`: JSONB元数据

#### conversation_messages (对话消息表)
- `id`: UUID主键
- `session_id`: 会话ID (外键)
- `user_id`: 用户ID (外键)
- `message_type`: 消息类型 ('user', 'assistant', 'system', 'tool')
- `content`: 消息内容 (TEXT)
- `role`: 角色 (50字符，默认'user')
- `tool_name`: 工具名称 (100字符，可选)
- `tool_params`: 工具参数 (JSONB，可选)
- `tool_result`: 工具结果 (JSONB，可选)
- `tokens_used`: 使用的token数量 (INTEGER，默认0)
- `created_at`: 创建时间
- `deleted_at`: 删除时间 (软删除)

### 索引和约束
- 用户会话名称唯一约束
- 消息类型检查约束
- 行级安全策略
- 性能优化索引

## API端点

### 会话管理

#### 创建对话会话
```http
POST /conversations/sessions
```

**请求体:**
```json
{
  "session_name": "我的对话",
  "session_type": "general",
  "metadata": {
    "description": "关于留学申请的对话",
    "tags": ["留学", "申请"]
  }
}
```

**响应:**
```json
{
  "id": "uuid",
  "session_name": "我的对话",
  "session_type": "general",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
      "session_metadata": {
      "description": "关于留学申请的对话",
      "tags": ["留学", "申请"]
    },
    "message_count": 0,
    "last_message_at": null
  }
```

#### 获取会话列表
```http
GET /conversations/sessions?session_type=general&limit=50&offset=0
```

**查询参数:**
- `session_type`: 会话类型过滤 (可选)
- `limit`: 返回数量 (1-100，默认50)
- `offset`: 跳过数量 (默认0)

**响应:**
```json
[
  {
    "id": "uuid",
    "session_name": "我的对话",
    "session_type": "general",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "session_metadata": {},
    "message_count": 5,
    "last_message_at": "2024-01-01T01:00:00Z"
  }
]
```

#### 获取会话详情
```http
GET /conversations/sessions/{session_id}
```

**响应:**
```json
{
  "session": {
    "id": "uuid",
    "session_name": "我的对话",
    "session_type": "general",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "session_metadata": {},
    "message_count": 3,
    "last_message_at": "2024-01-01T01:00:00Z"
  },
  "messages": [
    {
      "id": "uuid",
      "message_type": "user",
      "content": "你好",
      "role": "user",
      "tool_name": null,
      "tool_params": null,
      "tool_result": null,
      "tokens_used": 2,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### 更新会话
```http
PUT /conversations/sessions/{session_id}
```

**请求体:**
```json
{
  "session_name": "更新后的会话名称",
  "session_metadata": {
    "description": "更新后的描述"
  }
}
```

#### 删除会话
```http
DELETE /conversations/sessions/{session_id}
```

### 消息管理

#### 添加消息
```http
POST /conversations/sessions/{session_id}/messages
```

**请求体:**
```json
{
  "message_type": "user",
  "content": "我想了解留学申请",
  "role": "user",
  "tool_name": null,
  "tool_params": null,
  "tool_result": null,
  "tokens_used": 8
}
```

**工具消息示例:**
```json
{
  "message_type": "tool",
  "content": "已查询到申请时间线",
  "role": "tool",
  "tool_name": "schedule_reminder",
  "tool_params": {
    "action": "get_timeline",
    "country": "US"
  },
  "tool_result": {
    "status": "success",
    "data": {
      "timeline": [
        {"month": "9月", "task": "准备材料"}
      ]
    }
  },
  "tokens_used": 15
}
```

#### 获取消息列表
```http
GET /conversations/sessions/{session_id}/messages?limit=100&offset=0
```

**查询参数:**
- `limit`: 返回数量 (1-500，默认100)
- `offset`: 跳过数量 (默认0)

#### 删除消息
```http
DELETE /conversations/messages/{message_id}
```

## 消息类型说明

### user
用户发送的消息

### assistant
AI助手回复的消息

### system
系统消息，如错误提示、状态更新等

### tool
工具执行的消息，包含工具名称、参数和结果

## 错误处理

### 400 Bad Request
- 会话名称已存在
- 消息类型无效
- 请求参数验证失败

### 401 Unauthorized
- 未提供认证信息
- 认证失败

### 404 Not Found
- 会话不存在
- 消息不存在
- UUID格式无效

### 500 Internal Server Error
- 数据库操作失败
- 服务器内部错误

## 使用示例

### 前端集成示例

```javascript
// 创建会话
const createSession = async (sessionData) => {
  const response = await fetch('/conversations/sessions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify(sessionData)
  });
  return response.json();
};

// 添加消息
const addMessage = async (sessionId, messageData) => {
  const response = await fetch(`/conversations/sessions/${sessionId}/messages`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify(messageData)
  });
  return response.json();
};

// 获取会话列表
const getSessions = async () => {
  const response = await fetch('/conversations/sessions', {
    credentials: 'include'
  });
  return response.json();
};

// 获取会话详情
const getSession = async (sessionId) => {
  const response = await fetch(`/conversations/sessions/${sessionId}`, {
    credentials: 'include'
  });
  return response.json();
};
```

### React组件示例

```jsx
import React, { useState, useEffect } from 'react';

const ConversationManager = () => {
  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      const response = await fetch('/conversations/sessions', {
        credentials: 'include'
      });
      const data = await response.json();
      setSessions(data);
    } catch (error) {
      console.error('Failed to load sessions:', error);
    }
  };

  const createSession = async (name) => {
    try {
      const response = await fetch('/conversations/sessions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          session_name: name,
          session_type: 'general'
        })
      });
      const newSession = await response.json();
      setSessions([newSession, ...sessions]);
      return newSession;
    } catch (error) {
      console.error('Failed to create session:', error);
    }
  };

  const addMessage = async (content, type = 'user') => {
    if (!currentSession) return;

    try {
      const response = await fetch(`/conversations/sessions/${currentSession.id}/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          message_type: type,
          content: content,
          role: type,
          tokens_used: content.length
        })
      });
      const newMessage = await response.json();
      setMessages([...messages, newMessage]);
    } catch (error) {
      console.error('Failed to add message:', error);
    }
  };

  return (
    <div>
      <h2>对话管理</h2>
      {/* 会话列表 */}
      <div>
        <h3>会话列表</h3>
        {sessions.map(session => (
          <div key={session.id} onClick={() => setCurrentSession(session)}>
            {session.session_name} ({session.message_count}条消息)
          </div>
        ))}
      </div>

      {/* 消息列表 */}
      {currentSession && (
        <div>
          <h3>消息列表</h3>
          {messages.map(message => (
            <div key={message.id}>
              <strong>[{message.message_type}]</strong> {message.content}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ConversationManager;
```

## 性能优化

1. **分页查询**: 支持limit和offset参数，避免一次性加载大量数据
2. **索引优化**: 为常用查询字段创建索引
3. **软删除**: 使用deleted_at字段，避免物理删除
4. **行级安全**: 确保用户只能访问自己的数据

## 安全特性

1. **认证**: 所有API都需要用户认证
2. **授权**: 用户只能访问自己的会话和消息
3. **输入验证**: 严格验证所有输入参数
4. **SQL注入防护**: 使用参数化查询
5. **XSS防护**: 输出内容进行适当转义

## 扩展功能

1. **消息搜索**: 支持按内容搜索消息
2. **会话标签**: 支持为会话添加标签
3. **消息统计**: 提供消息数量、token使用量等统计
4. **导出功能**: 支持导出对话记录
5. **实时同步**: 支持WebSocket实时消息同步 