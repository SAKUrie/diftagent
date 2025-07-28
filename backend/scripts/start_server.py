#!/usr/bin/env python3
"""
启动文档管理服务器
"""
import uvicorn
import os
import sys

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

if __name__ == "__main__":
    print("启动文档管理服务器...")
    print("服务器地址: http://localhost:8000")
    print("API文档: http://localhost:8000/docs")
    print("按 Ctrl+C 停止服务器")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        timeout_keep_alive=180,
        timeout_graceful_shutdown=30
    ) 