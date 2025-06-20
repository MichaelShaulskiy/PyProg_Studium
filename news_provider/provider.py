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
        self._create_article_view()
        self._newssite.db.commit()
        self.soup = BeautifulSoup(self._article, "html.parser")


    def content(self):
        if not self.soup:
            raise Exception("soup not initialized")
        
        content_node = self.soup.find()

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
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self._current_index < len(self):
            try:
                self.cursor.executemany("SELECT raw_article FROM NewsArticles WHERE source_id = ?", (self.source_index,))
                a = self.cursor.fetchmany()
                self.cursor.commit()
            except sqlite3.Error as e:
                print("SQL Request failed")

    def __len__(self) -> int:
        cursor = self.db.cursor()
        cursor.execute("SELECT COUNT(*) FROM NewsArticles WHERE source_id = ?;", (self.source_index,))
        result = cursor.fetchone()
        self.db.commit()
        return result[0]
    
if __name__ == "__main__":
    NewsUtil.fetch_source("https://www.welt.de/")