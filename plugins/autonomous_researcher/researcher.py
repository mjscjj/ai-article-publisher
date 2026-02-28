#!/usr/bin/env python3
"""
【 Autonomous Researcher Core 】
完全解耦的核心研究引擎类。可将其导入任何需要的包内。
"""
import urllib.request
import urllib.parse
import re
import json

class AutonomousResearcher:
    def __init__(self, llm_callable, max_depth=2, max_urls_per_query=2):
        self.llm = llm_callable
        self.max_depth = max_depth
        self.max_urls_per_query = max_urls_per_query
        self.knowledge_base = [] # 知识池

    def _generate_queries(self, topic, prior_findings="", depth=1):
        """让大模型根据课题，拆解为具体的搜索引擎关键词"""
        sys_prompt = "你是一个专业的情报搜索引擎专家。只返回合法的 JSON 数组，如 [\"A\", \"B\"]，严禁回答多余字符或解释。"
        prompt = f"当前命题：【{topic}】\n"
        if prior_findings:
            prompt += f"目前线索：{prior_findings[:1000]}...\n请根据已有线索，补足盲区，生成 3 个新的搜索引擎检索词。\n"
        else:
            prompt += "请将该命题拆解为 3 个具体精准的搜索引擎词条以寻找数据和案例。\n"
        try:
            res = self.llm(prompt, sys_prompt)
            match = re.search(r'\[.*?\]', res, re.S)
            if match: return json.loads(match.group(0))
        except Exception: pass
        return [f"{topic} 深入分析", f"{topic} 数据 案例", f"{topic} 最新进展"]

    def _fetch_search_links(self, query):
        """DuckDuckGo HTML 抓取"""
        links = []
        url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/114.0.0.0 Safari/537.36'})
        
        try:
            html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
            # 兼容 duckduckgo html 的解析
            matches = re.findall(r'<a class="result__url" href="([^"]+)">', html)
            for m in matches:
                link = m
                if 'duckduckgo.com/l/?uddg=' in link:
                    # 剥洋葱拿出真实外链
                    link = urllib.parse.unquote(link.split('uddg=')[1].split('&rut=')[0])
                if link.startswith('http') and "duckduckgo" not in link:
                    links.append(link)
                if len(links) >= self.max_urls_per_query: break
        except Exception as e:
            print(f"搜索 {query} 出错:", e)
        return list(set(links))

    def _scrape_page(self, url):
        """纯净脱水抓取网页正文"""
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/114.0.0.0 Safari/537.36'})
        try:
            content = urllib.request.urlopen(req, timeout=8).read().decode('utf-8', errors='ignore')
            # 删 script, style, header, footer 等污染噪音
            content = re.sub(r'<(script|style|nav|footer|header)[^>]*>.*?</\1>', ' ', content, flags=re.S | re.I)
            text = re.sub(r'<[^>]+>', ' ', content)
            text = re.sub(r'\s+', ' ', text)
            return text.strip()[:6000] # 最多截取前 6000 个字符
        except Exception:
            return ""

    def _reflect(self, topic, prior):
        """自我反思回路：判断打捞上来的文本是否足够有营养"""
        if not prior: return False
        try:
            res = self.llm(f"课题：{topic}\n当前已获材料：{prior[:3000]}。\n如果材料内包含实质的数据、案例、强观点支撑长文则返回 ENOUGH，如果只是废话/太短则返回 NEED_MORE", "严禁说废话").upper()
            return "ENOUGH" in res
        except: return False

    def _synthesize(self, topic):
        """用 LLM 榨取 Fact-Pack"""
        if not self.knowledge_base:
            return "未能从外网捕获到高质量/即时的网页正文。这可能是由于目标关键词相关的网页开启了强反爬导致。但系统保留了命题和知识内建。请直接使用模型内建视野写作。"
        sys = "你是一名顶级的非虚构深挖编辑助手。"
        joined_knowledge = "\n- ".join(self.knowledge_base)[:20000]
        prompt = f"这是系统爬虫强行带回的关于【{topic}】的多文碎片数据：\n{joined_knowledge}\n\n请精炼出 4-6 条极具洞察的新闻事实包（Fact-Pack），必须包含你其中看到的真实例子、数字和事件。"
        return self.llm(prompt, sys)

    def run(self, topic):
        print(f"\n🚀 [Autonomous Researcher V3] 引擎启动。命题：{topic}")
        print(f"⚙️ 最大下潜层数: {self.max_depth}, 每词条点击外链数: {self.max_urls_per_query}")
        
        for depth_layer in range(1, self.max_depth + 1):
            print(f"\n🌊 [Depth {depth_layer}/{self.max_depth}] 发起深网探索...")
            prior_kb = " | ".join(self.knowledge_base)[:3000] if self.knowledge_base else ""
            
            # AI 智能多视角拆词
            queries = self._generate_queries(topic, prior_kb, depth=depth_layer)
            print(f"🎯 AI分裂触手关键词: {queries}")
            
            layer_docs = []
            for q in queries:
                print(f"  🕷️ 启动分布式触手 -> 鸭鸭搜: '{q}'")
                links = self._fetch_search_links(q)
                for link in links:
                    print(f"    📄 潜入并剥离正文: {link[:50]}...")
                    content = self._scrape_page(link)
                    # 反爬拦截了大量请求，这里要求至少取到点正文字符
                    if content and len(content) > 200:
                        self.knowledge_base.append(content)
                        layer_docs.append(content)
                        
            print(f"📦 此层打捞结束。成功解析高质量外网深潜长文: {len(layer_docs)} 篇。")
            
            # AI 自我反思机制
            if depth_layer < self.max_depth:
                current_k_str = " ".join(layer_docs)
                print("🤔 [Self-Reflection] AI正在反思：目前打捞的事实足够写长篇研报了吗？")
                if self._reflect(topic, current_k_str):
                    print("💡 AI 反思判定：已收集足量硬核事实，立刻中止下潜机制以节省时间/算力。")
                    break
                else:
                    print("📉 AI 反思判定：当前的材料干货太少或同质化，即将发起更深一层的定向找寻(继续下潜)！")
                    
        print("\n=============================================")
        print("🏭 打捞收工。将巨量残余文本推入高温熔炉，提炼终极骨架...")
        fact_pack = self._synthesize(topic)
        print("✅ =============== 终极调研包 Fact-Pack ===============")
        print(fact_pack)
        print("========================================================\n")
        return fact_pack

def test_researcher():
    import sys
    # 强制将 core 加入搜寻路径，以便能 import 你的免费大模型 SDK
    sys.path.append("/root/.openclaw/workspace-writer/ai-article-publisher/core")
    from llm_client import ask_ai
    
    # 比如我们想要了解大语言模型o3的技术内幕
    r = AutonomousResearcher(llm_callable=ask_ai, max_depth=2, max_urls_per_query=2)
    # 调用
    res = r.run("OpenAI o3-mini 模型对比 DeepSeek R1 性能差异具体案例")

if __name__ == "__main__":
    test_researcher()
