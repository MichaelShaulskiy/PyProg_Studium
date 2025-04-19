import requests
from pprint import pprint
from openai import OpenAI
import openai
import os
from typing import List, Tuple, Optional, Any
from bs4 import BeautifulSoup

# Import the classes from our new package
#from news_provider import NewsProvider, NewsArticle, News

class News(object):
    """Represents a news source with associated articles."""

    def __init__(self, name: str, url: str) -> None:
        self.name = name
        self.url = url
        self.content = ""
        self.file = f"{self.name}.html"
        self._retrycount: int = 0
        self.articles: List[Optional["NewsArticle"]] = []
    
    def extract_articles(self):
        pass


def extract_welt_articles(self: News) -> None:
    soup = BeautifulSoup(site.content, "html.parser")
    pprint(soup.findAll("a", class_="is-teaser-link"))

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = "deepseek/deepseek-chat-v3-0324:free"

openrouter_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY
)

NEWS_SOURCES = [
    News("welt","https://www.welt.de/"),
    News("spiegel","https:/www.spiegel.de/"),
    News("zeit","https://www.zeit.de/index"),
    News("kyivpost","https://www.kyivpost.com/")
]

MAX_RETRIES = 5

def fetch_source(source: News) -> News:
    req = requests.get(source.url)
    req.raise_for_status()
    source.content = req.text
    return source

def fetch_with_retry(source: News) -> Tuple[bool, News]:
    try:
        site = fetch_source(source)
        try:
            with open(site.file, "w", encoding='utf-8') as f:
                f.write(site.content)
            return (True, source)
        except (IOError, OSError) as e:
            print(f"Failed to write file for {source.name}: {str(e)}")
            return (False, source)
            
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error for {source.name} (status {e.response.status_code}): {str(e)}")
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error for {source.name}: {str(e)}")
    except requests.exceptions.Timeout as e:
        print(f"Timeout for {source.name}: {str(e)}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed for {source.name}: {str(e)}")
        if source._retrycount < MAX_RETRIES:
            source._retrycount += 1
            print(f"Retrying {source.name} (attempt {source._retrycount})")
            return fetch_with_retry(source)
        print(f"Max retries reached for {source.name}")
        return (False, source)

def main() -> None:
    for source in NEWS_SOURCES:
        try:
            state, site = fetch_with_retry(source)
            if not state:
                continue

            try:
                resumee = openrouter_client.chat.completions.create(
                    model=OPENROUTER_MODEL,
                    messages= [
                        {
                            "role": "system", 
                            "content": "Fasse die Nachrichten auf der übergebenen Titelseite kurz zusammen"
                        },
                        {
                            "role": "user",
                            "content": site.content
                        }
                    ]
                )
                pprint(resumee)
            except openai.AuthenticationError as e:
                print(f"OpenAI authentication failed for {source.name}: {str(e)}")
            except openai.RateLimitError as e:
                print(f"OpenAI rate limit exceeded for {source.name}: {str(e)}")
            except openai.APIError as e:
                print(f"OpenAI API error for {source.name}: {str(e)}")
                
        except Exception as e:
            print(f"Unexpected error processing {source.name}: {type(e).__name__}: {str(e)}")

def test_welt_extract():
    with open("welt.html", "r") as f:
        content = "".join(f.readlines())
        soup = BeautifulSoup(content, "html.parser")
        pprint(soup.findAll("a", class_="is-teaser-link"))