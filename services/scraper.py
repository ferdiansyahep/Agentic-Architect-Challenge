from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from utils.logger import get_logger


logger = get_logger(__name__)


class ScraperService:

    def _clean_text(self, value):
        return " ".join(value.split())

    def scrape(self, url):

        try:
            logger.info("Scraping url=%s", url)

            parsed_url = urlparse(url)

            if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
                logger.warning("Rejected invalid url=%s", url)
                return {
                    "success": False,
                    "error": "Invalid URL. Use http or https."
                }

            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; AgenticArchitect/1.0)"
            }

            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            for tag in soup(["script", "style", "noscript", "svg", "iframe"]):
                tag.decompose()

            article_root = soup.find("article") or soup.find("main") or soup.body or soup
            text_blocks = []

            for tag_name in ["h1", "h2", "h3", "p", "li"]:
                for node in article_root.find_all(tag_name):
                    text = self._clean_text(node.get_text(" ", strip=True))

                    if text:
                        text_blocks.append(text)

            if not text_blocks:
                fallback_text = self._clean_text(article_root.get_text(" ", strip=True))

                if fallback_text:
                    text_blocks = [fallback_text]

            article = "\n".join(text_blocks).strip()

            if len(article) > 12000:
                article = article[:12000].rsplit(" ", 1)[0]
                logger.warning("Trimmed scraped content for url=%s to 12000 characters", url)

            title = self._clean_text(soup.title.get_text()) if soup.title and soup.title.get_text() else ""

            logger.info("Scrape completed url=%s title=%s length=%d", url, title, len(article))

            return {
                "success": True,
                "content": article,
                "title": title,
                "url": url
            }

        except Exception as e:
            logger.exception("Scrape failed for url=%s", url)

            return {
                "success": False,
                "error": str(e)
            }


scraper = ScraperService()