# 开发指南

DiftAgent 项目的完整开发指南，包括环境搭建、代码规范、测试等。

## 📋 目录

- [环境搭建](./setup.md) - 开发环境配置
- [代码规范](./coding-standards.md) - 代码风格和规范
- [测试指南](./testing.md) - 测试策略和工具
- [贡献指南](./contributing.md) - 如何贡献代码

## 🏗️ 项目结构

```
diftagent/
├── backend/                 # 后端服务
│   ├── api/                # API 模块
│   ├── models/             # 数据模型
│   ├── tests/              # 测试文件
│   ├── scripts/            # 脚本文件
│   └── config/             # 配置文件
├── frontend/               # 前端应用
│   ├── src/                # 源代码
│   ├── public/             # 静态资源
│   └── components/         # 组件库
└── docs/                   # 项目文档
```

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/your-repo/diftagent.git
cd diftagent
```

### 2. 后端开发

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python scripts/init_database.py

# 启动开发服务器
python scripts/start_server.py
```

### 3. 前端开发

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 🛠️ 开发工具

### 后端工具

- **Python 3.8+**: 主要开发语言
- **FastAPI**: Web 框架
- **SQLAlchemy**: ORM 框架
- **PostgreSQL**: 数据库
- **Pytest**: 测试框架
- **Black**: 代码格式化
- **Flake8**: 代码检查

### 前端工具

- **Node.js 18+**: JavaScript 运行时
- **Next.js 14**: React 框架
- **TypeScript**: 类型安全
- **Tailwind CSS**: 样式框架
- **ESLint**: 代码检查
- **Prettier**: 代码格式化

## 📝 代码规范

### Python 代码规范

#### 命名规范

```python
# 变量和函数使用 snake_case
user_name = "john"
def get_user_info():
    pass

# 类使用 PascalCase
class UserManager:
    pass

# 常量使用 UPPER_CASE
MAX_RETRY_COUNT = 3
```

#### 导入规范

```python
# 标准库导入
import os
import sys
from datetime import datetime

# 第三方库导入
import fastapi
from sqlalchemy import Column

# 本地模块导入
from models.user import User
from api.auth import router
```

#### 文档字符串

```python
def create_user(username: str, email: str) -> User:
    """
    创建新用户
    
    Args:
        username: 用户名
        email: 邮箱地址
        
    Returns:
        User: 创建的用户对象
        
    Raises:
        ValueError: 当用户名或邮箱无效时
    """
    pass
```

### TypeScript 代码规范

#### 命名规范

```typescript
// 变量和函数使用 camelCase
const userName = "john";
function getUserInfo() {
  // ...
}

// 接口和类型使用 PascalCase
interface UserProfile {
  id: string;
  name: string;
}

// 常量使用 UPPER_CASE
const MAX_RETRY_COUNT = 3;
```

#### 类型定义

```typescript
// 使用接口定义对象结构
interface Document {
  id: string;
  title: string;
  content: string;
  createdAt: Date;
}

// 使用类型别名定义联合类型
type DocumentType = "resume" | "letter" | "sop";

// 使用泛型提高代码复用性
interface ApiResponse<T> {
  data: T;
  status: "success" | "error";
  message?: string;
}
```

## 🧪 测试策略

### 后端测试

#### 单元测试

```python
# tests/test_auth.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_user_registration():
    """测试用户注册功能"""
    response = client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
        "role": "guest"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
```

#### 集成测试

```python
# tests/test_document_api.py
def test_document_upload():
    """测试文档上传功能"""
    # 先登录获取认证
    login_response = client.post("/auth/login", data={
        "username": "testuser",
        "password": "password123"
    })
    
    # 上传文档
    response = client.post("/documents/upload", data={
        "doc_type": "resume",
        "title": "My Resume",
        "content": "Resume content",
        "content_format": "markdown"
    }, cookies=login_response.cookies)
    
    assert response.status_code == 200
```

### 前端测试

#### 组件测试

```typescript
// __tests__/components/DocumentCard.test.tsx
import { render, screen } from '@testing-library/react';
import DocumentCard from '@/components/DocumentCard';

describe('DocumentCard', () => {
  it('renders document information correctly', () => {
    const document = {
      id: '1',
      title: 'My Resume',
      type: 'resume',
      updatedAt: new Date()
    };
    
    render(<DocumentCard document={document} />);
    
    expect(screen.getByText('My Resume')).toBeInTheDocument();
    expect(screen.getByText('resume')).toBeInTheDocument();
  });
});
```

#### API 测试

```typescript
// __tests__/api/documents.test.ts
import { uploadDocument } from '@/lib/api';

describe('Document API', () => {
  it('uploads document successfully', async () => {
    const formData = new FormData();
    formData.append('doc_type', 'resume');
    formData.append('title', 'My Resume');
    formData.append('content', 'Resume content');
    
    const result = await uploadDocument(formData);
    
    expect(result.id).toBeDefined();
    expect(result.title).toBe('My Resume');
  });
});
```

## 🔄 Git 工作流

### 分支策略

```
main                    # 主分支，生产环境
├── develop             # 开发分支
├── feature/user-auth   # 功能分支
├── bugfix/login-error  # 修复分支
└── hotfix/security     # 热修复分支
```

### 提交规范

```bash
# 提交格式
<type>(<scope>): <subject>

# 示例
feat(auth): add JWT token authentication
fix(docs): correct API endpoint documentation
test(api): add unit tests for document upload
```

### 类型说明

- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

## 📊 代码质量

### 代码覆盖率

```bash
# 后端测试覆盖率
cd backend
pytest --cov=api --cov=models --cov-report=html

# 前端测试覆盖率
cd frontend
npm run test:coverage
```

### 代码检查

```bash
# 后端代码检查
cd backend
flake8 api/ models/ tests/
black --check api/ models/ tests/

# 前端代码检查
cd frontend
npm run lint
npm run type-check
```

## 🚀 部署流程

### 开发环境

```bash
# 后端
cd backend
python scripts/start_server.py

# 前端
cd frontend
npm run dev
```

### 测试环境

```bash
# 运行测试
cd backend && python -m pytest
cd frontend && npm run test

# 构建
cd frontend && npm run build
```

### 生产环境

```bash
# 使用 Docker
docker-compose up -d

# 或手动部署
cd backend && python scripts/start_server.py
cd frontend && npm start
```

## 🐛 调试技巧

### 后端调试

```python
# 使用 pdb 调试
import pdb; pdb.set_trace()

# 使用日志调试
import logging
logging.debug("Debug information")

# 使用 FastAPI 调试模式
uvicorn main:app --reload --log-level debug
```

### 前端调试

```typescript
// 使用 console 调试
console.log('Debug info:', data);

// 使用 React DevTools
// 安装浏览器扩展

// 使用 Next.js 调试
NODE_ENV=development npm run dev
```

## 📚 学习资源

### 后端学习

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [PostgreSQL 文档](https://www.postgresql.org/docs/)

### 前端学习

- [Next.js 文档](https://nextjs.org/docs)
- [TypeScript 手册](https://www.typescriptlang.org/docs/)
- [Tailwind CSS 文档](https://tailwindcss.com/docs)

### 测试学习

- [Pytest 文档](https://docs.pytest.org/)
- [Jest 文档](https://jestjs.io/docs/getting-started)
- [Testing Library](https://testing-library.com/)

## 📞 支持

- **技术问题**: [GitHub Issues](../../../issues)
- **功能建议**: [GitHub Discussions](../../../discussions)
- **文档问题**: [文档 Issues](../../../issues)

## 📄 许可证

本项目采用 MIT 许可证。 