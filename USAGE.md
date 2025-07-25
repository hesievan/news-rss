# 📖 RSS智能新闻系统完整使用指南

## 🎯 飞书通知功能完整指南

### 1️⃣ 飞书机器人创建步骤

#### 📱 创建飞书群聊机器人
**详细步骤：**
1. 打开飞书，进入目标群聊
2. 点击右上角的 `群设置` → `群机器人` → `添加机器人`
3. 选择 `自定义机器人`
4. 设置机器人名称（建议：`RSS新闻助手`）
5. 上传头像（可选，建议使用项目logo）
6. 点击 `完成`，复制webhook地址
   - 格式：`https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxxxxxxx`

#### 🔐 配置安全设置（强烈推荐）
**安全选项：**
- **自定义关键词**：设置关键词如"RSS"、"新闻"、"科技"
- **IP白名单**：添加GitHub Actions的IP范围（可选）
- **签名验证**：使用签名密钥（高级用户）

### 2️⃣ 配置方式详解

#### 🌟 方式A：GitHub Secrets配置（推荐）
**步骤：**
1. 进入GitHub仓库页面
2. 点击 `Settings` → `Secrets and variables` → `Actions`
3. 点击 `New repository secret`
4. 填写信息：
   - **Name**: `FEISHU_WEBHOOK_URL`
   - **Value**: 粘贴你的飞书webhook地址
5. 点击 `Add secret` 保存

#### 📝 方式B：本地配置文件
编辑 `config/feishu.json`：
```json
{
  "webhook_url": "https://open.feishu.cn/open-apis/bot/v2/hook/你的webhook地址",
  "notification_settings": {
    "enabled": true,
    "message_type": "card",
    "max_news_per_message": 10,
    "include_summary": true,
    "notification_time": "09:00"
  },
  "message_templates": {
    "card": {
      "color": "blue",
      "title": "📰 每日科技资讯"
    }
  }
}
```

#### ⚡ 方式C：环境变量
```bash
# Linux/Mac
export FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/你的webhook地址"

# Windows PowerShell
$env:FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/你的webhook地址"

# Windows CMD
set FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/你的webhook地址
```

### 3️⃣ 测试飞书通知

#### 🚀 快速测试
```bash
# 测试飞书连接（推荐）
python test_feishu.py

# 完整流程测试
python run.py

# 带调试信息的测试
python test_feishu.py --debug
```

#### ✅ 预期测试结果
- **成功**：飞书群聊收到测试消息，包含2条测试新闻
- **失败**：终端显示错误信息，根据提示排查

### 4️⃣ 消息样式预览

#### 📋 卡片消息完整示例
```
📰 每日科技资讯 - 2025年7月24日

📊 今日数据摘要
├─ 收集新闻：156 条
├─ 筛选结果：23 条相关
├─ 来源站点：5 个
└─ 匹配关键词：8 个

🏷️ AI人工智能 (8条)
├─ 1. [OpenAI正式发布GPT-5，性能提升300%](https://...)
│  📍 36氪 | 🕐 2小时前 | 👁️ 1.2万阅读
├─ 2. [谷歌发布Gemini 2.0，多模态能力突破](https://...)
│  📍 Solidot | 🕐 3小时前 | 👁️ 8.5千阅读
└─ 3. [百度文心一言4.0发布，中文能力超越GPT-4](https://...)
   📍 虎嗅网 | 🕐 5小时前 | 👁️ 2.3万阅读

🏷️ 区块链Web3 (5条)
├─ 1. [以太坊完成坎昆升级，Gas费降低90%](https://...)
│  📍 巴比特 | 🕐 1小时前 | 👁️ 5.6千阅读
└─ 2. [比特币突破10万美元，创历史新高](https://...)
   📍 链闻 | 🕐 30分钟前 | 👁️ 12.3万阅读

[📋 查看完整报告] [⚙️ 管理订阅]
```

### 5️⃣ 高级配置详解

#### 🔧 完整配置示例
```json
{
  "webhook_url": "https://open.feishu.cn/open-apis/bot/v2/hook/xxx",
  "notification_settings": {
    "enabled": true,
    "message_type": "card",
    "max_news_per_message": 15,
    "include_summary": true,
    "notification_time": "09:00",
    "timezone": "Asia/Shanghai"
  },
  "filtering": {
    "min_score": 1,
    "max_age_hours": 24,
    "exclude_duplicates": true
  },
  "message_templates": {
    "card": {
      "color": "blue",
      "title": "📰 每日科技资讯",
      "header_image": "https://example.com/header.jpg"
    },
    "text": {
      "prefix": "🔔",
      "suffix": "—— RSS新闻助手"
    }
  },
  "formatting": {
    "date_format": "Y年m月d日",
    "time_format": "H:i",
    "timezone": "Asia/Shanghai"
  }
}
```

#### 🎨 自定义消息模板
支持以下变量：
- `{date}`: 当前日期
- `{total_news}`: 总新闻数
- `{filtered_news}`: 筛选后新闻数
- `{sources_count}`: 来源数量
- `{keywords_count}`: 关键词数量

### 6️⃣ 故障排除完全指南

#### ❌ 常见问题及解决方案

**问题1：通知未发送**
```bash
# 检查webhook地址
curl -X POST $FEISHU_WEBHOOK_URL \
  -H "Content-Type: application/json" \
  -d '{"msg_type":"text","content":{"text":"连接测试"}}'

# 检查网络
ping open.feishu.cn

# 查看日志
python test_feishu.py --debug 2>&1 | tee debug.log
```

**问题2：消息格式异常**
- **症状**：消息显示乱码或格式错乱
- **解决**：检查新闻内容是否包含特殊字符，清理HTML标签
- **命令**：
  ```bash
  python src/utils.py --clean-content
  ```

**问题3：GitHub Actions失败**
- **症状**：Actions运行失败，无通知
- **解决**：
  1. 检查Secrets配置：Settings → Secrets → FEISHU_WEBHOOK_URL
  2. 查看Actions日志：Actions → 失败的工作流 → 查看日志
  3. 验证权限：仓库 Settings → Actions → General

**问题4：消息过长被截断**
- **症状**：消息不完整，显示"..."
- **解决**：调整 `max_news_per_message` 为较小值（如5-8条）

#### 🔍 调试工具集

**1. 网络连接测试**
```bash
# 测试飞书API连通性
python -c "import requests; print(requests.get('https://open.feishu.cn').status_code)"

# 测试webhook有效性
curl -X POST $FEISHU_WEBHOOK_URL \
  -d '{"msg_type":"text","content":{"text":"网络测试"}}'
```

**2. 配置验证**
```bash
# 验证配置文件
python -c "import json; json.load(open('config/feishu.json'))"

# 检查环境变量
echo $FEISHU_WEBHOOK_URL
```

**3. 日志分析**
```bash
# 查看详细运行日志
python src/notify.py --verbose

# 保存调试日志
python test_feishu.py --debug > feishu_debug.log 2>&1
```

### 7️⃣ 最佳实践指南

#### 📈 关键词优化策略

> **注意**：当前系统仅使用新闻标题进行关键词匹配，不包含描述内容。

**基础配置：**
```json
{
  "include_keywords": [
    "AI", "人工智能", "机器学习", "深度学习",
    "区块链", "Web3", "加密货币", "DeFi",
    "云计算", "大数据", "物联网", "5G"
  ],
  "exclude_keywords": [
    "广告", "推广", "营销", "招聘", "培训"
  ],
  "min_score": 2
}
```

**高级技巧：**
- 使用同义词扩展匹配范围
- 设置负向关键词排除无关内容
- 定期分析效果并调整关键词

#### ⏰ 通知时间优化
**推荐配置：**
- **工作日**：09:00（上班前查看）
- **周末**：10:00（稍晚一些）
- **特殊时段**：避开会议高峰期

#### 👥 群组管理最佳实践
**单群组模式：**
- 一个群聊接收所有通知
- 适合小团队或个人使用

**多群组模式：**
```json
{
  "groups": {
    "技术群": {
      "webhook": "webhook1",
      "keywords": ["AI", "编程", "开源"]
    },
    "产品群": {
      "webhook": "webhook2", 
      "keywords": ["产品", "设计", "用户"]
    }
  }
}
```

### 8️⃣ 扩展功能实现

#### 🌐 多群组通知配置
**配置文件示例：**
```json
{
  "webhooks": [
    {
      "name": "技术交流群",
      "url": "https://open.feishu.cn/open-apis/bot/v2/hook/xxx1",
      "keywords": ["AI", "编程", "开源", "技术"]
    },
    {
      "name": "产品讨论群", 
      "url": "https://open.feishu.cn/open-apis/bot/v2/hook/xxx2",
      "keywords": ["产品", "设计", "用户", "体验"]
    }
  ]
}
```

#### 🎯 条件通知规则
**智能触发条件：**
- 新闻数量 ≥ 5条
- 包含高优先级关键词
- 来源质量评分 ≥ 80分
- 用户活跃度考虑

### 9️⃣ 安全与隐私

#### 🔒 安全建议
**配置安全：**
- 不要在代码仓库中硬编码webhook地址
- 使用GitHub Secrets存储敏感信息
- 定期轮换webhook地址（每3-6个月）

**权限控制：**
- 限制机器人发送权限范围
- 设置群管理员审核机制
- 监控异常消息发送

#### 🛡️ 隐私保护
- 不收集用户个人信息
- 仅处理公开的RSS内容
- 日志中不包含敏感信息

### 🔟 更新与支持

#### 🔄 版本更新
**更新检查：**
```bash
# 检查最新版本
git fetch origin
git log --oneline origin/main -5

# 更新到最新版本
git pull origin main
```

#### 📞 获取支持
**问题反馈渠道：**
1. **GitHub Issues**: [创建Issue](https://github.com/hesievan/news-rss/issues)
   - 使用模板：Bug报告、功能请求、使用问题
2. **讨论区**: GitHub Discussions
3. **文档**: 查看Wiki页面获取详细文档

#### 📋 问题报告模板
```markdown
## 问题描述
简要描述遇到的问题

## 环境信息
- 操作系统: [例如 macOS 12.0]
- Python版本: [例如 3.9.7]
- 项目版本: [例如 v3.0.0]

## 复现步骤
1. 步骤1
2. 步骤2
3. 步骤3

## 期望结果
描述期望的行为

## 实际结果
描述实际发生的行为

## 日志信息
粘贴相关错误日志
```

---

**💡 提示：本指南持续更新，建议收藏以便查阅最新内容！**
