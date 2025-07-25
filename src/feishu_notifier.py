#!/usr/bin/env python3
"""
飞书消息通知模块
基于TrendRadar项目的通知功能实现
"""
import json
import os
import requests
import time
from datetime import datetime
from typing import Dict, List, Any
from src.utils import load_json_config, format_datetime

class FeishuNotifier:
    """飞书消息通知器"""
    
    def __init__(self):
        """
        初始化飞书通知器
        """
        self.webhook_url = os.getenv('FEISHU_WEBHOOK_URL')
        if not self.webhook_url:
            raise ValueError("请设置FEISHU_WEBHOOK_URL环境变量")
    
    def send_message(self, message: Dict[str, Any]) -> bool:
        """
        发送消息到飞书
        
        Args:
            message: 消息内容
            
        Returns:
            bool: 是否发送成功
        """
        try:
            response = requests.post(
                self.webhook_url,
                json=message,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get('StatusCode') == 0:
                print(f"[{format_datetime(datetime.now())}] 飞书消息发送成功")
                return True
            else:
                print(f"[{format_datetime(datetime.now())}] 飞书消息发送失败: {result}")
                return False
                
        except Exception as e:
            print(f"[{format_datetime(datetime.now())}] 发送飞书消息时出错: {e}")
            return False
    
    def create_news_card(self, news_items: List[Dict[str, Any]], summary: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建新闻卡片消息
        
        Args:
            news_items: 新闻列表
            summary: 摘要信息
            
        Returns:
            Dict: 飞书卡片消息
        """
        # 构建卡片头部
        header = {
            "title": {
                "tag": "plain_text",
                "content": f"📰 RSS新闻精选 - {summary.get('date', datetime.now().strftime('%Y-%m-%d'))}"
            },
            "template": "blue"
        }
        
        # 构建卡片内容
        elements = []
        
        # 添加摘要信息
        summary_text = (
            f"📊 **今日摘要**\n"
            f"• 共收集 {summary.get('total_collected', 0)} 条新闻\n"
            f"• 筛选出 {summary.get('filtered_count', 0)} 条相关新闻\n"
            f"• 来源: {', '.join(summary.get('sources', []))}\n"
            f"• 关键词: {', '.join(summary.get('keywords', []))}"
        )
        
        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": summary_text
            }
        })
        
        elements.append({"tag": "hr"})
        
        # 添加新闻列表
        for idx, item in enumerate(news_items[:10], 1):  # 最多显示10条
            title = item.get('title', '无标题')
            source = item.get('source', '未知来源')
            category = item.get('category', '未分类')
            published = item.get('published', '未知时间')
            
            # 清理描述文本，限制长度
            description = item.get('description', '')
            if len(description) > 200:
                description = description[:200] + "..."
            
            # 清理HTML标签
            import re
            description = re.sub(r'<[^>]+>', '', description)
            
            news_content = (
                f"**{idx}. [{title}]({item.get('link', '#')})**\n"
                f"📍 {source} | 🏷️ {category} | 🕐 {published}\n"
                f"{description}\n"
            )
            
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": news_content
                }
            })
            
            if idx < len(news_items) and idx < 10:
                elements.append({"tag": "hr"})
        
        # 如果新闻太多，添加提示
        if len(news_items) > 10:
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"\n*... 还有 {len(news_items) - 10} 条新闻，请查看完整报告 *"
                }
            })
        
        # 添加操作按钮
        elements.append({
            "tag": "action",
            "actions": [
                {
                    "tag": "button",
                    "text": {
                        "tag": "plain_text",
                        "content": "📋 查看完整报告"
                    },
                    "type": "primary",
                    "url": "https://github.com/hesievan/rss-email"
                }
            ]
        })
        
        card = {
            "msg_type": "interactive",
            "card": {
                "header": header,
                "elements": elements
            }
        }
        
        return card
    
    def create_simple_text(self, news_items: List[Dict[str, Any]], summary: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建简单文本消息
        
        Args:
            news_items: 新闻列表
            summary: 摘要信息
            
        Returns:
            Dict: 飞书文本消息
        """
        message = f"📰 RSS新闻精选 - {summary.get('date', datetime.now().strftime('%Y-%m-%d'))}\n\n"
        message += f"📊 今日摘要：共收集 {summary.get('total_collected', 0)} 条，筛选出 {summary.get('filtered_count', 0)} 条相关新闻\n\n"
        
        for idx, item in enumerate(news_items[:5], 1):
            title = item.get('title', '无标题')
            source = item.get('source', '未知来源')
            link = item.get('link', '#')
            message += f"{idx}. [{title}]({link}) - {source}\n"
        
        if len(news_items) > 5:
            message += f"\n... 还有 {len(news_items) - 5} 条新闻"
        
        return {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": "RSS新闻精选",
                        "content": [[{
                            "tag": "text",
                            "text": message
                        }]]
                    }
                }
            }
        }
    
    def notify_filtered_news(self, filtered_news_path: str = "output/filtered_news.json") -> bool:
        """
        发送筛选后的新闻通知
        
        Args:
            filtered_news_path: 筛选新闻文件路径
            
        Returns:
            bool: 是否发送成功
        """
        try:
            # 加载筛选后的新闻
            news_items = load_json_config(filtered_news_path)
            if not news_items:
                print(f"[{format_datetime(datetime.now())}] 没有筛选到的新闻，跳过通知")
                return True
            
            # 生成摘要信息
            sources = list(set(item.get('source', '未知') for item in news_items))
            keywords = []  # 可以从配置中获取
            
            summary = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'total_collected': len(news_items),  # 这里简化处理
                'filtered_count': len(news_items),
                'sources': sources[:5],  # 限制显示数量
                'keywords': keywords
            }
            
            # 创建并发送消息
            message = self.create_news_card(news_items, summary)
            return self.send_message(message)
            
        except Exception as e:
            print(f"[{format_datetime(datetime.now())}] 发送新闻通知时出错: {e}")
            return False

def main():
    """主函数"""
    try:
        notifier = FeishuNotifier()
        success = notifier.notify_filtered_news()
        if success:
            print("飞书通知发送完成")
        else:
            print("飞书通知发送失败")
    except Exception as e:
        print(f"初始化飞书通知器失败: {e}")

if __name__ == "__main__":
    main()
