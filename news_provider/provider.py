from typing import List, Optional, Iterable
from bs4 import BeautifulSoup

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
    
    def __init__(self, site: str) -> Iterable[None]:
        pass

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