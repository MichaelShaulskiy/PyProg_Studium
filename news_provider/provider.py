from database import get_db_connection
from news_provider.rssparser import RSS, RSSItem
from typing import List, Optional, Iterable, Iterator, Callable
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
from toolz import curry, memoize, pipe # type: ignore
import requests
from pprint import pprint
from openai import OpenAI
from .util import NewsUtil, cacheenabledressource
import sqlite3
import time
from enum import Enum

class NewsSourceIndex(Enum):
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




class NewsProvider(ABC):
    """
    Base class for all news providers.
    This is not intended to be used directly.
    It is intended to be subclassed by specific news providers.
    Each subclass should implement the extract_articles method.
    The extract_articles method should return a list of NewsArticle objects.
    A constructed NewsProvider Object is iterable.
    A NewsProvider is either an Iterable that provides all the Articles
    A NewsProvider either downloads the front page and parses the html himself
    Or gets his news from an rss feed
    On the front page or is a single article

    Purpose of the whole thing:
    Abstracting the core logic in the main function to

    for article in NewsProvider("welt"):
        ... etc...
    """
    
    def __init__(self, retrycount: int, name: str, source: int) -> None:
        self.__name = name
        self.__content = ""
        self.__file = ""
        self.__retrycount = retrycount

    @property
    def _retrycount(self) -> int:
        return self.__retrycount
    
    @_retrycount.setter
    def _retrycount(self, value) -> None:
        self.__retrycount = value

    @property
    def _file(self) -> str:
        return f"{self.__name}.html"

    @property
    def _content(self) -> str:
        return self.__content
    
    @_content.setter
    def _content(self, value) -> None:
        self.__content = value

    @abstractmethod
    def _download_page(self) -> bool:
        """
        Downloads the page and returns true if sucessfull, false if not
        """
        pass

    @abstractmethod
    def parse(self) -> Optional[List["NewsProvider"]]:
        pass

    @abstractmethod
    def __iter__(self) -> Iterator["NewsProvider"]:
        pass
    
    @abstractmethod
    def __next__(self) -> Iterable["NewsProvider"]:
        pass

class NewsArticle(NewsProvider):
    """Represents a single news article."""
    pass

class NewsSite:

    def __init__(self, source_index: NewsSourceIndex | int) -> None:
        self.source_index = source_index
        self.db = get_db_connection()
        self.rss_provider = None
        # lookup if the source index points to a valid news source
        cursor = self.db.cursor()
        result = cursor.execute("SELECT source_id FROM NewsSources WHERE source_id = ?", (source_index,))
        result = result.fetchone()

        if result is None:
            raise Exception("Invalid News Source")
        
        self.rss_provider = RSS(source_index)

        self.articles = []
        for item in self.rss_provider.items():
            @cacheenabledressource(self.source_index)
            def cached_fetch_articles(url):
                return NewsUtil.fetch_articles(url)
            
            art = cached_fetch_articles(item.link)
            self.articles.append(art)

    def num_articles(self):
        #would be more pythonic to use len(MyNewsSite)
        pass



if __name__ == "__main__":
    NewsUtil.fetch_source("https://www.welt.de/")