# RSS项目使用指南

## 飞书通知功能完整使用指南

### 1. 飞书机器人创建步骤

#### 步骤1：创建飞书群聊机器人
1. 打开飞书，进入目标群聊
2. 点击群设置 → 群机器人 → 添加机器人
3. 选择"自定义机器人"
4. 设置机器人名称和头像
5. 复制webhook地址（格式：`https://open.feishu.cn/open-apis/bot/v2/hook/xxx`）

#### 步骤2：配置安全设置（推荐）
- **自定义关键词**: 设置关键词如"RSS"、"新闻"等
- **IP白名单**: 添加GitHub Actions的IP范围（可选）

### 2. 配置方式

#### 方式A：GitHub Actions配置（推荐）
1. 进入GitHub仓库 → Settings → Secrets and variables → Actions
2. 点击"New repository secret"
3. Name: `FEISHU_WEBHOOK_URL`
4. Value: 粘贴你的飞书webhook地址
5. 保存即可

#### 方式B：本地配置文件
编辑 `config/feishu.json`:
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

#### 方式C：环境变量
```bash
# Linux/Mac
export FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/你的webhook地址"

# Windows
set FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/你的webhook地址
```

### 3. 测试飞书通知

#### 快速测试
```bash
# 设置环境变量后运行
python test_feishu.py

# 或使用完整流程测试
python run.py
```

#### 预期结果
- 飞书群聊收到测试消息
- 消息包含2条测试新闻
- 显示摘要统计信息

### 4. 消息样式预览

#### 卡片消息示例
```
📰 RSS新闻精选 - 2025-07-24

📊 今日摘要
• 共收集 25 条新闻
• 筛选出 8 条相关新闻
• 来源: 36氪, Solidot, 虎嗅网
• 关键词: AI, 机器学习, 区块链

1. [英伟达市值突破4万亿美元](https://...)
   📍 36氪 | 🏷️ 科技 | 🕐 2小时前
   英伟达股价创历史新高，市值突破4万亿美元...

2. [OpenAI发布新模型](https://...)
   📍 Solidot | 🏷️ AI | 🕐 3小时前
   OpenAI今日发布了新一代AI模型...
   
[📋 查看完整报告]
```

### 5. 高级配置

#### 自定义消息模板
在 `config/feishu.json` 中可配置：
- `message_type`: "card"（卡片）或 "text"（文本）
- `max_news_per_message`: 单条消息最多显示新闻数（1-20）
- `include_summary`: 是否包含摘要信息
- `notification_time`: 每日通知时间（HH:MM格式）

#### 示例配置
```json
{
  "webhook_url": "https://open.feishu.cn/open-apis/bot/v2/hook/xxx",
  "notification_settings": {
    "enabled": true,
    "message_type": "card",
    "max_news_per_message": 15,
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

### 6. 故障排除

#### 常见问题

**问题1：通知未发送**
- 检查webhook地址是否正确
- 确认机器人是否在目标群聊中
- 查看GitHub Actions日志中的错误信息

**问题2：消息格式异常**
- 检查新闻内容是否包含特殊字符
- 确认描述文本长度是否超限
- 验证JSON配置文件格式

**问题3：GitHub Actions失败**
- 检查Secrets配置是否正确
- 确认仓库有写入权限
- 查看Actions日志获取详细错误

#### 调试方法
1. 本地运行测试脚本：
   ```bash
   python test_feishu.py
   ```

2. 查看详细日志：
   ```bash
   python src/notify.py --debug
   ```

3. 检查网络连接：
   ```bash
   curl -X POST 你的webhook_url -d '{"msg_type":"text","content":{"text":"测试连接"}}'
   ```

### 7. 最佳实践

#### 关键词优化
- 使用具体关键词提高筛选精度
- 定期更新关键词列表
- 结合排除关键词过滤无关内容

#### 通知频率
- 建议每日一次，避免过度打扰
- 可根据新闻量调整通知时间
- 周末可减少通知频率

#### 群组管理
- 为不同主题创建专用群聊
- 设置合理的群成员权限
- 定期清理无效机器人

### 8. 扩展功能

#### 多群组通知
可通过配置多个webhook实现：
```json
{
  "webhooks": [
    {"url": "webhook1", "group": "技术群"},
    {"url": "webhook2", "group": "产品群"}
  ]
}
```

#### 条件通知
可根据新闻数量或关键词匹配度决定是否发送通知。

### 9. 安全建议
- 不要在代码中硬编码webhook地址
- 定期更换webhook地址
- 使用GitHub Secrets存储敏感信息
- 限制机器人权限范围

### 10. 更新与支持
- 关注项目GitHub获取最新功能
- 提交Issue报告问题
- 参与功能讨论和改进建议
