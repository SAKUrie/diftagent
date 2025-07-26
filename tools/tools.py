import openai
from openai import OpenAI
import json
from tools.models import UserMessage, IntentResponse, ToolResponse, ChatResponse
import os
import logging
import httpx

# 工具定义
TOOLS = [
    {
        "name": "school_recommendation",
        "description": "基于学生背景信息生成选校推荐",
        "parameters": {
            "type": "object",
            "properties": {
                "user_university": {"type": "string", "description": "用户当前大学"},
                "user_major": {"type": "string", "description": "用户专业"},
                "user_gpa": {"type": "number", "description": "用户GPA成绩"},
                "user_target": {
                    "type": "object",
                    "properties": {
                        "country": {"type": "string", "description": "目标国家"},
                        "degree": {"type": "string", "description": "目标学位"}
                    }
                }
            },
            "required": ["user_university", "user_major", "user_gpa", "user_target"]
        }
    },
    {
        "name": "deadline_query",
        "description": "查询指定院校的申请截止日期",
        "parameters": {
            "type": "object",
            "properties": {
                "school": {"type": "string", "description": "院校名称"}
            },
            "required": ["school"]
        }
    },
    {
        "name": "timeline_generation",
        "description": "基于截止日期生成个性化申请时间线",
        "parameters": {
            "type": "object",
            "properties": {
                "school": {"type": "string", "description": "院校名称"},
                "app_deadline": {"type": "string", "description": "申请截止日期", "format": "date"},
                "financial_deadline": {"type": "string", "description": "财务证明截止日期", "format": "date"}
            },
            "required": ["school", "app_deadline"]
        }
    },
    {
        "name": "schedule_reminder",
        "description": "为用户安排提醒任务",
        "parameters": {
            "type": "object",
            "properties": {
                "due_date": {"type": "string", "description": "提醒时间", "format": "date-time"},
                "message": {"type": "string", "description": "提醒内容"}
            },
            "required": ["due_date", "message"]
        }
    },
    {
        "name": "feishu_operation",
        "description": "执行飞书多维表格的CRUD操作",
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string", 
                    "enum": ["create", "read", "update", "delete", "query"],
                    "description": "操作类型"
                },
                "app_token": {"type": "string", "description": "飞书表格app_token"},
                "table_id": {"type": "string", "description": "表格ID"},
                "record_id": {
                    "type": "string", 
                    "description": "记录ID(update/delete/read时必填)"
                },
                "fields": {
                    "type": "object",
                    "description": "字段数据(create/update时必填)"
                }
            },
            "required": ["operation", "app_token", "table_id"]
        }
    }
]

def analyze_intent(user_message: UserMessage) -> IntentResponse:
    """
    使用OpenAI Function Calling进行意图分析和参数提取
    """
    try:
        # 构造消息历史
        messages = [
            {
                "role": "system",
                "content": "你是一个留学申请助手，负责分析用户意图并提取参数。当前用户：" + user_message.user_id
            },
            {
                "role": "user",
                "content": user_message.message
            }
        ]
        
        # 添加上下文
        if user_message.context:
            messages.append({
                "role": "system",
                "content": f"上下文信息: {json.dumps(user_message.context)}"
            })
        
        # 调用OpenAI
        response = openai_client.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"
        )
        
        # 解析响应
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        
        if tool_calls:
            # 只处理第一个工具调用（单意图）
            tool_call = tool_calls[0]
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            
            return IntentResponse(
                intent=tool_name,
                confidence=1.0,  # 使用OpenAI时置信度设为1
                parameters=tool_args,
                tool_name=tool_name
            )
        else:
            # 没有工具调用，视为普通对话
            return IntentResponse(
                intent="general_chat",
                confidence=1.0,
                parameters={},
                tool_name="general_chat"
            )
    
    except Exception as e:
        logger.error(f"意图分析失败: {str(e)}")
        return IntentResponse(
            intent="error",
            confidence=0.0,
            parameters={},
            tool_name="error_handler",
            error=str(e)
        )
    


async def call_school_recommendation(params: dict) -> ToolResponse:
    """调用选校推荐工具"""
    try:
        # 构造请求数据
        student_data = {
            "user_uid": params.get("user_id", "default_user"),
            "user_university": params["user_university"],
            "user_major": params["user_major"],
            "user_gpa": params["user_gpa"],
            "user_target": params["user_target"]
        }
        
        # 填充其他可选字段
        for field in ["user_grade", "user_graduate_year", "user_language_score", 
                     "user_internship_experience", "user_research_experience", 
                     "user_extracurricular_activities"]:
            if field in params:
                student_data[field] = params[field]
        
        # 调用API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/recommend-schools",
                json=student_data,
                timeout=60.0
            )
            response.raise_for_status()
            result = response.json()
            
        return ToolResponse(
            tool_name="school_recommendation",
            tool_params=student_data,
            result=result,
            success=True
        )
    except Exception as e:
        return ToolResponse(
            tool_name="school_recommendation",
            tool_params=params,
            result={},
            success=False,
            error=str(e)
        )

async def call_deadline_query(params: dict) -> ToolResponse:
    """调用截止日期查询工具"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/query-deadlines",
                json={"school": params["school"]},
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            
        return ToolResponse(
            tool_name="deadline_query",
            tool_params=params,
            result=result,
            success=True
        )
    except Exception as e:
        return ToolResponse(
            tool_name="deadline_query",
            tool_params=params,
            result={},
            success=False,
            error=str(e)
        )

async def call_timeline_generation(params: dict) -> ToolResponse:
    """调用时间线生成工具"""
    try:
        deadlines = {
            "app_deadline": params["app_deadline"],
            "financial_deadline": params.get("financial_deadline", "")
        }
        
        request_data = {
            "school": params["school"],
            "deadlines": deadlines,
            "user_level": params.get("user_level", "normal")
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/generate-timeline",
                json=request_data,
                timeout=60.0
            )
            response.raise_for_status()
            result = response.json()
            
        return ToolResponse(
            tool_name="timeline_generation",
            tool_params=request_data,
            result=result,
            success=True
        )
    except Exception as e:
        return ToolResponse(
            tool_name="timeline_generation",
            tool_params=params,
            result={},
            success=False,
            error=str(e)
        )

async def call_schedule_reminder(params: dict) -> ToolResponse:
    """调用提醒安排工具"""
    try:
        request_data = {
            "user_id": params.get("user_id", "default_user"),
            "due_date": params["due_date"],
            "message": params["message"],
            "method": params.get("method", "email"),
            "email": params.get("email"),
            "reminder_time": params.get("reminder_time", 24),
            "recurring": params.get("recurring", False)
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/schedule-reminder",
                json=request_data,
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            
        return ToolResponse(
            tool_name="schedule_reminder",
            tool_params=request_data,
            result=result,
            success=True
        )
    except Exception as e:
        return ToolResponse(
            tool_name="schedule_reminder",
            tool_params=params,
            result={},
            success=False,
            error=str(e)
        )

async def call_feishu_operation(params: dict) -> ToolResponse:
    """调用飞书表格操作工具"""
    try:
        operation = params["operation"]
        endpoint_map = {
            "create": "/records",
            "read": f"/records/{params.get('record_id', '')}",
            "update": f"/records/{params.get('record_id', '')}",
            "delete": f"/records/{params.get('record_id', '')}",
            "query": "/records/query"
        }
        
        endpoint = endpoint_map.get(operation)
        if not endpoint:
            raise ValueError(f"无效的操作类型: {operation}")
        
        # 构造请求数据
        request_data = {
            "app_token": params["app_token"],
            "table_id": params["table_id"]
        }
        
        if operation in ["create", "update"]:
            request_data["fields"] = params["fields"]
        if operation in ["read", "update", "delete"]:
            request_data["record_id"] = params["record_id"]
        if operation == "query":
            for key in ["filter", "sort", "page_size", "page_token"]:
                if key in params:
                    request_data[key] = params[key]
        
        # 确定HTTP方法
        method_map = {
            "create": "POST",
            "read": "GET",
            "update": "PUT",
            "delete": "DELETE",
            "query": "POST"
        }
        http_method = method_map[operation]
        
        # 调用API
        async with httpx.AsyncClient() as client:
            if http_method == "GET":
                response = await client.get(
                    f"{BASE_URL}{endpoint}",
                    params=request_data,
                    timeout=30.0
                )
            else:
                response = await client.request(
                    http_method,
                    f"{BASE_URL}{endpoint}",
                    json=request_data,
                    timeout=30.0
                )
            response.raise_for_status()
            result = response.json()
            
        return ToolResponse(
            tool_name="feishu_operation",
            tool_params=params,
            result=result,
            success=True
        )
    except Exception as e:
        return ToolResponse(
            tool_name="feishu_operation",
            tool_params=params,
            result={},
            success=False,
            error=str(e)
        )

# 工具调用映射
TOOL_HANDLERS = {
    "school_recommendation": call_school_recommendation,
    "deadline_query": call_deadline_query,
    "timeline_generation": call_timeline_generation,
    "schedule_reminder": call_schedule_reminder,
    "feishu_operation": call_feishu_operation
}