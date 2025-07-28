"""
对话日志数据模型
"""
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, JSON, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.models import Base
import uuid

class ConversationSession(Base):
    """对话会话表"""
    __tablename__ = "conversation_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_name = Column(String(255), nullable=False)
    session_type = Column(String(50), default="general")  # general, document_edit, tool_usage 等
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    session_metadata = Column(JSONB, default={})
    
    # 关系
    user = relationship("User", back_populates="conversation_sessions")
    messages = relationship("ConversationMessage", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ConversationSession(id={self.id}, name='{self.session_name}', type='{self.session_type}')>"

class ConversationMessage(Base):
    """对话消息表"""
    __tablename__ = "conversation_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("conversation_sessions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    message_type = Column(String(20), nullable=False)  # user, assistant, system, tool
    content = Column(Text, nullable=False)
    role = Column(String(50), default="user")  # user, assistant, system, tool
    tool_name = Column(String(100), nullable=True)  # 如果是工具消息，记录工具名称
    tool_params = Column(JSONB, nullable=True)  # 工具参数
    tool_result = Column(JSONB, nullable=True)  # 工具执行结果
    tokens_used = Column(Integer, default=0)  # 使用的token数量
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # 关系
    session = relationship("ConversationSession", back_populates="messages")
    user = relationship("User", foreign_keys=[user_id])
    
    # 约束
    __table_args__ = (
        CheckConstraint(
            "message_type IN ('user', 'assistant', 'system', 'tool')",
            name="check_message_type"
        ),
    )
    
    def __repr__(self):
        return f"<ConversationMessage(id={self.id}, type='{self.message_type}', role='{self.role}')>" 