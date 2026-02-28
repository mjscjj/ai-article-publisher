#!/usr/bin/env python3
"""
V3 智能选题模块数据库迁移脚本
创建表结构并初始化预置数据

执行方式:
    python scripts/migrate_topics_v3.py

依赖:
    - pymysql
    - 数据库连接配置 (同热点模块)
"""

import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.topic import CREATE_TABLE_SQL


def migrate():
    """执行数据库迁移"""
    print("\n" + "="*70)
    print("🗄️  V3 智能选题模块数据库迁移")
    print("="*70 + "\n")
    
    # 导入数据库连接
    try:
        from core.hot_database_mysql import HotNewsDatabaseMySQL
        print("✅ 加载数据库模块成功")
    except ImportError as e:
        print(f"❌ 数据库模块加载失败：{e}")
        print("\n请确保已安装 pymysql:")
        print("  pip install pymysql")
        return False
    
    # 连接数据库
    try:
        db = HotNewsDatabaseMySQL()
        print("✅ 数据库连接成功")
    except Exception as e:
        print(f"❌ 数据库连接失败：{e}")
        return False
    
    # 执行建表 SQL
    print("\n" + "-"*70)
    print("执行建表语句...")
    print("-"*70)
    
    try:
        # 分割 SQL 语句
        statements = [s.strip() for s in CREATE_TABLE_SQL.split(';') if s.strip()]
        
        for i, stmt in enumerate(statements, 1):
            if not stmt:
                continue
            
            # 执行语句 (不需要参数的 SQL)
            try:
                cursor = db.conn.cursor()
                cursor.execute(stmt)
                db.conn.commit()
                cursor.close()
                print(f"  [{i}/{len(statements)}] ✅ 执行成功")
            except Exception as e:
                error_str = str(e).lower()
                # 忽略"表已存在"错误
                if "already exists" in error_str or "duplicate" in error_str:
                    print(f"  [{i}/{len(statements)}] ⚠️  表已存在，跳过")
                else:
                    print(f"  [{i}/{len(statements)}] ❌ 执行失败：{e}")
                    raise
        
        print("\n✅ 建表完成")
    
    except Exception as e:
        print(f"\n❌ 建表过程出错：{e}")
        return False
    
    # 验证表结构
    print("\n" + "-"*70)
    print("验证表结构...")
    print("-"*70)
    
    try:
        tables = ['topics', 'topic_scores', 'topic_industries', 'topic_angles']
        
        for table in tables:
            rows = db._fetch_all(f"SHOW TABLES LIKE '{table}'")
            if rows:
                print(f"  ✅ {table} 表存在")
            else:
                print(f"  ❌ {table} 表不存在")
                return False
        
        # 检查预置数据
        print("\n检查预置数据...")
        
        # 检查行业数据
        rows = db._fetch_all("SELECT COUNT(*) as cnt FROM topic_industries")
        industry_count = rows[0]['cnt'] if rows else 0
        print(f"  行业数据：{industry_count} 条")
        
        # 检查角度数据
        rows = db._fetch_all("SELECT COUNT(*) as cnt FROM topic_angles")
        angle_count = rows[0]['cnt'] if rows else 0
        print(f"  角度数据：{angle_count} 条")
        
        if industry_count == 0 or angle_count == 0:
            print("\n⚠️  预置数据为空，需要手动插入")
        
        print("\n✅ 验证完成")
    
    except Exception as e:
        print(f"\n❌ 验证过程出错：{e}")
        return False
    
    # 显示表结构
    print("\n" + "-"*70)
    print("表结构详情:")
    print("-"*70)
    
    try:
        for table in tables:
            print(f"\n📋 {table}:")
            rows = db._fetch_all(f"DESCRIBE {table}")
            for row in rows:
                field = row['Field']
                field_type = row['Type']
                nullable = 'NULL' if row['Null'] == 'YES' else 'NOT NULL'
                key = row['Key']
                default = row['Default']
                
                key_mark = "🔑" if key else "  "
                print(f"  {key_mark} {field:25} {field_type:20} {nullable:10} DEFAULT {default}")
    
    except Exception as e:
        print(f"❌ 显示表结构失败：{e}")
    
    print("\n" + "="*70)
    print("🎉 数据库迁移完成!")
    print("="*70 + "\n")
    
    return True


def rollback():
    """回滚迁移 (删除所有表)"""
    print("\n" + "="*70)
    print("⚠️  回滚数据库迁移")
    print("="*70 + "\n")
    
    confirm = input("确认删除所有选题相关表？(yes/no): ")
    if confirm.lower() != 'yes':
        print("取消回滚")
        return
    
    try:
        from core.hot_database_mysql import HotNewsDatabaseMySQL
        db = HotNewsDatabaseMySQL()
    except Exception as e:
        print(f"❌ 数据库连接失败：{e}")
        return
    
    tables = ['topic_scores', 'topics', 'topic_angles', 'topic_industries']
    
    for table in tables:
        try:
            db._execute(f"DROP TABLE IF EXISTS {table}")
            print(f"  ✅ 删除 {table} 表")
        except Exception as e:
            print(f"  ❌ 删除 {table} 失败：{e}")
    
    print("\n✅ 回滚完成")


def show_data():
    """显示当前数据"""
    print("\n" + "="*70)
    print("📊 查看当前数据")
    print("="*70 + "\n")
    
    try:
        from core.hot_database_mysql import HotNewsDatabaseMySQL
        db = HotNewsDatabaseMySQL()
    except Exception as e:
        print(f"❌ 数据库连接失败：{e}")
        return
    
    # 显示行业
    print("📋 行业列表:")
    rows = db._fetch_all("SELECT * FROM topic_industries ORDER BY id")
    for row in rows:
        print(f"  {row['id']}. {row['name']} ({row['code']}) - {'启用' if row['enabled'] else '禁用'}")
    
    # 显示角度
    print("\n📋 角度列表:")
    rows = db._fetch_all("SELECT * FROM topic_angles ORDER BY id")
    for row in rows:
        icon = row.get('icon', '') or ''
        print(f"  {row['id']}. {icon} {row['name']} ({row['code']})")
    
    # 显示选题统计
    print("\n📋 选题统计:")
    rows = db._fetch_all("SELECT COUNT(*) as cnt FROM topics")
    total = rows[0]['cnt'] if rows else 0
    print(f"  总选题数：{total}")
    
    rows = db._fetch_all("SELECT grade, COUNT(*) as cnt FROM topic_scores GROUP BY grade")
    if rows:
        print("  评分分布:")
        for row in rows:
            print(f"    {row['grade']}级：{row['cnt']}个")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="V3 智能选题模块数据库迁移工具")
    parser.add_argument(
        "action",
        choices=["migrate", "rollback", "show"],
        default="migrate",
        help="操作类型：migrate(迁移), rollback(回滚), show(显示数据)"
    )
    
    args = parser.parse_args()
    
    if args.action == "migrate":
        success = migrate()
        sys.exit(0 if success else 1)
    elif args.action == "rollback":
        rollback()
    elif args.action == "show":
        show_data()
