"""
提取本文件作为 Article Generator 的对外唯一统一接口 (Facade)。
其他项目若引入本模块，只需：from article_generator import generate_article
"""
from typing import Dict, Union

# 占位符接口展示（待具体打通）
def generate_article(topic_or_outline: Union[str, Dict], fact_pack: Dict) -> str:
    """
    全量封装流程:
    1. Outliner(骨架) -> 2. Writer(织肉) -> 3. Editor(定稿)
    """
    pass
