#!/usr/bin/env python3
"""
文档API测试脚本
"""
import requests
import json
import time

# 配置
BASE_URL = "http://localhost:8000"

def test_document_api():
    """测试文档API功能"""
    print("🚀 文档API测试")
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
    
    # 2. 测试文档上传
    print("\n2. 测试文档上传...")
    
    # 上传简历
    resume_data = {
        "doc_type": "resume",
        "title": "我的简历",
        "content": "这是我的简历内容，包含我的教育背景和工作经验。",
        "content_format": "markdown"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/documents/upload", data=resume_data, cookies=cookies)
        if response.status_code == 200:
            resume_doc = response.json()
            resume_id = resume_doc['id']
            print("   ✅ 简历上传成功")
            print(f"   文档ID: {resume_id}")
        else:
            print(f"   ❌ 简历上传失败: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 简历上传异常: {e}")
        return False
    
    # 上传推荐信
    letter_data = {
        "doc_type": "letter",
        "title": "我的推荐信",
        "content": "这是我的推荐信内容，由我的导师撰写。",
        "content_format": "markdown"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/documents/upload", data=letter_data, cookies=cookies)
        if response.status_code == 200:
            letter_doc = response.json()
            letter_id = letter_doc['id']
            print("   ✅ 推荐信上传成功")
            print(f"   文档ID: {letter_id}")
        else:
            print(f"   ❌ 推荐信上传失败: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 推荐信上传异常: {e}")
        return False
    
    # 3. 测试获取文档详情
    print("\n3. 测试获取文档详情...")
    
    try:
        response = requests.get(f"{BASE_URL}/documents/resume/{resume_id}", cookies=cookies)
        if response.status_code == 200:
            doc_detail = response.json()
            print("   ✅ 获取文档详情成功")
            print(f"   标题: {doc_detail['title']}")
            print(f"   版本数: {len(doc_detail['versions'])}")
        else:
            print(f"   ❌ 获取文档详情失败: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 获取文档详情异常: {e}")
        return False
    
    # 4. 测试添加新版本
    print("\n4. 测试添加新版本...")
    
    version_data = {
        "content": "这是更新后的简历内容，添加了最新的工作经验。",
        "content_format": "markdown"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/documents/resume/{resume_id}/versions", data=version_data, cookies=cookies)
        if response.status_code == 200:
            print("   ✅ 添加新版本成功")
        else:
            print(f"   ❌ 添加新版本失败: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 添加新版本异常: {e}")
        return False
    
    # 5. 测试获取版本历史
    print("\n5. 测试获取版本历史...")
    
    try:
        response = requests.get(f"{BASE_URL}/documents/resume/{resume_id}/versions", cookies=cookies)
        if response.status_code == 200:
            versions = response.json()
            print("   ✅ 获取版本历史成功")
            print(f"   版本数量: {len(versions)}")
            for version in versions:
                print(f"   版本 {version['version_number']}: {version['content'][:20]}...")
        else:
            print(f"   ❌ 获取版本历史失败: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 获取版本历史异常: {e}")
        return False
    
    # 6. 测试版本回退
    print("\n6. 测试版本回退...")
    
    revert_data = {
        "version_number": 1
    }
    
    try:
        response = requests.post(f"{BASE_URL}/documents/resume/{resume_id}/revert", json=revert_data, cookies=cookies)
        if response.status_code == 200:
            print("   ✅ 版本回退成功")
        else:
            print(f"   ❌ 版本回退失败: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 版本回退异常: {e}")
        return False
    
    # 7. 测试获取指定版本
    print("\n7. 测试获取指定版本...")
    
    try:
        response = requests.get(f"{BASE_URL}/documents/resume/{resume_id}/versions/2", cookies=cookies)
        if response.status_code == 200:
            version_detail = response.json()
            print("   ✅ 获取指定版本成功")
            print(f"   版本号: {version_detail['version_number']}")
            print(f"   内容: {version_detail['content'][:30]}...")
        else:
            print(f"   ❌ 获取指定版本失败: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 获取指定版本异常: {e}")
        return False
    
    # 8. 测试获取用户所有文档
    print("\n8. 测试获取用户所有文档...")
    
    try:
        response = requests.get(f"{BASE_URL}/documents/resume", cookies=cookies)
        if response.status_code == 200:
            documents = response.json()
            print("   ✅ 获取用户文档列表成功")
            print(f"   文档数量: {len(documents)}")
            for doc in documents:
                print(f"   - {doc['title']} ({doc['type']})")
        else:
            print(f"   ❌ 获取用户文档列表失败: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 获取用户文档列表异常: {e}")
        return False
    
    # 9. 测试错误情况
    print("\n9. 测试错误情况...")
    
    # 测试无效文档类型
    try:
        response = requests.post(f"{BASE_URL}/documents/upload", data={
            "doc_type": "invalid",
            "title": "测试",
            "content": "内容",
            "content_format": "markdown"
        }, cookies=cookies)
        if response.status_code == 400:
            print("   ✅ 无效文档类型错误处理正确")
        else:
            print(f"   ❌ 无效文档类型错误处理失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 无效文档类型测试异常: {e}")
    
    # 测试访问不存在的文档
    try:
        response = requests.get(f"{BASE_URL}/documents/resume/nonexistent-id", cookies=cookies)
        if response.status_code == 404:
            print("   ✅ 不存在文档错误处理正确")
        else:
            print(f"   ❌ 不存在文档错误处理失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 不存在文档测试异常: {e}")
    
    # 测试未认证访问
    try:
        response = requests.post(f"{BASE_URL}/documents/upload", data={
            "doc_type": "resume",
            "title": "测试",
            "content": "内容",
            "content_format": "markdown"
        })
        if response.status_code == 401:
            print("   ✅ 未认证访问错误处理正确")
        else:
            print(f"   ❌ 未认证访问错误处理失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 未认证访问测试异常: {e}")
    
    return True

def main():
    """主函数"""
    success = test_document_api()
    
    if success:
        print("\n✅ 文档API测试完成，所有功能正常")
    else:
        print("\n❌ 文档API测试失败，请检查服务器状态")

if __name__ == "__main__":
    main() 