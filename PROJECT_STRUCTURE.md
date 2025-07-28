# 项目结构总结

DiftAgent 系统的完整项目结构，采用前后端分离架构。

## 🏗️ 整体架构

```
diftagent/
├── backend/                 # 后端服务 (FastAPI + PostgreSQL)
├── frontend/               # 前端应用 (Next.js + TypeScript)
├── docs/                   # 项目文档
├── files/                  # 项目资源文件
└── README.md              # 项目说明
```

## 📁 详细结构

### 后端 (Backend)

```
backend/
├── api/                    # API 路由模块
│   ├── auth/              # 认证相关 API
│   │   └── login.py       # 用户认证和授权
│   ├── documents/         # 文档管理 API
│   │   └── doc_api.py     # 文档 CRUD 操作
│   └── health/            # 健康检查 API
├── models/                # 数据模型
│   └── models.py          # SQLAlchemy 模型定义
├── tests/                 # 测试文件
│   ├── test_login.py      # 登录功能测试
│   ├── test_document_api.py # 文档 API 测试
│   └── quick_login_test.py # 快速登录测试
├── scripts/               # 部署和初始化脚本
│   ├── start_server.py    # 服务器启动脚本
│   └── init_database.py   # 数据库初始化脚本
├── config/                # 配置文件
│   └── sql/              # SQL 脚本
├── main.py               # FastAPI 应用入口
├── routers.py            # 路由配置
├── requirements.txt      # Python 依赖
├── Dockerfile           # Docker 配置
└── README.md            # 后端说明文档
```

### 前端 (Frontend)

```
frontend/
├── src/                    # 源代码
│   ├── app/               # Next.js App Router
│   │   ├── auth/          # 认证页面
│   │   │   ├── login/     # 登录页面
│   │   │   ├── signup/    # 注册页面
│   │   │   └── forgot-password/ # 忘记密码
│   │   ├── dashboard/     # 仪表板
│   │   ├── documents/     # 文档管理
│   │   │   └── [docId]/   # 文档详情页面
│   │   ├── tools/         # 工具页面
│   │   ├── globals.css    # 全局样式
│   │   ├── layout.tsx     # 根布局
│   │   └── page.tsx       # 首页
│   ├── components/        # 可复用组件
│   │   ├── ui/           # UI 组件库
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── input.tsx
│   │   │   └── separator.tsx
│   │   └── FloatingInput.tsx
│   └── lib/              # 工具库
│       └── utils.ts      # 工具函数
├── public/               # 静态资源
├── package.json          # 项目配置
├── tailwind.config.ts    # Tailwind 配置
├── tsconfig.json         # TypeScript 配置
├── next.config.js        # Next.js 配置
└── README.md            # 前端说明文档
```

### 文档 (Docs)

```
docs/
├── api/                   # API 文档
│   └── README.md         # API 文档总览
├── deployment/            # 部署文档
│   └── README.md         # 部署指南
├── development/           # 开发文档
│   ├── README.md         # 开发指南
│   └── LOGIN_TEST_README.md # 登录测试说明
└── README.md             # 文档总览
```

### 资源文件 (Files)

```
files/
├── dcl/                   # DCL 配置文件
│   ├── 学校信息查询.yml
│   ├── 申请时间线安排与提醒schedule_reminder.yml
│   ├── 申请时间线安排与提醒schedule_reminder(copy).yml
│   └── 留学咨询WebAPP.yml
└── tools/                 # 工具文件
    ├── feishu_crud.py
    ├── models.py
    ├── test_dify.py
    └── tools.py
```

## 🔄 重构前后对比

### 重构前
```
diftagent/
├── login.py              # 主应用文件
├── doc_api.py            # 文档 API
├── models.py             # 数据模型
├── routers.py            # 路由配置
├── main.py               # 应用入口
├── test_*.py             # 测试文件
├── start_server.py       # 启动脚本
├── init_database.py      # 数据库初始化
├── requirements.txt      # Python 依赖
├── Dockerfile           # Docker 配置
├── sql/                 # SQL 脚本
├── frontend/            # 前端应用
└── README.md           # 项目说明
```

### 重构后
```
diftagent/
├── backend/             # 后端服务 (模块化)
│   ├── api/            # API 模块
│   ├── models/         # 数据模型
│   ├── tests/          # 测试文件
│   ├── scripts/        # 脚本文件
│   ├── config/         # 配置文件
│   └── README.md       # 后端文档
├── frontend/           # 前端应用 (保持不变)
├── docs/               # 完整文档体系
│   ├── api/           # API 文档
│   ├── deployment/     # 部署文档
│   └── development/    # 开发文档
└── README.md          # 项目总览
```

## 📊 重构优势

### 1. 前后端分离
- ✅ **清晰分离**: 后端和前端完全独立
- ✅ **独立部署**: 可以分别部署和扩展
- ✅ **技术栈独立**: 各自使用最适合的技术栈

### 2. 模块化架构
- ✅ **API 模块化**: 按功能分组 API 路由
- ✅ **模型分离**: 数据模型独立管理
- ✅ **测试组织**: 测试文件按功能分类

### 3. 文档体系
- ✅ **完整文档**: API、部署、开发文档齐全
- ✅ **分类清晰**: 按用途分类文档
- ✅ **易于维护**: 文档结构清晰易读

### 4. 开发体验
- ✅ **快速定位**: 文件结构清晰，易于找到
- ✅ **团队协作**: 前后端可以并行开发
- ✅ **代码复用**: 模块化设计便于复用

## 🚀 快速导航

### 后端开发
```bash
cd backend
python scripts/start_server.py
```

### 前端开发
```bash
cd frontend
npm run dev
```

### 文档查看
- [项目总览](../README.md)
- [后端文档](./backend/README.md)
- [前端文档](./frontend/README.md)
- [API 文档](./docs/api/README.md)
- [部署指南](./docs/deployment/README.md)
- [开发指南](./docs/development/README.md)

## 📝 维护说明

### 添加新功能
1. **后端**: 在 `backend/api/` 下创建新模块
2. **前端**: 在 `frontend/src/app/` 下添加新页面
3. **文档**: 在 `docs/` 下更新相应文档

### 文件命名规范
- **Python**: 使用 snake_case
- **TypeScript**: 使用 camelCase
- **组件**: 使用 PascalCase
- **目录**: 使用 kebab-case

### 提交规范
```bash
feat(backend): add new API endpoint
fix(frontend): resolve login issue
docs(api): update API documentation
```

## ✅ 重构完成

项目结构重构已完成，现在具有：
- 🏗️ **清晰的前后端分离架构**
- 📁 **模块化的文件组织**
- 📚 **完整的文档体系**
- 🚀 **易于维护和扩展的结构**

所有功能保持不变，只是文件组织更加合理！ 