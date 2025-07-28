# 部署指南

DiftAgent 文档管理系统的完整部署指南。

## 📋 目录

- [开发环境部署](./development.md) - 本地开发环境
- [生产环境部署](./production.md) - 生产环境部署
- [Docker 部署](./docker.md) - 容器化部署
- [云平台部署](./cloud.md) - 云平台部署指南

## 🏗️ 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (PostgreSQL)  │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 5432    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 快速部署

### 1. 环境要求

- **操作系统**: Linux, macOS, Windows
- **Python**: 3.8+
- **Node.js**: 18+
- **PostgreSQL**: 12+
- **Docker**: 20.10+ (可选)

### 2. 一键部署脚本

```bash
#!/bin/bash
# deploy.sh

echo "🚀 开始部署 DiftAgent..."

# 克隆项目
git clone https://github.com/your-repo/diftagent.git
cd diftagent

# 部署后端
echo "📦 部署后端..."
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python scripts/init_database.py
python scripts/start_server.py &

# 部署前端
echo "🎨 部署前端..."
cd ../frontend
npm install
npm run build
npm start &

echo "✅ 部署完成！"
echo "🌐 前端: http://localhost:3000"
echo "🔧 后端: http://localhost:8000"
echo "📚 API文档: http://localhost:8000/docs"
```

## 🔧 环境配置

### 环境变量

创建 `.env` 文件：

```bash
# 数据库配置
DATABASE_URL=postgresql://username:password@localhost:5432/diftagent
POSTGRES_DB=diftagent
POSTGRES_USER=diftagent
POSTGRES_PASSWORD=your_password

# JWT 配置
JWT_SECRET=your-super-secret-jwt-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 应用配置
APP_NAME=DiftAgent
APP_VERSION=1.0.0
DEBUG=false

# 前端配置
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=DiftAgent
```

### 数据库配置

```sql
-- 创建数据库
CREATE DATABASE diftagent;

-- 创建用户
CREATE USER diftagent WITH PASSWORD 'your_password';

-- 授权
GRANT ALL PRIVILEGES ON DATABASE diftagent TO diftagent;
```

## 📦 部署方式

### 1. 传统部署

#### 后端部署

```bash
# 安装依赖
cd backend
pip install -r requirements.txt

# 初始化数据库
python scripts/init_database.py

# 启动服务
python scripts/start_server.py
```

#### 前端部署

```bash
# 安装依赖
cd frontend
npm install

# 构建生产版本
npm run build

# 启动服务
npm start
```

### 2. Docker 部署

```bash
# 构建镜像
docker build -t diftagent-backend ./backend
docker build -t diftagent-frontend ./frontend

# 运行容器
docker run -d -p 8000:8000 diftagent-backend
docker run -d -p 3000:3000 diftagent-frontend
```

### 3. Docker Compose 部署

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: diftagent
      POSTGRES_USER: diftagent
      POSTGRES_PASSWORD: your_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://diftagent:your_password@postgres:5432/diftagent
      JWT_SECRET: your-super-secret-jwt-key
    ports:
      - "8000:8000"
    depends_on:
      - postgres

  frontend:
    build: ./frontend
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  postgres_data:
```

## 🚀 云平台部署

### Vercel 部署（前端）

1. 连接 GitHub 仓库
2. 配置环境变量
3. 自动部署

### Railway 部署（后端）

1. 连接 GitHub 仓库
2. 配置 PostgreSQL 数据库
3. 设置环境变量
4. 自动部署

### AWS 部署

```bash
# 使用 AWS CLI
aws ec2 run-instances \
  --image-id ami-12345678 \
  --instance-type t3.micro \
  --key-name your-key-pair \
  --security-group-ids sg-12345678
```

## 📊 监控和日志

### 日志配置

```python
# backend/logging.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### 健康检查

```bash
# 检查后端健康状态
curl http://localhost:8000/health

# 检查数据库连接
psql -h localhost -U diftagent -d diftagent -c "SELECT 1;"
```

### 性能监控

```bash
# 监控系统资源
htop

# 监控网络连接
netstat -tulpn

# 监控日志
tail -f app.log
```

## 🔒 安全配置

### SSL/TLS 配置

```nginx
# nginx.conf
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:3000;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
    }
}
```

### 防火墙配置

```bash
# UFW 防火墙
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 数据库安全

```sql
-- 限制数据库访问
ALTER USER diftagent CONNECTION LIMIT 10;

-- 设置密码策略
ALTER USER diftagent PASSWORD 'strong_password';

-- 启用 SSL
ALTER SYSTEM SET ssl = on;
```

## 🔄 CI/CD 配置

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy Backend
        run: |
          cd backend
          pip install -r requirements.txt
          python scripts/init_database.py
          
      - name: Deploy Frontend
        run: |
          cd frontend
          npm install
          npm run build
```

## 🐛 故障排除

### 常见问题

1. **数据库连接失败**
   ```bash
   # 检查 PostgreSQL 服务
   sudo systemctl status postgresql
   
   # 检查连接
   psql -h localhost -U diftagent -d diftagent
   ```

2. **端口被占用**
   ```bash
   # 查找占用进程
   lsof -i :8000
   
   # 杀死进程
   kill -9 <PID>
   ```

3. **权限问题**
   ```bash
   # 修复文件权限
   chmod +x scripts/start_server.py
   chmod +x scripts/init_database.py
   ```

### 日志分析

```bash
# 查看应用日志
tail -f backend/app.log

# 查看系统日志
journalctl -u your-service -f

# 查看错误日志
grep ERROR backend/app.log
```

## 📞 支持

- **部署问题**: [GitHub Issues](../../../issues)
- **文档**: [项目文档](../)
- **社区**: [Discussions](../../../discussions)

## 📄 许可证

本项目采用 MIT 许可证。 