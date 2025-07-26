from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum, Text, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum
import uuid
from datetime import datetime
from login import Base, get_db, User,get_db, get_current_user_from_cookie
from pydantic import BaseModel, Field
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

class DocType(enum.Enum):
    resume = "resume"
    letter = "letter"
    sop = "sop"

class Document(Base):
    __tablename__ = "documents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    type = Column(Enum(DocType), nullable=False)
    title = Column(String, nullable=False, default="")
    current_version_id = Column(UUID(as_uuid=True), ForeignKey("document_versions.id"), nullable=True)
    # metadata = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    versions = relationship("DocumentVersion", back_populates="document", order_by="DocumentVersion.version_number")

class DocumentVersion(Base):
    __tablename__ = "document_versions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    content_format = Column(String, nullable=False, default="markdown")
    diff_from = Column(UUID(as_uuid=True), ForeignKey("document_versions.id"), nullable=True)
    checksum_sha256 = Column(String, nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    # metadata = Column(JSONB, nullable=False, default=dict)

    document = relationship("Document", back_populates="versions")

class DocumentVersionOut(BaseModel):
    id: str
    version_number: int
    content: str
    content_format: str
    created_at: datetime

    class Config:
        orm_mode = True

class DocumentOut(BaseModel):
    id: str
    user_id: str
    type: str
    title: str
    current_version_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    versions: List[DocumentVersionOut] = []

    class Config:
        orm_mode = True

class DocumentCreate(BaseModel):
    type: str
    title: str
    content: str
    content_format: str = "markdown"
    metadata: dict = Field(default_factory=dict)

doc_router = APIRouter(prefix="/documents", tags=["Documents"])

@doc_router.post("/", response_model=DocumentOut)
def create_document(
    doc: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)  # 修改此处
):
    try:
        document = Document(
            user_id=current_user.id,
            type=doc.type,
            title=doc.title,
            metadata=doc.metadata
        )
        db.add(document)
        db.flush()
        version = DocumentVersion(
            document_id=document.id,
            version_number=1,
            content=doc.content,
            content_format=doc.content_format,
            created_by=current_user.id
        )
        db.add(version)
        db.flush()
        document.current_version_id = version.id
        db.commit()
        db.refresh(document)
        return document
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Create document failed")

@doc_router.post("/{doc_id}/new_version", response_model=DocumentOut)
def add_version(
    doc_id: str,
    content: str,
    content_format: str = "markdown",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)  # 修改此处
):
    try:
        document = db.query(Document).filter(Document.id == doc_id, Document.user_id == current_user.id, Document.deleted_at == None).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        last_version = db.query(DocumentVersion).filter(DocumentVersion.document_id == doc_id).order_by(DocumentVersion.version_number.desc()).first()
        new_version_number = (last_version.version_number if last_version else 0) + 1
        version = DocumentVersion(
            document_id=doc_id,
            version_number=new_version_number,
            content=content,
            content_format=content_format,
            created_by=current_user.id
        )
        db.add(version)
        db.flush()
        document.current_version_id = version.id
        db.commit()
        db.refresh(document)
        return document
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Add version failed")

@doc_router.get("/{doc_id}", response_model=DocumentOut)
def get_document(
    doc_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)  # 修改此处
):
    try:
        document = db.query(Document).filter(Document.id == doc_id, Document.user_id == current_user.id, Document.deleted_at == None).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return document
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Get document failed")

@doc_router.post("/{doc_id}/revert/{version_number}", response_model=DocumentOut)
def revert_document(
    doc_id: str,
    version_number: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)  # 修改此处
):
    try:
        document = db.query(Document).filter(Document.id == doc_id, Document.user_id == current_user.id, Document.deleted_at == None).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        version = db.query(DocumentVersion).filter(DocumentVersion.document_id == doc_id, DocumentVersion.version_number == version_number).first()
        if not version:
            raise HTTPException(status_code=404, detail="Version not found")
        document.current_version_id = version.id
        db.commit()
        db.refresh(document)
        return document
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Revert document failed")

@doc_router.get("/{doc_id}/versions", response_model=List[DocumentVersionOut])
def list_versions(
    doc_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)  # 修改此处
):
    try:
        document = db.query(Document).filter(
            Document.id == doc_id,
            Document.user_id == current_user.id,
            Document.deleted_at == None
        ).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        versions = db.query(DocumentVersion).filter(
            DocumentVersion.document_id == doc_id,
            DocumentVersion.deleted_at == None
        ).order_by(DocumentVersion.updated_at.desc()).all()
        return versions
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="List versions failed")

@doc_router.get("/{doc_id}/version/{version_number}", response_model=DocumentVersionOut)
def get_version(
    doc_id: str,
    version_number: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)  # 修改此处
):
    try:
        document = db.query(Document).filter(
            Document.id == doc_id,
            Document.user_id == current_user.id,
            Document.deleted_at == None
        ).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        version = db.query(DocumentVersion).filter(
            DocumentVersion.document_id == doc_id,
            DocumentVersion.version_number == version_number,
            DocumentVersion.deleted_at == None
        ).first()
        if not version:
            raise HTTPException(status_code=404, detail="Version not found")
        return version
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Get version failed")

@doc_router.get("/", response_model=List[DocumentOut])
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)  # 修改此处
):
    try:
        docs = db.query(Document).filter(
            Document.user_id == current_user.id,
            Document.deleted_at == None
        ).order_by(Document.updated_at.desc()).all()
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail="List documents failed")