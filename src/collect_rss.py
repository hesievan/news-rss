#!/usr/bin/env python3
import feedparser
import json
import os
import sys
from datetime import datetime
from utils import load_json_config, save_json_data, format_datetime

def collect_rss_feeds():
    """收集RSS源内容"""
    # 加载RSS源配置
    rss_sources = load_json_config('config/rss-sources.json')
    if not rss_sources:
        print("未找到RSS源配置")
        return []
    
    all_news = []
    
    for source in rss_sources:
        name = source.get('name', '未知源')
        url = source.get('url', '')
        category = source.get('category', 'general')
        
        if not url:
            print(f"跳过无效源: {name}")
            continue
        
        print(f"正在收集: {name}")
        
        try:
            feed = feedparser.parse(url)
            
            for entry in feed.entries:
                news_item = {
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'description': entry.get('description', ''),
                    'published': entry.get('published', ''),
                    'source': name,
                    'category': category,
                    'collected_at': format_datetime(datetime.now())
                }
                
                # 尝试获取内容
                if hasattr(entry, 'content'):
                    news_item['content'] = entry.content[0].value if entry.content else ''
                else:
                    news_item['content'] = entry.get('summary', '')
                
                all_news.append(news_item)
                
        except Exception as e:
            print(f"收集 {name} 时出错: {e}")
    
    print(f"总共收集到 {len(all_news)} 条新闻")
    return all_news

def main():
    """主函数"""
    print("开始收集RSS内容...")
    
    # 收集RSS内容
    news_data = collect_rss_feeds()
    
    if news_data:
        # 保存原始数据
        output_file = 'output/raw_news.json'
        if save_json_data(news_data, output_file):
            print(f"原始数据已保存到: {output_file}")
        else:
            print("保存原始数据失败")
            sys.exit(1)
    else:
        print("未收集到任何新闻")
        sys.exit(1)

if __name__ == "__main__":
    main()
