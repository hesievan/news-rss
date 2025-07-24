#!/usr/bin/env python3
import json
import sys
from utils import load_json_config, save_json_data, filter_by_keywords

def filter_news():
    """根据关键词过滤新闻"""
    # 加载关键词配置
    keywords_config = load_json_config('config/keywords.json')
    if not keywords_config:
        print("未找到关键词配置")
        return []
    
    # 加载原始新闻数据
    try:
        with open('output/raw_news.json', 'r', encoding='utf-8') as f:
            news_data = json.load(f)
    except FileNotFoundError:
        print("未找到原始新闻数据，请先运行 collect_rss.py")
        return []
    except json.JSONDecodeError:
        print("原始新闻数据格式错误")
        return []
    
    print(f"开始过滤 {len(news_data)} 条新闻...")
    
    # 根据关键词过滤
    filtered_news = filter_by_keywords(news_data, keywords_config)
    
    print(f"过滤后得到 {len(filtered_news)} 条相关新闻")
    
    return filtered_news

def main():
    """主函数"""
    print("开始过滤新闻...")
    
    # 过滤新闻
    filtered_data = filter_news()
    
    if filtered_data:
        # 保存过滤后的数据
        output_file = 'output/filtered_news.json'
        if save_json_data(filtered_data, output_file):
            print(f"过滤结果已保存到: {output_file}")
            
            # 生成摘要报告
            summary = {
                'total_news': len(filtered_data),
                'sources': list(set(item['source'] for item in filtered_data)),
                'generated_at': filtered_data[0]['collected_at'] if filtered_data else None
            }
            
            summary_file = 'output/summary.json'
            if save_json_data(summary, summary_file):
                print(f"摘要报告已保存到: {summary_file}")
        else:
            print("保存过滤结果失败")
            sys.exit(1)
    else:
        print("没有找到匹配的新闻")
        # 创建空结果文件
        save_json_data([], 'output/filtered_news.json')
        save_json_data({'total_news': 0, 'sources': [], 'generated_at': None}, 'output/summary.json')

if __name__ == "__main__":
    main()
