#!/usr/bin/env python3
"""
数据库初始化脚本
"""
import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

def init_database():
    """初始化数据库"""
    # 数据库配置
    DB_CONFIG = {
        'host': '127.0.0.1',
        'port': 5400,
        'user': 'postgres',
        'password': '010921',
        'database': 'aiagent'
    }
    
    try:
        # 连接到数据库
        print("连接到数据库...")
        conn = psycopg2.connect(**DB_CONFIG)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('resume_documents', 'letter_documents', 'sop_documents')
        """)
        
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        if existing_tables:
            print(f"发现现有表: {existing_tables}")
            response = input("是否要重新创建表？这将删除现有数据 (y/N): ")
            if response.lower() != 'y':
                print("取消操作")
                return
        
        # 读取SQL文件
        sql_file_path = os.path.join(project_root, 'config', 'sql', 'documents_new_structure.sql')
        
        if not os.path.exists(sql_file_path):
            print(f"SQL文件不存在: {sql_file_path}")
            return
        
        print("读取SQL文件...")
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 执行SQL
        print("执行SQL语句...")
        cursor.execute(sql_content)
        
        print("数据库初始化完成！")
        
        # 验证表是否创建成功
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE '%_documents%'
            ORDER BY table_name
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        print(f"创建的表: {tables}")
        
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("=== 数据库初始化 ===")
    init_database()
    print("=== 初始化完成 ===") 