#!/usr/bin/env python3
import json
import os
from datetime import datetime
from typing import List, Dict, Any

def load_json_data(file_path: str) -> List[Dict[str, Any]]:
    """加载JSON数据"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"文件 {file_path} 不存在")
        return []
    except json.JSONDecodeError:
        print(f"文件 {file_path} JSON格式错误")
        return []

def generate_markdown(news_data: List[Dict[str, Any]], title: str) -> str:
    """生成Markdown格式的内容"""
    if not news_data:
        return f"# {title}\n\n没有找到相关新闻。\n"
    
    markdown_content = f"# {title}\n\n"
    markdown_content += f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    markdown_content += f"共找到 {len(news_data)} 条新闻\n\n"
    
    for item in news_data:
        title_text = item.get('title', '无标题')
        link = item.get('link', '#')
        source = item.get('source', '未知来源')
        published_date = item.get('published', '')
        
        markdown_content += f"- [{title_text}]({link})\n"
        markdown_content += f"  - 来源: {source}\n"
        if published_date:
            markdown_content += f"  - 发布时间: {published_date}\n"
        markdown_content += "\n"
    
    return markdown_content

def save_markdown(content: str, file_path: str) -> bool:
    """保存Markdown内容到文件"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"保存Markdown文件失败: {e}")
        return False

def generate_all_markdown():
    """生成所有Markdown文件"""
    # 生成原始新闻的Markdown
    raw_news = load_json_data('output/raw_news.json')
    raw_markdown = generate_markdown(raw_news, "RSS原始新闻列表")
    save_markdown(raw_markdown, 'output/raw_news.md')
    print(f"已生成原始新闻Markdown: output/raw_news.md ({len(raw_news)} 条)")
    
    # 生成过滤后新闻的Markdown
    filtered_news = load_json_data('output/filtered_news.json')
    filtered_markdown = generate_markdown(filtered_news, "过滤后新闻列表")
    save_markdown(filtered_markdown, 'output/filtered_news.md')
    print(f"已生成过滤后新闻Markdown: output/filtered_news.md ({len(filtered_news)} 条)")

def main():
    """主函数"""
    print("开始生成Markdown文件...")
    generate_all_markdown()
    print("Markdown文件生成完成！")

if __name__ == "__main__":
    main()
