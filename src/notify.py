#!/usr/bin/env python3
"""
飞书通知集成脚本
用于在RSS收集和筛选后发送通知
"""
import os
import sys
import logging
from datetime import datetime

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feishu_notifier import FeishuNotifier
from utils import load_json_config


def load_feishu_config():
    """加载飞书配置"""
    config_path = "config/feishu.json"
    if os.path.exists(config_path):
        return load_json_config(config_path)
    return {}


def should_send_notification(config: dict) -> bool:
    """检查是否应该发送通知"""
    notification_settings = config.get('notification_settings', {})
    return notification_settings.get('enabled', True)


def create_notification_summary():
    """创建通知摘要"""
    try:
        # 加载筛选后的新闻
        filtered_news = load_json_config("output/filtered_news.json")
        raw_news = load_json_config("output/raw_news.json")
        if not filtered_news:
            return None
        # 收集统计信息
        sources = list(set(item.get('source', '未知') for item in filtered_news))
        keywords = load_json_config("config/keywords.json")
        summary = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'total_collected': len(raw_news) if raw_news else 0,
            'filtered_count': len(filtered_news),
            'sources': sources,
            'keywords': keywords.get('include_keywords', [])
        }
        return summary
    except Exception as e:
        print(f"创建通知摘要时出错: {e}")
        return None


def main():
    """主函数"""
    print("开始发送飞书通知...")
    # 加载配置
    config = load_feishu_config()
    # 检查是否启用通知
    if not should_send_notification(config):
        print("飞书通知已禁用，跳过发送")
        return
    # 检查webhook配置
    webhook_url = config.get('webhook_url') or os.getenv('FEISHU_WEBHOOK_URL')
    if not webhook_url:
        print("错误: 未配置飞书webhook地址")
        print("请在 config/feishu.json 中设置 webhook_url 或设置 "
              "FEISHU_WEBHOOK_URL 环境变量")
        return
    try:
        # 设置环境变量
        os.environ['FEISHU_WEBHOOK_URL'] = webhook_url
        
        # 创建通知器
        notifier = FeishuNotifier()
        # 检查是否有筛选后的新闻
        if not os.path.exists("output/filtered_news.json"):
            print("未找到筛选后的新闻文件，跳过通知")
            return
        # 发送通知
        success = notifier.notify_filtered_news("output/filtered_news.json")
        if success:
            print("飞书通知发送成功")
        else:
            print("飞书通知发送失败")
            logging.warning(
                "飞书卡片消息发送失败，尝试发送文本消息"
            )
    except Exception as e:
        print(f"发送飞书通知时出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
