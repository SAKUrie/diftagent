#!/usr/bin/env python3
"""
快速对话日志测试脚本
用于快速验证对话日志API的基本功能
"""
import requests
import json
import time

# 配置
BASE_URL = "http://localhost:8000"

def quick_conversation_test():
    """快速对话日志测试"""
    print("🚀 快速对话日志测试")
    print(f"服务器地址: {BASE_URL}")
    
    # 创建会话
    session = requests.Session()
    
    # 1. 登录
    print("\n1. 登录...")
    login_data = {
        "username": "testuser",
        "password": "123456"
    }
    
    try:
        response = session.post(f"{BASE_URL}/auth/login", data=login_data)
        if response.status_code == 200:
            data = response.json()
            access_token = data.get('access_token')
            session.cookies.set("access_token", access_token)
            print("   ✅ 登录成功")
        else:
            print(f"   ❌ 登录失败: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 登录异常: {e}")
        return False
    
    # 2. 创建会话
    print("\n2. 创建会话...")
    session_data = {
        "session_name": f"快速测试_{int(time.time())}",
        "session_type": "general",
        "session_metadata": {
            "description": "快速测试会话",
            "tags": ["快速", "测试"]
        }
    }
    
    try:
        response = session.post(f"{BASE_URL}/conversations/sessions", json=session_data)
        if response.status_code == 200:
            conversation_session = response.json()
            session_id = conversation_session['id']
            print("   ✅ 会话创建成功")
            print(f"   会话ID: {session_id}")
        else:
            print(f"   ❌ 会话创建失败: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 会话创建异常: {e}")
        return False
    
    # 3. 添加消息
    print("\n3. 添加消息...")
    messages = [
        {
            "message_type": "user",
            "content": "你好，这是一个快速测试",
            "role": "user",
            "tokens_used": 10
        },
        {
            "message_type": "assistant",
            "content": "您好！这是一个快速测试回复",
            "role": "assistant",
            "tokens_used": 15
        }
    ]
    
    for i, message_data in enumerate(messages, 1):
        try:
            response = session.post(
                f"{BASE_URL}/conversations/sessions/{session_id}/messages", 
                json=message_data
            )
            if response.status_code == 200:
                print(f"   ✅ 消息{i}添加成功")
            else:
                print(f"   ❌ 消息{i}添加失败: {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ 消息{i}添加异常: {e}")
            return False
    
    # 4. 获取会话详情
    print("\n4. 获取会话详情...")
    try:
        response = session.get(f"{BASE_URL}/conversations/sessions/{session_id}")
        if response.status_code == 200:
            session_detail = response.json()
            print("   ✅ 获取会话详情成功")
            print(f"   消息数量: {session_detail['session']['message_count']}")
        else:
            print(f"   ❌ 获取会话详情失败: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 获取会话详情异常: {e}")
        return False
    
    # 5. 获取会话列表
    print("\n5. 获取会话列表...")
    try:
        response = session.get(f"{BASE_URL}/conversations/sessions")
        if response.status_code == 200:
            sessions = response.json()
            print("   ✅ 获取会话列表成功")
            print(f"   会话数量: {len(sessions)}")
        else:
            print(f"   ❌ 获取会话列表失败: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 获取会话列表异常: {e}")
        return False
    
    print("\n🎉 快速测试完成！")
    return True

def main():
    """主函数"""
    print("=== 快速对话日志测试 ===")
    success = quick_conversation_test()
    if success:
        print("\n✅ 快速测试通过")
    else:
        print("\n❌ 快速测试失败")
    print("=== 测试完成 ===")

if __name__ == "__main__":
    main() 