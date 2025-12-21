# 每日新闻抓取与AI翻译总结系统

这是一个自动化工具，用于从BBC News抓取每日新闻，并使用大语言模型（支持OpenAI格式API）翻译成中文并生成详细摘要。

## 🚀 功能特点

- **多源新闻抓取**: 支持从BBC News抓取头条、科技、商业、体育等多个类别的新闻
- **AI智能处理**: 使用大语言模型API进行翻译和详细总结（可配置任何兼容OpenAI格式的服务）
- **多格式输出**: 支持生成Markdown和HTML格式的报告
- **自动推送**: 可选的邮件通知和Slack消息推送
- **定时执行**: 可通过cron或systemd设置每天自动运行

## 📁 项目结构

```
├── config.py              # 配置文件（需先填写你的API信息）
├── main.py               # 主脚本入口
├── news_scraper.py       # 新闻爬虫模块
├── ai_processor.py       # AI翻译总结模块
├── output_formatter.py   # 输出格式化模块
└── requirements.txt      # Python依赖包列表
```

## 🔧 安装配置

### 1. 安装依赖

```bash
cd /code/py/news

# 创建Python虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置API参数

编辑 `config.py` 文件，填写以下必填信息：

```python
# API基础URL（根据你使用的服务商填写）
LLM_API_BASE_URL = "https://api.example.com/v1"

# API密钥（从服务商获取）
LLM_API_KEY = "your-api-key-here"

# 模型名称
LLM_MODEL_NAME = "your-model-name"
```

#### 常用服务商配置示例：

**Moonshot AI (月之暗面)**
```python
LLM_API_BASE_URL = "https://api.moonshot.cn/v1"
LLM_API_KEY = "sk-xxxxxxxxxxxxxx"
LLM_MODEL_NAME = "moonshot-v1-8k"  # 或 moonshot-v1-32k
```

**OpenAI**
```python
LLM_API_BASE_URL = "https://api.openai.com/v1"
LLM_API_KEY = "sk-xxxxxxxxxxxxxx"
LLM_MODEL_NAME = "gpt-4"  # 或 gpt-3.5-turbo
```

**智谱AI (ChatGLM)**
```python
LLM_API_BASE_URL = "https://open.bigmodel.cn/api/paas/v4"
LLM_API_KEY = "your-api-key"
LLM_MODEL_NAME = "glm-4"  # 或 glm-4-flash
```

**DeepSeek**
```python
LLM_API_BASE_URL = "https://api.deepseek.com/v1"
LLM_API_KEY = "your-api-key"
LLM_MODEL_NAME = "deepseek-chat"
```

### 3. 配置其他可选功能（可选）

#### 邮件推送配置

编辑 `config.py`：

```python
# SMTP服务器配置（以Gmail为例）
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "your-email@gmail.com"
SMTP_PASSWORD = "your-app-password"  # Gmail需要使用应用专用密码
TO_EMAIL = "recipient@example.com"
```

#### Slack推送配置

在Slack中创建Incoming Webhook，然后编辑 `config.py`：

```python
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/xxxxx/xxxxx/xxxxx"
SLACK_CHANNEL = "#daily-news"  # 或 @username
```

## 🎯 使用方法

### 手动运行

```bash
# 确保在正确的目录
cd /code/py/news

# 激活虚拟环境
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 运行主脚本
python main.py
```

程序会按顺序执行：
1. 抓取BBC新闻（多个类别）
2. 调用AI API翻译和总结
3. 生成Markdown和HTML报告
4. 发送邮件和Slack通知（如已配置）

**注意**：首次运行时，需要先正确配置 `config.py` 中的API参数，否则会提示配置错误。

### 定时自动执行

#### 方式一：使用cron（推荐Linux）

编辑crontab：
```bash
crontab -e
```

添加以下行（每天上午8点运行）：
```bash
0 8 * * * cd /code/py/news && /full/path/to/venv/bin/python main.py >> /code/py/news/logs/cron.log 2>&1
```

#### 方式二：使用systemd定时器（Linux）

1. 创建服务文件 `/etc/systemd/system/news-scraper.service`：

```ini
[Unit]
Description=Daily News Scraper and AI Summarizer
After=network.target

[Service]
Type=oneshot
WorkingDirectory=/code/py/news
ExecStart=/full/path/to/venv/bin/python /code/py/news/main.py
User=your-username
```

2. 创建定时器文件 `/etc/systemd/system/news-scraper.timer`：

```ini
[Unit]
Description=Run news scraper daily at 8:00 AM
Requires=news-scraper.service

[Timer]
OnCalendar=*-*-* 08:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

3. 启用并启动定时器：
```bash
sudo systemctl daemon-reload
sudo systemctl enable news-scraper.timer
sudo systemctl start news-scraper.timer
```

## 📊 输出示例

### Markdown报告

```markdown
# 每日新闻摘要 - 2024-01-15

**生成时间**: 2024-01-15 08:05:30

## 目录

1. [某科技公司发布新产品](#news-1)
2. [全球经济形势分析](#news-2)
...

---

## 某科技公司发布新产品

**类别**: 技术 | **原文链接**: [点击访问](https://www.bbc.com/news/...)

### 中文标题：创新突破 - 引领未来科技

- 📌 公司宣布推出革命性产品
- 📌 产品特点：更快、更智能、更环保
- 📌 预计将在下季度正式上市

详细内容：
...（约1000字详细摘要）

---
```

HTML报告会生成美观的网页版，包含目录、导航等功能。

## ⚙️ 配置参数说明

### 新闻抓取配置

```python
# 要抓取的BBC新闻类别
BBC_CATEGORIES = {
    "头条新闻": "/",
    "科技": "/technology",
    "商业": "/business",
    "体育": "/sport",
}

# 每个类别抓取的新闻数量（建议3-5条）
NEWS_PER_CATEGORY = 5

# RSS订阅源（可选）
ENABLE_RSS_SOURCES = True
RSS_SOURCES_FILE = "./信息源/news.md"  # 每行包含一个RSS链接，可在链接前写名称
RSS_FEEDS = [
    # {"name": "示例RSS", "url": "https://example.com/rss.xml", "max_items": 5},
]
RSS_PER_FEED = 5

# 请求配置（避免请求过快被封）
REQUEST_TIMEOUT = 30      # 超时时间（秒）
MAX_RETRIES = 3           # 请求失败重试次数
REQUEST_DELAY = 1         # 请求间隔（秒）
```

### AI处理配置

```python
# 摘要长度配置（目标和最小值）
SUMMARY_MAX_WORDS = 1000
SUMMARY_MIN_WORDS = 800

# AI翻译提示模板（可自定义）
TRANSLATION_PROMPT = """请对以下英文新闻标题和正文进行翻译和总结：

标题：{title}
正文：{content}

要求：
1. 将标题翻译成准确、简洁的中文
2. 将正文翻译成流畅自然的中文
3. 提供详细的内容摘要，约{summary_words}字左右
4. 摘要应包含新闻的关键信息：事件、时间、地点、人物、原因和影响
5. 使用Markdown格式输出，包含：
   - 中文标题（一级标题）
   - 要点总结（项目符号列表）
   - 详细内容（段落）
"""
```

### 输出配置

```python
# 输出目录
OUTPUT_DIR = "./output"

# 输出文件名格式（{date}将替换为实际日期）
MARKDOWN_FILENAME = "daily_news_{date}.md"
HTML_FILENAME = "daily_news_{date}.html"
```

## 🔍 故障排查

### 常见问题1：API配置验证失败

**症状**：程序提示"请先在config.py中配置..."

**解决方法**：确保已填写完整的API配置：
- LLM_API_BASE_URL
- LLM_API_KEY
- LLM_MODEL_NAME

### 常见问题2：爬虫抓取失败

**症状**：无法获取BBC新闻

**解决方法**：
1. 检查网络连接是否正常
2. 确保可以访问BBC.com
3. 增加REQUEST_DELAY值，避免请求过快

### 常见问题3：AI处理超时或速率限制

**症状**：API调用失败或需要很长时间

**解决方法**：
1. 检查API余额是否充足
2. 减小NEWS_PER_CATEGORY的值，减少处理的条目数
3. 增加REQUEST_DELAY的值，降低请求频率
4. 选择更快的模型降低token消耗

### 常见问题4：邮件发送失败

**症状**：SMTP错误

**解决方法**：
1. 检查SMTP服务器地址和端口是否正确
2. 对于Gmail，需要使用"应用专用密码"代替常规密码
3. 确保邮箱已开启SMTP功能

## 📋 API Token估算

根据不同的模型和处理的新闻数量，token消耗如下（估算）：

| 新闻数量 | 输入token | 输出token | 总计(8k模型) | 总计(32k模型) |
|---------|----------|----------|------------|-------------|
| 5条     | ~10k     | ~5k      | ~15k       | ~15k        |
| 10条    | ~20k     | ~10k     | ~30k       | ~30k        |
| 20条    | ~40k     | ~20k     | ~60k       | ~60k        |

**建议**：
- 使用8k或32k模型足够处理每日20条新闻
- 如需更长内容，可选择128k模型

## 🔄 更新日志

- 2025年11月23日: 初始版本发布
  - 支持BBC多类别新闻抓取
  - 支持OpenAI格式API
  - 生成Markdown和HTML报告
  - 支持邮件和Slack推送

## 📄 许可证

本项目仅供学习和个人使用。请遵守BBC的使用条款和相关API服务商的规定。

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📞 支持

如有问题，请：
1. 先查看本README的故障排查部分
2. 检查 `logs/news_scraper.log` 日志文件
3. 提交Issue并附上相关日志

---

**注意**：使用本程序抓取BBC新闻内容时，请遵守BBC的使用条款和版权规定。建议设置合理的请求频率，避免对BBC服务器造成负担。
Disclaimer / 说明
本项目部分代码由 AI (ChatGPT/Claude/Copilot) 辅助生成。我已尽力测试并修复 bug，但作为初学者，代码可能仍有不足之处。欢迎大佬们提 Issue 或 PR 指正！
(This project was built with the assistance of AI tools. While I have tested the code, suggestions for improvement are highly welcome!)
