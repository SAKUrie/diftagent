"""
路由管理模块
集中管理所有API路由，避免循环导入问题
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Cookie, Header
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
import traceback
import logging

from models import User
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import traceback
import logging

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

# 密码哈希
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

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
        "token_type": "bearer",
        "refresh_token": refresh_token
    }

# 数据库依赖
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

engine = create_engine(settings.pg_dsn)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 认证依赖
from fastapi import Depends, HTTPException, status, Cookie
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_token_from_cookie(access_token: str = Cookie(None)):
    return access_token

async def get_current_user_from_cookie(
    access_token: str = Depends(get_token_from_cookie),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials"
    )
    try:
        if not access_token:
            raise credentials_exception
        payload = jwt.decode(
            access_token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    except Exception as e:
        logger.error(f"JWT decode error: {e}")
        raise credentials_exception
    try:
        user = db.query(User).filter(User.username == username).first()
        if user is None or not user.is_active:
            logger.warning(f"User not found or inactive: {username}")
            raise credentials_exception
        return user
    except Exception as e:
        logger.error(f"DB error in get_current_user_from_cookie: {traceback.format_exc()}")
        raise credentials_exception

async def get_api_key(
    x_api_key: str = Header(None, alias="X-API-Key")
):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    # TODO: 实现API key验证逻辑
    return {"role": "student"}

# 创建路由器
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])
agent_router = APIRouter(prefix="/agent", tags=["Agent"])
health_router = APIRouter(tags=["Health"])

# --------------------- 认证路由 ---------------------

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "guest"

class UserInDB(BaseModel):
    id: str
    username: str
    email: str
    role: str
    is_active: bool

@auth_router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """用户登录"""
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
        raise
    except Exception as e:
        logger.error(f"Login error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")

@auth_router.post("/refresh", response_model=Token)
async def refresh_access_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """刷新访问令牌"""
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
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"DB error in refresh: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")

@auth_router.post("/register", response_model=UserInDB)
async def register_user(
    user_create: UserCreate,
    db: Session = Depends(get_db)
):
    """用户注册"""
    try:
        # 检查邮箱是否已存在
        existing_user = db.query(User).filter(User.email == user_create.email, User.deleted_at == None).first()
        if existing_user:
            logger.warning(f"Register failed, email exists: {user_create.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # 检查用户名是否已存在
        existing_username = db.query(User).filter(User.username == user_create.username, User.deleted_at == None).first()
        if existing_username:
            logger.warning(f"Register failed, username exists: {user_create.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # 验证角色是否有效
        valid_roles = ['guest', 'vvip', 'consultant', 'etc..']
        if user_create.role not in valid_roles:
            logger.warning(f"Register failed, invalid role: {user_create.role}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
            )
        
        # 验证密码长度
        if len(user_create.password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters long"
            )
        
        hashed_password = get_password_hash(user_create.password)
        db_user = User(
            username=user_create.username,
            email=user_create.email,
            password_hash=hashed_password,
            role=user_create.role,
            status=1,
            failed_login_attempts=0,
            user_metadata={}
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"User registered: {user_create.email}")
        return UserInDB(
            id=str(db_user.id),
            username=db_user.username,
            email=db_user.email,
            role=db_user.role,
            is_active=(db_user.status == 1)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Register error: {traceback.format_exc()}")
        # 检查是否是数据库约束错误
        error_str = str(e).lower()
        if "unique" in error_str or "duplicate" in error_str:
            if "email" in error_str:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            elif "username" in error_str:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Duplicate entry"
                )
        elif "check" in error_str and "role" in error_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role"
            )
        elif "check" in error_str and "password" in error_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password does not meet requirements"
            )
        else:
            raise HTTPException(status_code=500, detail="Internal server error")

# --------------------- 健康检查路由 ---------------------

@health_router.get("/health")
def health_check():
    """健康检查"""
    try:
        logger.info("Health check requested")
        return {"status": "ok", "timestamp": datetime.utcnow()}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Health check error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")

# --------------------- 权限检查路由 ---------------------

# 权限配置
PERMISSIONS = {
    "guest": ["tool_basic", "tool_essay", "tool_polish", "tool_plan", "tool_material"],
    "student": ["tool_basic", "tool_essay", "tool_polish", "tool_plan", "tool_material", "tool_university"],
    "teacher": ["all_tools"]
}

def authorize(role: str, tool: str):
    """检查用户权限"""
    allowed = PERMISSIONS.get(role, [])
    if "all_tools" in allowed or tool in allowed:
        return True
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"Insufficient permissions for this tool {tool}"
    )

class ToolCheckRequest(BaseModel):
    tool: str

@agent_router.post("/authz")
async def check_tool_permission(
    req: ToolCheckRequest,
    user: User = Depends(get_current_user_from_cookie)
):
    """检查工具权限"""
    try:
        authorize(user.role, req.tool)
        return {"status": "ok"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authz error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")

# --------------------- 工具调用路由 ---------------------

class InvokePayload(BaseModel):
    tool: str
    params: dict

@agent_router.post("/invoke")
async def invoke_tool(
    payload: InvokePayload,
    request: Request,
    auth: dict = Depends(get_current_user_from_cookie) or Depends(get_api_key)
):
    """调用工具"""
    try:
        role = auth.role if hasattr(auth, 'role') else auth['role']
        authorize(role, payload.tool)
        logger.info(f"Invoke tool: {payload.tool} by {role} user")
        # TODO: 实现实际的工具调用逻辑
        result = {"message": f"Tool {payload.tool} invoked successfully"}
        logger.info(f"Tool {payload.tool} invoked successfully")
        return {
            "status": "success",
            "tool": payload.tool,
            "result": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Tool invoke error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error") 