#!/usr/bin/env python3
"""
评价系统数据库迁移脚本
创建 evaluations 表用于存储评价记录
"""

import os
import sys
import pymysql

# 数据库配置
DB_CONFIG = {
    'host': os.getenv('DB_HOST', '43.134.234.4'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'database': os.getenv('DB_NAME', 'youmind'),
    'user': os.getenv('DB_USER', 'youmind'),
    'password': os.getenv('DB_PASSWORD', 'YouMind2026'),
    'charset': 'utf8mb4'
}


def create_evaluations_table():
    """创建评价记录表"""
    conn = None
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 创建评价表
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS evaluations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            target_type VARCHAR(50) NOT NULL COMMENT '目标类型 (article|topic)',
            target_id VARCHAR(64) COMMENT '目标 ID',
            target_title VARCHAR(500) COMMENT '目标标题',
            model_used VARCHAR(50) COMMENT '使用的模型',
            total_score FLOAT COMMENT '总分',
            grade VARCHAR(10) COMMENT '等级 (S/A/B/C/D)',
            content_score FLOAT COMMENT '内容分',
            structure_score FLOAT COMMENT '结构分',
            expression_score FLOAT COMMENT '表达分',
            viral_score FLOAT COMMENT '传播分',
            innovation_score FLOAT COMMENT '创新分',
            heat_score FLOAT COMMENT '热度分 (选题)',
            potential_score FLOAT COMMENT '潜力分 (选题)',
            match_score FLOAT COMMENT '匹配分 (选题)',
            novelty_score FLOAT COMMENT '新颖分 (选题)',
            feasibility_score FLOAT COMMENT '可行分 (选题)',
            strengths JSON COMMENT '优点列表',
            improvements JSON COMMENT '改进建议',
            recommendation VARCHAR(100) COMMENT '推荐操作',
            comment TEXT COMMENT '总体评价',
            raw_result JSON COMMENT '原始评价结果',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_target (target_type, target_id),
            INDEX idx_score (total_score),
            INDEX idx_grade (grade),
            INDEX idx_created (created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
        COMMENT='工作评价记录表';
        """
        
        cursor.execute(create_table_sql)
        conn.commit()
        
        print("✅ evaluations 表创建成功")
        
        # 显示表结构
        cursor.execute("DESCRIBE evaluations")
        columns = cursor.fetchall()
        
        print(f"\n📋 表结构 ({len(columns)} 个字段):")
        print("-" * 60)
        for col in columns:
            print(f"  {col[0]:<25} {col[1]:<20} {col[2]:<10}")
        
        # 测试插入
        test_insert_sql = """
        INSERT INTO evaluations (
            target_type, target_title, model_used, total_score, grade,
            content_score, structure_score, expression_score, viral_score, innovation_score,
            strengths, improvements, recommendation, comment
        ) VALUES (
            'article', '测试文章', 'deepseek-chat-v3', 85.5, 'A',
            88, 85, 82, 87, 84,
            '["内容充实", "结构清晰"]', '["增加数据支撑", "优化开头"]',
            '正常发布', '总体质量较好'
        )
        """
        
        cursor.execute(test_insert_sql)
        conn.commit()
        
        print("\n✅ 测试数据插入成功")
        
        # 查询测试数据
        cursor.execute("SELECT * FROM evaluations ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        
        if row:
            print(f"\n📊 测试数据:")
            print(f"  ID: {row[0]}")
            print(f"  标题：{row[3]}")
            print(f"  总分：{row[5]} ({row[6]}级)")
            print(f"  模型：{row[4]}")
        
        cursor.close()
        
    except Exception as e:
        print(f"❌ 错误：{e}")
        raise
    finally:
        if conn:
            conn.close()
            print("\n✅ 数据库连接已关闭")


def drop_evaluations_table():
    """删除评价表 (危险操作)"""
    conn = None
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        confirm = input("⚠️  确定要删除 evaluations 表吗？(输入 yes 确认): ")
        if confirm != 'yes':
            print("❌ 操作已取消")
            return
        
        cursor.execute("DROP TABLE IF EXISTS evaluations")
        conn.commit()
        
        print("✅ evaluations 表已删除")
        
        cursor.close()
    except Exception as e:
        print(f"❌ 错误：{e}")
        raise
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'drop':
        drop_evaluations_table()
    else:
        create_evaluations_table()
