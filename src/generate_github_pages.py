#!/usr/bin/env python3
"""
Generate GitHub Pages HTML from filtered news
"""
import json
import os
import logging
import sys
from datetime import datetime
from typing import Dict, List, Any
import re

# 添加Python路径处理
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import load_config


def load_filtered_news() -> List[Dict[str, Any]]:
    """
    加载筛选后的新闻数据
    从output/filtered_news.json文件中读取已筛选的新闻数据
    如果文件不存在或为空，返回空列表
    @return {List[Dict[str, Any]]} 新闻数据列表，每个元素为包含新闻信息的字典
    """
    # 新闻数据文件路径
    news_file = "output/filtered_news.json"
    # 检查文件是否存在
    if not os.path.exists(news_file):
        logging.warning(f"新闻数据文件不存在: {news_file}")
        return []
    # 读取并返回JSON数据
    with open(news_file, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            logging.error(f"新闻数据文件格式错误: {news_file}")
            return []


def extract_keywords_from_text(text: str, keywords: List[str]) -> List[str]:
    """
    从文本中提取匹配的关键词
    将文本和关键词都转为小写后进行匹配，避免大小写敏感问题
    @param {str} text - 需要提取关键词的文本内容
    @param {List[str]} keywords - 关键词列表
    @return {List[str]} 匹配到的关键词列表
    """
    # 将文本转为小写，实现大小写不敏感匹配
    text_lower = text.lower()
    matched_keywords = []
    # 遍历所有关键词，检查是否在文本中出现
    for keyword in keywords:
        if keyword.lower() in text_lower:
            matched_keywords.append(keyword)
    return matched_keywords


def group_news_by_keywords(news_list: List[Dict[str, Any]], keywords: List[str]) -> Dict[str, List[Dict[str, Any]]]:
    """
    将新闻按匹配的关键词分组
    组合新闻标题、描述和内容，提取匹配的关键词，并将新闻归类到对应的关键词组
    @param {List[Dict[str, Any]]} news_list - 新闻列表
    @param {List[str]} keywords - 关键词列表
    @return {Dict[str, List[Dict[str, Any]]]} 按关键词分组的新闻字典
    """
    keyword_groups = {}
    for news in news_list:
        # 提取新闻的标题、描述和内容
        title = news.get('title', '')
        description = news.get('description', '')
        content = news.get('content', '')
        # 组合所有文本用于关键词匹配
        full_text = f"{title} {description} {content}"
        matched_keywords = extract_keywords_from_text(full_text, keywords)
        # 将新闻添加到每个匹配的关键词组
        for keyword in matched_keywords:
            if keyword not in keyword_groups:
                keyword_groups[keyword] = []
            keyword_groups[keyword].append(news)
    return keyword_groups


def format_date(date_str: str) -> str:
    """Format date string for display"""
    try:
        # Handle different date formats
        if 'T' in date_str:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            dt = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
        return dt.strftime('%Y-%m-%d %H:%M')
    except:
        return date_str


def truncate_text(text: str, max_length: int = 200) -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + '...'


def clean_html(text: str) -> str:
    """Clean HTML tags from text"""
    if not text:
        return ""
    # Remove HTML tags
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def generate_html(news_data: List[Dict[str, Any]], keywords: List[str]) -> str:
    """Generate HTML content for GitHub Pages"""
    keyword_groups = group_news_by_keywords(news_data, keywords)
    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>科技新闻聚合 - RSS精选</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 
                        'Segoe UI', 'PingFang SC', 
                        'Hiragino Sans GB', 'Microsoft YaHei', 
                        sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 0;
            text-align: center;
            margin-bottom: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        .stats {{
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-top: 20px;
            flex-wrap: wrap;
        }}
        .stat-item {{
            text-align: center;
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            display: block;
        }}
        .keyword-section {{
            background: white;
            margin-bottom: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .keyword-header {{
            background: #4CAF50;
            color: white;
            padding: 15px 20px;
            font-size: 1.3em;
            font-weight: bold;
        }}
        .news-list {{
            padding: 0;
        }}
        .news-item {{
            padding: 20px;
            border-bottom: 1px solid #eee;
            transition: background-color 0.3s;
        }}
        .news-item:hover {{
            background-color: #f9f9f9;
        }}
        .news-item:last-child {{
            border-bottom: none;
        }}
        .news-title {{
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 8px;
        }}
        .news-title a {{
            color: #2c3e50;
            text-decoration: none;
        }}
        .news-title a:hover {{
            color: #667eea;
            text-decoration: underline;
        }}
        .news-meta {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 10px;
        }}
        .news-description {{
            color: #555;
            line-height: 1.5;
            margin-bottom: 10px;
        }}
        .news-tags {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }}
        .tag {{
            background: #e3f2fd;
            color: #1976d2;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
        }}
        .source-tag {{
            background: #fff3e0;
            color: #f57c00;
        }}
        .category-tag {{
            background: #e8f5e8;
            color: #388e3c;
        }}
        .footer {{
            text-align: center;
            padding: 40px 0;
            color: #666;
            border-top: 1px solid #ddd;
            margin-top: 40px;
        }}
        .update-time {{
            background: white;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
            margin-bottom: 20px;
        }}
        @media (max-width: 768px) {{
            .container {{
                padding: 10px;
            }}
            h1 {{
                font-size: 2em;
            }}
            .stats {{
                gap: 20px;
            }}
            .news-item {{
                padding: 15px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>科技新闻聚合</h1>
            <p class="subtitle">基于关键词的智能新闻筛选与聚合</p>
            <div class="stats">
                <div class="stat-item">
                    <span class="stat-number">{len(news_data)}</span>
                    <span>篇精选文章</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{len(keyword_groups)}</span>
                    <span>个关键词</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{len(set([news.get('source', 'Unknown') for news in news_data]))}</span>
                    <span>个来源</span>
                </div>
            </div>
        </header>
        <div class="update-time">
            <strong>最后更新：</strong>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (UTC+8)
        </div>
"""
    # Add keyword sections
    for keyword, news_list in sorted(keyword_groups.items(), key=lambda x: len(x[1]), reverse=True):
        html_content += f"""
        <div class="keyword-section">
            <div class="keyword-header">
                {keyword} ({len(news_list)} 篇)
            </div>
            <div class="news-list">
"""
        for news in news_list:
            title = clean_html(news.get('title', '无标题'))
            link = news.get('link', '#')
            description = clean_html(news.get('description', ''))
            source = news.get('source', '未知来源')
            category = news.get('category', '未分类')
            published = format_date(news.get('published', ''))
            html_content += f"""
                <div class="news-item">
                    <div class="news-title">
                        <a href="{link}" target="_blank" rel="noopener noreferrer">{title}</a>
                    </div>
                    <div class="news-meta">
                        📅 {published} | 🏢 {source}
                    </div>
                    <div class="news-description">
                        {truncate_text(description, 300)}
                    </div>
                    <div class="news-tags">
                        <span class="tag source-tag">{source}</span>
                        <span class="tag category-tag">{category}</span>
                    </div>
                </div>
"""
        html_content += """
            </div>
        </div>
"""
    html_content += """
        <div class="footer">
            <p>由 RSS 新闻聚合器自动生成 | 数据来源：各大科技媒体 RSS 订阅源</p>
            <p>更新时间：每6小时自动更新一次</p>
        </div>
    </div>
</body>
</html>
"""
    return html_content


def save_html_to_pages(html_content: str) -> bool:
    """
    将HTML内容保存到GitHub Pages所需的目录
    保存路径为docs/index.html，该目录是GitHub Pages默认的发布目录
    如果目录不存在会自动创建
    @param {str} html_content - 要保存的HTML内容
    @return {bool} 保存成功返回True，失败返回False
    """
    try:
        # 创建docs目录（如果不存在）
        # GitHub Pages默认使用docs目录作为发布源
        os.makedirs("docs", exist_ok=True)
        # 保存HTML内容到docs/index.html
        with open("docs/index.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        logging.info("✅ GitHub Pages HTML 已生成并保存到 docs/index.html")
        return True
    except Exception as e:
        logging.error(f"保存HTML文件失败: {str(e)}")
        return False


def main():
    """
    主函数：生成GitHub Pages的HTML页面
    流程：
    1. 加载筛选后的新闻数据
    2. 加载关键词配置
    3. 生成HTML内容
    4. 保存HTML到docs目录
    如有任何步骤失败，记录错误并退出程序
    """
    # 配置logging模块
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    try:
        logging.info("开始生成GitHub Pages...")
        # 加载筛选后的新闻数据
        news_data = load_filtered_news()
        # 检查是否有新闻数据
        if not news_data:
            logging.warning("没有新闻数据可供生成页面")
            return
        # 加载关键词配置
        try:
            # 关键词配置文件路径：config/keywords.yaml
            keywords_config = load_config('config/keywords.yaml')
        except json.JSONDecodeError:
            logging.error("关键词配置文件JSON格式错误，请检查文件语法")
            sys.exit(1)
        except Exception as e:
            logging.error(f"加载关键词配置失败: {str(e)}")
            sys.exit(1)
        # 提取需要匹配的关键词列表
        keywords = keywords_config.get('include_keywords', [])
        if not keywords:
            logging.warning("未配置任何关键词，将无法按关键词分组")
        # 生成HTML内容
        try:
            html_content = generate_html(news_data, keywords)
        except Exception as e:
            logging.error(f"生成HTML内容失败: {str(e)}")
            sys.exit(1)
        # 保存HTML到GitHub Pages目录
        if save_html_to_pages(html_content):
            logging.info("GitHub Pages生成成功，文件已保存到docs/index.html")
        else:
            logging.error("GitHub Pages生成失败")
            sys.exit(1)
    except Exception as e:
        logging.error(f'生成HTML页面失败: {str(e)}')
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f'生成HTML页面失败: {str(e)}')
        sys.exit(1)
