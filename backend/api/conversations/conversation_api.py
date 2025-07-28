"""
对话日志API接口
提供对话会话和消息的CRUD操作
"""
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field, validator
from models.models import User
from models.conversation import ConversationSession, ConversationMessage
from api.routers import get_db, get_current_user_from_cookie
import uuid

# Pydantic模型
class ConversationSessionCreate(BaseModel):
    session_name: str = Field(..., min_length=1, max_length=255)
    session_type: str = Field(default="general", max_length=50)
    session_metadata: Dict[str, Any] = Field(default_factory=dict)

class ConversationSessionUpdate(BaseModel):
    session_name: Optional[str] = Field(None, min_length=1, max_length=255)
    session_type: Optional[str] = Field(None, max_length=50)
    session_metadata: Optional[Dict[str, Any]] = None

class ConversationSessionOut(BaseModel):
    id: str
    session_name: str
    session_type: str
    created_at: datetime
    updated_at: datetime
    session_metadata: Dict[str, Any]
    message_count: int = 0
    last_message_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ConversationMessageCreate(BaseModel):
    message_type: str = Field(..., pattern="^(user|assistant|system|tool)$")
    content: str = Field(..., min_length=1)
    role: str = Field(default="user", max_length=50)
    tool_name: Optional[str] = Field(None, max_length=100)
    tool_params: Optional[Dict[str, Any]] = None
    tool_result: Optional[Dict[str, Any]] = None
    tokens_used: int = Field(default=0, ge=0)

    @validator('message_type')
    def validate_message_type(cls, v):
        if v not in ['user', 'assistant', 'system', 'tool']:
            raise ValueError('message_type must be one of: user, assistant, system, tool')
        return v

class ConversationMessageOut(BaseModel):
    id: str
    message_type: str
    content: str
    role: str
    tool_name: Optional[str]
    tool_params: Optional[Dict[str, Any]]
    tool_result: Optional[Dict[str, Any]]
    tokens_used: int
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationSessionWithMessages(BaseModel):
    session: ConversationSessionOut
    messages: List[ConversationMessageOut] = []

    class Config:
        from_attributes = True

# 创建路由器
conversation_router = APIRouter(prefix="/conversations", tags=["Conversations"])

# 会话管理API
@conversation_router.post("/sessions", response_model=ConversationSessionOut)
async def create_conversation_session(
    session_data: ConversationSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)
):
    """创建新的对话会话"""
    try:
        # 检查会话名称是否已存在
        existing_session = db.query(ConversationSession).filter(
            ConversationSession.user_id == current_user.id,
            ConversationSession.session_name == session_data.session_name,
            ConversationSession.deleted_at == None
        ).first()
        
        if existing_session:
            raise HTTPException(
                status_code=400, 
                detail=f"Session name '{session_data.session_name}' already exists"
            )
        
        # 创建新会话
        session = ConversationSession(
            user_id=current_user.id,
            session_name=session_data.session_name,
            session_type=session_data.session_type,
            session_metadata=session_data.session_metadata
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        return ConversationSessionOut(
            id=str(session.id),
            session_name=session.session_name,
            session_type=session.session_type,
            created_at=session.created_at,
            updated_at=session.updated_at,
            session_metadata=session.session_metadata,
            message_count=0,
            last_message_at=None
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Create session failed: {str(e)}")

@conversation_router.get("/sessions", response_model=List[ConversationSessionOut])
async def list_conversation_sessions(
    session_type: Optional[str] = Query(None, description="Filter by session type"),
    limit: int = Query(50, ge=1, le=100, description="Number of sessions to return"),
    offset: int = Query(0, ge=0, description="Number of sessions to skip"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)
):
    """获取用户的对话会话列表"""
    try:
        query = db.query(ConversationSession).filter(
            ConversationSession.user_id == current_user.id,
            ConversationSession.deleted_at == None
        )
        
        if session_type:
            query = query.filter(ConversationSession.session_type == session_type)
        
        sessions = query.order_by(ConversationSession.updated_at.desc()).offset(offset).limit(limit).all()
        
        result = []
        for session in sessions:
            # 获取消息数量
            message_count = db.query(ConversationMessage).filter(
                ConversationMessage.session_id == session.id,
                ConversationMessage.deleted_at == None
            ).count()
            
            # 获取最后消息时间
            last_message = db.query(ConversationMessage).filter(
                ConversationMessage.session_id == session.id,
                ConversationMessage.deleted_at == None
            ).order_by(ConversationMessage.created_at.desc()).first()
            
            result.append(ConversationSessionOut(
                id=str(session.id),
                session_name=session.session_name,
                session_type=session.session_type,
                created_at=session.created_at,
                updated_at=session.updated_at,
                session_metadata=session.session_metadata,
                message_count=message_count,
                last_message_at=last_message.created_at if last_message else None
            ))
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"List sessions failed: {str(e)}")

@conversation_router.get("/sessions/{session_id}", response_model=ConversationSessionWithMessages)
async def get_conversation_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)
):
    """获取对话会话详情和消息"""
    try:
        # 验证UUID格式
        try:
            session_uuid = uuid.UUID(session_id)
        except ValueError:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = db.query(ConversationSession).filter(
            ConversationSession.id == session_uuid,
            ConversationSession.user_id == current_user.id,
            ConversationSession.deleted_at == None
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # 获取消息
        messages = db.query(ConversationMessage).filter(
            ConversationMessage.session_id == session.id,
            ConversationMessage.deleted_at == None
        ).order_by(ConversationMessage.created_at.asc()).all()
        
        # 构建响应
        session_out = ConversationSessionOut(
            id=str(session.id),
            session_name=session.session_name,
            session_type=session.session_type,
            created_at=session.created_at,
            updated_at=session.updated_at,
            session_metadata=session.session_metadata,
            message_count=len(messages),
            last_message_at=messages[-1].created_at if messages else None
        )
        
        messages_out = [
            ConversationMessageOut(
                id=str(msg.id),
                message_type=msg.message_type,
                content=msg.content,
                role=msg.role,
                tool_name=msg.tool_name,
                tool_params=msg.tool_params,
                tool_result=msg.tool_result,
                tokens_used=msg.tokens_used,
                created_at=msg.created_at
            ) for msg in messages
        ]
        
        return ConversationSessionWithMessages(
            session=session_out,
            messages=messages_out
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Get session failed: {str(e)}")

@conversation_router.put("/sessions/{session_id}", response_model=ConversationSessionOut)
async def update_conversation_session(
    session_id: str,
    session_data: ConversationSessionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)
):
    """更新对话会话"""
    try:
        # 验证UUID格式
        try:
            session_uuid = uuid.UUID(session_id)
        except ValueError:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = db.query(ConversationSession).filter(
            ConversationSession.id == session_uuid,
            ConversationSession.user_id == current_user.id,
            ConversationSession.deleted_at == None
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # 更新字段
        if session_data.session_name is not None:
            # 检查新名称是否与其他会话冲突
            existing_session = db.query(ConversationSession).filter(
                ConversationSession.user_id == current_user.id,
                ConversationSession.session_name == session_data.session_name,
                ConversationSession.id != session_uuid,
                ConversationSession.deleted_at == None
            ).first()
            
            if existing_session:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Session name '{session_data.session_name}' already exists"
                )
            session.session_name = session_data.session_name
        
        if session_data.session_type is not None:
            session.session_type = session_data.session_type
        
        if session_data.session_metadata is not None:
            session.session_metadata = session_data.session_metadata
        
        db.commit()
        db.refresh(session)
        
        return ConversationSessionOut(
            id=str(session.id),
            session_name=session.session_name,
            session_type=session.session_type,
            created_at=session.created_at,
            updated_at=session.updated_at,
            session_metadata=session.session_metadata,
            message_count=0,
            last_message_at=None
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Update session failed: {str(e)}")

@conversation_router.delete("/sessions/{session_id}")
async def delete_conversation_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)
):
    """删除对话会话（软删除）"""
    try:
        # 验证UUID格式
        try:
            session_uuid = uuid.UUID(session_id)
        except ValueError:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = db.query(ConversationSession).filter(
            ConversationSession.id == session_uuid,
            ConversationSession.user_id == current_user.id,
            ConversationSession.deleted_at == None
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # 软删除会话和所有消息
        session.deleted_at = datetime.utcnow()
        
        # 删除相关消息
        messages = db.query(ConversationMessage).filter(
            ConversationMessage.session_id == session.id,
            ConversationMessage.deleted_at == None
        ).all()
        
        for message in messages:
            message.deleted_at = datetime.utcnow()
        
        db.commit()
        
        return {"message": "Session deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Delete session failed: {str(e)}")

# 消息管理API
@conversation_router.post("/sessions/{session_id}/messages", response_model=ConversationMessageOut)
async def add_conversation_message(
    session_id: str,
    message_data: ConversationMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)
):
    """添加对话消息"""
    try:
        # 验证UUID格式
        try:
            session_uuid = uuid.UUID(session_id)
        except ValueError:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = db.query(ConversationSession).filter(
            ConversationSession.id == session_uuid,
            ConversationSession.user_id == current_user.id,
            ConversationSession.deleted_at == None
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # 创建消息
        message = ConversationMessage(
            session_id=session.id,
            user_id=current_user.id,
            message_type=message_data.message_type,
            content=message_data.content,
            role=message_data.role,
            tool_name=message_data.tool_name,
            tool_params=message_data.tool_params,
            tool_result=message_data.tool_result,
            tokens_used=message_data.tokens_used
        )
        
        db.add(message)
        db.commit()
        db.refresh(message)
        
        return ConversationMessageOut(
            id=str(message.id),
            message_type=message.message_type,
            content=message.content,
            role=message.role,
            tool_name=message.tool_name,
            tool_params=message.tool_params,
            tool_result=message.tool_result,
            tokens_used=message.tokens_used,
            created_at=message.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Add message failed: {str(e)}")

@conversation_router.get("/sessions/{session_id}/messages", response_model=List[ConversationMessageOut])
async def list_conversation_messages(
    session_id: str,
    limit: int = Query(100, ge=1, le=500, description="Number of messages to return"),
    offset: int = Query(0, ge=0, description="Number of messages to skip"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)
):
    """获取对话消息列表"""
    try:
        # 验证UUID格式
        try:
            session_uuid = uuid.UUID(session_id)
        except ValueError:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # 验证会话存在且属于当前用户
        session = db.query(ConversationSession).filter(
            ConversationSession.id == session_uuid,
            ConversationSession.user_id == current_user.id,
            ConversationSession.deleted_at == None
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # 获取消息
        messages = db.query(ConversationMessage).filter(
            ConversationMessage.session_id == session.id,
            ConversationMessage.deleted_at == None
        ).order_by(ConversationMessage.created_at.asc()).offset(offset).limit(limit).all()
        
        return [
            ConversationMessageOut(
                id=str(msg.id),
                message_type=msg.message_type,
                content=msg.content,
                role=msg.role,
                tool_name=msg.tool_name,
                tool_params=msg.tool_params,
                tool_result=msg.tool_result,
                tokens_used=msg.tokens_used,
                created_at=msg.created_at
            ) for msg in messages
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"List messages failed: {str(e)}")

@conversation_router.delete("/messages/{message_id}")
async def delete_conversation_message(
    message_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)
):
    """删除对话消息（软删除）"""
    try:
        # 验证UUID格式
        try:
            message_uuid = uuid.UUID(message_id)
        except ValueError:
            raise HTTPException(status_code=404, detail="Message not found")
        
        message = db.query(ConversationMessage).filter(
            ConversationMessage.id == message_uuid,
            ConversationMessage.user_id == current_user.id,
            ConversationMessage.deleted_at == None
        ).first()
        
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        # 软删除消息
        message.deleted_at = datetime.utcnow()
        db.commit()
        
        return {"message": "Message deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Delete message failed: {str(e)}") 