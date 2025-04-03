import requests
from pprint import pprint
from openai import OpenAI
import os

class News(object):

    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.content = ""
        self.file = f"{self.name}.html"
        self._retrycount = 0

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = "deepseek/deepseek-chat-v3-0324:free"

openrouter_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY
)

NEWS_SOURCES = [
    News("welt","https://www.welt.de/"),
    News("spiegel","https://www.spiegel.de/"),
    News("zeit","https://www.zeit.de/index"),
    News("kyivpost","https://www.kyivpost.com/")
]

MAX_RETRIES = 5

def fetch_source(source):
    req = requests.get(source.url)
    req.raise_for_status()
    source.content = req.text
    return source

def fetch_with_retry(source):
    try:
        site = fetch_source(source)
        with open(site.file, "w", encoding='utf-8') as f:
            f.write(site.content)
        return (True, source)
    except requests.exceptions.RequestException as e:
        print(f"Request to {source.name} failed: {str(e)}")
        if source._retrycount < MAX_RETRIES:
            source._retrycount += 1
            print(f"Retrying {source.name} (attempt {source._retrycount})")
            return fetch_with_retry(source)
        print(f"Max retries reached for {source.name}")
        return False

def main():
    for source in NEWS_SOURCES:
        state, site = fetch_with_retry(source)
        if state:
            resumee = openrouter_client.chat.completions.create(
                model=OPENROUTER_MODEL,
                messages= [
                    {
                        "role": "system",
                        "content": "Fasse die Nachrichten auf der übergebenen Titelseite kurz zusammen",
                        "role": "user",
                        "content": site.content
                    }
                ]
            )
            pprint(resumee)

main()
