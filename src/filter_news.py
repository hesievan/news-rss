#!/usr/bin/env python3
import json
import sys
from utils import load_json_config, save_json_data, filter_by_keywords

def filter_news():
    """过滤新闻内容"""
    # 加载新闻数据
    try:
        with open('output/raw_news.json', 'r', encoding='utf-8') as f:
            news_data = json.load(f)
    except json.JSONDecodeError:
        logging.error("原始新闻数据JSON格式错误")
        return []
    except Exception as e:
        logging.error(f"加载原始新闻数据失败: {str(e)}")
        return []
    
    # 加载关键词配置
    keywords_config = load_config('config/keywords.yaml', 'config/schema/keywords.schema.json')
    if not keywords_config:
        logging.warning("关键词配置为空，使用默认过滤规则")
        return []
    
    # 过滤新闻
    filtered_news = filter_by_keywords(news_data, keywords_config)
    
    # 按发布时间排序（最新的在前）
    filtered_news.sort(key=lambda x: x.get('published', ''), reverse=True)
    
    # 保存过滤后的新闻
    if save_json_data(filtered_news, 'output/filtered_news.json'):
        print(f"已过滤 {len(filtered_news)} 条新闻")
    else:
        logging.error("保存过滤后新闻失败")
        return []
    
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
