#!/usr/bin/env python3
"""
飞书通知测试脚本
"""
import os
import sys
from src.feishu_notifier import FeishuNotifier

def test_feishu_notification():
    """测试飞书通知功能"""
    print("🧪 测试飞书通知功能")
    print("=" * 50)
    
    # 检查webhook配置
    webhook_url = os.getenv('FEISHU_WEBHOOK_URL')
    if not webhook_url:
        print("❌ 未找到飞书webhook配置")
        print("请设置环境变量 FEISHU_WEBHOOK_URL")
        print("或编辑 config/feishu.json 文件")
        return False
    
    try:
        # 创建测试数据
        test_news = [
            {
                "title": "测试新闻标题1",
                "link": "https://example.com/news1",
                "description": "这是一条测试新闻的描述内容，用于验证飞书通知功能是否正常工作。",
                "published": "2025-07-24 14:30:00",
                "source": "测试来源",
                "category": "科技"
            },
            {
                "title": "测试新闻标题2",
                "link": "https://example.com/news2",
                "description": "这是第二条测试新闻，包含一些技术关键词如AI、机器学习等。",
                "published": "2025-07-24 14:25:00",
                "source": "测试博客",
                "category": "人工智能"
            }
        ]
        
        test_summary = {
            'date': '2025-07-24',
            'total_collected': 25,
            'filtered_count': 2,
            'sources': ['测试来源', '测试博客'],
            'keywords': ['AI', '机器学习', '测试']
        }
        
        # 创建通知器
        notifier = FeishuNotifier(webhook_url)
        
        # 发送测试消息
        print("📤 正在发送测试消息...")
        message = notifier.create_news_card(test_news, test_summary)
        success = notifier.send_message(message)
        
        if success:
            print("✅ 测试消息发送成功！")
            print("请检查飞书群聊是否收到测试通知")
        else:
            print("❌ 测试消息发送失败")
            
        return success
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        return False

if __name__ == "__main__":
    success = test_feishu_notification()
    sys.exit(0 if success else 1)
