#!/bin/bash
# RSSHub 热门数据源测试脚本
# 本地实例: http://localhost:1200

RSSHUB="http://localhost:1200"

echo "=========================================="
echo "       RSSHub 热点采集测试"
echo "=========================================="
echo ""

# 不需要 Puppeteer 的数据源
echo "【Hacker News Best】"
echo "-------------------------------------------"
curl -s "$RSSHUB/hackernews/best" 2>/dev/null | grep -oP '(?<=<title>)[^<]+(?=</title>)' | head -5
echo ""

echo "【V2EX 热门】"
echo "-------------------------------------------"
curl -s "$RSSHUB/v2ex/topics/hot" 2>/dev/null | grep -oP '(?<=<title>)[^<]+(?=</title>)' | head -5
echo ""

echo "【GitHub Trending Daily】"
echo "-------------------------------------------"
curl -s "$RSSHUB/github/trending/daily" 2>/dev/null | grep -oP '(?<=<title>)[^<]+(?=</title>)' | head -5
echo ""

echo "【少数派】"
echo "-------------------------------------------"
curl -s "$RSSHUB/sspai/index" 2>/dev/null | grep -oP '(?<=<title>)[^<]+(?=</title>)' | head -5
echo ""

echo "【IT之家】"
echo "-------------------------------------------"
curl -s "$RSSHUB/ithome/ranking/7days" 2>/dev/null | grep -oP '(?<=<title>)[^<]+(?=</title>)' | head -5
echo ""

echo "【掘金热门】"
echo "-------------------------------------------"
curl -s "$RSSHUB/juejin/trending/all/monthly" 2>/dev/null | grep -oP '(?<=<title>)[^<]+(?=</title>)' | head -5
echo ""

echo "=========================================="
echo "注意: 部分数据源需要 Puppeteer/Chrome"
echo "=========================================="