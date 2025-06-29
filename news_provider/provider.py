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
        self.id = id
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
        cursor: sqlite3.Cursor = self._newssite.db.cursor()
        self.article_id = article_id
        cursor.execute("SELECT raw_article FROM NewsArticles WHERE article_id = ?", (article_id,))
        result = cursor.fetchone()
        if result is None:
            raise Exception("Article not found in database")
        self._article = result[0]
        self._newssite.db.commit()
        self.soup = BeautifulSoup(self._article, "html.parser")


    def content(self):
        if not self.soup:
            raise Exception("soup not initialized")
        
        content_node = self.soup.find("div", id="content").article
        if content_node:
            article_text = " " .join(content_node.get_text().splitlines())
            cursor = self._newssite.db.cursor()
            cursor.execute("UPDATE NewsArticles SET article_text = ? WHERE article_id = ?", (article_text, self.article_id))
            self._newssite.db.commit()
            

class NewsSite:

    def __init__(self, source_index: NewsSourceIndex | int, article_processor: None | ArticleProcessor = None) -> None:
        self.source_index = source_index
        self.db = get_db_connection()
        self.rss_provider = None
        self.article_processor = article_processor
        self._current_index = 0
        # lookup if the source index points to a valid news source
        self.cursor = self.db.cursor()
        result = self.cursor.execute("SELECT source_id FROM NewsSources WHERE source_id = ?", (source_index,))
        result = result.fetchone()
        self_article_id = None
        self.db.commit()

        if result is None:
            raise Exception("Invalid News Source")
        
        self.rss_provider = RSS(source_index)

        self._articles = []

        @cacheenabledressource(self.source_index)
        def cached_fetch_articles(url):
            return NewsUtil.fetch_articles(url)
        
        for item in self.rss_provider.items():
            
            art = cached_fetch_articles(item.link)
            self._articles.append(art)

    # Builder Pattern could be useful here
    def addArticleProcessor(self, aproc_constructor: type[ArticleProcessor]):
        self.article_processor = aproc_constructor
        return self
    
    def build(self):
        if not self.article_processor:
            raise Exception("No ArticleProcessor, can't build object")
        
        self.article_processor = self.article_processor(self._current_index, self)
    
    def __iter__(self):
        # Query all article_ids for this source_id and store them
        self.cursor.execute("SELECT article_id FROM NewsArticles WHERE source_id = ?", (self.source_index,))
        self._articles = [row[0] for row in self.cursor.fetchall()]
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
        return result.content()

    def __len__(self) -> int:
        cursor = self.db.cursor()
        cursor.execute("SELECT COUNT(*) FROM NewsArticles WHERE source_id = ?;", (self.source_index,))
        result = cursor.fetchone()
        self.db.commit()
        return result[0]
    
if __name__ == "__main__":
    NewsUtil.fetch_source("https://www.welt.de/")