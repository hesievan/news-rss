# RSS 内容收集与筛选项目

## 项目功能
1. 收集RSS源中的内容
2. 使用关键词对RSS新闻进行筛选
3. 关键词可修改可维护
4. GitHub Actions自动定时执行
5. **飞书消息通知功能**
6. **GitHub Pages 自动部署** - 实时展示筛选结果

## 项目结构
```
├── .github/
│   └── workflows/
│       └── rss-collector.yml
├── config/
│   ├── keywords.json
│   ├── rss-sources.json
│   └── feishu.json          # 飞书通知配置
├── src/
│   ├── collect_rss.py
│   ├── filter_news.py
│   ├── generate_github_pages.py  # GitHub Pages生成
│   ├── utils.py
│   ├── feishu_notifier.py   # 飞书通知模块
│   └── notify.py            # 通知集成脚本
├── docs/                    # GitHub Pages静态文件
│   ├── index.html          # 主页面
│   └── README.md           # 部署说明
├── output/
│   ├── raw_news.json
│   ├── filtered_news.json
│   └── summary.json
├── requirements.txt
├── run.py                   # 一键运行脚本
└── README.md
```

## 🚀 新增功能：GitHub Pages 实时展示

### 功能特色
- 📊 **实时统计**：显示文章数量、关键词数量、来源数量
- 🏷️ **关键词分组**：新闻按匹配的关键词智能分组
- 🔗 **直达链接**：点击标题可直接访问原文
- 📱 **响应式设计**：支持桌面和移动设备
- 🔄 **自动更新**：每6小时自动同步最新内容

### 访问地址
部署成功后，可通过以下地址访问：
```
https://[你的用户名].github.io/[仓库名]/
```

### 页面预览
- 顶部统计卡片显示实时数据
- 按关键词分组展示新闻
- 每条新闻包含标题、摘要、来源、发布时间
- 点击标题可直接跳转到原文

## 使用方法

### 1. 基础配置
- **RSS源配置**: 编辑 `config/rss-sources.json`
- **关键词配置**: 编辑 `config/keywords.json`

### 2. GitHub Pages 配置
1. 在GitHub仓库的 Settings > Pages 中启用GitHub Pages
2. 选择部署源为 "GitHub Actions"
3. 工作流会自动部署到 `docs/` 目录

### 3. 飞书通知配置

#### 方式一：GitHub Actions配置
1. 在GitHub仓库的 Settings > Secrets and variables > Actions 中添加：
   - `FEISHU_WEBHOOK_URL`: 你的飞书机器人webhook地址

#### 方式二：本地配置
1. 编辑 `config/feishu.json`:
   ```json
   {
     "webhook_url": "https://open.feishu.cn/open-apis/bot/v2/hook/你的webhook地址",
     "notification_settings": {
       "enabled": true,
       "message_type": "card",
       "max_news_per_message": 10,
       "include_summary": true
     }
   }
   ```
2. 或者设置环境变量:
   ```bash
   export FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/你的webhook地址"
   ```

### 4. 飞书机器人设置
1. 在飞书群聊中添加自定义机器人
2. 获取webhook地址
3. 配置安全设置（可选）

## 本地测试

### 基础测试
```bash
pip install -r requirements.txt
python src/collect_rss.py
python src/filter_news.py
python src/generate_github_pages.py  # 生成GitHub Pages
```

### 飞书通知测试
```bash
# 设置webhook地址后测试
python src/notify.py

# 或者使用一键脚本
python run.py
```

## GitHub Actions自动化
- **每6小时**自动运行RSS收集和筛选
- **自动部署**到GitHub Pages
- **自动提交**结果到仓库
- **自动发送**飞书通知（如已配置webhook）

## 环境变量
- `FEISHU_WEBHOOK_URL`: 飞书机器人webhook地址
- 其他配置优先使用环境变量，其次使用配置文件

## 故障排除
1. **GitHub Pages未更新**: 检查Actions运行状态
2. **通知未发送**: 检查webhook地址是否正确
3. **消息格式错误**: 检查 `config/feishu.json` 配置
4. **网络问题**: 确保能访问GitHub和飞书服务器
5. **权限问题**: 检查飞书机器人是否有发送权限

## 更新日志
- **v3.0**: 新增GitHub Pages实时展示功能
- **v2.0**: 新增飞书消息通知功能
- **v1.0**: 基础RSS收集和筛选功能
