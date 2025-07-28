# 登录功能测试说明

## 概述

本项目提供了两个登录测试脚本，用于验证登录功能的完整性：

1. **`test_login.py`** - 完整的登录功能测试套件
2. **`quick_login_test.py`** - 快速登录测试脚本

## 测试脚本说明

### 1. 完整测试套件 (`test_login.py`)

这个脚本包含以下测试项目：

#### 基础功能测试
- ✅ **健康检查** - 验证服务器是否正常运行
- ✅ **用户注册** - 测试新用户注册功能
- ✅ **用户登录** - 测试正常登录流程
- ✅ **错误密码登录** - 验证密码错误处理
- ✅ **不存在用户登录** - 验证用户不存在处理

#### 高级功能测试
- ✅ **重复注册** - 验证重复邮箱注册处理
- ✅ **不同邮箱注册** - 测试多用户注册
- ✅ **Cookie权限检查** - 验证登录后的权限验证
- ✅ **无Cookie权限检查** - 验证未登录的权限拒绝
- ✅ **刷新Token** - 测试Token刷新功能

#### 使用方法

```bash
# 激活虚拟环境
source .venv/bin/activate

# 运行完整测试
python test_login.py
```

#### 测试结果示例

```
🚀 开始登录功能测试
测试时间: 2024-01-01 12:00:00
服务器地址: http://localhost:8000

=== 测试健康检查 ===
健康检查状态码: 200
健康检查响应: {'status': 'ok', 'timestamp': '2024-01-01T12:00:00'}

=== 测试用户注册 ===
用户名: testuser
邮箱: testuser@example.com
角色: student
注册状态码: 200
注册成功: {'id': 'uuid', 'username': 'testuser', 'email': 'testuser@example.com', 'role': 'student', 'is_active': True}

=== 测试用户登录 ===
用户名/邮箱: testuser@example.com
登录状态码: 200
登录成功: {'access_token': '...', 'refresh_token': '...', 'token_type': 'bearer'}
Cookies: {'access_token': '...', 'last_page': '/dashboard'}

==================================================
📊 测试结果汇总
==================================================
健康检查: ✅ 通过
用户注册: ✅ 通过
用户登录: ✅ 通过
错误密码登录: ✅ 通过
不存在用户登录: ✅ 通过
重复注册: ✅ 通过
不同邮箱注册: ✅ 通过
Cookie权限检查: ✅ 通过
无Cookie权限检查: ✅ 通过
刷新Token: ✅ 通过

总计: 10/10 测试通过
成功率: 100.0%
🎉 所有测试通过！
```

### 2. 快速测试脚本 (`quick_login_test.py`)

这个脚本提供快速验证登录功能的基本测试：

#### 测试项目
- ✅ **健康检查** - 验证服务器状态
- ✅ **用户注册** - 快速注册测试
- ✅ **用户登录** - 快速登录测试

#### 使用方法

```bash
# 运行快速测试
python quick_login_test.py

# 使用指定凭据测试登录
python quick_login_test.py testuser@example.com 123456
```

#### 测试结果示例

```
🚀 快速登录测试
服务器地址: http://localhost:8000

1. 测试健康检查...
   状态码: 200
   ✅ 健康检查通过

2. 测试用户注册...
   状态码: 200
   ✅ 注册成功

3. 测试用户登录...
   状态码: 200
   ✅ 登录成功
   Access Token: eyJhbGciOiJIUzI1NiIs...
   Refresh Token: eyJhbGciOiJIUzI1NiIs...
   Cookies: {'access_token': '...', 'last_page': '/dashboard'}

✅ 快速登录测试完成，登录功能正常
```

## 测试环境要求

### 1. 服务器状态
确保服务器正在运行：
```bash
# 启动服务器
python start_server.py

# 或者使用uvicorn
uvicorn login:app --host 0.0.0.0 --port 8000 --reload
```

### 2. 数据库状态
确保数据库已初始化：
```bash
# 初始化数据库
python init_database.py
```

### 3. 依赖安装
确保所有依赖已安装：
```bash
pip install -r requirements.txt
```

## API 接口说明

### 登录相关接口

#### 1. 用户注册
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

#### 2. 用户登录
```http
POST /login
Content-Type: application/x-www-form-urlencoded

username=testuser@example.com&password=testpassword
```

#### 3. 刷新Token
```http
POST /refresh
Content-Type: application/json

{
  "refresh_token": "your_refresh_token"
}
```

#### 4. 权限检查
```http
POST /authz
Content-Type: application/json

{
  "tool": "tool_basic"
}
```

#### 5. 健康检查
```http
GET /health
```

## 常见问题

### 1. 服务器连接失败
```
❌ 健康检查异常: Connection refused
```
**解决方案：**
- 确保服务器正在运行
- 检查端口8000是否被占用
- 使用 `lsof -ti:8000 | xargs kill -9` 释放端口

### 2. 数据库连接失败
```
❌ 注册异常: connection to server at 127.0.0.1 (127.0.0.1), port 5400 failed
```
**解决方案：**
- 确保PostgreSQL数据库正在运行
- 检查数据库连接配置
- 运行 `python init_database.py` 初始化数据库

### 3. 登录失败
```
❌ 登录失败: {"detail":"Incorrect username or password"}
```
**解决方案：**
- 确保用户已注册
- 检查用户名和密码是否正确
- 使用 `python quick_login_test.py` 重新注册用户

### 4. 权限检查失败
```
❌ 权限检查失败: {"detail":"Could not validate credentials (cookie)"}
```
**解决方案：**
- 确保先登录获取Cookie
- 检查Cookie是否正确设置
- 使用Session保持登录状态

## 测试最佳实践

### 1. 测试顺序
1. 先运行健康检查确保服务器正常
2. 运行快速测试验证基本功能
3. 运行完整测试套件验证所有功能

### 2. 测试环境
- 使用独立的测试数据库
- 定期清理测试数据
- 使用不同的测试用户

### 3. 错误处理
- 检查服务器日志获取详细错误信息
- 验证数据库连接和表结构
- 确认所有依赖包已正确安装

## 扩展测试

### 1. 添加自定义测试
在 `test_login.py` 中添加新的测试方法：

```python
def test_custom_function(self):
    """自定义测试"""
    print("=== 自定义测试 ===")
    # 添加测试逻辑
    return True
```

### 2. 性能测试
可以扩展测试脚本添加性能测试：

```python
def test_login_performance(self):
    """测试登录性能"""
    import time
    start_time = time.time()
    # 执行登录操作
    end_time = time.time()
    print(f"登录耗时: {end_time - start_time:.2f}秒")
```

### 3. 压力测试
可以添加并发测试：

```python
def test_concurrent_login(self):
    """测试并发登录"""
    import threading
    # 实现并发登录测试
    pass
```

## 总结

登录测试脚本提供了完整的登录功能验证，包括：

- ✅ **基础功能测试** - 注册、登录、错误处理
- ✅ **高级功能测试** - Token刷新、权限验证
- ✅ **错误场景测试** - 错误密码、不存在用户
- ✅ **安全测试** - Cookie验证、权限控制

通过这些测试，可以确保登录功能的稳定性和安全性。 