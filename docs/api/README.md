# API 文档

DiftAgent 文档管理系统的完整 API 文档。

## 📋 目录

- [认证 API](./auth.md) - 用户认证和授权
- [文档管理 API](./documents.md) - 文档 CRUD 操作
- [健康检查 API](./health.md) - 系统健康检查
- [错误处理](./errors.md) - API 错误码和响应格式

## 🚀 快速开始

### 基础信息

- **Base URL**: `http://localhost:8000`
- **API 版本**: v1
- **认证方式**: JWT Token (Cookie)
- **内容类型**: `application/json` / `application/x-www-form-urlencoded`

### 认证流程

1. **注册用户**
   ```http
   POST /auth/register
   Content-Type: application/json
   
   {
     "username": "testuser",
     "email": "test@example.com",
     "password": "password123",
     "role": "guest"
   }
   ```

2. **用户登录**
   ```http
   POST /auth/login
   Content-Type: application/x-www-form-urlencoded
   
   username=testuser&password=password123
   ```

3. **使用认证**
   - 登录成功后，服务器会设置认证 Cookie
   - 后续请求会自动携带认证信息

## 📊 响应格式

### 成功响应

```json
{
  "id": "uuid",
  "status": "success",
  "data": {
    // 响应数据
  }
}
```

### 错误响应

```json
{
  "detail": "错误描述信息"
}
```

## 🔐 认证

所有 API 端点（除了 `/auth/*` 和 `/health`）都需要用户认证。

### 认证方式

1. **Cookie 认证**（推荐）
   - 登录后自动设置认证 Cookie
   - 浏览器自动发送认证信息

2. **Header 认证**
   ```http
   Authorization: Bearer <jwt_token>
   ```

## 📄 文档类型

系统支持以下文档类型：

- `resume` - 简历文档
- `letter` - 推荐信文档
- `sop` - 个人陈述文档

## 🗄️ 数据库设计

### 表结构

```
users
├── id (UUID, PK)
├── username (VARCHAR)
├── email (VARCHAR, UNIQUE)
├── password_hash (VARCHAR)
├── role (VARCHAR)
├── created_at (TIMESTAMP)
└── updated_at (TIMESTAMP)

{type}_documents
├── id (UUID, PK)
├── user_id (UUID, FK)
├── title (VARCHAR)
├── current_version_id (UUID, FK)
├── created_at (TIMESTAMP)
├── updated_at (TIMESTAMP)
└── deleted_at (TIMESTAMP)

{type}_document_versions
├── id (UUID, PK)
├── document_id (UUID, FK)
├── version_number (INTEGER)
├── content (TEXT)
├── content_format (VARCHAR)
├── checksum_sha256 (VARCHAR)
├── created_by (UUID, FK)
├── created_at (TIMESTAMP)
└── deleted_at (TIMESTAMP)
```

### 特性

- **RLS (Row Level Security)**: 用户只能访问自己的数据
- **软删除**: 数据不会物理删除
- **版本控制**: 完整的版本历史
- **内容校验**: SHA256 校验和
- **大小限制**: 内容最大 5000 字符

## 📈 性能特性

### 索引优化

```sql
-- 用户文档索引
CREATE INDEX idx_documents_user ON {type}_documents(user_id) 
WHERE deleted_at IS NULL;

-- 版本历史索引
CREATE INDEX idx_versions_history ON {type}_document_versions(document_id, created_at DESC) 
INCLUDE (version_number, content_format)
WHERE deleted_at IS NULL;
```

### 查询优化

- 使用 `INCLUDE` 减少回表
- 时间降序排列
- 软删除过滤
- 延迟外键约束

## 🔒 安全特性

### 数据安全

- **RLS**: 数据库级别的访问控制
- **输入验证**: Pydantic 数据验证
- **SQL 注入防护**: 参数化查询
- **XSS 防护**: 内容清理

### 认证安全

- **JWT 令牌**: 安全的身份验证
- **密码哈希**: bcrypt 加密
- **会话管理**: 安全的 Cookie 设置
- **CORS 配置**: 跨域请求控制

## 📝 开发指南

### 添加新 API 端点

1. 在 `backend/api/` 下创建新模块
2. 定义路由和处理器
3. 在 `routers.py` 中注册路由
4. 添加相应的测试

### 错误处理

```python
from fastapi import HTTPException

# 业务逻辑错误
raise HTTPException(status_code=400, detail="Invalid input")

# 认证错误
raise HTTPException(status_code=401, detail="Unauthorized")

# 资源不存在
raise HTTPException(status_code=404, detail="Resource not found")
```

### 数据验证

```python
from pydantic import BaseModel, validator

class DocumentCreate(BaseModel):
    title: str
    content: str
    content_format: str = "markdown"
    
    @validator('content')
    def validate_content_length(cls, v):
        if len(v) > 5000:
            raise ValueError('Content too long')
        return v
```

## 🧪 测试

### API 测试

```bash
# 运行所有测试
cd backend/tests
python test_document_api.py
python test_login.py
```

### 手动测试

```bash
# 健康检查
curl http://localhost:8000/health

# 用户注册
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"123456","role":"guest"}'

# 用户登录
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test&password=123456"
```

## 📞 支持

- **API 文档**: http://localhost:8000/docs
- **交互式文档**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health
- **问题反馈**: [GitHub Issues](../../../issues) 