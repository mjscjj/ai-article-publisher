-- V3 数据库初始化脚本

-- 创建评价表
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

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'writer',
    status VARCHAR(20) DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='用户表';

-- 创建发布队列表
CREATE TABLE IF NOT EXISTS publish_queue (
    id INT AUTO_INCREMENT PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,
    title VARCHAR(500),
    content TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    scheduled_at DATETIME,
    published_at DATETIME,
    retry_count INT DEFAULT 0,
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_platform (platform)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='发布队列表';

-- 创建用户行为追踪表
CREATE TABLE IF NOT EXISTS user_actions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action_type VARCHAR(50),
    action_data JSON,
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user (user_id),
    INDEX idx_action (action_type),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='用户行为追踪表';

-- 创建工作流表
CREATE TABLE IF NOT EXISTS workflows (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    version VARCHAR(20) DEFAULT '1.0',
    status VARCHAR(20) DEFAULT 'draft',
    definition JSON,
    created_by INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_created_by (created_by)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='工作流定义表';

-- 插入默认管理员用户 (密码：admin123)
INSERT INTO users (username, email, password_hash, role) VALUES
('admin', 'admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS3MebAJu', 'admin')
ON DUPLICATE KEY UPDATE username=username;

-- 插入测试数据
INSERT INTO evaluations (target_type, target_title, model_used, total_score, grade, comment) VALUES
('article', '测试文章', 'deepseek-chat-v3', 85.5, 'A', '总体质量较好'),
('topic', '测试选题', 'deepseek-chat-v3', 78.2, 'B', '有潜力但需完善')
ON DUPLICATE KEY UPDATE id=id;
