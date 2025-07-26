import os
import requests
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="飞书多维表格 API 封装",
    description="提供对飞书多维表格的 CRUD 操作接口",
    version="1.0.0"
)
TABLE_ID = "tblrvt47sVCclhSp"

# 飞书配置
FEISHU_APP_ID = os.getenv("FEISHU_APP_ID", "cli_a8e82762f83bd00b")
FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET", "1L2qLhLheEePVh5iq2mShbnrbe6YXiSV")
FEISHU_API_BASE = "https://open.feishu.cn/open-apis"

# 存储访问令牌及其过期时间
feishu_token = {
    "access_token": None,
    "expires_at": 0  # Unix 时间戳
}

class FeishuTableConfig(BaseModel):
    app_token: str = Field(..., description="多维表格的 app_token")
    table_id: str = Field(..., description="多维表格的 table_id")

class RecordField(BaseModel):
    field_id: str = Field(..., description="字段ID")
    value: Any = Field(..., description="字段值")

class CreateRecordRequest(BaseModel):
    app_token: str = Field(..., description="多维表格的 app_token")
    table_id: str = Field(..., description="多维表格的 table_id")
    fields: Dict[str, Any] = Field(..., description="字段键值对")

class UpdateRecordRequest(BaseModel):
    app_token: str = Field(..., description="多维表格的 app_token")
    table_id: str = Field(..., description="多维表格的 table_id")
    record_id: str = Field(..., description="记录ID")
    fields: Dict[str, Any] = Field(..., description="要更新的字段键值对")

class QueryRecordsRequest(BaseModel):
    app_token: str = Field(..., description="多维表格的 app_token")
    table_id: str = Field(..., description="多维表格的 table_id")
    filter: Optional[str] = Field(None, description="筛选条件")
    sort: Optional[str] = Field(None, description="排序条件")
    page_size: int = Field(100, description="每页记录数")
    page_token: Optional[str] = Field(None, description="分页令牌")

class BatchRequest(BaseModel):
    app_token: str = Field(..., description="多维表格的 app_token")
    table_id: str = Field(..., description="多维表格的 table_id")
    requests: List[Dict] = Field(..., description="批量操作请求列表")

# --- 飞书认证管理 ---

def get_feishu_token():
    """获取或刷新飞书访问令牌"""
    global feishu_token
    
    # 如果令牌在有效期内，直接返回
    if feishu_token["access_token"] and datetime.now().timestamp() < feishu_token["expires_at"] - 60:
        return feishu_token["access_token"]
    
    # 获取新令牌
    url = f"{FEISHU_API_BASE}/auth/v3/tenant_access_token/internal"
    payload = {
        "app_id": FEISHU_APP_ID,
        "app_secret": FEISHU_APP_SECRET
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        
        if data["code"] != 0:
            logger.error(f"获取飞书令牌失败: {data['msg']}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="获取飞书访问令牌失败"
            )
        
        # 更新令牌信息
        feishu_token["access_token"] = data["tenant_access_token"]
        feishu_token["expires_at"] = datetime.now().timestamp() + data["expire"]
        
        logger.info("飞书访问令牌已更新")
        return feishu_token["access_token"]
    
    except Exception as e:
        logger.error(f"获取飞书令牌异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="无法连接飞书服务"
        )

def get_auth_headers():
    """获取认证头"""
    token = get_feishu_token()
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

# --- 多维表格操作封装 ---

def get_table_info(app_token: str, table_id: str):
    """获取表格元数据"""
    headers = get_auth_headers()
    url = f"{FEISHU_API_BASE}/bitable/v1/apps/{app_token}/tables/{table_id}"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if data["code"] != 0:
            logger.error(f"获取表格信息失败: {data['msg']}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"获取表格信息失败: {data['msg']}"
            )
        
        return data["data"]
    
    except requests.exceptions.HTTPError as e:
        logger.error(f"获取表格信息HTTP错误: {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail="飞书API请求失败"
        )

def create_record(app_token: str, table_id: str, fields: dict):
    """创建新记录"""
    headers = get_auth_headers()
    url = f"{FEISHU_API_BASE}/bitable/v1/apps/{app_token}/tables/{table_id}/records"
    payload = {
        "fields": fields
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        if data["code"] != 0:
            logger.error(f"创建记录失败: {data['msg']}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"创建记录失败: {data['msg']}"
            )
        
        return data["data"]
    
    except requests.exceptions.HTTPError as e:
        logger.error(f"创建记录HTTP错误: {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail="创建记录请求失败"
        )

def get_record(app_token: str, table_id: str, record_id: str):
    """获取单条记录"""
    headers = get_auth_headers()
    url = f"{FEISHU_API_BASE}/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if data["code"] != 0:
            logger.error(f"获取记录失败: {data['msg']}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"记录不存在: {data['msg']}"
            )
        
        return data["data"]
    
    except requests.exceptions.HTTPError as e:
        logger.error(f"获取记录HTTP错误: {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail="获取记录请求失败"
        )

def update_record(app_token: str, table_id: str, record_id: str, fields: dict):
    """更新记录"""
    headers = get_auth_headers()
    url = f"{FEISHU_API_BASE}/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}"
    payload = {
        "fields": fields
    }
    
    try:
        response = requests.put(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        if data["code"] != 0:
            logger.error(f"更新记录失败: {data['msg']}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"更新记录失败: {data['msg']}"
            )
        
        return data["data"]
    
    except requests.exceptions.HTTPError as e:
        logger.error(f"更新记录HTTP错误: {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail="更新记录请求失败"
        )

def delete_record(app_token: str, table_id: str, record_id: str):
    """删除记录"""
    headers = get_auth_headers()
    url = f"{FEISHU_API_BASE}/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}"
    
    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if data["code"] != 0:
            logger.error(f"删除记录失败: {data['msg']}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"删除记录失败: {data['msg']}"
            )
        
        return {"success": True, "record_id": record_id}
    
    except requests.exceptions.HTTPError as e:
        logger.error(f"删除记录HTTP错误: {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail="删除记录请求失败"
        )

def query_records(
    app_token: str, 
    table_id: str, 
    filter: str = None, 
    sort: str = None, 
    page_size: int = 100, 
    page_token: str = None
):
    """查询记录"""
    headers = get_auth_headers()
    url = f"{FEISHU_API_BASE}/bitable/v1/apps/{app_token}/tables/{table_id}/records"
    
    params = {
        "page_size": page_size
    }
    
    if filter:
        params["filter"] = filter
    if sort:
        params["sort"] = sort
    if page_token:
        params["page_token"] = page_token
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data["code"] != 0:
            logger.error(f"查询记录失败: {data['msg']}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"查询记录失败: {data['msg']}"
            )
        
        return data["data"]
    
    except requests.exceptions.HTTPError as e:
        logger.error(f"查询记录HTTP错误: {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail="查询记录请求失败"
        )

def batch_operations(app_token: str, table_id: str, requests: list):
    """批量操作"""
    headers = get_auth_headers()
    url = f"{FEISHU_API_BASE}/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_update"
    
    payload = {
        "requests": requests
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        if data["code"] != 0:
            logger.error(f"批量操作失败: {data['msg']}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"批量操作失败: {data['msg']}"
            )
        
        return data["data"]
    
    except requests.exceptions.HTTPError as e:
        logger.error(f"批量操作HTTP错误: {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail="批量操作请求失败"
        )

# --- API 端点 ---

@app.get("/table-info", summary="获取表格元数据")
async def get_table_info_endpoint(config: FeishuTableConfig = Depends()):
    """
    获取多维表格的元数据信息，包括字段定义等
    """
    return get_table_info(config.app_token, config.table_id)

@app.post("/records", summary="创建新记录", status_code=status.HTTP_201_CREATED)
async def create_record_endpoint(request: CreateRecordRequest):
    """
    在多维表格中创建新记录
    """
    return create_record(request.app_token, request.table_id, request.fields)

@app.get("/records/{record_id}", summary="获取单条记录")
async def get_record_endpoint(
    record_id: str,
    app_token: str,
    table_id: str
):
    """
    根据记录ID获取单条记录详情
    """
    return get_record(app_token, table_id, record_id)

@app.put("/records/{record_id}", summary="更新记录")
async def update_record_endpoint(
    record_id: str,
    request: UpdateRecordRequest
):
    """
    更新指定记录
    """
    return update_record(
        request.app_token, 
        request.table_id, 
        record_id, 
        request.fields
    )

@app.delete("/records/{record_id}", summary="删除记录")
async def delete_record_endpoint(
    record_id: str,
    app_token: str,
    table_id: str
):
    """
    删除指定记录
    """
    return delete_record(app_token, table_id, record_id)

@app.post("/records/query", summary="查询记录")
async def query_records_endpoint(request: QueryRecordsRequest):
    """
    查询记录，支持筛选、排序和分页
    """
    return query_records(
        request.app_token,
        request.table_id,
        request.filter,
        request.sort,
        request.page_size,
        request.page_token
    )

@app.post("/batch", summary="批量操作")
async def batch_operations_endpoint(request: BatchRequest):
    """
    执行批量操作（创建、更新、删除）
    
    请求示例:
    {
      "requests": [
        {
          "method": "POST",
          "path": "/records",
          "body": {
            "fields": {
              "字段ID": "值"
            }
          }
        },
        {
          "method": "PUT",
          "path": "/records/rec123",
          "body": {
            "fields": {
              "字段ID": "新值"
            }
          }
        },
        {
          "method": "DELETE",
          "path": "/records/rec456"
        }
      ]
    }
    """
    return batch_operations(
        request.app_token,
        request.table_id,
        request.requests
    )

# 健康检查端点
@app.get("/health")
async def health_check():
    try:
        # 测试获取令牌
        token = get_feishu_token()
        return {
            "status": "healthy",
            "feishu_connected": bool(token),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)