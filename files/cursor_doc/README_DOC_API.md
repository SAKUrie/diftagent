# 文档API功能说明

## 概述

基于 `login.py` 和 `doc_api.py` 实现的文档管理系统，支持文件上传、版本更新和历史版本回退功能。

## 数据库设计

### 表结构

系统为每种文档类型创建了独立的表结构：

1. **Resume文档**
   - `resume_documents` - 简历文档表
   - `resume_document_versions` - 简历版本表

2. **Letter文档**
   - `letter_documents` - 推荐信文档表
   - `letter_document_versions` - 推荐信版本表

3. **SOP文档**
   - `sop_documents` - SOP文档表
   - `sop_document_versions` - SOP版本表

### 特性

- **RLS (Row Level Security)**: 确保用户只能访问自己的文档
- **延迟外键约束**: 使用 `DEFERRABLE INITIALLY DEFERRED` 避免插入阻塞
- **内容大小限制**: 每个版本内容限制为5000字符
- **索引优化**: 包含索引减少回表，提升查询性能
- **软删除**: 支持软删除，保留历史数据

## API接口

### 1. 上传文档

```http
POST /documents/upload
Content-Type: application/x-www-form-urlencoded

doc_type=resume&title=My Resume&content=Resume content&content_format=markdown
```

**参数:**
- `doc_type`: 文档类型 (resume/letter/sop)
- `title`: 文档标题
- `content`: 文档内容
- `content_format`: 内容格式 (默认: markdown)

**响应:**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "type": "resume",
  "title": "My Resume",
  "current_version_id": "uuid",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "versions": [...]
}
```

### 2. 添加新版本

```http
POST /documents/{doc_type}/{doc_id}/versions
Content-Type: application/x-www-form-urlencoded

content=New version content&content_format=markdown
```

**参数:**
- `doc_type`: 文档类型
- `doc_id`: 文档ID
- `content`: 新版本内容
- `content_format`: 内容格式

### 3. 获取文档详情

```http
GET /documents/{doc_type}/{doc_id}
```

**响应:**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "type": "resume",
  "title": "My Resume",
  "current_version_id": "uuid",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "versions": [
    {
      "id": "uuid",
      "version_number": 1,
      "content": "Content",
      "content_format": "markdown",
      "created_at": "2024-01-01T00:00:00Z",
      "checksum_sha256": "hash"
    }
  ]
}
```

### 4. 获取版本历史

```http
GET /documents/{doc_type}/{doc_id}/versions
```

**响应:**
```json
[
  {
    "id": "uuid",
    "version_number": 2,
    "content": "Latest content",
    "content_format": "markdown",
    "created_at": "2024-01-01T00:00:00Z",
    "checksum_sha256": "hash"
  },
  {
    "id": "uuid",
    "version_number": 1,
    "content": "Original content",
    "content_format": "markdown",
    "created_at": "2024-01-01T00:00:00Z",
    "checksum_sha256": "hash"
  }
]
```

### 5. 回退到指定版本

```http
POST /documents/{doc_type}/{doc_id}/revert
Content-Type: application/json

{
  "version_number": 1
}
```

### 6. 获取指定版本详情

```http
GET /documents/{doc_type}/{doc_id}/versions/{version_number}
```

### 7. 获取用户的所有文档

```http
GET /documents/{doc_type}
```

### 8. 异步添加版本（预留接口）

```http
POST /documents/{doc_type}/{doc_id}/versions/async
Content-Type: application/x-www-form-urlencoded

content=New version content&content_format=markdown
```

## 数据库迁移

### 创建新表结构

运行以下SQL文件创建新的表结构：

```bash
psql -d your_database -f sql/documents_new_structure.sql
```

### 表结构特性

1. **外键约束**: 使用延迟约束避免插入阻塞
2. **内容约束**: 限制内容大小为5000字符
3. **索引优化**: 
   - 用户索引
   - 版本历史索引（包含索引）
   - 唯一版本号索引
4. **RLS策略**: 确保数据安全
5. **自动时间戳**: 自动更新 `updated_at` 字段

## 前端集成

### 认证

所有API都需要通过Cookie认证，登录后会自动设置 `access_token` cookie。

### 错误处理

API返回标准HTTP状态码：
- `200`: 成功
- `400`: 请求参数错误
- `401`: 未认证
- `404`: 资源不存在
- `500`: 服务器错误

### 示例前端调用

```javascript
// 上传文档
const formData = new FormData();
formData.append('doc_type', 'resume');
formData.append('title', 'My Resume');
formData.append('content', 'Resume content');
formData.append('content_format', 'markdown');

const response = await fetch('/documents/upload', {
  method: 'POST',
  body: formData,
  credentials: 'include'
});

// 添加版本
const versionData = new FormData();
versionData.append('content', 'New version content');
versionData.append('content_format', 'markdown');

const versionResponse = await fetch(`/documents/resume/${docId}/versions`, {
  method: 'POST',
  body: versionData,
  credentials: 'include'
});

// 获取版本历史
const versionsResponse = await fetch(`/documents/resume/${docId}/versions`, {
  credentials: 'include'
});

// 回退版本
const revertResponse = await fetch(`/documents/resume/${docId}/revert`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ version_number: 1 }),
  credentials: 'include'
});
```

## 测试

运行测试脚本验证API功能：

```bash
python test_doc_api.py
```

## 异步队列（预留）

系统预留了异步队列接口，用于处理高并发场景下的版本创建：

- `AsyncQueueService.enqueue_version_creation()`: 将任务加入队列
- `AsyncQueueService.process_version_creation()`: 处理队列任务

## 性能优化

1. **索引优化**: 使用包含索引减少回表
2. **延迟约束**: 避免外键约束阻塞插入
3. **软删除**: 保留历史数据，支持数据恢复
4. **内容校验**: SHA256校验确保数据完整性
5. **RLS**: 数据库级别的安全控制

## 部署说明

1. 确保PostgreSQL数据库已安装并配置
2. 运行数据库迁移脚本
3. 启动FastAPI应用
4. 配置前端调用API

## 注意事项

1. 所有API都需要用户认证
2. 内容大小限制为5000字符
3. 版本号自动递增
4. 支持markdown、html、plain格式
5. 使用软删除保留历史数据 