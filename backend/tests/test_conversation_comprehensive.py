#!/usr/bin/env python3
"""
对话日志API综合测试脚本
包含更全面的测试场景
"""
import requests
import json
import time
from datetime import datetime
import uuid

# 配置
BASE_URL = "http://localhost:8000"

class ConversationTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.test_session_id = None
    
    def test_login(self):
        """测试登录"""
        print("1. 测试登录...")
        login_data = {
            "username": "testuser",
            "password": "123456"
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/auth/login", data=login_data)
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access_token')
                
                # 设置cookie用于认证
                self.session.cookies.set("access_token", self.access_token)
                
                print("   ✅ 登录成功")
                print(f"   Access Token: {self.access_token[:20]}...")
                return True
            else:
                print(f"   ❌ 登录失败: {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ 登录异常: {e}")
            return False
    
    def test_create_session(self):
        """测试创建会话"""
        print("\n2. 测试创建会话...")
        session_data = {
            "session_name": f"测试会话_{int(time.time())}",
            "session_type": "general",
            "session_metadata": {
                "description": "这是一个测试会话",
                "tags": ["测试", "对话"],
                "created_by": "test_user"
            }
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/conversations/sessions", json=session_data)
            if response.status_code == 200:
                session = response.json()
                self.test_session_id = session['id']
                print("   ✅ 会话创建成功")
                print(f"   会话ID: {self.test_session_id}")
                print(f"   会话名称: {session['session_name']}")
                return True
            else:
                print(f"   ❌ 会话创建失败: {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ 会话创建异常: {e}")
            return False
    
    def test_add_messages(self):
        """测试添加消息"""
        print("\n3. 测试添加消息...")
        
        messages = [
            {
                "message_type": "user",
                "content": "你好，我想了解留学申请的相关信息",
                "role": "user",
                "tokens_used": 15
            },
            {
                "message_type": "assistant",
                "content": "您好！我很乐意为您提供留学申请的相关信息。请问您想了解哪个方面的内容？",
                "role": "assistant",
                "tokens_used": 25
            },
            {
                "message_type": "user",
                "content": "我想了解申请流程和时间安排",
                "role": "user",
                "tokens_used": 12
            },
            {
                "message_type": "tool",
                "content": "已为您查询到申请时间线信息",
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
            },
            {
                "message_type": "assistant",
                "content": "根据查询结果，申请时间线如下：\n1. 9月：准备申请材料\n2. 10月：提交申请\n3. 11月：等待结果",
                "role": "assistant",
                "tokens_used": 35
            }
        ]
        
        for i, message_data in enumerate(messages, 1):
            try:
                response = self.session.post(
                    f"{BASE_URL}/conversations/sessions/{self.test_session_id}/messages", 
                    json=message_data
                )
                if response.status_code == 200:
                    message = response.json()
                    print(f"   ✅ 消息{i}添加成功: [{message_data['message_type']}] {message_data['content'][:20]}...")
                else:
                    print(f"   ❌ 消息{i}添加失败: {response.text}")
                    return False
            except Exception as e:
                print(f"   ❌ 消息{i}添加异常: {e}")
                return False
        
        return True
    
    def test_get_session_details(self):
        """测试获取会话详情"""
        print("\n4. 测试获取会话详情...")
        
        try:
            response = self.session.get(f"{BASE_URL}/conversations/sessions/{self.test_session_id}")
            if response.status_code == 200:
                session_detail = response.json()
                print("   ✅ 获取会话详情成功")
                print(f"   会话名称: {session_detail['session']['session_name']}")
                print(f"   消息数量: {session_detail['session']['message_count']}")
                print(f"   消息列表长度: {len(session_detail['messages'])}")
                
                # 显示消息摘要
                for i, msg in enumerate(session_detail['messages'], 1):
                    print(f"   消息{i}: [{msg['message_type']}] {msg['content'][:30]}...")
                
                return True
            else:
                print(f"   ❌ 获取会话详情失败: {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ 获取会话详情异常: {e}")
            return False
    
    def test_list_sessions(self):
        """测试获取会话列表"""
        print("\n5. 测试获取会话列表...")
        
        try:
            response = self.session.get(f"{BASE_URL}/conversations/sessions")
            if response.status_code == 200:
                sessions = response.json()
                print("   ✅ 获取会话列表成功")
                print(f"   会话数量: {len(sessions)}")
                
                for i, session in enumerate(sessions, 1):
                    print(f"   会话{i}: {session['session_name']} ({session['message_count']}条消息)")
                
                return True
            else:
                print(f"   ❌ 获取会话列表失败: {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ 获取会话列表异常: {e}")
            return False
    
    def test_update_session(self):
        """测试更新会话"""
        print("\n6. 测试更新会话...")
        
        update_data = {
            "session_name": f"更新后的会话_{int(time.time())}",
            "session_metadata": {
                "description": "这是更新后的测试会话",
                "tags": ["测试", "对话", "更新"],
                "updated_at": datetime.now().isoformat()
            }
        }
        
        try:
            response = self.session.put(f"{BASE_URL}/conversations/sessions/{self.test_session_id}", json=update_data)
            if response.status_code == 200:
                updated_session = response.json()
                print("   ✅ 会话更新成功")
                print(f"   新名称: {updated_session['session_name']}")
                return True
            else:
                print(f"   ❌ 会话更新失败: {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ 会话更新异常: {e}")
            return False
    
    def test_pagination(self):
        """测试分页功能"""
        print("\n7. 测试分页功能...")
        
        # 测试消息分页
        try:
            response = self.session.get(f"{BASE_URL}/conversations/sessions/{self.test_session_id}/messages?limit=2&offset=0")
            if response.status_code == 200:
                messages = response.json()
                print("   ✅ 消息分页测试成功")
                print(f"   返回消息数量: {len(messages)}")
                return True
            else:
                print(f"   ❌ 消息分页测试失败: {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ 消息分页测试异常: {e}")
            return False
    
    def test_error_handling(self):
        """测试错误处理"""
        print("\n8. 测试错误处理...")
        
        # 测试无效的会话ID
        try:
            response = self.session.get(f"{BASE_URL}/conversations/sessions/invalid-uuid")
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
            response = self.session.post(
                f"{BASE_URL}/conversations/sessions/{self.test_session_id}/messages", 
                json=invalid_message
            )
            if response.status_code == 422:
                print("   ✅ 无效消息类型错误处理正确")
            else:
                print(f"   ❌ 无效消息类型错误处理失败: {response.status_code}")
        except Exception as e:
            print(f"   ❌ 无效消息类型测试异常: {e}")
        
        # 测试未认证访问
        try:
            response = requests.get(f"{BASE_URL}/conversations/sessions")
            if response.status_code == 401:
                print("   ✅ 未认证访问错误处理正确")
            else:
                print(f"   ❌ 未认证访问错误处理失败: {response.status_code}")
        except Exception as e:
            print(f"   ❌ 未认证访问测试异常: {e}")
        
        return True
    
    def test_session_types(self):
        """测试不同会话类型"""
        print("\n9. 测试不同会话类型...")
        
        session_types = [
            {"name": "文档编辑会话", "type": "document_edit"},
            {"name": "工具使用会话", "type": "tool_usage"},
            {"name": "一般咨询会话", "type": "general"}
        ]
        
        created_sessions = []
        for session_info in session_types:
            session_data = {
                "session_name": f"{session_info['name']}_{int(time.time())}",
                "session_type": session_info["type"],
                "session_metadata": {
                    "description": f"这是一个{session_info['name']}",
                    "tags": [session_info["type"], "测试"]
                }
            }
            
            try:
                response = self.session.post(f"{BASE_URL}/conversations/sessions", json=session_data)
                if response.status_code == 200:
                    session = response.json()
                    created_sessions.append(session['id'])
                    print(f"   ✅ {session_info['name']}创建成功")
                else:
                    print(f"   ❌ {session_info['name']}创建失败: {response.text}")
            except Exception as e:
                print(f"   ❌ {session_info['name']}创建异常: {e}")
        
        # 测试按类型过滤
        try:
            response = self.session.get(f"{BASE_URL}/conversations/sessions?session_type=general")
            if response.status_code == 200:
                sessions = response.json()
                print(f"   ✅ 按类型过滤成功，找到{len(sessions)}个general类型会话")
            else:
                print(f"   ❌ 按类型过滤失败: {response.text}")
        except Exception as e:
            print(f"   ❌ 按类型过滤异常: {e}")
        
        return len(created_sessions) > 0
    
    def test_message_search(self):
        """测试消息搜索功能（模拟）"""
        print("\n10. 测试消息搜索功能...")
        
        # 获取所有消息
        try:
            response = self.session.get(f"{BASE_URL}/conversations/sessions/{self.test_session_id}/messages")
            if response.status_code == 200:
                messages = response.json()
                
                # 模拟搜索包含"申请"的消息
                search_results = [msg for msg in messages if "申请" in msg['content']]
                print(f"   ✅ 消息搜索模拟成功，找到{len(search_results)}条包含'申请'的消息")
                
                for i, msg in enumerate(search_results, 1):
                    print(f"   搜索结果{i}: [{msg['message_type']}] {msg['content'][:30]}...")
                
                return True
            else:
                print(f"   ❌ 消息搜索失败: {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ 消息搜索异常: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 对话日志API综合测试")
        print(f"服务器地址: {BASE_URL}")
        
        tests = [
            self.test_login,
            self.test_create_session,
            self.test_add_messages,
            self.test_get_session_details,
            self.test_list_sessions,
            self.test_update_session,
            self.test_pagination,
            self.test_error_handling,
            self.test_session_types,
            self.test_message_search
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    print(f"   ❌ 测试失败: {test.__name__}")
            except Exception as e:
                print(f"   ❌ 测试异常: {test.__name__} - {e}")
        
        print(f"\n📊 测试结果: {passed}/{total} 通过")
        
        if passed == total:
            print("🎉 所有测试通过！")
            return True
        else:
            print("❌ 部分测试失败")
            return False

def main():
    """主函数"""
    print("=== 对话日志API综合测试 ===")
    tester = ConversationTester()
    success = tester.run_all_tests()
    if success:
        print("\n✅ 所有测试通过")
    else:
        print("\n❌ 部分测试失败")
    print("=== 测试完成 ===")

if __name__ == "__main__":
    main() 