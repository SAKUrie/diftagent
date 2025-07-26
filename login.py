import os
import logging
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from sqlalchemy import create_engine, Column, String, Boolean, Integer, SmallInteger, DateTime, func
from sqlalchemy.orm import sessionmaker, Session,declarative_base
from sqlalchemy.dialects.postgresql import UUID, JSONB, CITEXT
import httpx
import uuid
import traceback
from typing import Dict, List, Optional

from fastapi import (
    FastAPI, 
    Depends, 
    HTTPException, 
    Header, 
    status, 
    Request,
    APIRouter,
    Cookie
)
from fastapi.responses import JSONResponse


# --------------------- 日志配置 ---------------------
logger = logging.getLogger("diftagent")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


# --------------------- 路由器定义 ---------------------
auth_router = APIRouter()
agent_router = APIRouter()

# --------------------- 配置管理 ---------------------
class Settings(BaseSettings):
    pg_dsn: str = "postgresql+psycopg2://postgres:010921@127.0.0.1:5400/aiagent"
    jwt_secret: str = "aiagent-gateway-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60*24 # 1天  
    refresh_token_expire_days: int = 7
    dify_agent_url: str = "-----------"
    api_keys: Dict[str, str] = {
        "9589ca16aa2844de6975809fbac3891ef2a105eadcde6f56e044c60b6b774ec4": "student"
    }
    
    class Config:
        env_file = ".env"

settings = Settings()

# --------------------- 数据库模型 ---------------------
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    username = Column(String, nullable=False, index=True)
    email = Column(CITEXT(), nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default="user")
    status = Column(SmallInteger, nullable=False, default=1)
    failed_login_attempts = Column(Integer, nullable=False, default=0)
    locked_until = Column(DateTime, nullable=True)
    last_login_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)
    user_metadata = Column(JSONB, nullable=False, default=dict)  # 修改这里
    refresh_token = Column(String, nullable=True)  # 刷新令牌
    is_active = Column(Boolean, nullable=False, default=True)  # 是否激活
    # 如需软删除过滤，可加 __mapper_args__ = {"eager_defaults": True}

# 初始化数据库
engine = create_engine(settings.pg_dsn)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 创建表（实际部署中应使用迁移工具）
Base.metadata.create_all(bind=engine)

# --------------------- 密码哈希 ---------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# --------------------- 认证模型 ---------------------
class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "free"

class UserInDB(BaseModel):
    id: str
    username: str
    email: str
    role: str
    is_active: bool

class InvokePayload(BaseModel):
    tool: str
    params: dict



# --------------------- JWT 管理 ---------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode, 
        settings.jwt_secret, 
        algorithm=settings.jwt_algorithm
    )

def create_tokens(user: User):
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    refresh_token_expires = timedelta(days=settings.refresh_token_expire_days)
    
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    
    refresh_token = create_access_token(
        data={"sub": user.username, "token_type": "refresh"},
        expires_delta=refresh_token_expires
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

# --------------------- 认证依赖 ---------------------
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, 
            settings.jwt_secret, 
            algorithms=[settings.jwt_algorithm]
        )
        username: str = payload.get("sub")
        if username is None:
            logger.warning("JWT payload missing 'sub'")
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Unexpected error in get_current_user: {traceback.format_exc()}")
        raise credentials_exception
    
    try:
        user = db.query(User).filter(User.username == token_data.username).first()
        if user is None or not user.is_active:
            logger.warning(f"User not found or inactive: {token_data.username}")
            raise credentials_exception
        return user
    except Exception as e:
        logger.error(f"DB error in get_current_user: {traceback.format_exc()}")
        raise credentials_exception

async def get_api_key(
    x_api_key: str = Header(None, alias="X-API-Key")
):
    if not x_api_key:
        logger.warning("API Key missing")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key missing"
        )
    role = settings.api_keys.get(x_api_key)
    if not role:
        logger.warning(f"Invalid API Key: {x_api_key}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    return {"api_key": x_api_key, "role": role}

from fastapi import Cookie

def get_token_from_cookie(access_token: str = Cookie(None)):
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return access_token

async def get_current_user_from_cookie(
    access_token: str = Depends(get_token_from_cookie),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials (cookie)",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            access_token, 
            settings.jwt_secret, 
            algorithms=[settings.jwt_algorithm]
        )
        username: str = payload.get("sub")
        if username is None:
            logger.warning("JWT payload missing 'sub'")
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Unexpected error in get_current_user_from_cookie: {traceback.format_exc()}")
        raise credentials_exception
    
    try:
        user = db.query(User).filter(User.username == token_data.username).first()
        if user is None or not user.is_active:
            logger.warning(f"User not found or inactive: {token_data.username}")
            raise credentials_exception
        return user
    except Exception as e:
        logger.error(f"DB error in get_current_user_from_cookie: {traceback.format_exc()}")
        raise credentials_exception

app = FastAPI()

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 前端开发地址
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法，包括 OPTIONS
    allow_headers=["*"],  # 允许所有请求头
)

# --------------------- 登录 ---------------------
@app.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    try:
        # 支持用户名或邮箱登录
        user = db.query(User).filter(
            (User.username == form_data.username) | (User.email == form_data.username)
        ).first()
        if not user:
            logger.warning(f"Login failed: user not found ({form_data.username})")
            raise HTTPException(status_code=401, detail="Incorrect username or password")
        if not verify_password(form_data.password, user.password_hash):
            logger.warning(f"Login failed: wrong password for {form_data.username}")
            raise HTTPException(status_code=401, detail="Incorrect username or password")
        if not user.is_active:
            logger.warning(f"Login failed: user inactive ({form_data.username})")
            raise HTTPException(status_code=403, detail="User is inactive")
        tokens = create_tokens(user)
        user.refresh_token = tokens["refresh_token"]
        db.commit()
        response = JSONResponse(content=tokens)
        # 写入 token 到 cookie
        response.set_cookie(
            key="access_token",
            value=tokens["access_token"],
            httponly=True,
            secure=True,
            samesite="Lax",
            max_age=60*60*24
        )
        # 可选：写入页面跳转信息
        response.set_cookie(
            key="last_page",
            value="/dashboard",
            httponly=False,
            secure=True,
            samesite="Lax"
        )
        return response
    except HTTPException:
        raise  # 让 FastAPI 正常返回 401/403
    except Exception as e:
        logger.error(f"Login error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")

# --------------------- 刷新令牌 ---------------------
@app.post("/refresh", response_model=Token)
async def refresh_access_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token"
    )
    try:
        payload = jwt.decode(
            refresh_token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )
        username: str = payload.get("sub")
        token_type: str = payload.get("token_type")
        if username is None or token_type != "refresh":
            logger.warning("Refresh token payload invalid")
            raise credentials_exception
    except JWTError as e:
        logger.error(f"JWT decode error in refresh: {e}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Unexpected error in refresh: {traceback.format_exc()}")
        raise credentials_exception
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user or user.refresh_token != refresh_token:
            logger.warning(f"Refresh token mismatch for user: {username}")
            raise credentials_exception
        tokens = create_tokens(user)
        user.refresh_token = tokens["refresh_token"]
        db.commit()
        logger.info(f"Refresh token success for user: {username}")
        return tokens
    except Exception as e:
        logger.error(f"DB error in refresh: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")

# --------------------- 注册 ---------------------
@app.post("/register", response_model=UserInDB)
async def register_user(
    user_create: UserCreate,
    db: Session = Depends(get_db)
):
    try:
        existing_user = db.query(User).filter(User.email == user_create.email, User.deleted_at == None).first()
        if existing_user:
            logger.warning(f"Register failed, email exists: {user_create.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        hashed_password = get_password_hash(user_create.password)
        db_user = User(
            username=user_create.username,
            email=user_create.email,
            password_hash=hashed_password,
            role=user_create.role,
            status=1,
            failed_login_attempts=0,
            user_metadata={}  # 注意这里字段名
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"User registered: {user_create.email}")
        return UserInDB(
            id=str(db_user.id),
            username=db_user.username,  # 你的表结构没有username字段，如有需要请补充
            email=db_user.email,
            role=db_user.role,
            is_active=(db_user.status == 1)
        )
    except Exception as e:
        logger.error(f"Register error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
# --------------------- 权限配置 ---------------------
# 注意：实际应用中应从数据库或配置中心加载
PERMISSIONS = {
    "guest": ["tool_basic", "tool_essay", "tool_polish", "tool_plan", "tool_material"],  # guest不能访问 tool_university
    "student": ["tool_basic", "tool_essay", "tool_polish", "tool_plan", "tool_material", "tool_university"],
    "teacher": ["all_tools"]
}

def authorize(role: str, tool: str):
    allowed = PERMISSIONS.get(role, [])
    if "all_tools" in allowed or tool in allowed:
        return True
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"Insufficient permissions for this tool {tool}"
    )



class ToolCheckRequest(BaseModel):
    tool: str

@app.post("/authz")
async def check_tool_permission(
    req: ToolCheckRequest,
    user: User = Depends(get_current_user_from_cookie)
):
    try:
        authorize(user.role, req.tool)
        return {"status": "ok"}
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"Authz error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")

# --------------------- 工具调用 ---------------------
@app.post("/invoke")
async def invoke_tool(
    payload: InvokePayload,
    request: Request,
    auth: dict = Depends(get_current_user_from_cookie) or Depends(get_api_key)
):
    try:
        role = auth.role if hasattr(auth, 'role') else auth['role']
        authorize(role, payload.tool)
        logger.info(f"Invoke tool: {payload.tool} by {role} user")
        result = await agent_client.invoke(payload.tool, payload.params)
        logger.info(f"Tool {payload.tool} invoked successfully")
        return {
            "status": "success",
            "tool": payload.tool,
            "result": result
        }
    except HTTPException as e:
        logger.warning(f"Tool invoke HTTP error: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Tool invoke error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")

# --------------------- 健康检查 ---------------------
@app.get("/health")
def health_check():
    try:
        logger.info("Health check requested")
        return {"status": "ok", "timestamp": datetime.utcnow()}
    except Exception as e:
        logger.error(f"Health check error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")

# --------------------- 中间件 ---------------------
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