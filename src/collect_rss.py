#!/usr/bin/env python3
import feedparser
import json
import os
import sys
import time
import requests
import logging
from datetime import datetime, timedelta
from diskcache import Cache
from utils import load_config, save_json_data, format_datetime

def collect_rss_feeds():
    """收集RSS源内容"""
    # 加载配置
    rss_sources = load_config('config/rss-sources.json')
    health_config = load_config('config/health-check.json')
    health_status = load_config('config/rss-health-status.json') or {}
    
    # 用于记录无效RSS源
    invalid_sources = []
    
    if not rss_sources:
        logging.error("未找到RSS源配置")
        return []
    
    # 健康检查功能开关
    health_check_enabled = health_config.get('enabled', False)
    failure_threshold = health_config.get('failure_threshold', 3)
    check_interval = timedelta(hours=health_config.get('check_interval_hours', 24))
    timeout = health_config.get('timeout_seconds', 10)
    auto_disable = health_config.get('auto_disable', True)
    
    all_news = []
    current_time = datetime.now()
    
    for source in rss_sources:
        name = source.get('name', '未知源')
        url = source.get('url', '')
        category = source.get('category', 'general')
        enabled = source.get('enabled', True)
        
        # 如果源已手动禁用，跳过处理
        if not enabled:
            logging.info(f"源 {name} 已手动禁用，跳过处理")
            continue
            
        # 健康检查功能处理
        if health_check_enabled:
            # 获取源的健康状态
            source_status = health_status.get(url, {
                'failures': 0,
                'last_check': None,
                'disabled': False,
                'last_disabled_time': None
            })
            
            # 如果源已被自动禁用，检查是否超过检查间隔
            if source_status['disabled']:
                if source_status['last_disabled_time']:
                    last_disabled = datetime.fromisoformat(source_status['last_disabled_time'])
                    if current_time - last_disabled < check_interval:
                        logging.info(f"源 {name} 因多次失败已被自动禁用，跳过处理")
                        continue
                    else:
                        # 超过检查间隔，尝试重新启用并检查
                        logging.info(f"源 {name} 自动禁用时间已过，尝试重新检查")
                        source_status['disabled'] = False
                        source_status['failures'] = 0
                else:
                    # 没有禁用时间记录，视为需要重新检查
                    source_status['disabled'] = False
                    source_status['failures'] = 0
            
            # 执行健康检查
            try:
                # 发送HEAD请求检查URL是否可达
                response = requests.head(url, timeout=timeout, allow_redirects=True)
                if response.status_code < 400:
                    # URL可达，重置失败计数
                    source_status['failures'] = 0
                    source_status['last_check'] = current_time.isoformat()
                    logging.debug(f"源 {name} 健康检查通过")
                else:
                    # HTTP状态码错误
                    raise Exception(f"HTTP状态码错误: {response.status_code}")
            except Exception as e:
                # 健康检查失败
                source_status['failures'] += 1
                source_status['last_check'] = current_time.isoformat()
                logging.warning(f"源 {name} 健康检查失败 ({source_status['failures']}/{failure_threshold}): {str(e)}")
                
                # 达到失败阈值，自动禁用
            if source_status['failures'] >= failure_threshold and auto_disable:
                source_status['disabled'] = True
                source_status['last_disabled_time'] = current_time.isoformat()
                logging.error(f"源 {name} 连续失败 {failure_threshold} 次，已自动禁用")
                health_status[url] = source_status
                invalid_sources.append({
                    'name': name,
                    'url': url,
                    'reason': f'健康检查失败{source_status["failures"]}次',
                    'timestamp': current_time.isoformat()
                })
                continue
            
            # 更新健康状态
            health_status[url] = source_status
            
            # 如果检查后被禁用，跳过处理
            if source_status['disabled']:
                continue
        
        # 现有RSS收集逻辑
        if not url:
            logging.warning(f"跳过无效源: {name}")
            continue
            
        logging.info(f"正在收集: {name}")
        try:
            # 初始化缓存，设置1小时超时
            with Cache('cache/rss_feeds', timeout=3600) as cache:
                # 尝试从缓存获取
                cached_content = cache.get(url)
                if cached_content:
                    logging.info(f"从缓存获取 {name} 的内容")
                    feed = feedparser.parse(cached_content)
                else:
                    logging.info(f"从网络获取 {name} 的内容")
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()
                    content = response.text
                    # 存入缓存
                    cache.set(url, content)
                    feed = feedparser.parse(content)
            
            # 检查RSS解析错误
            if feed.bozo > 0:
                logging.warning(f"{name} RSS解析警告: {feed.bozo_exception}")
                if isinstance(feed.bozo_exception, feedparser.CharacterEncodingOverride):
                    logging.info("已自动纠正编码问题")
                else:
                    logging.error(f"{name} RSS解析失败: {feed.bozo_exception}")
                    # 解析失败也计入健康状态
                    if health_check_enabled:
                        source_status['failures'] += 1
                        health_status[url] = source_status
                    invalid_sources.append({
                        'name': name,
                        'url': url,
                        'reason': f'RSS解析失败: {feed.bozo_exception}',
                        'timestamp': current_time.isoformat()
                    })
                    continue
            
            for entry in feed.entries:
                news_item = {
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'description': entry.get('description', ''),
                    'published': entry.get('published', ''),
                    'source': name,
                    'category': category,
                    'collected_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # 尝试获取内容
                if hasattr(entry, 'content'):
                    news_item['content'] = entry.content[0].value if entry.content else ''
                else:
                    news_item['content'] = entry.get('summary', '')
                
                all_news.append(news_item)
            
            # 检查该源是否产生了0条新闻
            if not any(n['source'] == name for n in all_news):
                invalid_sources.append({
                    'name': name,
                    'url': url,
                    'reason': '0条新闻',
                    'timestamp': current_time.isoformat()
                })
                
        except Exception as e:
            logging.error(f"收集 {name} 时出错: {str(e)}")
            if health_check_enabled:
                source_status['failures'] += 1
                health_status[url] = source_status
            invalid_sources.append({
                'name': name,
                'url': url,
                'reason': f'收集出错: {str(e)}',
                'timestamp': current_time.isoformat()
            })
    
    # 保存健康状态
    if health_check_enabled:
        save_json_data(health_status, 'config/rss-health-status.json')
    
    # 保存无效RSS源信息
    if invalid_sources:
        save_json_data(invalid_sources, 'output/invalid_rss_sources.json')
    
    logging.info(f"总共收集到 {len(all_news)} 条新闻")
    return all_news

def main():
    """主函数"""
    print("开始收集RSS内容...")
    # 收集RSS内容
    news_data = collect_rss_feeds()
    if news_data:
        # 保存原始数据
        output_file = 'output/raw_news.json'
        if save_json_data(news_data, output_file):
            print(f"原始数据已保存到: {output_file}")
        else:
            print("保存原始数据失败")
            sys.exit(1)
    else:
        print("未收集到任何新闻")
        sys.exit(1)

if __name__ == "__main__":
    main()
