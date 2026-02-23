"""
AI Article Publisher - 数据采集模块

包含:
- dailyhot_collector: DailyHotApi 采集器 (40+ 平台)
- extended_collectors_v2: RSSHub 扩展采集器
- unified_collector: 统一采集入口
"""

__version__ = "1.0.0"

# 可用的采集器
COLLECTORS = {
    "dailyhot": {
        "name": "DailyHotApi",
        "platforms": 31,
        "description": "40+ 国内热榜平台"
    },
    "rsshub": {
        "name": "RSSHub",
        "platforms": 25,
        "description": "国际+国内 RSS 源"
    }
}