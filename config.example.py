"""
新闻抓取与AI翻译总结系统配置文件

重要提示：请在使用前填写以下配置项
"""

# ======================================================
# 大模型API配置（必填 - 需用户填写）
# ======================================================

# OpenAI格式API的Base URL
# 示例：https://api.openai.com/v1
#      https://api.moonshot.cn/v1
#      https://api.deepseek.com/v1
LLM_API_BASE_URL = "YOUR_API_BASE_URL_HERE"

# API密钥（从服务提供商获取）
LLM_API_KEY = "YOUR_API_KEY_HERE"

# 使用的模型名称
# 示例：gpt-4, gpt-3.5-turbo, moonshot-v1-8k, deepseek-chat
LLM_MODEL_NAME = "YOUR_MODEL_NAME_HERE"

# ======================================================
# BBC新闻源配置
# ======================================================

# BBC新闻基础URL
BBC_BASE_URL = "https://www.bbc.com"

# 要抓取的BBC新闻类别
# 键名：显示名称，值：URL路径
BBC_CATEGORIES = {
    "头条新闻": "/",
    "科技": "/technology",
    "商业": "/business",
    "体育": "/sport",
}

# 每个类别抓取的新闻数量
NEWS_PER_CATEGORY = 5  # 总共4个类别 × 5条 = 20条

# ======================================================
# 输出配置
# ======================================================

# 摘要语言目标（中文）
SUMMARY_LANGUAGE = "中文"

# 摘要长度设置（约1000字）
SUMMARY_MAX_WORDS = 1000
SUMMARY_MIN_WORDS = 800

# 输出目录
OUTPUT_DIR = "./output"

# 输出文件名（日期将自动添加）
MARKDOWN_FILENAME = "daily_news_{date}.md"
HTML_FILENAME = "daily_news_{date}.html"

# ======================================================
# 请求配置
# ======================================================

# User-Agent（模拟浏览器访问）
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# 请求超时时间（秒）
REQUEST_TIMEOUT = 30

# 重试次数
MAX_RETRIES = 3

# 请求间隔（秒，防止被封IP）
REQUEST_DELAY = 1

# ======================================================
# AI处理配置
# ======================================================

# 翻译和总结的prompt模板
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

请开始翻译和总结："""

# ======================================================
# 日志配置
# ======================================================

# 日志文件
LOG_FILE = "./logs/news_scraper.log"

# 日志级别: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL = "INFO"

# ======================================================
# 邮件推送配置（可选）
# ======================================================

# SMTP服务器配置
SMTP_SERVER = "smtp.gmail.com"  # 或你的邮件服务商地址
SMTP_PORT = 587
SMTP_USERNAME = "your_email@gmail.com"
SMTP_PASSWORD = "your_app_password"

# 收件人邮箱
TO_EMAIL = "recipient@example.com"

# 邮件主题
EMAIL_SUBJECT = "每日新闻摘要 - {date}"

# ======================================================
# Slack推送配置（可选）
# ======================================================

# Slack Webhook URL（在Slack工作区创建）
SLACK_WEBHOOK_URL = "YOUR_SLACK_WEBHOOK_URL_HERE"

# Slack频道
SLACK_CHANNEL = "#daily-news"
