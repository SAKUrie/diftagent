from sqlalchemy.orm import Session
from datetime import datetime
from models.models import (
    Base, User, DocType,
    ResumeDocument, ResumeDocumentVersion,
    LetterDocument, LetterDocumentVersion,
    SopDocument, SopDocumentVersion
)
from api.routers import get_db, get_current_user_from_cookie
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import hashlib



# Pydantic模型
class DocumentVersionOut(BaseModel):
    id: str
    version_number: int
    content: str
    content_format: str
    created_at: datetime
    checksum_sha256: Optional[str]

    class Config:
        from_attributes = True

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
        from_attributes = True

class DocumentCreate(BaseModel):
    type: str
    title: str
    content: str
    content_format: str = "markdown"

    @validator('type')
    def validate_type(cls, v):
        if v not in ['resume', 'letter', 'sop']:
            raise ValueError('type must be resume, letter, or sop')
        return v

class DocumentUpdate(BaseModel):
    content: str
    content_format: str = "markdown"

class VersionRevertRequest(BaseModel):
    version_number: int

# 工具函数
def get_document_model(doc_type: str):
    """根据文档类型返回对应的模型类"""
    models = {
        'resume': (ResumeDocument, ResumeDocumentVersion),
        'letter': (LetterDocument, LetterDocumentVersion),
        'sop': (SopDocument, SopDocumentVersion)
    }
    return models.get(doc_type)

def calculate_checksum(content: str) -> str:
    """计算内容的SHA256校验和"""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

# 异步队列接口（预留）
class AsyncQueueService:
    """异步队列服务接口（预留实现）"""
    
    @staticmethod
    async def enqueue_version_creation(doc_type: str, doc_id: str, content: str, user_id: str):
        """将版本创建任务加入队列"""
        # TODO: 实现异步队列
        pass
    
    @staticmethod
    async def process_version_creation(doc_type: str, doc_id: str, content: str, user_id: str):
        """处理版本创建任务"""
        # TODO: 实现异步处理
        pass

doc_router = APIRouter(prefix="/documents", tags=["Documents"])

@doc_router.post("/upload", response_model=DocumentOut)
async def upload_document(
    doc_type: str = Form(...),
    title: str = Form(...),
    content: str = Form(...),
    content_format: str = Form("markdown"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)
):
    """上传新文档"""
    try:
        models = get_document_model(doc_type)
        if not models:
            raise HTTPException(status_code=400, detail=f"Invalid document type: {doc_type}. Must be one of: resume, letter, sop")
        doc_model, version_model = models
        
        # 创建文档
        document = doc_model(
            user_id=current_user.id,
            title=title
        )
        db.add(document)
        db.flush()
        
        # 创建第一个版本
        checksum = calculate_checksum(content)
        version = version_model(
            document_id=document.id,
            version_number=1,
            content=content,
            content_format=content_format,
            created_by=current_user.id,
            checksum_sha256=checksum
        )
        db.add(version)
        db.flush()
        
        # 设置当前版本
        document.current_version_id = version.id
        db.commit()
        db.refresh(document)
        
        return DocumentOut(
            id=str(document.id),
            user_id=str(document.user_id),
            type=doc_type,
            title=document.title,
            current_version_id=str(document.current_version_id),
            created_at=document.created_at,
            updated_at=document.updated_at,
            versions=[DocumentVersionOut(
                id=str(version.id),
                version_number=version.version_number,
                content=version.content,
                content_format=version.content_format,
                created_at=version.created_at,
                checksum_sha256=version.checksum_sha256
            )]
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        # 检查是否是UUID格式错误
        if "invalid input syntax for type uuid" in str(e).lower():
            raise HTTPException(status_code=404, detail="Document not found")
        else:
            raise HTTPException(status_code=500, detail="Internal server error")

@doc_router.post("/{doc_type}/{doc_id}/versions", response_model=DocumentOut)
async def add_version(
    doc_type: str,
    doc_id: str,
    content: str = Form(...),
    content_format: str = Form("markdown"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)
):
    """添加新版本"""
    try:
        doc_model, version_model = get_document_model(doc_type)
        if not doc_model:
            raise HTTPException(status_code=400, detail="Invalid document type")
        
        # 查找文档
        document = db.query(doc_model).filter(
            doc_model.id == doc_id,
            doc_model.user_id == current_user.id,
            doc_model.deleted_at == None
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # 获取最新版本号
        last_version = db.query(version_model).filter(
            version_model.document_id == doc_id,
            version_model.deleted_at == None
        ).order_by(version_model.version_number.desc()).first()
        
        new_version_number = (last_version.version_number if last_version else 0) + 1
        
        # 创建新版本
        checksum = calculate_checksum(content)
        version = version_model(
            document_id=doc_id,
            version_number=new_version_number,
            content=content,
            content_format=content_format,
            created_by=current_user.id,
            checksum_sha256=checksum
        )
        db.add(version)
        db.flush()
        
        # 更新当前版本
        document.current_version_id = version.id
        db.commit()
        db.refresh(document)
        
        return DocumentOut(
            id=str(document.id),
            user_id=str(document.user_id),
            type=doc_type,
            title=document.title,
            current_version_id=str(document.current_version_id),
            created_at=document.created_at,
            updated_at=document.updated_at,
            versions=[]
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Add version failed: {str(e)}")

@doc_router.get("/{doc_type}/{doc_id}", response_model=DocumentOut)
async def get_document(
    doc_type: str,
    doc_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)
):
    """获取文档详情"""
    try:
        doc_model, version_model = get_document_model(doc_type)
        if not doc_model:
            raise HTTPException(status_code=400, detail="Invalid document type")
        
        document = db.query(doc_model).filter(
            doc_model.id == doc_id,
            doc_model.user_id == current_user.id,
            doc_model.deleted_at == None
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # 获取所有版本
        versions = db.query(version_model).filter(
            version_model.document_id == doc_id,
            version_model.deleted_at == None
        ).order_by(version_model.created_at.desc()).all()
        
        return DocumentOut(
            id=str(document.id),
            user_id=str(document.user_id),
            type=doc_type,
            title=document.title,
            current_version_id=str(document.current_version_id) if document.current_version_id else None,
            created_at=document.created_at,
            updated_at=document.updated_at,
            versions=[DocumentVersionOut(
                id=str(v.id),
                version_number=v.version_number,
                content=v.content,
                content_format=v.content_format,
                created_at=v.created_at,
                checksum_sha256=v.checksum_sha256
            ) for v in versions]
        )
    except HTTPException:
        raise
    except Exception as e:
        # 检查是否是UUID格式错误
        if "invalid input syntax for type uuid" in str(e).lower():
            raise HTTPException(status_code=404, detail="Document not found")
        else:
            raise HTTPException(status_code=500, detail="Internal server error")

@doc_router.post("/{doc_type}/{doc_id}/revert", response_model=DocumentOut)
async def revert_document(
    doc_type: str,
    doc_id: str,
    revert_request: VersionRevertRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)
):
    """回退到指定版本"""
    try:
        doc_model, version_model = get_document_model(doc_type)
        if not doc_model:
            raise HTTPException(status_code=400, detail="Invalid document type")
        
        # 查找文档
        document = db.query(doc_model).filter(
            doc_model.id == doc_id,
            doc_model.user_id == current_user.id,
            doc_model.deleted_at == None
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # 查找指定版本
        version = db.query(version_model).filter(
            version_model.document_id == doc_id,
            version_model.version_number == revert_request.version_number,
            version_model.deleted_at == None
        ).first()
        
        if not version:
            raise HTTPException(status_code=404, detail="Version not found")
        
        # 回退到指定版本
        document.current_version_id = version.id
        db.commit()
        db.refresh(document)
        
        return DocumentOut(
            id=str(document.id),
            user_id=str(document.user_id),
            type=doc_type,
            title=document.title,
            current_version_id=str(document.current_version_id),
            created_at=document.created_at,
            updated_at=document.updated_at,
            versions=[]
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Revert document failed: {str(e)}")

@doc_router.get("/{doc_type}/{doc_id}/versions", response_model=List[DocumentVersionOut])
async def list_versions(
    doc_type: str,
    doc_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)
):
    """获取文档版本历史"""
    try:
        doc_model, version_model = get_document_model(doc_type)
        if not doc_model:
            raise HTTPException(status_code=400, detail="Invalid document type")
        
        # 验证文档存在且属于当前用户
        document = db.query(doc_model).filter(
            doc_model.id == doc_id,
            doc_model.user_id == current_user.id,
            doc_model.deleted_at == None
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # 获取版本历史
        versions = db.query(version_model).filter(
            version_model.document_id == doc_id,
            version_model.deleted_at == None
        ).order_by(version_model.created_at.desc()).all()
        
        return [DocumentVersionOut(
            id=str(v.id),
            version_number=v.version_number,
            content=v.content,
            content_format=v.content_format,
            created_at=v.created_at,
            checksum_sha256=v.checksum_sha256
        ) for v in versions]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"List versions failed: {str(e)}")

@doc_router.get("/{doc_type}/{doc_id}/versions/{version_number}", response_model=DocumentVersionOut)
async def get_version(
    doc_type: str,
    doc_id: str,
    version_number: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)
):
    """获取指定版本详情"""
    try:
        doc_model, version_model = get_document_model(doc_type)
        if not doc_model:
            raise HTTPException(status_code=400, detail="Invalid document type")
        
        # 验证文档存在且属于当前用户
        document = db.query(doc_model).filter(
            doc_model.id == doc_id,
            doc_model.user_id == current_user.id,
            doc_model.deleted_at == None
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # 获取指定版本
        version = db.query(version_model).filter(
            version_model.document_id == doc_id,
            version_model.version_number == version_number,
            version_model.deleted_at == None
        ).first()
        
        if not version:
            raise HTTPException(status_code=404, detail="Version not found")
        
        return DocumentVersionOut(
            id=str(version.id),
            version_number=version.version_number,
            content=version.content,
            content_format=version.content_format,
            created_at=version.created_at,
            checksum_sha256=version.checksum_sha256
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Get version failed: {str(e)}")

@doc_router.get("/{doc_type}", response_model=List[DocumentOut])
async def list_documents(
    doc_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)
):
    """获取用户的所有文档"""
    try:
        doc_model, version_model = get_document_model(doc_type)
        if not doc_model:
            raise HTTPException(status_code=400, detail="Invalid document type")
        
        documents = db.query(doc_model).filter(
            doc_model.user_id == current_user.id,
            doc_model.deleted_at == None
        ).order_by(doc_model.updated_at.desc()).all()
        
        return [DocumentOut(
            id=str(doc.id),
            user_id=str(doc.user_id),
            type=doc_type,
            title=doc.title,
            current_version_id=str(doc.current_version_id) if doc.current_version_id else None,
            created_at=doc.created_at,
            updated_at=doc.updated_at,
            versions=[]
        ) for doc in documents]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"List documents failed: {str(e)}")

# 异步队列接口（预留）
@doc_router.post("/{doc_type}/{doc_id}/versions/async")
async def add_version_async(
    doc_type: str,
    doc_id: str,
    content: str = Form(...),
    content_format: str = Form("markdown"),
    current_user: User = Depends(get_current_user_from_cookie)
):
    """异步添加新版本（预留接口）"""
    try:
        # 验证文档类型
        doc_model, version_model = get_document_model(doc_type)
        if not doc_model:
            raise HTTPException(status_code=400, detail="Invalid document type")
        
        # 将任务加入异步队列
        await AsyncQueueService.enqueue_version_creation(
            doc_type=doc_type,
            doc_id=doc_id,
            content=content,
            user_id=str(current_user.id)
        )
        
        return {"status": "queued", "message": "Version creation queued successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Queue version creation failed: {str(e)}")