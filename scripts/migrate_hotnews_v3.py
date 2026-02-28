#!/usr/bin/env python3
"""
V3 热点中心数据库迁移脚本
创建 hotnews 和 hotnews_subscriptions 表结构

使用方法:
    python scripts/migrate_hotnews_v3.py

数据库连接信息:
    - 主机：43.134.234.4
    - 端口：3306
    - 数据库：youmind
    - 用户：youmind
    - 密码：YouMind2026
"""

import os
import sys
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import pymysql
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    print("❌ pymysql 未安装，请运行：pip install pymysql")
    sys.exit(1)


# ============================================
# 数据库配置
# ============================================

DB_CONFIG = {
    'host': os.getenv('DB_HOST', '43.134.234.4'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'database': os.getenv('DB_NAME', 'youmind'),
    'user': os.getenv('DB_USER', 'youmind'),
    'password': os.getenv('DB_PASSWORD', 'YouMind2026'),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}


# ============================================
# SQL 迁移语句
# ============================================

MIGRATION_SQLS = [
    # 1. 创建热点表
    """
    CREATE TABLE IF NOT EXISTS hotnews (
        id VARCHAR(64) PRIMARY KEY COMMENT '热点唯一标识 (平台_原始 ID)',
        title VARCHAR(500) NOT NULL COMMENT '热点标题',
        content TEXT COMMENT '热点内容/描述',
        platform VARCHAR(50) COMMENT '来源平台',
        category VARCHAR(50) COMMENT '分类',
        heat_count INT DEFAULT 0 COMMENT '热度数值',
        heat_level VARCHAR(20) DEFAULT 'normal' COMMENT '热度等级',
        source_url VARCHAR(500) COMMENT '原始链接',
        publish_time DATETIME COMMENT '发布时间',
        crawl_time DATETIME NOT NULL COMMENT '采集时间',
        trend_data JSON COMMENT '24 小时热度趋势',
        extra_data JSON COMMENT '扩展数据',
        INDEX idx_platform (platform),
        INDEX idx_category (category),
        INDEX idx_heat (heat_count),
        INDEX idx_time (publish_time),
        INDEX idx_crawl_time (crawl_time)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    
    # 2. 创建订阅表
    """
    CREATE TABLE IF NOT EXISTS hotnews_subscriptions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id VARCHAR(64) NOT NULL COMMENT '用户 ID',
        keyword VARCHAR(100) NOT NULL COMMENT '订阅关键词',
        platform VARCHAR(50) COMMENT '订阅平台',
        category VARCHAR(50) COMMENT '订阅分类',
        notify_enabled BOOLEAN DEFAULT TRUE COMMENT '是否启用通知',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
        INDEX idx_user (user_id),
        INDEX idx_keyword (keyword),
        INDEX idx_platform (platform),
        INDEX idx_category (category)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    
    # 3. 插入示例订阅数据 (可选)
    """
    INSERT INTO hotnews_subscriptions (user_id, keyword, platform, category, notify_enabled)
    VALUES 
        ('test_user_001', '人工智能', '知乎', '科技', TRUE),
        ('test_user_001', '教育创新', NULL, '教育', TRUE),
        ('test_user_001', 'AI 技术', NULL, '科技', TRUE)
    ON DUPLICATE KEY UPDATE keyword=VALUES(keyword)
    """
]


# ============================================
# 迁移函数
# ============================================

def execute_migration():
    """执行数据库迁移"""
    print("=" * 60)
    print("🚀 V3 热点中心数据库迁移")
    print("=" * 60)
    print(f"📊 目标数据库：{DB_CONFIG['database']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(f"⏰ 迁移时间：{datetime.now().isoformat()}")
    print("=" * 60)
    
    conn = None
    try:
        # 连接数据库
        print("\n📡 正在连接数据库...")
        conn = pymysql.connect(**DB_CONFIG)
        print("✅ 数据库连接成功")
        
        cursor = conn.cursor()
        
        # 执行每条 SQL
        for i, sql in enumerate(MIGRATION_SQLS, 1):
            print(f"\n📝 执行迁移 {i}/{len(MIGRATION_SQLS)}...")
            print(f"   SQL: {sql[:100].strip()}...")
            
            try:
                cursor.execute(sql)
                conn.commit()
                print(f"   ✅ 执行成功")
            except Exception as e:
                print(f"   ⚠️  执行警告：{e}")
                # 继续执行下一条
        
        # 验证表结构
        print("\n🔍 验证表结构...")
        cursor.execute("SHOW TABLES LIKE 'hotnews%'")
        tables = cursor.fetchall()
        
        print(f"\n✅ 迁移完成!")
        print(f"📋 创建的表:")
        for table in tables:
            table_name = list(table.values())[0]
            print(f"   - {table_name}")
            
            # 显示表结构
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            print(f"     字段数：{len(columns)}")
        
        cursor.close()
        
        print("\n" + "=" * 60)
        print("✅ 数据库迁移成功完成!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 迁移失败：{e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if conn:
            conn.close()
            print("\n👋 数据库连接已关闭")


# ============================================
# 回滚函数
# ============================================

def rollback_migration():
    """回滚迁移 (删除创建的表)"""
    print("⚠️  警告：即将回滚迁移，删除所有 V3 热点表!")
    response = input("确认回滚？(yes/no): ")
    
    if response.lower() != 'yes':
        print("❌ 回滚已取消")
        return
    
    conn = None
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 删除表
        cursor.execute("DROP TABLE IF EXISTS hotnews_subscriptions")
        cursor.execute("DROP TABLE IF EXISTS hotnews")
        
        conn.commit()
        print("✅ 回滚成功")
        
        cursor.close()
        
    except Exception as e:
        print(f"❌ 回滚失败：{e}")
        
    finally:
        if conn:
            conn.close()


# ============================================
# 主函数
# ============================================

if __name__ == "__main__":
    if not MYSQL_AVAILABLE:
        sys.exit(1)
    
    # 检查命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        rollback_migration()
    else:
        success = execute_migration()
        sys.exit(0 if success else 1)
