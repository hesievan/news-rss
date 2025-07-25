import json
import os
import logging
import sys
import yaml
from jsonschema import validate
from datetime import datetime
from typing import Dict, List, Any
from logging.handlers import TimedRotatingFileHandler

# 配置日志系统
def setup_logging():
    """配置日志系统，按时间轮转生成日志文件"""
    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # 确保日志目录存在
    os.makedirs('logs', exist_ok=True)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    
    # 文件处理器，每天轮换一次日志文件
    file_handler = TimedRotatingFileHandler(
        'logs/news_rss.log',
        when='midnight',
        interval=1,
        backupCount=7,
        encoding='utf-8'
    )
    file_handler.setFormatter(log_formatter)
    
    # 获取根日志器并配置
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

# 初始化日志
setup_logging()

def load_config(file_path: str, schema_path: str = None) -> Dict[str, Any]:
    """加载配置文件（支持JSON和YAML）并可选进行Schema验证

    Args:
        file_path: 配置文件路径（.json或.yaml/.yml）
        schema_path: JSON Schema文件路径，若提供则进行验证

    Returns:
        解析后的配置数据字典，如果发生错误则返回空字典
    """
    try:
        # 根据文件扩展名选择解析方式
        ext = os.path.splitext(file_path)[1].lower()
        with open(file_path, 'r', encoding='utf-8') as f:
            if ext in ['.json']:
                config_data = json.load(f)
            elif ext in ['.yaml', '.yml']:
                config_data = yaml.safe_load(f)
            else:
                logging.error(f"不支持的配置文件格式: {ext}")
                return {}

        # 如果提供了Schema路径，则进行验证
        if schema_path and os.path.exists(schema_path):
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema = json.load(f)
            validate(instance=config_data, schema=schema)
            logging.debug(f"配置文件 {file_path} 已通过Schema验证")

        return config_data

    except FileNotFoundError:
        logging.error(f"配置文件 {file_path} 不存在")
        return {}
    except (json.JSONDecodeError, yaml.YAMLError) as e:
        logging.error(f"配置文件 {file_path} 格式错误: {str(e)}")
        return {}
    except Exception as e:
        logging.error(f"加载配置文件失败: {str(e)}")
        return {}

def save_json_data(data: Any, file_path: str) -> bool:
    """保存JSON数据到文件

    Args:
        data: 要保存的JSON数据
        file_path: 目标文件路径

    Returns:
        保存成功返回True，失败返回False
    """
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except PermissionError:
        logging.error(f"没有权限写入文件: {file_path}")
        return False
    except Exception as e:
        logging.error(f"保存文件失败: {str(e)}")
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
    """根据关键词过滤新闻（仅匹配标题）

    Args:
        news_items: 原始新闻列表
        keywords_config: 关键词配置，包含include_keywords和exclude_keywords

    Returns:
        过滤后的新闻列表
    """
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
    """格式化日期时间

    Args:
        dt: datetime对象

    Returns:
        格式化后的日期时间字符串

    Raises:
        TypeError: 如果输入不是datetime对象
    """
    if not isinstance(dt, datetime):
        logging.error(f"无效的datetime对象: {dt}")
        raise TypeError("输入必须是datetime对象")
    return dt.strftime('%Y-%m-%d %H:%M:%S')
