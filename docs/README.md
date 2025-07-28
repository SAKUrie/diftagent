# 文档管理系统

基于 FastAPI 和 PostgreSQL 的文档管理系统，支持文件上传、版本更新和历史版本回退功能。

## 功能特性

- ✅ **多文档类型支持**: Resume、Letter、SOP 三种文档类型
- ✅ **版本管理**: 完整的版本历史记录和回退功能
- ✅ **用户认证**: 基于 JWT 的用户认证系统
- ✅ **数据安全**: RLS (Row Level Security) 确保数据安全
- ✅ **性能优化**: 索引优化和延迟约束
- ✅ **软删除**: 保留历史数据，支持数据恢复
- ✅ **内容校验**: SHA256 校验确保数据完整性

## 快速开始

### 1. 环境要求

- Python 3.8+
- PostgreSQL 12+
- pip

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 数据库配置

确保 PostgreSQL 数据库已启动，并更新 `login.py` 中的数据库连接配置：

```python
pg_dsn: str = "postgresql+psycopg2://postgres:010921@127.0.0.1:5400/aiagent"
```

### 4. 初始化数据库

```bash
python init_database.py
```

### 5. 启动服务器

```bash
python start_server.py
```

或者直接使用 uvicorn：

```bash
uvicorn login:app --host 0.0.0.0 --port 8000 --reload
```

### 6. 访问API

- 服务器地址: http://localhost:8000
- API文档: http://localhost:8000/docs
- 交互式API文档: http://localhost:8000/redoc

## API 接口

### 认证

所有API都需要用户认证。首先注册用户，然后登录获取认证cookie。

#### 注册用户

```http
POST /register
Content-Type: application/json

{
  "username": "testuser",
  "email": "testuser@example.com",
  "password": "testpassword",
  "role": "student"
}
```

#### 用户登录

```http
POST /login
Content-Type: application/x-www-form-urlencoded

username=testuser@example.com&password=testpassword
```

### 文档管理

#### 上传文档

```http
POST /documents/upload
Content-Type: application/x-www-form-urlencoded

doc_type=resume&title=My Resume&content=Resume content&content_format=markdown
```

#### 添加新版本

```http
POST /documents/{doc_type}/{doc_id}/versions
Content-Type: application/x-www-form-urlencoded

content=New version content&content_format=markdown
```

#### 获取文档详情

```http
GET /documents/{doc_type}/{doc_id}
```

#### 获取版本历史

```http
GET /documents/{doc_type}/{doc_id}/versions
```

#### 回退到指定版本

```http
POST /documents/{doc_type}/{doc_id}/revert
Content-Type: application/json

{
  "version_number": 1
}
```

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

## 测试

运行测试脚本验证API功能：

```bash
python test_doc_api.py
```

## 前端集成

### JavaScript 示例

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

## 项目结构

```
diftagent/
├── login.py                 # 主应用文件，包含认证和路由
├── doc_api.py              # 文档API实现
├── requirements.txt         # Python依赖
├── start_server.py         # 服务器启动脚本
├── init_database.py        # 数据库初始化脚本
├── test_doc_api.py         # API测试脚本
├── sql/
│   ├── documents_new_structure.sql  # 新表结构SQL
│   ├── documents.sql               # 旧表结构（参考）
│   └── documents_versions.sql      # 旧版本表结构（参考）
├── README.md              # 项目说明
└── README_DOC_API.md      # API详细说明
```

## 部署

### 生产环境部署

1. **数据库配置**
   ```bash
   # 创建生产数据库
   createdb production_db
   
   # 运行迁移
   psql -d production_db -f sql/documents_new_structure.sql
   ```

2. **环境变量**
   ```bash
   export DATABASE_URL="postgresql://user:password@host:port/db"
   export JWT_SECRET="your-secret-key"
   ```

3. **启动服务**
   ```bash
   gunicorn login:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

### Docker 部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "login:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 性能优化

1. **索引优化**: 使用包含索引减少回表
2. **延迟约束**: 避免外键约束阻塞插入
3. **软删除**: 保留历史数据，支持数据恢复
4. **内容校验**: SHA256校验确保数据完整性
5. **RLS**: 数据库级别的安全控制

## 异步队列（预留）

系统预留了异步队列接口，用于处理高并发场景下的版本创建：

- `AsyncQueueService.enqueue_version_creation()`: 将任务加入队列
- `AsyncQueueService.process_version_creation()`: 处理队列任务

## 注意事项

1. 所有API都需要用户认证
2. 内容大小限制为5000字符
3. 版本号自动递增
4. 支持markdown、html、plain格式
5. 使用软删除保留历史数据
6. 确保PostgreSQL数据库已正确配置

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License 