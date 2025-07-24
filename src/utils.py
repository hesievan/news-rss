import json
import os
from datetime import datetime
from typing import Dict, List, Any

def load_json_config(file_path: str) -> Dict[str, Any]:
    """加载JSON配置文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"配置文件 {file_path} 不存在")
        return {}
    except json.JSONDecodeError:
        print(f"配置文件 {file_path} JSON格式错误")
        return {}

def save_json_data(data: Any, file_path: str) -> bool:
    """保存JSON数据到文件"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存文件失败: {e}")
        return False

def contains_keywords(text: str, keywords: List[str]) -> bool:
    """检查文本是否包含关键词"""
    if not text:
        return False
    
    text_lower = text.lower()
    for keyword in keywords:
        if keyword.lower() in text_lower:
            return True
    return False

def filter_by_keywords(news_items: List[Dict], keywords_config: Dict[str, List[str]]) -> List[Dict]:
    """根据关键词过滤新闻（仅匹配标题）"""
    include_keywords = keywords_config.get('include_keywords', [])
    exclude_keywords = keywords_config.get('exclude_keywords', [])
    
    filtered_items = []
    
    for item in news_items:
        title = item.get('title', '')
        
        # 检查标题是否包含排除关键词
        if contains_keywords(title, exclude_keywords):
            continue
            
        # 检查标题是否包含包含关键词
        if contains_keywords(title, include_keywords):
            filtered_items.append(item)
    
    return filtered_items

def format_datetime(dt: datetime) -> str:
    """格式化日期时间"""
    return dt.strftime('%Y-%m-%d %H:%M:%S')
