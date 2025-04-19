from typing import List, Optional, Iterable, Iterator
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
from toolz import curry, memoize # type: ignore
import requests
from pprint import pprint
from openai import OpenAI

def _fetch_source(url: str) -> Optional[str]:
    def __inner_try(url):
        res = requests.get(url)
        res.raise_for_status()
        return res.text
    try:
       res = __inner_try(url)
       pprint(res)
       return res
    except:
        print("fetch failed")

    return ""

class NewsProvider(ABC):
    """
    Base class for all news providers.
    This is not intended to be used directly.
    It is intended to be subclassed by specific news providers.
    Each subclass should implement the extract_articles method.
    The extract_articles method should return a list of NewsArticle objects.
    A constructed NewsProvider Object is iterable.
    A NewsProvider is either an Iterable that provides all the Articles
    On the front page or is a single article
    """
    
    def __init__(self, retrycount: int, name: str, site: str) -> None:
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

class CBaseNewsProvider(NewsProvider):
    """
    NOT A BASE CLASS
    Wrapper of the abstract base class to make it constructable via toolz curry
    BaseNewsProvier = curry(CBaseNewsProvider)
    WeltNewsProvider = BaseNewsProvider("welt.de")
    etc...
    """
    def __init__(self, name: str, site: str) -> None:
        super().__init__(site)

    def _download_page(self) -> None:
        pass

BaseNewsProvider = curry(CBaseNewsProvider)



class News(object):
    """Represents a news source with associated articles."""

    def __init__(self, name: str, url: str) -> None:
        self.name = name
        self.url = url
        self.content = ""
        self.file = f"{self.name}.html"
        self._retrycount: int = 0
        self.articles: List[Optional[NewsArticle]] = []
    
    def extract_articles(self):
        pass

if __name__ == "__main__":
    _fetch_source("https://www.welt.de/")