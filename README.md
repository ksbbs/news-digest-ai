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
├── requirements.txt      # Python依赖包列表
├── output/               # 运行产物输出目录
├── logs/                 # 日志文件目录
└── 信息源/news.md        # 额外信息源清单
```

## 🔧 快速开始

### 1. 环境准备
确保你的系统中已安装 Python 3.9+。在 Debian 13 上，你可以通过以下命令准备环境：

```bash
# 更新系统并安装必要组件
sudo apt update && sudo apt install -y python3-venv python3-pip git

# 克隆项目
git clone https://github.com/your-repo/digest-ai.git
cd digest-ai/news-digest-ai
```

### 2. 安装依赖
建议使用虚拟环境以避免依赖冲突：

```bash
# 创建并激活虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装核心依赖
pip install -r requirements.txt
```

### 3. 配置系统
项目使用 `config.py` 进行集中管理。你需要从模板创建一个真实的配置文件：

```bash
cp config.example.py config.py
```

编辑 `config.py`，重点修改以下部分：
- **必填**：`LLM_API_KEY`、`LLM_API_BASE_URL` 和 `LLM_MODEL_NAME`。
- **新闻源**：在 `BBC_CATEGORIES` 中调整你感兴趣的板块。
- **RSS 扩展**：将 `ENABLE_RSS_SOURCES` 设为 `True`，并在 `信息源/news.md` 中按行添加自定义 RSS 地址。
- **通知**：如需推送，配置 `SMTP`（邮件）或 `SLACK_WEBHOOK_URL`。

## 🎯 运行指南

### 手动执行
在激活虚拟环境的状态下，直接运行主程序：

```bash
python main.py
```

程序启动后会自动执行以下验证与流程：
1. **配置校验**：检查 API Key 是否有效并尝试一次轻量级连接测试。
2. **多模态抓取**：并行抓取 BBC 指定板块以及 `news.md` 中定义的 RSS 订阅源。
3. **AI 深度处理**：调用大模型进行中文翻译、核心要点提取及 800-1000 字的深度摘要。
4. **格式化输出**：在 `output/` 目录下生成同名的 `.md` 和 `.html` 报告。
5. **分发通知**：根据配置发送邮件或 Slack 消息。

### 自动化部署 (Debian/Linux)

#### 方案 A：使用 Cron 定时任务
每天早上 8:30 自动生成新闻简报：
```bash
# 打开定时任务编辑器
crontab -e

# 添加以下行（请替换为实际的项目绝对路径）
30 8 * * * cd /path/to/digest-ai/news-digest-ai && /path/to/digest-ai/news-digest-ai/venv/bin/python main.py >> /path/to/digest-ai/news-digest-ai/logs/cron.log 2>&1
```

#### 方案 B：Systemd Timer (更现代的方案)
项目根目录下提供了 systemd 配置思路：
1. 配置 `ExecStart` 指向虚拟环境中的 python 解释器。
2. 使用 `systemctl enable --now news-scraper.timer` 激活。

## 📊 产物说明
- **Markdown (`output/*.md`)**: 适合在 Obsidian、Notion 或 GitHub 中阅读，支持清晰的目录跳转。
- **HTML (`output/*.html`)**: 响应式设计，适配手机端阅读，具备精美的排版和原文链接跳转。
- **日志 (`logs/*.log`)**: 记录了抓取耗时、API 消耗及可能的报错信息。

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

## 📋 项目指南

### 项目结构与模块组织
- 代码集中在仓库根目录：`main.py` 为入口，`news_scraper.py` 负责抓取，`ai_processor.py` 负责调用模型，`output_formatter.py` 负责生成 Markdown/HTML。
- 配置示例在 `config.example.py`，实际运行需复制为 `config.py` 并填写其中的 API/推送参数。
- 依赖清单在 `requirements.txt`。
- 运行产物默认输出到 `output/`，日志写入 `logs/`（见 `config.py` 中的 `OUTPUT_DIR`、`LOG_FILE`）。
- `信息源/news.md` 保存额外的信息源清单（如需扩展抓取源可参考）。

### 构建、测试与开发命令
- 安装依赖：`python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt`
- 准备配置：`cp config.example.py config.py` 后编辑其中的 `LLM_API_*`。
- 本地运行：`python main.py`（会抓取新闻、调用模型、生成报告并可选推送）。
- 当前无构建步骤；依赖均为纯 Python 包。

### 编码风格与命名约定
- 遵循 Python PEP 8：4 空格缩进，函数/变量用 `snake_case`，类名用 `CapWords`。
- 模块文件使用小写下划线命名（如 `news_scraper.py`）。
- 未配置格式化/静态检查工具；提交前请保持代码整洁、日志信息清晰。

### 测试指南
- 目前未配置自动化测试与覆盖率要求。
- 如新增测试，建议引入 `pytest` 并放在 `tests/` 目录，文件以 `test_*.py` 命名；同时说明如何运行。

### 提交与合并请求规范
- 提交历史以简短英文动词开头的陈述句为主（如 "Include …""Update …"），建议延续这种简洁风格。
- PR 请包含：变更说明、相关配置变更（如有）、运行/手动验证结果；若影响输出格式，附示例片段。
- 不要提交 `config.py`、`.env`、`output/`、`logs/` 等包含敏感或运行产物的文件（已在 `.gitignore` 中忽略）。

### 配置与安全提示
- API Key/SMTP/Slack Webhook 属于敏感信息，仅放在本地 `config.py` 或 `.env`（如自建环境变量读取）。
- 线上或自动化环境建议使用最小权限的 API Key，并限制日志中泄露敏感字段。
