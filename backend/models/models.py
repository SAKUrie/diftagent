from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum, Text, func, CheckConstraint, Index, SmallInteger, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB, CITEXT
from sqlalchemy.orm import relationship
import enum
import uuid
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# User模型
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    username = Column(String, nullable=True, index=True)
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
    user_metadata = Column(JSONB, nullable=False, default=dict)
    refresh_token = Column(String, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # 反向关系
    resume_documents = relationship("ResumeDocument", back_populates="user")
    letter_documents = relationship("LetterDocument", back_populates="user")
    sop_documents = relationship("SopDocument", back_populates="user")

class DocType(enum.Enum):
    resume = "resume"
    letter = "letter"
    sop = "sop"

# 基础文档表
class ResumeDocument(Base):
    __tablename__ = "resume_documents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False, default="")
    current_version_id = Column(UUID(as_uuid=True), ForeignKey("resume_document_versions.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    versions = relationship("ResumeDocumentVersion", back_populates="document", foreign_keys="ResumeDocumentVersion.document_id", order_by="ResumeDocumentVersion.version_number")
    user = relationship("User", back_populates="resume_documents")

class ResumeDocumentVersion(Base):
    __tablename__ = "resume_document_versions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("resume_documents.id", deferrable=True, initially="DEFERRED"), nullable=False)
    version_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    content_format = Column(String, nullable=False, default="markdown")
    checksum_sha256 = Column(String, nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    document = relationship("ResumeDocument", back_populates="versions", foreign_keys=[document_id])
    user = relationship("User", foreign_keys=[created_by])

    # 添加内容大小约束 (5k字符)
    __table_args__ = (
        CheckConstraint("char_length(content) <= 5000", name="content_size_limit"),
    )

# Letter文档表
class LetterDocument(Base):
    __tablename__ = "letter_documents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False, default="")
    current_version_id = Column(UUID(as_uuid=True), ForeignKey("letter_document_versions.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    versions = relationship("LetterDocumentVersion", back_populates="document", foreign_keys="LetterDocumentVersion.document_id", order_by="LetterDocumentVersion.version_number")
    user = relationship("User", back_populates="letter_documents")

class LetterDocumentVersion(Base):
    __tablename__ = "letter_document_versions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("letter_documents.id", deferrable=True, initially="DEFERRED"), nullable=False)
    version_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    content_format = Column(String, nullable=False, default="markdown")
    checksum_sha256 = Column(String, nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    document = relationship("LetterDocument", back_populates="versions", foreign_keys=[document_id])
    user = relationship("User", foreign_keys=[created_by])

    __table_args__ = (
        CheckConstraint("char_length(content) <= 5000", name="content_size_limit"),
    )

# SOP文档表
class SopDocument(Base):
    __tablename__ = "sop_documents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False, default="")
    current_version_id = Column(UUID(as_uuid=True), ForeignKey("sop_document_versions.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    versions = relationship("SopDocumentVersion", back_populates="document", foreign_keys="SopDocumentVersion.document_id", order_by="SopDocumentVersion.version_number")
    user = relationship("User", back_populates="sop_documents")

class SopDocumentVersion(Base):
    __tablename__ = "sop_document_versions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("sop_documents.id", deferrable=True, initially="DEFERRED"), nullable=False)
    version_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    content_format = Column(String, nullable=False, default="markdown")
    checksum_sha256 = Column(String, nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    document = relationship("SopDocument", back_populates="versions", foreign_keys=[document_id])
    user = relationship("User", foreign_keys=[created_by])

    __table_args__ = (
        CheckConstraint("char_length(content) <= 5000", name="content_size_limit"),
    )

# 添加关系到User模型
User.resume_documents = relationship("ResumeDocument", back_populates="user")
User.letter_documents = relationship("LetterDocument", back_populates="user")
User.sop_documents = relationship("SopDocument", back_populates="user")
User.conversation_sessions = relationship("ConversationSession", back_populates="user")

# 创建索引
Index('idx_resume_versions_history', ResumeDocumentVersion.document_id, ResumeDocumentVersion.created_at.desc(), 
      ResumeDocumentVersion.deleted_at, postgresql_include=[ResumeDocumentVersion.version_number, ResumeDocumentVersion.content_format])
Index('idx_letter_versions_history', LetterDocumentVersion.document_id, LetterDocumentVersion.created_at.desc(), 
      LetterDocumentVersion.deleted_at, postgresql_include=[LetterDocumentVersion.version_number, LetterDocumentVersion.content_format])
Index('idx_sop_versions_history', SopDocumentVersion.document_id, SopDocumentVersion.created_at.desc(), 
      SopDocumentVersion.deleted_at, postgresql_include=[SopDocumentVersion.version_number, SopDocumentVersion.content_format])

# 导入对话日志模型
from .conversation import ConversationSession, ConversationMessage 