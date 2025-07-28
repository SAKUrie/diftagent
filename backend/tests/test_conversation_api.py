#!/usr/bin/env python3
"""
对话日志API测试脚本
"""
import requests
import json
import time
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8000"

def test_conversation_api():
    """测试对话日志API功能"""
    print("🚀 对话日志API测试")
    print(f"服务器地址: {BASE_URL}")
    
    # 1. 登录获取访问令牌
    print("\n1. 登录获取访问令牌...")
    login_data = {
        "username": "testuser",
        "password": "123456"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        if response.status_code == 200:
            data = response.json()
            access_token = data.get('access_token')
            print("   ✅ 登录成功")
            print(f"   Access Token: {access_token[:20]}...")
        else:
            print(f"   ❌ 登录失败: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 登录异常: {e}")
        return False
    
    # 设置cookies用于认证
    cookies = {"access_token": access_token}
    
    # 2. 创建对话会话
    print("\n2. 测试创建对话会话...")
    session_data = {
        "session_name": "测试会话",
        "session_type": "general",
        "session_metadata": {
            "description": "这是一个测试会话",
            "tags": ["测试", "对话"]
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/conversations/sessions", json=session_data, cookies=cookies)
        if response.status_code == 200:
            session = response.json()
            session_id = session['id']
            print("   ✅ 会话创建成功")
            print(f"   会话ID: {session_id}")
            print(f"   会话名称: {session['session_name']}")
        else:
            print(f"   ❌ 会话创建失败: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 会话创建异常: {e}")
        return False
    
    # 3. 添加对话消息
    print("\n3. 测试添加对话消息...")
    
    # 添加用户消息
    user_message = {
        "message_type": "user",
        "content": "你好，我想了解一下留学申请的相关信息",
        "role": "user",
        "tokens_used": 15
    }
    
    try:
        response = requests.post(f"{BASE_URL}/conversations/sessions/{session_id}/messages", json=user_message, cookies=cookies)
        if response.status_code == 200:
            message = response.json()
            print("   ✅ 用户消息添加成功")
            print(f"   消息ID: {message['id']}")
        else:
            print(f"   ❌ 用户消息添加失败: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 用户消息添加异常: {e}")
        return False
    
    # 添加助手消息
    assistant_message = {
        "message_type": "assistant",
        "content": "您好！我很乐意为您提供留学申请的相关信息。请问您想了解哪个方面的内容？比如：\n1. 申请流程\n2. 材料准备\n3. 时间安排\n4. 费用预算",
        "role": "assistant",
        "tokens_used": 45
    }
    
    try:
        response = requests.post(f"{BASE_URL}/conversations/sessions/{session_id}/messages", json=assistant_message, cookies=cookies)
        if response.status_code == 200:
            message = response.json()
            print("   ✅ 助手消息添加成功")
            print(f"   消息ID: {message['id']}")
        else:
            print(f"   ❌ 助手消息添加失败: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 助手消息添加异常: {e}")
        return False
    
    # 添加工具消息
    tool_message = {
        "message_type": "tool",
        "content": "已为您查询到最新的申请时间线信息",
        "role": "tool",
        "tool_name": "schedule_reminder",
        "tool_params": {
            "action": "get_timeline",
            "country": "US"
        },
        "tool_result": {
            "status": "success",
            "data": {
                "timeline": [
                    {"month": "9月", "task": "准备申请材料"},
                    {"month": "10月", "task": "提交申请"},
                    {"month": "11月", "task": "等待结果"}
                ]
            }
        },
        "tokens_used": 30
    }
    
    try:
        response = requests.post(f"{BASE_URL}/conversations/sessions/{session_id}/messages", json=tool_message, cookies=cookies)
        if response.status_code == 200:
            message = response.json()
            print("   ✅ 工具消息添加成功")
            print(f"   消息ID: {message['id']}")
        else:
            print(f"   ❌ 工具消息添加失败: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 工具消息添加异常: {e}")
        return False
    
    # 4. 获取会话详情和消息
    print("\n4. 测试获取会话详情...")
    
    try:
        response = requests.get(f"{BASE_URL}/conversations/sessions/{session_id}", cookies=cookies)
        if response.status_code == 200:
            session_detail = response.json()
            print("   ✅ 获取会话详情成功")
            print(f"   会话名称: {session_detail['session']['session_name']}")
            print(f"   消息数量: {session_detail['session']['message_count']}")
            print(f"   消息列表长度: {len(session_detail['messages'])}")
            
            # 显示消息内容
            for i, msg in enumerate(session_detail['messages'], 1):
                print(f"   消息{i}: [{msg['message_type']}] {msg['content'][:50]}...")
        else:
            print(f"   ❌ 获取会话详情失败: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 获取会话详情异常: {e}")
        return False
    
    # 5. 获取消息列表
    print("\n5. 测试获取消息列表...")
    
    try:
        response = requests.get(f"{BASE_URL}/conversations/sessions/{session_id}/messages", cookies=cookies)
        if response.status_code == 200:
            messages = response.json()
            print("   ✅ 获取消息列表成功")
            print(f"   消息数量: {len(messages)}")
            
            for i, msg in enumerate(messages, 1):
                print(f"   消息{i}: [{msg['message_type']}] {msg['content'][:30]}...")
        else:
            print(f"   ❌ 获取消息列表失败: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 获取消息列表异常: {e}")
        return False
    
    # 6. 获取会话列表
    print("\n6. 测试获取会话列表...")
    
    try:
        response = requests.get(f"{BASE_URL}/conversations/sessions", cookies=cookies)
        if response.status_code == 200:
            sessions = response.json()
            print("   ✅ 获取会话列表成功")
            print(f"   会话数量: {len(sessions)}")
            
            for i, session in enumerate(sessions, 1):
                print(f"   会话{i}: {session['session_name']} ({session['message_count']}条消息)")
        else:
            print(f"   ❌ 获取会话列表失败: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 获取会话列表异常: {e}")
        return False
    
    # 7. 更新会话信息
    print("\n7. 测试更新会话信息...")
    
    update_data = {
        "session_name": "更新后的测试会话",
        "session_metadata": {
            "description": "这是更新后的测试会话",
            "tags": ["测试", "对话", "更新"],
            "updated_at": datetime.now().isoformat()
        }
    }
    
    try:
        response = requests.put(f"{BASE_URL}/conversations/sessions/{session_id}", json=update_data, cookies=cookies)
        if response.status_code == 200:
            updated_session = response.json()
            print("   ✅ 会话更新成功")
            print(f"   新名称: {updated_session['session_name']}")
        else:
            print(f"   ❌ 会话更新失败: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 会话更新异常: {e}")
        return False
    
    # 8. 测试错误情况
    print("\n8. 测试错误情况...")
    
    # 测试无效的会话ID
    try:
        response = requests.get(f"{BASE_URL}/conversations/sessions/invalid-uuid", cookies=cookies)
        if response.status_code == 404:
            print("   ✅ 无效会话ID错误处理正确")
        else:
            print(f"   ❌ 无效会话ID错误处理失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 无效会话ID测试异常: {e}")
    
    # 测试无效的消息类型
    invalid_message = {
        "message_type": "invalid_type",
        "content": "这是一个无效的消息类型",
        "role": "user"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/conversations/sessions/{session_id}/messages", json=invalid_message, cookies=cookies)
        if response.status_code == 422:
            print("   ✅ 无效消息类型错误处理正确")
        else:
            print(f"   ❌ 无效消息类型错误处理失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 无效消息类型测试异常: {e}")
    
    # 9. 测试未认证访问
    print("\n9. 测试未认证访问...")
    
    try:
        response = requests.get(f"{BASE_URL}/conversations/sessions")
        if response.status_code == 401:
            print("   ✅ 未认证访问错误处理正确")
        else:
            print(f"   ❌ 未认证访问错误处理失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 未认证访问测试异常: {e}")
    
    print("\n🎉 对话日志API测试完成！")
    return True

def main():
    """主函数"""
    print("=== 对话日志API测试 ===")
    success = test_conversation_api()
    if success:
        print("\n✅ 所有测试通过")
    else:
        print("\n❌ 测试失败")
    print("=== 测试完成 ===")

if __name__ == "__main__":
    main() 