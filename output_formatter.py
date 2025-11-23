"""
输出格式化模块
生成Markdown、HTML格式，并支持邮件/Slack推送
"""

import os
import re
import smtplib
import time
import logging
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, List
import json

import requests
import bleach
import config


class OutputFormatter:
    """输出格式化器类"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._ensure_output_dir()

    def _ensure_output_dir(self):
        """确保输出目录存在"""
        os.makedirs(config.OUTPUT_DIR, exist_ok=True)
        os.makedirs(os.path.dirname(config.LOG_FILE), exist_ok=True)

    def generate_markdown(self, processed_news: List[Dict], date: str = None) -> str:
        """
        生成Markdown格式的新闻报告

        Args:
            processed_news: 处理后的新闻列表
            date: 日期字符串，默认为今天

        Returns:
            Markdown内容
        """
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")

        title = f"每日新闻摘要 - {date}"

        # 生成目录
        md_content = f"# {title}\n\n"
        md_content += f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        md_content += "## 目录\n\n"

        for idx, news in enumerate(processed_news, 1):
            if news.get('processing_status') == 'success':
                original_title = news.get('original_title', '')
                md_content += f"{idx}. [{original_title}](#news-{idx})\n"

        md_content += "\n---\n\n"

        # 生成详细内容
        for idx, news in enumerate(processed_news, 1):
            original_title = news.get('original_title', '无标题')
            category = news.get('original_category', '未分类')
            url = news.get('url', '')
            translated_content = news.get('translated_content', '')

            md_content += f"## <a name=\"news-{idx}\"></a>{idx}. {original_title}\n\n"
            md_content += f"**类别**: {category} | **原文链接**: [点击访问]({url})\n\n"

            if news.get('processing_status') == 'success':
                md_content += f"{translated_content}\n\n"
            else:
                md_content += f"> **⚠️ AI处理失败**\n>\n> {translated_content}\n\n"

            md_content += "---\n\n"

        self.logger.info(f"Markdown报告生成完成（{len(processed_news)}条新闻）")
        return md_content

    def save_markdown(self, markdown_content: str, date: str = None) -> str:
        """
        保存Markdown文件

        Args:
            markdown_content: Markdown内容
            date: 日期字符串

        Returns:
            保存的文件路径
        """
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")

        filename = config.MARKDOWN_FILENAME.format(date=date)
        filepath = os.path.join(config.OUTPUT_DIR, filename)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            self.logger.info(f"Markdown文件已保存: {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"保存Markdown文件失败: {e}")
            return ""

    def generate_html(self, processed_news: List[Dict], date: str = None) -> str:
        """
        生成HTML格式的新闻报告

        Args:
            processed_news: 处理后的新闻列表
            date: 日期字符串

        Returns:
            HTML内容
        """
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")

        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>每日新闻摘要 - {date}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        .header {{
            background-color: #fff;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            color: #1a1a1a;
            font-size: 2.2em;
            margin: 0;
        }}
        .header .meta {{
            color: #888;
            margin: 10px 0 0 0;
        }}
        .toc {{
            background-color: #fff;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .toc h2 {{
            margin-top: 0;
            color: #1a1a1a;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 10px;
        }}
        .toc ol {{
            margin: 0;
            padding-left: 25px;
        }}
        .toc li {{
            margin: 8px 0;
            font-size: 1.1em;
        }}
        .toc a {{
            color: #0066cc;
            text-decoration: none;
        }}
        .toc a:hover {{
            text-decoration: underline;
        }}
        .news-item {{
            background-color: #fff;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .news-item h2 {{
            color: #1a1a1a;
            font-size: 1.8em;
            margin: 0 0 15px 0;
            padding-bottom: 15px;
            border-bottom: 1px solid #e0e0e0;
        }}
        .news-item .meta {{
            color: #666;
            margin-bottom: 20px;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 5px;
        }}
        .news-item .meta strong {{
            color: #1a1a1a;
        }}
        .news-item .content {{
            color: #444;
            font-size: 1.1em;
            line-height: 1.8;
        }}
        .news-item .content h1, .content h2, .content h3 {{
            color: #1a1a1a;
        }}
        .news-item .content ul, .content ol {{
            padding-left: 25px;
        }}
        .news-item .content li {{
            margin: 10px 0;
        }}
        .news-item .content a {{
            color: #0066cc;
            text-decoration: none;
        }}
        .news-item .content a:hover {{
            text-decoration: underline;
        }}
        .warning {{
            background-color: #fff3cd;
            border: 1px solid #ffeeba;
            border-radius: 5px;
            padding: 15px;
            margin: 15px 0;
            color: #856404;
        }}
        .warning strong {{
            color: #856404;
        }}
        hr {{
            border: none;
            border-top: 1px solid #e0e0e0;
            margin: 40px 0;
        }}
        .footer {{
            text-align: center;
            color: #888;
            margin: 50px 0 30px 0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>每日新闻摘要 - {date}</h1>
        <p class="meta">生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="toc">
        <h2>目录</h2>
        <ol>
"""

        for idx, news in enumerate(processed_news, 1):
            if news.get('processing_status') == 'success':
                original_title = news.get('original_title', '')
                html_content += f'<li><a href="#news-{idx}">{original_title}</a></li>\n'

        html_content += """
        </ol>
    </div>

    <hr>

"""

        # 生成新闻详细内容
        for idx, news in enumerate(processed_news, 1):
            original_title = news.get('original_title', '无标题')
            category = news.get('original_category', '未分类')
            url = news.get('url', '#')
            translated_content = news.get('translated_content', '')

            html_content += f'    <div class="news-item" id="news-{idx}">\n'
            html_content += f'        <h2>{original_title}</h2>\n'
            html_content += f'        <div class="meta">'
            html_content += f'<strong>类别:</strong> {category} | '
            html_content += f'<strong>原文链接:</strong> <a href="{url}" target="_blank">点击访问</a>'
            html_content += f'</div>\n'

            if news.get('processing_status') == 'success':
                # 将Markdown转换为简单的HTML
                content_html = self._markdown_to_html(translated_content)
                html_content += f'        <div class="content">{content_html}</div>\n'
            else:
                html_content += f'        <div class="warning">'
                html_content += f'<strong>⚠️ AI处理失败</strong><br><br>\n'
                html_content += f'{translated_content}</div>\n'

            html_content += '    </div>\n\n'

        html_content += """
    <hr>

    <div class="footer">
        <p>由新闻抓取与AI翻译总结系统自动生成</p>
    </div>
</body>
</html>
"""

        self.logger.info(f"HTML报告生成完成（{len(processed_news)}条新闻）")
        return html_content

    def _markdown_to_html(self, markdown_text: str) -> str:
        """
        安全的Markdown转HTML（支持基本格式）

        安全特性：
        1. 对输入进行HTML转义，防止XSS攻击
        2. 使用bleach库净化输出，只允许安全的标签和属性
        3. 对链接的href属性进行验证

        Args:
            markdown_text: Markdown文本

        Returns:
            净化后的HTML文本
        """
        import html

        # 对原始文本进行HTML转义，防止XSS
        # 注意：我们需要在转义后处理Markdown标记
        escaped_text = html.escape(markdown_text)

        # 将标题转换为HTML标题
        html_content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', escaped_text, flags=re.MULTILINE)
        html_content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html_content, flags=re.MULTILINE)

        # 将粗体转换为<strong>（输入已转义，需要匹配*&lt;*&gt;*形式）
        html_content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_content)

        # 将斜体转换为<em>
        html_content = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html_content)

        # 将链接转换为<a>（需要特别小心）
        # 这里我们先识别链接语法，然后仔细处理
        def replace_link(match):
            link_text = match.group(1)
            url = match.group(2)
            # 对链接文本进行转义（以防万一）
            safe_text = html.escape(link_text)
            # 验证URL协议，只允许http/https
            if url.startswith(('http://', 'https://')):
                return f'<a href="{url}" rel="noopener noreferrer">{safe_text}</a>'
            else:
                # 对于不安全的协议，只显示文本不创建链接
                return safe_text

        html_content = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', replace_link, html_content)

        # 将代码块转换为<pre><code>
        html_content = re.sub(r'```(.+?)```', r'<pre><code>\1</code></pre>', html_content, flags=re.DOTALL)
        html_content = re.sub(r'`(.+?)`', r'<code>\1</code>', html_content)

        # 将段落转换为<p>
        lines = html_content.split('\n')
        result_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            # 跳过空行
            if not line.strip():
                i += 1
                continue

            # 如果行已经是块级元素，直接添加
            if line.strip().startswith('<h') or line.strip().startswith('<pre>') or line.strip().startswith('<ul>') or line.strip().startswith('<ol>'):
                result_lines.append(line)
                i += 1
                continue

            # 收集段落行
            para_lines = []
            while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith('<h'):
                para_lines.append(lines[i])
                i += 1

            if para_lines:
                para = ' '.join(para_lines)
                # 检测列表
                if para.startswith('- ') or para.startswith('* '):
                    para = '<ul><li>' + para[2:] + '</li></ul>'
                elif re.match(r'^\d+\. ', para):
                    para = '<ol><li>' + para[para.index('. ') + 2:] + '</li></ol>'
                else:
                    para = '<p>' + para + '</p>'
                result_lines.append(para)

        html_content = '\n'.join(result_lines)

        # 使用bleach进行最终的HTML净化
        # 只允许安全的标签和属性
        allowed_tags = [
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'p', 'br', 'hr',
            'strong', 'em', 'b', 'i', 'u',
            'a', 'ul', 'ol', 'li',
            'pre', 'code', 'blockquote'
        ]

        allowed_attributes = {
            'a': ['href', 'title', 'rel'],
            '*': ['class', 'id']
        }

        # 净化HTML，移除危险的内容
        clean_html = bleach.clean(
            html_content,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=True  # 移除不允许的标签，而不是转义它们
        )

        return clean_html

    def save_html(self, html_content: str, date: str = None) -> str:
        """
        保存HTML文件

        Args:
            html_content: HTML内容
            date: 日期字符串

        Returns:
            保存的文件路径
        """
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")

        filename = config.HTML_FILENAME.format(date=date)
        filepath = os.path.join(config.OUTPUT_DIR, filename)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)

            self.logger.info(f"HTML文件已保存: {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"保存HTML文件失败: {e}")
            return ""

    def send_email(self, markdown_content: str, html_content: str, date: str = None) -> bool:
        """
        发送邮件（需要配置SMTP）

        Args:
            markdown_content: Markdown内容（用于正文）
            html_content: HTML内容（用于HTML邮件）
            date: 日期字符串

        Returns:
            发送成功返回True
        """
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")

        # 检查配置
        if config.SMTP_USERNAME == "your_email@gmail.com" or config.SMTP_PASSWORD == "your_app_password":
            self.logger.warning("邮件配置未设置，跳过发送")
            return False

        try:
            self.logger.info(f"正在发送邮件到: {config.TO_EMAIL}")

            msg = MIMEMultipart('alternative')
            msg['Subject'] = config.EMAIL_SUBJECT.format(date=date)
            msg['From'] = config.SMTP_USERNAME
            msg['To'] = config.TO_EMAIL

            # 纯文本版本
            part1 = MIMEText(markdown_content, 'plain', 'utf-8')
            msg.attach(part1)

            # HTML版本
            part2 = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(part2)

            # 发送邮件（使用SSL加密连接）
            # 如果使用端口465，使用SMTP_SSL；如果使用端口587，使用STARTTLS
            if config.SMTP_PORT == 465:
                server = smtplib.SMTP_SSL(config.SMTP_SERVER, config.SMTP_PORT)
            else:
                server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
                server.starttls()

            server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
            server.send_message(msg)
            server.quit()

            self.logger.info("邮件发送成功")
            return True

        except Exception as e:
            self.logger.error(f"邮件发送失败: {e}")
            return False

    def send_slack_notification(self, processed_news: List[Dict], date: str = None) -> bool:
        """
        发送Slack通知（需要配置Webhook）

        Args:
            processed_news: 处理后的新闻列表
            date: 日期字符串

        Returns:
            发送成功返回True
        """
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")

        # 检查配置
        if config.SLACK_WEBHOOK_URL == "YOUR_SLACK_WEBHOOK_URL_HERE":
            self.logger.warning("Slack Webhook未配置，跳过发送")
            return False

        try:
            self.logger.info("正在发送Slack通知...")

            # Slack消息格式
            message = {
                "channel": config.SLACK_CHANNEL,
                "username": "每日新闻助手",
                "icon_emoji": ":newspaper:",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"📰 每日新闻摘要 - {date}"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*生成时间*: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n*新闻数量*: {len(processed_news)}条"
                        }
                    }
                ]
            }

            # 添加新闻列表（仅显示标题和类别）
            news_list = "\n".join([
                f"• *{news.get('original_category', '未分类')}*: {news.get('original_title', '')[:60]}..."
                for i, news in enumerate(processed_news[:10])
            ])

            if len(processed_news) > 10:
                news_list += f"\n*及{len(processed_news) - 10}条更多新闻...*"

            message["blocks"].append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*今日新闻列表*:\n{news_list}"
                }
            })

            # 添加链接到完整报告（如果有HTML版本）
            html_file = os.path.join(config.OUTPUT_DIR, config.HTML_FILENAME.format(date=date))
            markdown_file = os.path.join(config.OUTPUT_DIR, config.MARKDOWN_FILENAME.format(date=date))

            if os.path.exists(html_file):
                report_text = f"完整报告已保存为HTML和Markdown文件"
            else:
                report_text = f"Markdown报告已保存"

            message["blocks"].append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*今日新闻列表*:\n{news_list}"
                }
            })

            # 添加链接到完整报告（如果有HTML版本）
            html_file = os.path.join(config.OUTPUT_DIR, config.HTML_FILENAME.format(date=date))
            markdown_file = os.path.join(config.OUTPUT_DIR, config.MARKDOWN_FILENAME.format(date=date))

            if os.path.exists(html_file):
                report_text = f"完整报告已保存为HTML和Markdown文件"
            else:
                report_text = f"Markdown报告已保存"

            message["blocks"].append({
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "💡 *提示*: 请检查output目录获取完整报告"
                    }
                ]
            })

            response = requests.post(
                config.SLACK_WEBHOOK_URL,
                json=message,
                timeout=30
            )

            response.raise_for_status()
            self.logger.info("Slack通知发送成功")
            return True

        except Exception as e:
            self.logger.error(f"Slack通知发送失败: {e}")
            return False
