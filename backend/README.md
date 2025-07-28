# Backend - FastAPI 文档管理系统

基于 FastAPI 和 PostgreSQL 的后端服务，提供完整的文档管理 API。

## 🏗️ 项目结构

```
backend/
├── api/                    # API路由模块
│   ├── auth/              # 认证相关API
│   │   └── login.py       # 用户认证和授权
│   ├── documents/         # 文档管理API
│   │   └── doc_api.py     # 文档CRUD操作
│   └── health/            # 健康检查API
├── models/                # 数据模型
│   └── models.py          # SQLAlchemy模型定义
├── tests/                 # 测试文件
│   ├── test_login.py      # 登录功能测试
│   ├── test_document_api.py # 文档API测试
│   └── quick_login_test.py # 快速登录测试
├── scripts/               # 部署和初始化脚本
│   ├── start_server.py    # 服务器启动脚本
│   └── init_database.py   # 数据库初始化脚本
├── config/                # 配置文件
│   └── sql/              # SQL脚本
├── main.py               # FastAPI应用入口
├── routers.py            # 路由配置
├── requirements.txt      # Python依赖
└── Dockerfile           # Docker配置
```

## 🚀 快速开始

### 1. 环境要求

- Python 3.8+
- PostgreSQL 12+
- pip

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 数据库配置

确保 PostgreSQL 数据库已启动，并更新数据库连接配置：

```python
# 在 main.py 中配置
DATABASE_URL = "postgresql+psycopg2://username:password@localhost:5432/database"
```

### 4. 初始化数据库

```bash
python scripts/init_database.py
```

### 5. 启动服务器

```bash
# 使用启动脚本
python scripts/start_server.py

# 或直接使用 uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 📚 API 文档

### 认证 API

- `POST /auth/login` - 用户登录
- `POST /auth/register` - 用户注册
- `POST /auth/refresh` - 刷新令牌

### 文档管理 API

- `POST /documents/upload` - 上传文档
- `GET /documents/{doc_type}/{doc_id}` - 获取文档详情
- `POST /documents/{doc_type}/{doc_id}/versions` - 添加新版本
- `GET /documents/{doc_type}/{doc_id}/versions` - 获取版本历史
- `POST /documents/{doc_type}/{doc_id}/revert` - 版本回退
- `GET /documents/{doc_type}` - 获取用户所有文档

### 健康检查

- `GET /health` - 健康检查

## 🧪 测试

### 运行所有测试

```bash
cd tests
python test_login.py
python test_document_api.py
```

### 快速测试

```bash
python quick_login_test.py
```

## 🗄️ 数据库设计

### 表结构

1. **用户表** (`users`)
   - 用户基本信息
   - 角色权限管理

2. **文档表** (按类型分离)
   - `resume_documents` - 简历文档
   - `letter_documents` - 推荐信文档
   - `sop_documents` - SOP文档

3. **版本表** (按类型分离)
   - `resume_document_versions` - 简历版本
   - `letter_document_versions` - 推荐信版本
   - `sop_document_versions` - SOP版本

### 特性

- **RLS (Row Level Security)**: 数据安全隔离
- **软删除**: 保留历史数据
- **版本控制**: 完整的版本管理
- **内容校验**: SHA256 校验和
- **索引优化**: 性能优化

## 🔧 配置

### 环境变量

```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/db"
export JWT_SECRET="your-secret-key"
export JWT_ALGORITHM="HS256"
export ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 数据库配置

参考 `config/sql/` 目录下的 SQL 脚本进行数据库初始化。

## 🚀 部署

### 开发环境

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 生产环境

```bash
# 使用 gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker

# 使用 Docker
docker build -t diftagent-backend .
docker run -p 8000:8000 diftagent-backend
```

## 📊 性能优化

1. **数据库索引**: 优化查询性能
2. **连接池**: 数据库连接复用
3. **异步处理**: 支持异步队列
4. **缓存机制**: 减少数据库查询

## 🔒 安全特性

1. **JWT 认证**: 安全的令牌认证
2. **RLS 安全**: 数据库级别的访问控制
3. **输入验证**: Pydantic 数据验证
4. **CORS 配置**: 跨域请求控制

## 📝 开发指南

### 添加新的 API 端点

1. 在 `api/` 目录下创建新的模块
2. 在 `routers.py` 中注册路由
3. 在 `main.py` 中包含路由

### 添加新的数据模型

1. 在 `models/` 目录下定义模型
2. 更新数据库迁移脚本
3. 运行数据库初始化

### 运行测试

```bash
# 单元测试
python -m pytest tests/

# 集成测试
python tests/test_document_api.py
```

## 🐛 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查 PostgreSQL 服务状态
   - 验证数据库连接配置

2. **认证失败**
   - 检查 JWT 密钥配置
   - 验证用户凭据

3. **API 错误**
   - 查看服务器日志
   - 检查请求格式

## 📞 支持

- 查看 [API 文档](http://localhost:8000/docs)
- 提交 [Issue](../../issues)
- 查看 [开发文档](../../docs/development/) 