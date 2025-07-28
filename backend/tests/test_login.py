#!/usr/bin/env python3
"""
登录功能测试脚本
"""
import requests
import json
import time
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/auth/login"
REGISTER_URL = f"{BASE_URL}/auth/register"
REFRESH_URL = f"{BASE_URL}/auth/refresh"
HEALTH_URL = f"{BASE_URL}/health"
AUTHZ_URL = f"{BASE_URL}/authz"

class LoginTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.refresh_token = None
    
    def test_health_check(self):
        """测试健康检查"""
        print("=== 测试健康检查 ===")
        try:
            response = self.session.get(HEALTH_URL)
            print(f"健康检查状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"健康检查响应: {data}")
                return True
            else:
                print(f"健康检查失败: {response.text}")
                return False
        except Exception as e:
            print(f"健康检查异常: {e}")
            return False
    
    def test_register(self, username="testuser", email="testuser@example.com", password="testpassword", role="guest"):
        """测试用户注册"""
        print(f"\n=== 测试用户注册 ===")
        print(f"用户名: {username}")
        print(f"邮箱: {email}")
        print(f"角色: {role}")
        
        register_data = {
            "username": username,
            "email": email,
            "password": password,
            "role": role
        }
        
        try:
            response = self.session.post(REGISTER_URL, json=register_data)
            print(f"注册状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"注册成功: {data}")
                return True
            else:
                print(f"注册失败: {response.text}")
                return False
        except Exception as e:
            print(f"注册异常: {e}")
            return False
    
    def test_login(self, username="testuser@example.com", password="testpassword"):
        """测试用户登录"""
        print(f"\n=== 测试用户登录 ===")
        print(f"用户名/邮箱: {username}")
        
        login_data = {
            "username": username,
            "password": password
        }
        
        try:
            response = self.session.post(LOGIN_URL, data=login_data)
            print(f"登录状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"登录成功: {data}")
                
                # 保存token
                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                
                # 检查cookie
                cookies = response.cookies
                print(f"Cookies: {dict(cookies)}")
                
                return True
            else:
                print(f"登录失败: {response.text}")
                return False
        except Exception as e:
            print(f"登录异常: {e}")
            return False
    
    def test_login_with_wrong_password(self):
        """测试错误密码登录"""
        print(f"\n=== 测试错误密码登录 ===")
        
        login_data = {
            "username": "testuser@example.com",
            "password": "wrongpassword"
        }
        
        try:
            response = self.session.post(LOGIN_URL, data=login_data)
            print(f"错误密码登录状态码: {response.status_code}")
            
            if response.status_code == 401:
                print("错误密码登录被正确拒绝")
                return True
            else:
                print(f"错误密码登录响应: {response.text}")
                return False
        except Exception as e:
            print(f"错误密码登录异常: {e}")
            return False
    
    def test_login_with_nonexistent_user(self):
        """测试不存在的用户登录"""
        print(f"\n=== 测试不存在用户登录 ===")
        
        login_data = {
            "username": "nonexistent@example.com",
            "password": "testpassword"
        }
        
        try:
            response = self.session.post(LOGIN_URL, data=login_data)
            print(f"不存在用户登录状态码: {response.status_code}")
            
            if response.status_code == 401:
                print("不存在用户登录被正确拒绝")
                return True
            else:
                print(f"不存在用户登录响应: {response.text}")
                return False
        except Exception as e:
            print(f"不存在用户登录异常: {e}")
            return False
    
    def test_refresh_token(self):
        """测试刷新token"""
        print(f"\n=== 测试刷新Token ===")
        
        if not self.refresh_token:
            print("没有refresh token，跳过测试")
            return False
        
        try:
            response = self.session.post(REFRESH_URL, json={"refresh_token": self.refresh_token})
            print(f"刷新token状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"刷新token成功: {data}")
                
                # 更新token
                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                
                return True
            else:
                print(f"刷新token失败: {response.text}")
                return False
        except Exception as e:
            print(f"刷新token异常: {e}")
            return False
    
    def test_authz_with_cookie(self):
        """测试使用cookie的权限检查"""
        print(f"\n=== 测试Cookie权限检查 ===")
        
        authz_data = {
            "tool": "tool_basic"
        }
        
        try:
            response = self.session.post(AUTHZ_URL, json=authz_data)
            print(f"权限检查状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"权限检查成功: {data}")
                return True
            else:
                print(f"权限检查失败: {response.text}")
                return False
        except Exception as e:
            print(f"权限检查异常: {e}")
            return False
    
    def test_authz_without_cookie(self):
        """测试不使用cookie的权限检查"""
        print(f"\n=== 测试无Cookie权限检查 ===")
        
        # 创建新的session，不包含cookie
        new_session = requests.Session()
        
        authz_data = {
            "tool": "tool_basic"
        }
        
        try:
            response = new_session.post(AUTHZ_URL, json=authz_data)
            print(f"无Cookie权限检查状态码: {response.status_code}")
            
            if response.status_code == 401:
                print("无Cookie权限检查被正确拒绝")
                return True
            else:
                print(f"无Cookie权限检查响应: {response.text}")
                return False
        except Exception as e:
            print(f"无Cookie权限检查异常: {e}")
            return False
    
    def test_duplicate_register(self):
        """测试重复注册"""
        print(f"\n=== 测试重复注册 ===")
        
        register_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword",
            "role": "guest"
        }
        
        try:
            response = self.session.post(REGISTER_URL, json=register_data)
            print(f"重复注册状态码: {response.status_code}")
            
            if response.status_code == 400:
                print("重复注册被正确拒绝")
                return True
            else:
                print(f"重复注册响应: {response.text}")
                return False
        except Exception as e:
            print(f"重复注册异常: {e}")
            return False
    
    def test_different_email_register(self):
        """测试不同邮箱注册"""
        print(f"\n=== 测试不同邮箱注册 ===")
        
        register_data = {
            "username": "testuser2",
            "email": "testuser2@example.com",
            "password": "testpassword",
            "role": "guest"
        }
        
        try:
            response = self.session.post(REGISTER_URL, json=register_data)
            print(f"不同邮箱注册状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"不同邮箱注册成功: {data}")
                return True
            else:
                print(f"不同邮箱注册失败: {response.text}")
                return False
        except Exception as e:
            print(f"不同邮箱注册异常: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始登录功能测试")
        print(f"测试时间: {datetime.now()}")
        print(f"服务器地址: {BASE_URL}")
        
        test_results = []
        
        # 1. 健康检查
        test_results.append(("健康检查", self.test_health_check()))
        
        # 2. 注册测试
        test_results.append(("用户注册", self.test_register()))
        
        # 3. 登录测试
        test_results.append(("用户登录", self.test_login()))
        
        # 4. 错误密码测试
        test_results.append(("错误密码登录", self.test_login_with_wrong_password()))
        
        # 5. 不存在用户测试
        test_results.append(("不存在用户登录", self.test_login_with_nonexistent_user()))
        
        # 6. 重复注册测试
        test_results.append(("重复注册", self.test_duplicate_register()))
        
        # 7. 不同邮箱注册测试
        test_results.append(("不同邮箱注册", self.test_different_email_register()))
        
        # 8. 权限检查测试（需要先登录）
        if self.access_token:
            test_results.append(("Cookie权限检查", self.test_authz_with_cookie()))
            test_results.append(("无Cookie权限检查", self.test_authz_without_cookie()))
        
        # 9. 刷新token测试
        if self.refresh_token:
            test_results.append(("刷新Token", self.test_refresh_token()))
        
        # 输出测试结果
        print(f"\n{'='*50}")
        print("📊 测试结果汇总")
        print(f"{'='*50}")
        
        passed = 0
        total = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ 通过" if result else "❌ 失败"
            print(f"{test_name}: {status}")
            if result:
                passed += 1
        
        print(f"\n总计: {passed}/{total} 测试通过")
        success_rate = (passed / total) * 100 if total > 0 else 0
        print(f"成功率: {success_rate:.1f}%")
        
        if passed == total:
            print("🎉 所有测试通过！")
        else:
            print("⚠️  部分测试失败，请检查服务器状态")
        
        return passed == total

def main():
    """主函数"""
    tester = LoginTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ 登录功能测试完成，所有功能正常")
    else:
        print("\n❌ 登录功能测试完成，存在问题需要修复")
    
    return success

if __name__ == "__main__":
    main() 