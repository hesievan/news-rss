#!/usr/bin/env python3
"""
GitHub Pages 设置助手
帮助用户快速配置和启用GitHub Pages功能
"""

import os
import json
from datetime import datetime

def check_github_pages_setup():
    """检查GitHub Pages设置状态"""
    print("🔍 检查GitHub Pages设置状态...")
    
    # 检查docs目录
    if os.path.exists("docs/index.html"):
        print("✅ docs/index.html 已存在")
    else:
        print("❌ docs/index.html 不存在，需要生成")
    
    # 检查工作流文件
    if os.path.exists(".github/workflows/rss-collector.yml"):
        with open(".github/workflows/rss-collector.yml", 'r', encoding='utf-8') as f:
            content = f.read()
            if "deploy-pages-artifact" in content:
                print("✅ GitHub Pages工作流已配置")
            else:
                print("❌ GitHub Pages工作流未配置")
    else:
        print("❌ 工作流文件不存在")

def generate_sample_data():
    """生成示例数据用于测试"""
    print("📝 生成示例数据...")
    
    # 创建示例新闻数据
    sample_news = [
        {
            "title": "示例新闻：AI技术取得重大突破",
            "link": "https://example.com/ai-breakthrough",
            "description": "这是一个示例新闻，展示GitHub Pages的效果。AI技术在图像识别领域取得了重大突破。",
            "published": "Wed, 24 Jul 2025 15:30:00 +0800",
            "source": "示例来源",
            "category": "tech",
            "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        {
            "title": "示例新闻：区块链技术应用扩展",
            "link": "https://example.com/blockchain-expansion",
            "description": "区块链技术在金融、医疗、供应链等多个领域得到广泛应用。",
            "published": "Wed, 24 Jul 2025 14:20:00 +0800",
            "source": "示例来源",
            "category": "tech",
            "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    ]
    
    # 保存示例数据
    os.makedirs("output", exist_ok=True)
    with open("output/filtered_news.json", "w", encoding="utf-8") as f:
        json.dump(sample_news, f, ensure_ascii=False, indent=2)
    
    print("✅ 示例数据已生成到 output/filtered_news.json")

def test_github_pages_generation():
    """测试GitHub Pages生成功能"""
    print("🧪 测试GitHub Pages生成功能...")
    
    try:
        import subprocess
        result = subprocess.run(["python", "src/generate_github_pages.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ GitHub Pages生成成功")
            print("📁 生成的文件：docs/index.html")
        else:
            print("❌ GitHub Pages生成失败")
            print("错误信息：", result.stderr)
    except Exception as e:
        print(f"❌ 测试失败：{e}")

def show_setup_instructions():
    """显示设置说明"""
    print("\n" + "="*60)
    print("🚀 GitHub Pages 设置指南")
    print("="*60)
    
    print("\n📋 设置步骤：")
    print("1. 确保代码已推送到GitHub仓库")
    print("2. 访问GitHub仓库的 Settings > Pages")
    print("3. 在 'Build and deployment' 中选择 'GitHub Actions'")
    print("4. 工作流会自动部署到 https://[用户名].github.io/[仓库名]/")
    
    print("\n🔧 手动触发：")
    print("1. 访问仓库的 Actions 标签页")
    print("2. 选择 'RSS 内容收集与筛选及GitHub Pages部署'")
    print("3. 点击 'Run workflow' 手动运行")
    
    print("\n📊 访问地址：")
    print("   https://[你的用户名].github.io/[仓库名]/")
    
    print("\n⚙️ 自定义配置：")
    print("- 修改关键词：编辑 config/keywords.json")
    print("- 调整页面样式：编辑 src/generate_github_pages.py")
    
    print("\n" + "="*60)

def main():
    """主函数"""
    print("🎯 GitHub Pages 设置助手")
    print("="*40)
    
    # 检查当前设置
    check_github_pages_setup()
    
    # 生成示例数据
    generate_sample_data()
    
    # 测试生成功能
    test_github_pages_generation()
    
    # 显示设置说明
    show_setup_instructions()

if __name__ == "__main__":
    main()
