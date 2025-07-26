import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import httpx
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="留学选校推荐系统",
    description="基于 Dify 工作流的留学选校推荐 API",
    version="1.0.0"
)

# Dify 配置
DIFY_API_KEY = os.getenv("DIFY_API_KEY", "app-CkYZiKp2StPkYPEI57ttpmYP")
DIFY_WORKFLOW_ENDPOINT = os.getenv("DIFY_WORKFLOW_ENDPOINT", "http://localhost/v1/workflows/run")

# 学生信息模型
class StudentProfile(BaseModel):
    user_uid: str = Field(..., description="用户唯一ID")
    user_university: str = Field(..., description="当前就读大学")
    user_grade: str = Field(..., description="年级")
    user_graduate_year: str = Field(..., description="毕业年份")
    user_major: str = Field(..., description="专业")
    user_gpa: float = Field(..., description="GPA成绩", ge=0.0, le=4.0)
    user_language_score: Dict[str, float] = Field(
        default_factory=dict,
        description="语言成绩，如 {'IELTS': 7.5, 'TOEFL': 105}"
    )
    user_internship_experience: List[str] = Field(
        default_factory=list,
        description="实习经历列表"
    )
    user_research_experience: List[str] = Field(
        default_factory=list,
        description="研究经历列表"
    )
    user_extracurricular_activities: List[str] = Field(
        default_factory=list,
        description="课外活动列表"
    )
    user_target: Dict[str, str] = Field(
        default_factory=dict,
        description="留学目标，如 {'country': '美国', 'degree': '硕士'}"
    )

# Dify 响应模型
class CompletionResponse(BaseModel):
    workflow_run_id: str = Field(..., description="工作流执行ID")
    task_id: str = Field(..., description="任务ID，用于跟踪")
    data: Dict[str, Any] = Field(..., description="响应数据详情")
    
    class DataModel(BaseModel):
        id: str = Field(..., description="工作流执行ID")
        workflow_id: str = Field(..., description="关联Workflow ID")
        status: str = Field(..., description="执行状态: running/succeeded/failed/stopped")
        outputs: Optional[Dict[str, Any]] = Field(None, description="输出内容")
        error: Optional[str] = Field(None, description="错误原因")
        elapsed_time: Optional[float] = Field(None, description="耗时(s)")
        total_tokens: Optional[int] = Field(None, description="总使用tokens")
        total_steps: int = Field(0, description="总步数")
        created_at: Optional[datetime] = Field(None, description="开始时间")
        finished_at: Optional[datetime] = Field(None, description="结束时间")

# 最终响应模型
class RecommendationResponse(BaseModel):
    success: bool = Field(..., description="请求是否成功")
    message: str = Field(..., description="结果消息")
    workflow_run_id: str = Field(..., description="工作流执行ID")
    status: str = Field(..., description="工作流执行状态")
    elapsed_time: Optional[float] = Field(None, description="处理耗时(秒)")
    total_tokens: Optional[int] = Field(None, description="消耗的token数量")
    recommendations: Optional[str] = Field(None, description="选校推荐结果文本")
    raw_output: Optional[Dict[str, Any]] = Field(None, description="原始输出内容")

@app.post("/recommend-schools", response_model=RecommendationResponse)
async def recommend_schools(student: StudentProfile):
    """
    调用Dify工作流获取选校推荐
    """
    try:
        # 1. 准备Dify请求
        payload = {
            "inputs": {
                "query": json.dumps(student.dict())
            },
            "response_mode": "blocking",
            "user": student.user_uid,
        }
        print(len(payload["inputs"]["query"]))

        headers = {
            "Authorization": f"Bearer {DIFY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"调用Dify工作流API: {DIFY_WORKFLOW_ENDPOINT}")
        
        # 2. 调用Dify API - 设置更长的超时时间
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(
                DIFY_WORKFLOW_ENDPOINT,
                json=payload,
                headers=headers
            )
            
            # 检查HTTP状态码
            if response.status_code != 200:
                error_detail = f"Dify API错误: {response.status_code} - {response.text}"
                logger.error(error_detail)
                raise HTTPException(
                    status_code=502,
                    detail=error_detail
                )
            
            # 3. 解析Dify响应
            dify_response = response.json()
            logger.debug(f"Dify原始响应: {json.dumps(dify_response, indent=2)}")
            
            # 验证响应结构
            if "workflow_run_id" not in dify_response or "data" not in dify_response:
                logger.error("Dify响应缺少必要字段")
                raise HTTPException(
                    status_code=502,
                    detail="Dify响应格式无效"
                )
            
            # 4. 提取关键信息
            data = dify_response["data"]
            status = data.get("status", "unknown")
            
            # 5. 处理不同状态
            if status == "succeeded":
                outputs = data.get("outputs", {})
                
                # 尝试提取LLM生成的文本内容
                recommendation_text = None
                
                # 方法1: 尝试从outputs中提取文本
                if outputs and isinstance(outputs, dict):
                    # 查找可能的文本字段
                    for key in ["text", "output", "result", "response", "answer"]:
                        if key in outputs and isinstance(outputs[key], str):
                            recommendation_text = outputs[key]
                            break
                
                # 方法2: 如果上面没找到，尝试直接使用整个outputs
                if not recommendation_text:
                    recommendation_text = json.dumps(outputs, ensure_ascii=False, indent=2)
                
                return RecommendationResponse(
                    success=True,
                    message="选校推荐生成成功",
                    workflow_run_id=dify_response["workflow_run_id"],
                    status=status,
                    elapsed_time=data.get("elapsed_time"),
                    total_tokens=data.get("total_tokens"),
                    recommendations=recommendation_text,
                    raw_output=outputs
                )
            
            elif status == "failed":
                error_msg = data.get("error", "未知错误")
                logger.error(f"Dify工作流失败: {error_msg}")
                return RecommendationResponse(
                    success=False,
                    message=f"工作流执行失败: {error_msg}",
                    workflow_run_id=dify_response["workflow_run_id"],
                    status=status,
                    elapsed_time=data.get("elapsed_time"),
                    raw_output=data
                )
            
            else:  # running 或其他状态
                return RecommendationResponse(
                    success=False,
                    message="工作流仍在处理中，请稍后查询结果",
                    workflow_run_id=dify_response["workflow_run_id"],
                    status=status,
                    elapsed_time=data.get("elapsed_time"),
                    raw_output=data
                )
    
    except httpx.HTTPStatusError as e:
        logger.error(f"Dify API HTTP错误: {e.response.text}")
        raise HTTPException(
            status_code=502,
            detail=f"Dify服务错误: {e.response.status_code}"
        )
    
    except httpx.ReadTimeout:
        logger.error("Dify API请求超时")
        raise HTTPException(
            status_code=504,
            detail="Dify服务响应超时"
        )
    
    except Exception as e:
        logger.exception("处理请求时出错")
        raise HTTPException(
            status_code=500,
            detail=f"服务器内部错误: {str(e)}"
        )

# 获取工作流状态端点
@app.get("/workflow-status/{workflow_run_id}", response_model=RecommendationResponse)
async def get_workflow_status(workflow_run_id: str):
    """
    根据工作流ID查询状态和结果
    """
    try:
        headers = {
            "Authorization": f"Bearer {DIFY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        url = f"{DIFY_WORKFLOW_ENDPOINT}/{workflow_run_id}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
            dify_response = response.json()
            data = dify_response["data"]
            status = data.get("status", "unknown")
            
            if status == "succeeded":
                outputs = data.get("outputs", {})
                recommendation_text = None
                
                # 提取文本内容
                if outputs and isinstance(outputs, dict):
                    for key in ["text", "output", "result", "response", "answer"]:
                        if key in outputs and isinstance(outputs[key], str):
                            recommendation_text = outputs[key]
                            break
                
                if not recommendation_text:
                    recommendation_text = json.dumps(outputs, ensure_ascii=False, indent=2)
                
                return RecommendationResponse(
                    success=True,
                    message="选校推荐已生成",
                    workflow_run_id=workflow_run_id,
                    status=status,
                    elapsed_time=data.get("elapsed_time"),
                    total_tokens=data.get("total_tokens"),
                    recommendations=recommendation_text,
                    raw_output=outputs
                )
            
            else:
                return RecommendationResponse(
                    success=False,
                    message=f"工作流状态: {status}",
                    workflow_run_id=workflow_run_id,
                    status=status,
                    elapsed_time=data.get("elapsed_time"),
                    total_tokens=data.get("total_tokens"),
                    raw_output=data
                )
    
    except Exception as e:
        logger.error(f"查询工作流状态失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"查询工作流状态失败: {str(e)}"
        )

# 健康检查端点
@app.get("/health", tags=["监控"])
async def health_check():
    return {
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "dify_configured": bool(DIFY_API_KEY)
    }

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