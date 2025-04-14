from bs4 import BeautifulSoup
from typing import List, Optional
from .provider import NewsProvider, NewsArticle, News

class WeltArticle(NewsArticle):
    """Represents a news article from Welt.de"""
    
    def __init__(self, title: str, url: str, summary: Optional[str] = None):
        self.title = title
        self.url = url
        self.summary = summary
    
    def __str__(self) -> str:
        return f"WeltArticle: {self.title}"
    
    def __repr__(self) -> str:
        return f"<WeltArticle title='{self.title}' url='{self.url}'>"


class WeltProvider(NewsProvider):
    """News provider for Welt.de"""
    
    def __init__(self, content: str):
        self.content = content
        self.articles: List[WeltArticle] = []
        
    def extract_articles(self) -> List[WeltArticle]:
        """Extract articles from Welt.de content"""
        soup = BeautifulSoup(self.content, "html.parser")
        article_links = soup.findAll("a", class_="is-teaser-link")
        
        for link in article_links:
            try:
                url = link.get('href')
                # Ensure URL is complete
                if url and not url.startswith('http'):
                    url = f"https://www.welt.de{url}"
                
                title = link.get_text().strip()
                if title and url:
                    self.articles.append(WeltArticle(title=title, url=url))
            except Exception as e:
                print(f"Error extracting article: {str(e)}")
                
        return self.articles
    
    def __iter__(self):
        return iter(self.articles)


# Helper function to create a WeltProvider from a News object
def create_welt_provider(news: News) -> WeltProvider:
    if news.name != "welt":
        raise ValueError("News source is not Welt")
    return WeltProvider(news.content)