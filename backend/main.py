"""
主应用文件
整合所有路由和中间件，避免循环导入问题
"""
import os
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import traceback

# 导入路由
from api.routers import auth_router, agent_router, health_router
from models.models import Base

# 创建日志记录器
logger = logging.getLogger("diftagent")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# 配置
class Settings:
    pg_dsn: str = "postgresql+psycopg2://postgres:010921@127.0.0.1:5400/aiagent"
    jwt_secret: str = "aiagent-gateway-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60*24 # 1天  
    refresh_token_expire_days: int = 7

settings = Settings()

# 创建FastAPI应用
app = FastAPI(
    title="DiftAgent API",
    description="DiftAgent API for document management and authentication",
    version="1.0.0"
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 前端开发地址
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法，包括 OPTIONS
    allow_headers=["*"],  # 允许所有请求头
)

# 初始化数据库
engine = create_engine(settings.pg_dsn)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建表（实际部署中应使用迁移工具）
Base.metadata.create_all(bind=engine)

# 包含路由
app.include_router(auth_router)
app.include_router(agent_router)
app.include_router(health_router)

# 延迟导入文档路由以避免循环导入
def include_document_routes():
    try:
        from api.documents.doc_api import doc_router as document_router
        app.include_router(document_router)
        logger.info("Document routes included successfully")
    except ImportError as e:
        logger.warning(f"Could not import document routes: {e}")
    except Exception as e:
        logger.error(f"Error including document routes: {e}")

# 中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    try:
        response = await call_next(request)
        logger.info(f"Response status: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Request error: {traceback.format_exc()}")
        raise

# 启动事件
@app.on_event("startup")
async def startup_event():
    logger.info("Starting DiftAgent API server...")
    # 包含文档路由
    include_document_routes()
    logger.info("DiftAgent API server started successfully")

# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down DiftAgent API server...")

if __name__ == "__main__":
    import uvicorn
    
    # 启动配置 - 延长超时时间
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        timeout_keep_alive=180,  # 保持连接超时时间设为3分钟
        timeout_graceful_shutdown=30
    ) 