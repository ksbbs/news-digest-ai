"""
主脚本
新闻抓取与AI翻译总结的完整工作流
"""

import os
import sys
import time
import logging
from datetime import datetime
from typing import List

import config
from news_scraper import NewsScraper
from ai_processor import AIProcessor
from output_formatter import OutputFormatter


def setup_logging():
    """
    设置日志系统
    """
    # 确保日志目录存在
    log_dir = os.path.dirname(config.LOG_FILE)
    os.makedirs(log_dir, exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.LOG_FILE, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """
    主函数：执行完整的新闻抓取和AI处理流程
    """
    start_time = time.time()
    logger = logging.getLogger(__name__)

    logger.info("=" * 60)
    logger.info("每日新闻抓取与AI翻译总结系统启动")
    logger.info("=" * 60)

    try:
        # 步骤1：抓取新闻
        logger.info("\n[步骤 1/3] 开始抓取BBC新闻...")
        scraper = NewsScraper()
        raw_news = scraper.scrape_all()

        if not raw_news:
            logger.error("未抓取到任何新闻，程序退出")
            return False

        logger.info(f"成功抓取 {len(raw_news)} 条新闻")

        # 步骤2：AI翻译和总结
        logger.info("\n[步骤 2/3] 开始AI翻译和总结...")
        try:
            processor = AIProcessor()
        except ValueError as e:
            logger.error(f"AI处理器初始化失败: {e}")
            logger.error("请先在config.py中配置API相关信息")
            return False

        # 验证API配置
        if not processor.validate_config():
            return False

        processed_news = processor.process_batch(raw_news)

        if not processed_news:
            logger.error("AI处理失败，没有成功处理任何新闻")
            return False

        # 统计成功/失败数量
        success_count = len([n for n in processed_news if n.get('processing_status') == 'success'])
        logger.info(f"AI处理完成。成功: {success_count}/{len(processed_news)}")

        # 步骤3：生成输出
        logger.info("\n[步骤 3/3] 生成输出文件...")
        formatter = OutputFormatter()
        date_str = datetime.now().strftime("%Y-%m-%d")

        # 生成Markdown
        markdown_content = formatter.generate_markdown(processed_news, date_str)
        markdown_path = formatter.save_markdown(markdown_content, date_str)

        # 生成HTML
        html_content = formatter.generate_html(processed_news, date_str)
        html_path = formatter.save_html(html_content, date_str)

        # 发送通知（可选）
        if config.SMTP_USERNAME != "your_email@gmail.com":
            logger.info("\n[可选] 发送邮件通知...")
            formatter.send_email(markdown_content, html_content, date_str)
        else:
            logger.info("\n[可选] 邮件未配置，跳过发送")

        if config.SLACK_WEBHOOK_URL != "YOUR_SLACK_WEBHOOK_URL_HERE":
            logger.info("\n[可选] 发送Slack通知...")
            formatter.send_slack_notification(processed_news, date_str)
        else:
            logger.info("\n[可选] Slack未配置，跳过发送")

        # 输出总结
        execution_time = time.time() - start_time
        logger.info("\n" + "=" * 60)
        logger.info("执行完成！")
        logger.info("=" * 60)
        logger.info(f"总执行时间: {execution_time:.2f} 秒")
        logger.info(f"抓取新闻: {len(raw_news)} 条")
        logger.info(f"AI处理成功: {success_count} 条")
        logger.info(f"AI处理失败: {len(processed_news) - success_count} 条")

        if markdown_path:
            logger.info(f"Markdown文件: {markdown_path}")
        if html_path:
            logger.info(f"HTML文件: {html_path}")

        return True

    except KeyboardInterrupt:
        logger.warning("程序被用户中断")
        return False

    except Exception as e:
        logger.exception(f"程序执行出错: {e}")
        return False


def display_config_status():
    """
    显示配置状态
    """
    logger = logging.getLogger(__name__)

    logger.info("\n配置状态:")
    logger.info("-" * 40)

    # 检查API配置
    if config.LLM_API_KEY == "YOUR_API_KEY_HERE":
        logger.warning("⚠  LLM_API_KEY 未配置")
    else:
        logger.info("✓  LLM_API_KEY 已配置")

    if config.LLM_API_BASE_URL == "YOUR_API_BASE_URL_HERE":
        logger.warning("⚠  LLM_API_BASE_URL 未配置")
    else:
        logger.info("✓  LLM_API_BASE_URL 已配置")

    if config.LLM_MODEL_NAME == "YOUR_MODEL_NAME_HERE":
        logger.warning("⚠  LLM_MODEL_NAME 未配置")
    else:
        logger.info("✓  LLM_MODEL_NAME 已配置")

    # 检查邮件配置
    if config.SMTP_USERNAME == "your_email@gmail.com":
        logger.info("  邮件功能: 未配置（可选）")
    else:
        logger.info("✓ 邮件功能: 已配置")

    # 检查Slack配置
    if config.SLACK_WEBHOOK_URL == "YOUR_SLACK_WEBHOOK_URL_HERE":
        logger.info("  Slack通知: 未配置（可选）")
    else:
        logger.info("✓ Slack通知: 已配置")

    # 检查新闻类别
    logger.info(f"  新闻类别: {len(config.BBC_CATEGORIES)}个（{', '.join(config.BBC_CATEGORIES.keys())}）")
    logger.info(f"  每类数量: {config.NEWS_PER_CATEGORY}条")
    logger.info(f"  预计总数: {len(config.BBC_CATEGORIES) * config.NEWS_PER_CATEGORY}条")


if __name__ == "__main__":
    # 设置日志
    setup_logging()
    logger = logging.getLogger(__name__)

    # 显示欢迎信息
    logger.info("=" * 60)
    logger.info("每日新闻抓取与AI翻译总结系统")
    logger.info("=" * 60)

    # 显示配置状态
    display_config_status()

    # 执行主程序
    success = main()

    if success:
        logger.info("\n🎉 程序执行成功！")
        sys.exit(0)
    else:
        logger.error("\n❌ 程序执行失败，请检查日志")
        sys.exit(1)
