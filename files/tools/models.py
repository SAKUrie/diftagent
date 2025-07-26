from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Literal
import json
import logging
from datetime import datetime
import httpx

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserMessage(BaseModel):
    user_id: str = Field(..., description="用户ID")
    message: str = Field(..., description="用户消息内容")
    context: Optional[Dict[str, Any]] = Field(
        {}, 
        description="对话上下文信息"
    )

class ToolResponse(BaseModel):
    tool_name: str = Field(..., description="调用的工具名称")
    tool_params: Dict[str, Any] = Field(..., description="工具调用参数")
    result: Dict[str, Any] = Field(..., description="工具调用结果")
    success: bool = Field(..., description="是否成功")
    error: Optional[str] = Field(None, description="错误信息")

class IntentResponse(BaseModel):
    intent: str = Field(..., description="识别的意图")
    confidence: float = Field(..., description="置信度")
    parameters: Dict[str, Any] = Field(..., description="提取的参数")
    tool_name: str = Field(..., description="需要调用的工具")

class ChatResponse(BaseModel):
    user_id: str = Field(..., description="用户ID")
    response: str = Field(..., description="自然语言回复")
    tool_responses: List[ToolResponse] = Field(..., description="工具调用结果")
    structured_data: Dict[str, Any] = Field(..., description="结构化数据")
    timestamp: datetime = Field(..., description="响应时间")