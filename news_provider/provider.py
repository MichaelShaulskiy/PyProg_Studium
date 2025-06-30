from database import get_db_connection
from news_provider.rssparser import RSS, RSSItem
from typing import List, Optional, Iterable, Iterator, Callable
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
from toolz import curry, memoize, pipe # type: ignore
import requests
from pprint import pprint
from openai import OpenAI
from news_provider.util import NewsUtil, cacheenabledressource
import sqlite3
import time
from enum import Enum

class NewsSourceIndex(int, Enum):
    Tagesschau = 1
    Welt = 2
    SZ = 3
    Spiegel = 4

# After meeting with Matthias we decided to limit us to 4 major news sources
# which all provide rss feeds making this a whole lot simpler

class NewsP(ABC):

    def __init__(self, source_index: int) -> None:
        self.source_index = source_index
        self._created_time = time.time()
        self._database_time = self._fetch_database_time()

    def _fetch_database_time(self):
        with sqlite3.connect("News.db") as conn:
            cursor = conn.cursor()

            result = cursor.execute("SELECT last_queried from NewsSources WHERE source_id = ?", (self.source_index,))
            last_queried = int(result.fetchone()[0])



class ArticleProcessor:
    """
    friend classing like in C++ would be immensiley useful here
    """

    def __init__(self, article_id= 0, parent_site = None) -> None:
        self.id = article_id
        self.soup = None
        self._newssite = parent_site

    def add_parent_site(self, parent) -> None:
        self._newssite = parent

    def content(self):
        raise Exception("Needs to be implemented in a Subclass")
    
    def _create_article_view(self) -> None:
        cursor = self._newssite.db.cursor()
        cursor.execute("""
                       CREATE VIEW IF NOT EXISTS NewsArticlesBySource AS
                       SELECT *
                       FROM NewsArticles
                       WHERE source_id = ?;
                       """, (self._newssite.source_index,))
        self._newssite.db.commit()


class TagesschauProcessor(ArticleProcessor):

    def __init__(self, article_id: int = 0, parent_site = None) -> None:
        super().__init__(article_id=article_id, parent_site=parent_site)
        conn = sqlite3.connect("News.db")
        cursor: sqlite3.Cursor = conn.cursor()
        self.article_id = article_id
        cursor.execute("SELECT raw_article FROM NewsArticles WHERE article_id = ?", (article_id,))
        result = cursor.fetchone()
        if result is None:
            raise Exception("Article not found in database")
        self._article = result[0]
        conn.commit()
        conn.close()
        self.soup = BeautifulSoup(self._article, "html.parser")


    def content(self):
        if not self.soup:
            raise Exception("soup not initialized")
        div_content = self.soup.find("div", id="content")
        if div_content and div_content.article:
            content_node = div_content.article
            article_text = " ".join(content_node.get_text().splitlines())
            conn = sqlite3.connect("News.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE NewsArticles SET article_text = ? WHERE article_id = ?", (article_text, self.article_id))
            conn.commit()
            conn.close()
            return article_text
        else:
            return "skip"
        
class WeltProcessor(ArticleProcessor):

    def __init__(self, article_id: int = 0, parent_site = None) -> None:
        super().__init__(article_id=article_id, parent_site=parent_site)
        conn = sqlite3.connect("News.db")
        cursor: sqlite3.Cursor = conn.cursor()
        self.article_id = article_id
        cursor.execute("SELECT raw_article FROM NewsArticles WHERE article_id = ?", (article_id,))
        result = cursor.fetchone()
        if result is None:
            raise Exception("Article not found in database")
        self._article = result[0]
        conn.commit()
        conn.close()
        self.soup = BeautifulSoup(self._article, "html.parser")


    def content(self):
        if not self.soup:
            raise Exception("soup not initialized")
        
        content_node = self.soup.find("div", class_="c-article-page__content")
        if content_node:
            article_text = " " .join(content_node.get_text().splitlines())
            conn = sqlite3.connect("News.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE NewsArticles SET article_text = ? WHERE article_id = ?", (article_text, self.article_id))
            conn.commit()
            conn.close()
            return article_text
        else:
            with sqlite3.connect("News.db") as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE NewsArticles SET article_text = ? WHERE article_id = ?", ("Artikel nicht gefunden", self.article_id))
                conn.commit()
            return "Artikel nicht gefunden"


        
class SpiegelProcessor(ArticleProcessor):

    def __init__(self, article_id: int = 0, parent_site = None) -> None:
        super().__init__(article_id=article_id, parent_site=parent_site)
        conn = sqlite3.connect("News.db")
        cursor: sqlite3.Cursor = conn.cursor()
        self.article_id = article_id
        cursor.execute("SELECT raw_article FROM NewsArticles WHERE article_id = ?", (article_id,))
        result = cursor.fetchone()
        if result is None:
            raise Exception("Article not found in database")
        self._article = result[0]
        conn.commit()
        conn.close()
        self.soup = BeautifulSoup(self._article, "html.parser")


    def content(self):
        if not self.soup:
            raise Exception("soup not initialized")
        
        content_node = self.soup.find("section", class_="relative")
        if content_node:
            article_text = " " .join(content_node.get_text().splitlines())
            conn = sqlite3.connect("News.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE NewsArticles SET article_text = ? WHERE article_id = ?", (article_text, self.article_id))
            conn.commit()
            conn.close()
            return article_text
        
class SZProcessor(ArticleProcessor):

    def __init__(self, article_id: int = 0, parent_site = None) -> None:
        super().__init__(article_id=article_id, parent_site=parent_site)
        conn = sqlite3.connect("News.db")
        cursor: sqlite3.Cursor = conn.cursor()
        self.article_id = article_id
        cursor.execute("SELECT raw_article FROM NewsArticles WHERE article_id = ?", (article_id,))
        result = cursor.fetchone()
        if result is None:
            raise Exception("Article not found in database")
        self._article = result[0]
        conn.commit()
        conn.close()
        self.soup = BeautifulSoup(self._article, "html.parser")


    def content(self):
        if not self.soup:
            raise Exception("soup not initialized")
        
        content_node = self.soup.find("div", class_="cXsenseParse", attrs={"data-testid": "article-content"})
        if content_node:
            article_text = " " .join(content_node.get_text().splitlines())
            conn = sqlite3.connect("News.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE NewsArticles SET article_text = ? WHERE article_id = ?", (article_text, self.article_id))
            conn.commit()
            conn.close()
            return article_text
        
class SWRProcessor(ArticleProcessor):

    def __init__(self, article_id: int = 0, parent_site = None) -> None:
        super().__init__(article_id=article_id, parent_site=parent_site)
        conn = sqlite3.connect("News.db")
        cursor: sqlite3.Cursor = conn.cursor()
        self.article_id = article_id
        cursor.execute("SELECT raw_article FROM NewsArticles WHERE article_id = ?", (article_id,))
        result = cursor.fetchone()
        if result is None:
            raise Exception("Article not found in database")
        self._article = result[0]
        conn.commit()
        conn.close()
        self.soup = BeautifulSoup(self._article, "html.parser")


    def content(self):
        if not self.soup:
            raise Exception("soup not initialized")
        
        content_node = self.soup.find("article", id="article")
        if content_node:
            article_text = " " .join(content_node.get_text().splitlines())
            conn = sqlite3.connect("News.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE NewsArticles SET article_text = ? WHERE article_id = ?", (article_text, self.article_id))
            conn.commit()
            conn.close()
            return article_text
        else:
            return "skip"
        
class GoodNewsProcessor(ArticleProcessor):

    def __init__(self, article_id: int = 0, parent_site = None) -> None:
        super().__init__(article_id=article_id, parent_site=parent_site)
        conn = sqlite3.connect("News.db")
        cursor: sqlite3.Cursor = conn.cursor()
        self.article_id = article_id
        cursor.execute("SELECT raw_article FROM NewsArticles WHERE article_id = ?", (article_id,))
        result = cursor.fetchone()
        if result is None:
            raise Exception("Article not found in database")
        self._article = result[0]
        conn.commit()
        conn.close()
        self.soup = BeautifulSoup(self._article, "html.parser")


    def content(self):
        if not self.soup:
            raise Exception("soup not initialized")
        
        content_node = self.soup.find("div", class_="td-ss-main-content")
        if content_node:
            article_text = " " .join(content_node.get_text().splitlines())
            conn = sqlite3.connect("News.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE NewsArticles SET article_text = ? WHERE article_id = ?", (article_text, self.article_id))
            conn.commit()
            conn.close()
            return article_text
        else:
            return "skip"
            

class NewsSite:

    def __init__(self, source_index: NewsSourceIndex | int, article_processor: None | ArticleProcessor = None) -> None:
        self.source_index = source_index
        self.rss_provider = RSS(source_index)
        self._articles = []

        @cacheenabledressource(self.source_index)
        def cached_fetch_articles(url):
            return NewsUtil.fetch_articles(url)
        
        for item in self.rss_provider.items():
            art = cached_fetch_articles(item.link)
            self._articles.append(art)

        self.article_processor = article_processor
        self._current_index = 0
        # Query all article_ids for this source_id and store them
        with sqlite3.connect("News.db") as conn:
            cursor = conn.cursor()
            result = cursor.execute("SELECT source_id FROM NewsSources WHERE source_id = ?", (source_index,))
            result = result.fetchone()
            if result is None:
                raise Exception("Invalid News Source")
            cursor.execute("SELECT article_id FROM NewsArticles WHERE source_id = ?", (self.source_index,))
            self._articles = [row[0] for row in cursor.fetchall()]
        self._current_index = 0

    # Builder Pattern could be useful here
    def addArticleProcessor(self, aproc_constructor: type[ArticleProcessor]):
        self.article_processor = aproc_constructor
        return self
    
    def build(self):
        if not self.article_processor:
            raise Exception("No ArticleProcessor, can't build object")
        
        self.article_processor = self.article_processor(self._current_index, self)
    
    def __iter__(self):
        self._current_index = 0
        return self
    
    def __next__(self):
        if not self.article_processor:
            raise Exception("No Article Processor set")
        if self._current_index >= len(self._articles):
            raise StopIteration
        article_id = self._articles[self._current_index]
        result = self.article_processor(article_id, self)
        self._current_index += 1
        return result

    def __len__(self) -> int:
        cursor = self.db.cursor()
        cursor.execute("SELECT COUNT(*) FROM NewsArticles WHERE source_id = ?;", (self.source_index,))
        result = cursor.fetchone()
        self.db.commit()
        return result[0]
    
if __name__ == "__main__":
    NewsUtil.fetch_source("https://www.welt.de/")