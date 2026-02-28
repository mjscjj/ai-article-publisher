# 📝 Article Generator (独立文章生成引擎)

> 本模块为**绝对物理隔离**的文字处理工厂。可作为独立库抽离出本项目，放入任何 Python 环境运行。

## 核心特性 (Features)
- 🚫 断网沙盒：禁止外部网络请求，严防大模型产生检索性崩溃。
- ⚡ 异步并发：利用 asyncio 并发驱动 3 路 Agent 分段写作。
- ⚖️ 左右互搏：自带 "毒舌主编" 环路，自我质检去 AI 味。

## 入口协议 (API Contract)

### `generate_article(outline_directive: str | dict, fact_pack: dict) -> str`
*   **入参**:
    *   `outline_directive` (str 或 dict): 用户想要写的主题，或明确的大纲指令。
    *   `fact_pack` (dict): 带有事实弹药库的字典 (可传空字典 `{}` 以纯瞎编模式运行)。
*   **出参**: 
    *   纯净、经过两轮审校的高质量 Markdown 长文本字符串。

## 独立运行 (Standalone Usage)
如果抽出此文件夹，仅需配置环境变量并执行：
```bash
export OPENROUTER_API_KEY="sk-..."
python3 standalone.py -p "分析特斯拉最新财报"
```
