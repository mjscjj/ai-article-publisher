#!/usr/bin/env python3
"""
【缓存中间件】Cache Middleware
为搜索和 LLM 调用添加缓存层，减少重复请求

功能:
1. 搜索缓存 (相同 query 直接返回)
2. LLM 响应缓存 (相同 prompt 返回缓存)
3. 缓存过期策略 (TTL)
4. 缓存统计
"""

import json
import os
import hashlib
import time
from typing import Any, Dict, Optional
from datetime import datetime

DEFAULT_TTL = {
    "search": 3600,      # 搜索缓存 1 小时
    "llm": 86400,        # LLM 缓存 24 小时
    "topic": 1800,       # 话题发现 30 分钟
}

class CacheMiddleware:
    def __init__(self, cache_dir: str = None):
        self.cache_dir = cache_dir or os.path.join(
            os.path.dirname(__file__), '..', 'data', 'cache'
        )
        os.makedirs(self.cache_dir, exist_ok=True)
        self.stats = {"hits": 0, "misses": 0, "writes": 0}
    
    def _get_key(self, prefix: str, data: Any) -> str:
        """生成缓存键"""
        content = json.dumps(data, sort_keys=True, ensure_ascii=False)
        hash_md5 = hashlib.md5(content.encode('utf-8')).hexdigest()[:12]
        return f"{prefix}_{hash_md5}.json"
    
    def _get_path(self, key: str) -> str:
        return os.path.join(self.cache_dir, key)
    
    def get(self, prefix: str, data: Any) -> Optional[Any]:
        """获取缓存"""
        key = self._get_key(prefix, data)
        path = self._get_path(key)
        
        if not os.path.exists(path):
            self.stats["misses"] += 1
            return None
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                cache_entry = json.load(f)
            
            # 检查过期
            if time.time() - cache_entry["timestamp"] > cache_entry.get("ttl", DEFAULT_TTL.get(prefix, 3600)):
                os.remove(path)
                self.stats["misses"] += 1
                return None
            
            self.stats["hits"] += 1
            return cache_entry["value"]
            
        except Exception as e:
            print(f"[Cache] 读取失败：{e}")
            self.stats["misses"] += 1
            return None
    
    def set(self, prefix: str, data: Any, value: Any, ttl: int = None) -> bool:
        """设置缓存"""
        try:
            key = self._get_key(prefix, data)
            path = self._get_path(key)
            
            cache_entry = {
                "timestamp": time.time(),
                "ttl": ttl or DEFAULT_TTL.get(prefix, 3600),
                "value": value,
            }
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(cache_entry, f, ensure_ascii=False, indent=2)
            
            self.stats["writes"] += 1
            return True
            
        except Exception as e:
            print(f"[Cache] 写入失败：{e}")
            return False
    
    def clear(self, prefix: str = None) -> int:
        """清除缓存"""
        count = 0
        for filename in os.listdir(self.cache_dir):
            if prefix is None or filename.startswith(prefix):
                os.remove(os.path.join(self.cache_dir, filename))
                count += 1
        return count
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        total = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total * 100) if total > 0 else 0
        
        # 缓存文件大小
        total_size = sum(
            os.path.getsize(os.path.join(self.cache_dir, f))
            for f in os.listdir(self.cache_dir)
            if os.path.isfile(os.path.join(self.cache_dir, f))
        )
        
        return {
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "writes": self.stats["writes"],
            "hit_rate": f"{hit_rate:.1f}%",
            "cache_files": len(os.listdir(self.cache_dir)),
            "cache_size_kb": round(total_size / 1024, 2),
        }


# 装饰器
def cached(prefix: str, ttl: int = None):
    """缓存装饰器"""
    def decorator(func):
        cache = CacheMiddleware()
        
        def wrapper(*args, **kwargs):
            # 尝试缓存
            cache_key = {"func": func.__name__, "args": args, "kwargs": kwargs}
            cached_result = cache.get(prefix, cache_key)
            
            if cached_result is not None:
                return cached_result
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 写入缓存
            cache.set(prefix, cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


if __name__ == "__main__":
    cache = CacheMiddleware()
    
    # 测试缓存
    print("测试缓存功能:")
    
    # 第一次调用 (miss)
    result1 = cache.get("test", {"query": "AI 教育"})
    print(f"第一次获取：{result1}")
    
    # 写入缓存
    cache.set("test", {"query": "AI 教育"}, {"results": ["结果 1", "结果 2"]})
    
    # 第二次调用 (hit)
    result2 = cache.get("test", {"query": "AI 教育"})
    print(f"第二次获取：{result2}")
    
    # 统计
    stats = cache.get_stats()
    print(f"\n缓存统计: {stats}")
    
    # 清理
    cleared = cache.clear("test")
    print(f"\n清理缓存：{cleared} 个文件")
