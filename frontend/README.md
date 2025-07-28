# Frontend - Next.js 文档管理系统

基于 Next.js 和 TypeScript 的现代化前端应用，提供直观的文档管理界面。

## 🏗️ 项目结构

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
│   │   ├── ui/           # UI组件库
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── input.tsx
│   │   │   └── separator.tsx
│   │   └── FloatingInput.tsx
│   └── lib/              # 工具库
│       └── utils.ts      # 工具函数
├── public/               # 静态资源
├── package.json          # 项目配置
├── tailwind.config.ts    # Tailwind配置
├── tsconfig.json         # TypeScript配置
└── next.config.js        # Next.js配置
```

## 🚀 快速开始

### 1. 环境要求

- Node.js 18+
- npm 或 yarn 或 bun

### 2. 安装依赖

```bash
# 使用 npm
npm install

# 使用 yarn
yarn install

# 使用 bun
bun install
```

### 3. 环境配置

创建 `.env.local` 文件：

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=DiftAgent
```

### 4. 启动开发服务器

```bash
# 使用 npm
npm run dev

# 使用 yarn
yarn dev

# 使用 bun
bun dev
```

访问 [http://localhost:3000](http://localhost:3000) 查看应用。

## 📚 功能特性

### 🔐 用户认证
- 用户注册/登录
- 密码重置
- JWT 令牌管理
- 会话持久化

### 📄 文档管理
- 文档上传和编辑
- 版本历史查看
- 版本回退功能
- 多文档类型支持

### 🎨 用户界面
- 响应式设计
- 现代化 UI
- 暗色/亮色主题
- 无障碍访问

### ⚡ 性能优化
- 代码分割
- 图片优化
- 缓存策略
- SEO 优化

## 🛠️ 技术栈

### 核心框架
- **Next.js 14** - React 全栈框架
- **TypeScript** - 类型安全
- **React 18** - 用户界面库

### 样式和 UI
- **Tailwind CSS** - 实用优先的 CSS 框架
- **shadcn/ui** - 高质量 UI 组件
- **Lucide React** - 图标库

### 状态管理
- **React Context** - 全局状态管理
- **React Hook Form** - 表单处理
- **Zod** - 数据验证

### 开发工具
- **ESLint** - 代码检查
- **Prettier** - 代码格式化
- **Biome** - 代码质量工具

## 📱 页面结构

### 认证页面
- `/auth/login` - 用户登录
- `/auth/signup` - 用户注册
- `/auth/forgot-password` - 密码重置

### 主要功能
- `/dashboard` - 用户仪表板
- `/documents` - 文档列表
- `/documents/[docId]` - 文档详情
- `/tools` - 工具页面

## 🧪 测试

### 运行测试

```bash
# 单元测试
npm run test

# 端到端测试
npm run test:e2e

# 类型检查
npm run type-check
```

### 代码质量

```bash
# 代码检查
npm run lint

# 代码格式化
npm run format

# 构建检查
npm run build
```

## 🚀 部署

### Vercel 部署（推荐）

1. 连接 GitHub 仓库
2. 配置环境变量
3. 自动部署

### 手动部署

```bash
# 构建生产版本
npm run build

# 启动生产服务器
npm start
```

### Docker 部署

```dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
```

## 🔧 配置

### 环境变量

```bash
# API 配置
NEXT_PUBLIC_API_URL=http://localhost:8000

# 应用配置
NEXT_PUBLIC_APP_NAME=DiftAgent
NEXT_PUBLIC_APP_VERSION=1.0.0

# 认证配置
NEXTAUTH_SECRET=your-secret-key
NEXTAUTH_URL=http://localhost:3000
```

### Tailwind 配置

自定义 Tailwind CSS 配置在 `tailwind.config.ts` 中。

### TypeScript 配置

TypeScript 配置在 `tsconfig.json` 中。

## 📊 性能优化

### 构建优化
- 代码分割和懒加载
- 图片优化和 WebP 支持
- 字体优化和预加载
- 缓存策略

### 运行时优化
- React 18 并发特性
- 虚拟滚动
- 内存管理
- 网络请求优化

## 🔒 安全特性

### 前端安全
- XSS 防护
- CSRF 防护
- 内容安全策略 (CSP)
- 输入验证和清理

### 认证安全
- JWT 令牌管理
- 安全的密码处理
- 会话管理
- 权限控制

## 📝 开发指南

### 添加新页面

1. 在 `src/app/` 下创建新目录
2. 添加 `page.tsx` 文件
3. 配置路由和布局

### 添加新组件

1. 在 `src/components/` 下创建组件
2. 使用 TypeScript 定义类型
3. 添加必要的测试

### 样式指南

- 使用 Tailwind CSS 类名
- 遵循设计系统
- 保持响应式设计
- 支持暗色主题

### API 集成

```typescript
// API 客户端示例
const apiClient = {
  async uploadDocument(data: FormData) {
    const response = await fetch('/api/documents/upload', {
      method: 'POST',
      body: data,
      credentials: 'include'
    });
    return response.json();
  }
};
```

## 🐛 故障排除

### 常见问题

1. **构建失败**
   - 检查 TypeScript 错误
   - 验证依赖版本
   - 清理缓存

2. **API 连接失败**
   - 检查后端服务状态
   - 验证 API URL 配置
   - 检查 CORS 设置

3. **样式问题**
   - 检查 Tailwind 配置
   - 验证 CSS 导入
   - 清理样式缓存

## 📞 支持

- 查看 [Next.js 文档](https://nextjs.org/docs)
- 提交 [Issue](../../issues)
- 查看 [开发文档](../../docs/development/)

## 📄 许可证

本项目采用 MIT 许可证。
