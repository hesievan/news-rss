import json
import os
import logging
import sys
import yaml
from jsonschema import validate
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler


def setup_logging():
    """配置日志系统，按时间轮转生成日志文件"""
    log_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
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


def load_config(config_path, schema_path=None):
    """加载配置文件，支持JSON和YAML格式，并可选进行schema验证
    
    Args:
        config_path (str): 配置文件路径
        schema_path (str, optional): JSON Schema文件路径. Defaults to None.
    
    Returns:
        dict: 配置内容
    """
    if not os.path.exists(config_path):
        logging.error(f"配置文件不存在: {config_path}")
        return {}
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                config = yaml.safe_load(f)
            else:
                config = json.load(f)
    except Exception as e:
        logging.error(f"加载配置文件失败: {e}")
        return {}
    # 如果提供了schema，进行验证
    if schema_path and os.path.exists(schema_path):
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema = json.load(f)
            validate(config, schema)
        except Exception as e:
            logging.error(f"配置文件验证失败: {e}")
            return {}
    return config


def load_json_config(file_path):
    """加载JSON配置文件"""
    return load_config(file_path)


def save_json_data(data, file_path):
    """保存数据到JSON文件"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logging.error(f"保存JSON文件失败: {e}")
        return False


def contains_keywords(text, keywords):
    """检查文本是否包含关键词
    Args:
        text (str): 要检查的文本
        keywords (list): 关键词列表
    Returns:
        bool: 如果包含任一关键词返回True
    """
    if not text or not keywords:
        return False
    text_lower = text.lower()
    return any(keyword.lower() in text_lower for keyword in keywords)


def filter_by_keywords(news_list, keywords, exclude_keywords=None):
    """根据关键词筛选新闻
    Args:
        news_list (list): 新闻列表
        keywords (list): 包含关键词列表
        exclude_keywords (list, optional): 排除关键词列表. Defaults to None.
    Returns:
        list: 筛选后的新闻列表
    """
    if not news_list:
        return []
    if not keywords:
        return news_list
    filtered = []
    for news in news_list:
        title = news.get('title', '')
        description = news.get('description', '')
        content = title
        # 检查是否包含关键词
        if contains_keywords(content, keywords):
            # 检查是否包含排除关键词
            if exclude_keywords and contains_keywords(content, exclude_keywords):
                continue
            filtered.append(news)
    return filtered


def format_datetime(dt_str, input_format="%a, %d %b %Y %H:%M:%S %z",
                   output_format="%Y-%m-%d %H:%M:%S"):
    """格式化日期时间字符串
    Args:
        dt_str (str): 输入的日期时间字符串
        input_format (str): 输入格式. Defaults to "%a, %d %b %Y %H:%M:%S %z"
        output_format (str): 输出格式. Defaults to "%Y-%m-%d %H:%M:%S"
    Returns:
        str: 格式化后的日期时间字符串
    """
    try:
        dt = datetime.strptime(dt_str, input_format)
        return dt.strftime(output_format)
    except (ValueError, TypeError):
        return dt_str
