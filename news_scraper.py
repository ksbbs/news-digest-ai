"""
BBC新闻爬虫模块
负责从BBC网站抓取新闻内容
"""

import time
import logging
from typing import List, Dict
import os
import xml.etree.ElementTree as ET
import requests
from bs4 import BeautifulSoup
import re

import config


class NewsScraper:
    """BBC新闻爬虫类"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": config.USER_AGENT
        })
        self.logger = logging.getLogger(__name__)

    def fetch_page(self, url: str) -> str:
        """
        获取网页内容

        Args:
            url: 要访问的URL

        Returns:
            网页HTML内容

        Raises:
            requests.RequestException: 请求失败时抛出异常
        """
        for attempt in range(config.MAX_RETRIES):
            try:
                response = self.session.get(
                    url,
                    timeout=config.REQUEST_TIMEOUT,
                    allow_redirects=True
                )
                response.raise_for_status()
                self.logger.info(f"成功获取页面: {url}")
                return response.text

            except requests.RequestException as e:
                self.logger.warning(f"第 {attempt + 1}/{config.MAX_RETRIES} 次请求失败: {url} - {e}")
                if attempt < config.MAX_RETRIES - 1:
                    time.sleep(config.REQUEST_DELAY * (attempt + 1))
                else:
                    self.logger.error(f"请求失败（已重试{config.MAX_RETRIES}次）: {url}")
                    raise

    def _clean_text(self, text: str) -> str:
        """
        清理HTML文本，提取纯文本内容
        """
        if not text:
            return ""
        return BeautifulSoup(text, 'html.parser').get_text(' ', strip=True)

    def _get_xml_text_by_suffix(self, element: ET.Element, suffixes: List[str]) -> str:
        """
        根据标签后缀提取XML文本（兼容命名空间）
        """
        for child in element.iter():
            for suffix in suffixes:
                if child.tag.endswith(suffix):
                    text = ''.join(child.itertext()).strip()
                    if text:
                        return text
        return ""

    def _get_xml_link(self, element: ET.Element) -> str:
        """
        提取RSS/Atom条目的链接
        """
        fallback_link = ""
        for child in element.iter():
            if child.tag.endswith('link'):
                href = child.attrib.get('href')
                if href:
                    rel = child.attrib.get('rel', 'alternate')
                    if rel == 'alternate':
                        return href.strip()
                    if not fallback_link:
                        fallback_link = href.strip()
                if child.text:
                    if not fallback_link:
                        fallback_link = child.text.strip()
        return fallback_link

    def _parse_rss_sources_file(self, file_path: str) -> List[Dict]:
        """
        从文件中解析RSS源列表，每行一个URL（可在URL前写名称）
        """
        if not file_path or not os.path.exists(file_path):
            return []

        sources = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    url_match = re.search(r'https?://\S+', line)
                    if not url_match:
                        continue

                    url = url_match.group(0).rstrip(').,;，。')
                    name_part = line[:url_match.start()].strip()
                    name_part = re.sub(r'^[\-\*\d\.\)\s]+', '', name_part)
                    name_part = name_part.rstrip('：:，,')
                    name = name_part or url

                    sources.append({
                        'name': name,
                        'url': url
                    })
        except Exception as e:
            self.logger.error(f"读取RSS源文件失败: {file_path} - {e}")

        return sources

    def _get_rss_sources(self) -> List[Dict]:
        """
        合并配置项与文件中的RSS源
        """
        sources: List[Dict] = []

        config_sources = getattr(config, "RSS_FEEDS", [])
        for source in config_sources:
            if isinstance(source, dict):
                url = source.get("url")
                if not url:
                    continue
                name = source.get("name") or url
                item = {
                    "name": name,
                    "url": url
                }
                if source.get("max_items"):
                    item["max_items"] = source["max_items"]
                sources.append(item)
            elif isinstance(source, str):
                sources.append({
                    "name": source,
                    "url": source
                })

        file_path = getattr(config, "RSS_SOURCES_FILE", "")
        sources.extend(self._parse_rss_sources_file(file_path))

        unique_sources = {}
        for source in sources:
            url = source.get("url")
            if not url:
                continue
            if url in unique_sources:
                if unique_sources[url].get("name") == url and source.get("name"):
                    unique_sources[url]["name"] = source["name"]
                if "max_items" in source:
                    unique_sources[url]["max_items"] = source["max_items"]
            else:
                unique_sources[url] = dict(source)

        return list(unique_sources.values())

    def parse_news_list(self, html: str, category: str, url: str) -> List[Dict]:
        """
        解析新闻列表页面

        Args:
            html: 页面HTML内容
            category: 新闻类别名称
            url: 页面URL

        Returns:
            新闻条目列表，每个条目包含标题、链接、摘要等
        """
        soup = BeautifulSoup(html, 'html.parser')
        news_items = []

        try:
            # BBC网站使用不同的class名，这里尝试匹配常见的模式
            # 寻找文章链接
            article_links = soup.find_all('a', href=re.compile(r'/news/|/sport/|/business/|/technology/'))

            # 去重链接
            unique_links = {}
            for link in article_links:
                href = link.get('href')
                if not href or href.startswith('http'):
                    continue

                if not href.startswith('http'):
                    href = config.BBC_BASE_URL + href

                if href not in unique_links:
                    unique_links[href] = link

            # 限制每个类别的新闻数量
            for idx, (href, link_elem) in enumerate(unique_links.items()):
                if idx >= config.NEWS_PER_CATEGORY:
                    break

                # 提取标题
                title = ""
                title_elem = link_elem.find(['h1', 'h2', 'h3', 'h4', 'span'], class_=re.compile(r'title|headline', re.I))
                if title_elem:
                    title = title_elem.get_text(strip=True)
                elif link_elem.find(string=True):
                    title = link_elem.find(string=True).strip()

                if not title:
                    continue

                # 提取摘要
                summary = ""
                parent = link_elem.parent
                if parent:
                    summary_elem = parent.find('p') or parent.find(['div', 'span'], class_=re.compile(r'summary|excerpt', re.I))
                    if summary_elem:
                        summary = summary_elem.get_text(strip=True)

                news_items.append({
                    'title': title,
                    'url': href,
                    'summary': summary,
                    'category': category
                })

                self.logger.info(f"发现新闻: [{category}] {title}")

        except Exception as e:
            self.logger.error(f"解析新闻列表失败: {e}")

        return news_items

    def parse_rss_items(self, xml_content: str, source_name: str, source_url: str, max_items: int) -> List[Dict]:
        """
        解析RSS/Atom内容
        """
        items = []
        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            self.logger.error(f"解析RSS失败: {source_url} - {e}")
            return items

        if root.tag.endswith('feed'):
            entries = root.findall(".//{*}entry")
            if not entries:
                entries = root.findall(".//entry")
        else:
            entries = root.findall(".//item")
            if not entries:
                entries = root.findall(".//{*}item")

        for entry in entries:
            title = self._get_xml_text_by_suffix(entry, ["title"])
            link = self._get_xml_link(entry)
            summary_raw = self._get_xml_text_by_suffix(entry, ["summary", "description", "content", "encoded"])
            summary = self._clean_text(summary_raw)

            if not title and not summary:
                continue

            if not link:
                link = source_url

            if not title:
                title = summary[:80] if summary else "未命名"

            items.append({
                'title': title,
                'url': link,
                'summary': summary,
                'category': source_name,
                'content': summary or title
            })

            if len(items) >= max_items:
                break

        self.logger.info(f"RSS源解析完成: {source_name}（{len(items)}条）")
        return items

    def scrape_rss_sources(self) -> List[Dict]:
        """
        抓取配置的RSS/Atom订阅源
        """
        if not getattr(config, "ENABLE_RSS_SOURCES", True):
            self.logger.info("RSS抓取已关闭，跳过RSS源")
            return []

        sources = self._get_rss_sources()
        if not sources:
            self.logger.info("未配置RSS源，跳过RSS抓取")
            return []

        per_feed = getattr(config, "RSS_PER_FEED", config.NEWS_PER_CATEGORY)
        all_items: List[Dict] = []

        for source in sources:
            name = source.get("name", "RSS")
            url = source.get("url")
            if not url:
                continue

            max_items = source.get("max_items", per_feed)
            try:
                max_items = int(max_items)
            except (TypeError, ValueError):
                max_items = per_feed
            if max_items <= 0:
                continue
            try:
                self.logger.info(f"开始抓取RSS: {name}")
                xml_content = self.fetch_page(url)
                feed_items = self.parse_rss_items(xml_content, name, url, max_items)
                all_items.extend(feed_items)
                time.sleep(config.REQUEST_DELAY)
            except Exception as e:
                self.logger.error(f"抓取RSS失败: {name} - {url} - {e}")
                continue

        self.logger.info(f"RSS抓取完成，总共 {len(all_items)} 条")
        return all_items

    def extract_article_content(self, url: str) -> str:
        """
        提取新闻正文的详细内容

        Args:
            url: 新闻详情页URL

        Returns:
            新闻正文文本
        """
        try:
            html = self.fetch_page(url)
            soup = BeautifulSoup(html, 'html.parser')

            # 尝试多种方式提取正文
            content = ""

            # 方式1：查找article标签
            article = soup.find('article')
            if article:
                paragraphs = article.find_all('p')
                content = ' '.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20])

            # 方式2：查找content-text类
            if not content:
                content_divs = soup.find_all('div', class_=re.compile(r'content-text|story-body', re.I))
                if content_divs:
                    for div in content_divs:
                        paragraphs = div.find_all('p')
                        content = ' '.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20])
                        if content:
                            break

            # 方式3：查找所有段落（排除header、footer等）
            if not content:
                paragraphs = soup.find_all('p')
                # 过滤掉过短的段落和可能属于导航的段落
                valid_paragraphs = []
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    # 排除导航、广告等
                    if len(text) > 50 and not p.find_parent(['header', 'footer', 'nav', 'aside']):
                        valid_paragraphs.append(text)

                content = ' '.join(valid_paragraphs[:20])  # 限制段落数量

            self.logger.info(f"提取正文成功（{len(content)}字）: {url}")
            return content

        except Exception as e:
            self.logger.error(f"提取正文失败: {url} - {e}")
            return ""

    def scrape_category(self, category_name: str, category_path: str) -> List[Dict]:
        """
        抓取指定类别的新闻

        Args:
            category_name: 类别名称
            category_path: URL路径

        Returns:
            新闻列表
        """
        self.logger.info(f"开始抓取类别: {category_name}")

        url = config.BBC_BASE_URL + category_path
        html = self.fetch_page(url)
        news_list = self.parse_news_list(html, category_name, url)

        # 获取每篇新闻的详细内容
        for news in news_list:
            content = self.extract_article_content(news['url'])
            news['content'] = content
            time.sleep(config.REQUEST_DELAY)  # 避免请求过快

        self.logger.info(f"类别抓取完成: {category_name}（{len(news_list)}条）")
        return news_list

    def scrape_all(self) -> List[Dict]:
        """
        抓取所有配置类别的新闻

        Returns:
            所有新闻列表
        """
        self.logger.info("开始抓取所有类别新闻")
        all_news = []

        for category_name, category_path in config.BBC_CATEGORIES.items():
            try:
                category_news = self.scrape_category(category_name, category_path)
                all_news.extend(category_news)
                time.sleep(config.REQUEST_DELAY * 2)  # 类别间延迟
            except Exception as e:
                self.logger.error(f"抓取类别失败: {category_name} - {e}")
                continue

        rss_news = self.scrape_rss_sources()
        all_news.extend(rss_news)

        self.logger.info(f"新闻抓取完成，总共 {len(all_news)} 条")
        return all_news


# 测试代码
if __name__ == "__main__":
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    scraper = NewsScraper()
    news = scraper.scrape_all()

    print(f"\n抓取到 {len(news)} 条新闻：\n")
    for item in news[:5]:
        print(f"类别: {item['category']}")
        print(f"标题: {item['title']}")
        print(f"URL: {item['url']}")
        print(f"摘要: {item['summary'][:100]}...")
        print(f"正文长度: {len(item['content'])} 字\n")
