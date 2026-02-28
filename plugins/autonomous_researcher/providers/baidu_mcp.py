#!/usr/bin/env python3
"""
【百度 Provider】baidu_mcp.py
使用 curl_cffi 绕过反爬，获取百度新闻。

备用方案：
1. 百度新闻 RSS (无需登录)
2. 其他中文新闻源 (新浪/腾讯/网易)
"""

import json
from typing import List, Dict, Any

try:
    from curl_cffi import requests
    HAS_CURL_CFFI = True
except ImportError:
    HAS_CURL_CFFI = False

class BaiduProvider:
    """
    负责抓取宏观政策、官媒通报、行业投融资等"硬事实"。
    """
    
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        百度搜索
        
        优先级:
        1. curl_cffi 直接抓取 (绕过反爬)
        2. 百度新闻 RSS (备用)
        3. Mock 数据 (最终降级)
        """
        if HAS_CURL_CFFI:
            results = self._search_curl_cffi(query, max_results)
            if results:
                return results
        
        # 降级：RSS
        results = self._search_rss(query, max_results)
        if results:
            return results
        
        # 最终降级：Mock
        return self._get_mock(query, max_results)
    
    def _search_curl_cffi(self, query: str, max_results: int) -> List[Dict]:
        """使用 curl_cffi 抓取"""
        try:
            import urllib.parse
            url = f"https://m.baidu.com/s?word={urllib.parse.quote(query)}&tn=news"
            
            response = requests.get(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15',
                    'Accept': 'text/html,application/xhtml+xml',
                },
                impersonate='chrome120',
                timeout=15,
            )
            
            return self._parse_html(response.text, max_results)
        except Exception as e:
            print(f"    [Baidu] curl_cffi 失败：{e}")
            return []
    
    def _search_rss(self, query: str, max_results: int) -> List[Dict]:
        """
        使用百度新闻 RSS (备用方案)
        RSS 地址：https://news.baidu.com/ns?word={query}&tn=newsrss
        """
        try:
            import urllib.request
            import xml.etree.ElementTree as ET
            import urllib.parse
            import re
            
            url = f"https://news.baidu.com/ns?word={urllib.parse.quote(query)}&tn=newsrss&from=1"
            
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                xml_data = response.read().decode('utf-8', errors='ignore')
            
            # 检查是否是有效的 XML
            if not xml_data.strip().startswith('<?xml') and not xml_data.strip().startswith('<rss'):
                # 可能返回的是 HTML，降级到 HTML 解析
                return self._parse_html(xml_data, max_results)
            
            # 解析 RSS
            root = ET.fromstring(xml_data.encode('utf-8'))
            results = []
            
            for item in root.findall('.//item')[:max_results]:
                title_elem = item.find('title')
                link_elem = item.find('link')
                desc_elem = item.find('description')
                
                if title_elem is not None and title_elem.text:
                    results.append({
                        "title": title_elem.text.strip()[:100],
                        "url": link_elem.text if link_elem is not None and link_elem.text else "",
                        "snippet": desc_elem.text[:200] if desc_elem is not None and desc_elem.text else "",
                    })
            
            if results:
                print(f"    [Baidu] ✅ RSS 获取 {len(results)} 条结果")
            
            return results
            
        except Exception as e:
            print(f"    [Baidu] RSS 失败：{e}")
            return []
    
    def _parse_html(self, html: str, max_results: int) -> List[Dict]:
        """解析百度 HTML"""
        import re
        
        # 百度新闻结构：<h3 class="c-title"><a href="...">标题</a></h3>
        title_pattern = r'<h3[^>]*class="c-title"[^>]*>\s*<a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>'
        matches = re.findall(title_pattern, html, re.S | re.I)
        
        results = []
        for title, url in matches[:max_results]:
            results.append({
                "title": title.strip(),
                "url": url,
                "snippet": "",
            })
        
        if results:
            print(f"    [Baidu] ✅ 获取 {len(results)} 条结果")
        
        return results
    
    def _get_mock(self, query: str, max_results: int) -> List[Dict]:
        """Mock 数据 (最终降级)"""
        mock_news = [
            f"{query} 相关政策发布，多部门联合推进",
            f"专家解读：{query} 的未来发展趋势",
            f"{query} 市场规模持续扩大，预计 2025 年达新高",
            f"行业巨头纷纷布局{query}赛道",
            f"{query} 引发社会广泛关注，网友热议",
        ]
        
        results = []
        for i in range(min(max_results, len(mock_news))):
            results.append({
                "title": mock_news[i],
                "url": f"https://www.baidu.com/s?wd={query}",
                "snippet": f"关于{query}的最新报道...",
                "is_mock": True,
            })
        
        print(f"    [Baidu] ⚠️ 返回 {len(results)} 条 Mock 数据")
        return results
    
    def fetch_url(self, url: str) -> str:
        """抓取网页内容"""
        try:
            if HAS_CURL_CFFI:
                response = requests.get(url, impersonate='chrome120', timeout=10)
                return response.text[:5000]
            else:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                return urllib.request.urlopen(req, timeout=10).read().decode('utf-8', errors='ignore')[:5000]
        except Exception as e:
            print(f"[BaiduProvider] ⚠️ 抓取失败：{e}")
            return ""


if __name__ == "__main__":
    provider = BaiduProvider()
    results = provider.search("AI 教育", max_results=5)
    print(json.dumps(results, ensure_ascii=False, indent=2))
