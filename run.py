#!/usr/bin/env python3
"""
一键运行脚本
"""
import subprocess
import sys
import os

def run_command(command, description):
    """运行命令并处理错误"""
    print(f"\n{'='*50}")
    print(f"正在执行: {description}")
    print(f"命令: {command}")
    print('='*50)
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"错误: {e}")
        if e.stderr:
            print(f"错误信息: {e.stderr}")
        return False

def main():
    """主函数"""
    print("开始RSS内容收集与筛选...")
    
    # 检查Python环境
    if not run_command("python --version", "检查Python版本"):
        sys.exit(1)
    
    # 安装依赖
    if not run_command("pip install -r requirements.txt", "安装依赖"):
        sys.exit(1)
    
    # 创建输出目录
    os.makedirs('output', exist_ok=True)
    
    # 收集RSS内容
    if not run_command("python src/collect_rss.py", "收集RSS内容"):
        sys.exit(1)
    
    # 过滤新闻
    if not run_command("python src/filter_news.py", "过滤新闻"):
        sys.exit(1)
    
    # 生成Markdown文件
    if not run_command("python src/generate_markdown.py", "生成Markdown文件"):
        sys.exit(1)
    
    # 发送飞书通知
    print("\n" + "="*50)
    print("正在发送飞书通知...")
    run_command("python src/notify.py", "发送飞书通知")
    
    print("\n" + "="*50)
    print("执行完成！")
    print("结果文件:")
    print("- output/raw_news.json: 原始收集的新闻")
    print("- output/filtered_news.json: 过滤后的新闻")
    print("- output/summary.json: 摘要报告")
    print("- output/raw_news.md: 原始新闻Markdown格式")
    print("- output/filtered_news.md: 过滤后新闻Markdown格式")
    print("- 飞书通知已发送 (如已配置)")
    print("="*50)

if __name__ == "__main__":
    main()
