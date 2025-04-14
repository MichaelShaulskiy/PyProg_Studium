from typing import List, Optional, Iterable, Iterator, ForwardRef
from bs4 import BeautifulSoup
from abc import ABC

class NewsArticle(object):
    """Represents a single news article."""
    pass

class NewsProvider(object):
    """
    Base class for all news providers.
    This is not intended to be used directly.
    It is intended to be subclassed by specific news providers.
    Each subclass should implement the extract_articles method.
    The extract_articles method should return a list of NewsArticle objects.
    A constructed NewsProvider Object is iterable.
    """
    
    def __init__(self, site: str) -> None:
        pass

    def __iter__(self) -> Iterator["NewsProvider"]:
        """
        Returns an iterator over the articles.
        This method should be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement __iter__ method")
    
    def __next__(self) -> Iterable["NewsProvider"]:
        """
        Returns the next article.
        This method should be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement __next__ method")

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