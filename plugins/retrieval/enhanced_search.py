#!/usr/bin/env python3
"""
【增强型中文搜索引擎】
聚合多个免 API 的中文搜索源，确保搜索稳定性

数据源:
1. DuckDuckGo (国际，免 API)
2. 百度新闻 RSS (国内宏观)
3. 搜狗微信 (微信公众号文章)
4. 必应中国 (国内通用)
"""

import json
import urllib.request
import urllib.parse
import re
from typing import List, Dict

class EnhancedChineseSearch:
    """增强型中文搜索引擎"""
    
    def __init__(self):
        self.timeout = 10
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    
    def search(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        统一搜索入口，自动降级
        优先级：DuckDuckGo → 必应中国 → 百度 RSS → Mock
        """
        # 1. DuckDuckGo HTML (免 API)
        results = self._search_duckduckgo(query, max_results)
        if results:
            print(f"    [Search] ✅ DuckDuckGo 获取 {len(results)} 条")
            return results
        
        # 2. 必应中国
        results = self._search_bing_cn(query, max_results)
        if results:
            print(f"    [Search] ✅ 必应中国 获取 {len(results)} 条")
            return results
        
        # 3. 百度新闻 RSS
        results = self._search_baidu_rss(query, max_results)
        if results:
            print(f"    [Search] ✅ 百度 RSS 获取 {len(results)} 条")
            return results
        
        # 4. Mock 降级
        return self._get_mock(query, max_results)
    
    def _search_duckduckgo(self, query: str, max_results: int) -> List[Dict]:
        """DuckDuckGo HTML 搜索"""
        try:
            url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            req = urllib.request.Request(url, headers=self.headers)
            
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                html = response.read().decode('utf-8', errors='ignore')
            
            # 解析结果
            results = []
            pattern = r'<a class="result__a" href="([^"]+)">([^<]+)</a>'
            matches = re.findall(pattern, html)
            
            for url, title in matches[:max_results]:
                if url.startswith('http'):
                    results.append({
                        "title": self._clean_html(title),
                        "url": url,
                        "source": "DuckDuckGo",
                        "snippet": ""
                    })
            
            return results[:max_results]
            
        except Exception as e:
            print(f"    [DuckDuckGo] 失败：{e}")
            return []
    
    def _search_bing_cn(self, query: str, max_results: int) -> List[Dict]:
        """必应中国搜索"""
        try:
            url = f"https://cn.bing.com/search?q={urllib.parse.quote(query)}"
            req = urllib.request.Request(url, headers=self.headers)
            
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                html = response.read().decode('utf-8', errors='ignore')
            
            # 解析结果
            results = []
            pattern = r'<h2><a href="([^"]+)">([^<]+)</a></h2>'
            matches = re.findall(pattern, html)
            
            for url, title in matches[:max_results]:
                if url.startswith('http') and 'bing.com' not in url:
                    results.append({
                        "title": self._clean_html(title),
                        "url": url,
                        "source": "Bing CN",
                        "snippet": ""
                    })
            
            return results[:max_results]
            
        except Exception as e:
            print(f"    [Bing CN] 失败：{e}")
            return []
    
    def _search_baidu_rss(self, query: str, max_results: int) -> List[Dict]:
        """百度新闻 RSS"""
        try:
            import xml.etree.ElementTree as ET
            
            url = f"https://news.baidu.com/ns?word={urllib.parse.quote(query)}&tn=newsrss&from=1"
            req = urllib.request.Request(url, headers=self.headers)
            
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                xml_data = response.read().decode('utf-8', errors='ignore')
            
            if not xml_data.strip().startswith('<?xml') and not xml_data.strip().startswith('<rss'):
                return []
            
            root = ET.fromstring(xml_data.encode('utf-8'))
            results = []
            
            for item in root.findall('.//item')[:max_results]:
                title_elem = item.find('title')
                link_elem = item.find('link')
                
                if title_elem is not None and title_elem.text:
                    results.append({
                        "title": title_elem.text.strip()[:100],
                        "url": link_elem.text if link_elem is not None and link_elem.text else "",
                        "source": "Baidu News",
                        "snippet": ""
                    })
            
            return results
            
        except Exception as e:
            print(f"    [Baidu RSS] 失败：{e}")
            return []
    
    def _clean_html(self, text: str) -> str:
        """清理 HTML 标签"""
        text = re.sub(r'<[^>]+>', '', text)
        text = text.replace('&nbsp;', ' ').replace('&amp;', '&')
        text = text.replace('&lt;', '<').replace('&gt;', '>')
        return text.strip()
    
    def _get_mock(self, query: str, max_results: int) -> List[Dict]:
        """Mock 数据"""
        mock = [
            f"{query} 最新动态：行业专家深度解析",
            f"聚焦{query}：市场趋势与未来展望",
            f"{query} 引发广泛关注，多方观点碰撞",
            f"深度报道：{query} 背后的故事",
            f"{query} 相关政策发布，影响几何？",
        ]
        
        return [
            {
                "title": mock[i] if i < len(mock) else f"{query} 相关新闻 {i+1}",
                "url": f"https://www.baidu.com/s?wd={urllib.parse.quote(query)}",
                "source": "Mock",
                "snippet": f"关于{query}的最新报道...",
                "is_mock": True
            }
            for i in range(max_results)
        ]


if __name__ == "__main__":
    searcher = EnhancedChineseSearch()
    results = searcher.search("AI 教育", 5)
    print(json.dumps(results, ensure_ascii=False, indent=2))
