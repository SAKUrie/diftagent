#!/usr/bin/env python3
"""
快速登录测试脚本
"""
import requests
import json

# 配置
BASE_URL = "http://localhost:8000"

def test_quick_login():
    """快速登录测试"""
    print("🚀 快速登录测试")
    print(f"服务器地址: {BASE_URL}")
    
    # 1. 健康检查
    print("\n1. 测试健康检查...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ 健康检查通过")
        else:
            print(f"   ❌ 健康检查失败: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 健康检查异常: {e}")
        return False
    
    # 2. 注册用户
    print("\n2. 测试用户注册...")
    register_data = {
        "username": "quicktest",
        "email": "quicktest@example.com",
        "password": "123456",
        "role": "guest"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ 注册成功")
        elif response.status_code == 400 and "already registered" in response.text:
            print("   ⚠️  用户已存在，继续测试")
        else:
            print(f"   ❌ 注册失败: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 注册异常: {e}")
        return False
    
    # 3. 用户登录
    print("\n3. 测试用户登录...")
    login_data = {
        "username": "quicktest@example.com",
        "password": "123456"
    }
    
    session = requests.Session()
    try:
        response = session.post(f"{BASE_URL}/auth/login", data=login_data)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("   ✅ 登录成功")
            print(f"   Access Token: {data.get('access_token', '')[:20]}...")
            print(f"   Refresh Token: {data.get('refresh_token', '')[:20]}...")
            
            # 检查cookie
            cookies = response.cookies
            if cookies:
                print(f"   Cookies: {dict(cookies)}")
            
            return True
        else:
            print(f"   ❌ 登录失败: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 登录异常: {e}")
        return False

def test_login_with_credentials(username, password):
    """使用指定凭据测试登录"""
    print(f"\n🔐 使用凭据测试登录")
    print(f"用户名: {username}")
    
    login_data = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 登录成功")
            print(f"Access Token: {data.get('access_token', '')[:20]}...")
            print(f"Refresh Token: {data.get('refresh_token', '')[:20]}...")
            
            # 检查cookie
            cookies = response.cookies
            if cookies:
                print(f"Cookies: {dict(cookies)}")
            
            return True
        else:
            print(f"❌ 登录失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return False

def main():
    """主函数"""
    import sys
    
    if len(sys.argv) > 2:
        # 使用命令行参数进行登录测试
        username = sys.argv[1]
        password = sys.argv[2]
        test_login_with_credentials(username, password)
    else:
        # 运行完整的快速测试
        success = test_quick_login()
        
        if success:
            print("\n✅ 快速登录测试完成，登录功能正常")
        else:
            print("\n❌ 快速登录测试失败，请检查服务器状态")

if __name__ == "__main__":
    main() 