#!/usr/bin/env python3
"""
V3 热点中心 API 快速启动脚本

使用方法:
    python scripts/run_hotnews_api.py

API 文档:
    http://localhost:8081/api/v3/docs
"""

import os
import sys
import uvicorn

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    """启动 API 服务"""
    print("=" * 60)
    print("🚀 V3 HotNews API 启动")
    print("=" * 60)
    print("📡 服务地址：http://0.0.0.0:8081")
    print("📚 API 文档：http://localhost:8081/api/v3/docs")
    print("🔧 ReDoc: http://localhost:8081/api/v3/redoc")
    print("=" * 60)
    print("\n按 Ctrl+C 停止服务\n")
    
    # 启动服务
    uvicorn.run(
        "api.v3.hotnews:app",
        host="0.0.0.0",
        port=8081,
        reload=False,  # 生产环境关闭热重载
        log_level="info"
    )

if __name__ == "__main__":
    main()
