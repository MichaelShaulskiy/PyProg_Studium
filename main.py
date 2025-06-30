import requests
from pprint import pprint
from openai import OpenAI
import openai
import os
from typing import List, Tuple, Optional, Any
from bs4 import BeautifulSoup
import sqlite3
import time
from PySide6.QtCore import QObject, Signal, Slot, QCoreApplication, QThread
from news_provider.rssparser import RSSItem, RSS
from news_provider.provider import NewsSite, NewsSourceIndex, TagesschauProcessor, WeltProcessor, SWRProcessor, SZProcessor, GoodNewsProcessor

ENDPOINT = "https://openrouter.ai/api/v1" #http://127.0.0.1:1234/v1"
MODEL = "deepseek/deepseek-chat-v3-0324:free"
NEWS_SITES = []
NEWS_SOURCES = [
    {
        "name": "Tagesschau",
        "url": "https://www.tagesschau.de/index~rss2.xml"
    },
    {
        "name": "Welt",
        "url": "https://www.welt.de/?service=Rss"
    },
    {
        "name": "GoodNews",
        "url": "https://www.goodnewsnetwork.org/category/news/feed/"
    },
    {
        "name": "SWR",
        "url": "https://www.swr.de/~rss/index.xml"
    }
] 

def fetch_with_retry(url, times=5, timeout=1000):
    for curr in range(0, times):
        try:
            ret = requests.get(url)
            ret.raise_for_status()
            return ret.text
        except requests.HTTPError as e:
            time.sleep(timeout)
            continue

# TODO: Kann die erstellung einer sqllite db überhaupt fehlschlagen?
# Error handling betreiben wenn ja

# SOMEHOW THIS DOESN'T WORK ON WINDOWS
# IT CREATES A DB FILE BUT WITH NO SCHEMA
# SO WE WILL CREATE THE DB EXTERNALY
# WORKS FINE ON MAC THOUGH
def setup_db():
    if os.path.exists("News.db"):
        return  # Do not recreate if DB already exists
    with sqlite3.connect("News.db") as conn:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS NewsSources (source_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, url TEXT, last_queried INTEGER, rss_content TEXT, hash TEXT);")
        cursor.execute("""CREATE TABLE IF NOT EXISTS NewsArticles (
                        article_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        source_id INTEGER,
                        title TEXT,
                        author TEXT,
                        article_text TEXT,
                        raw_article TEXT,
                        category TEXT,
                        timestamp INTEGER,
                        reading_time INTEGER,
                        subscription INTEGER,
                        hash TEXT,
                        FOREIGN KEY (source_id) REFERENCES NewsSources (source_id));""")
        
        for source in NEWS_SOURCES:
            rss_feed = fetch_with_retry(source["url"])
            cursor.execute(""" 
                INSERT INTO NewsSources (name, url, last_queried, rss_content, hash)
                VALUES (?, ?, ?, ?, ?)
                """, (source["name"], source["url"], int(time.time()), rss_feed, "NOT HASHED"))
        conn.commit()

def initial_rss_fetch():
    with sqlite3.connect("News.db") as conn:
        cursor = conn.cursor()

def rss_fetch():
    for source in NEWS_SOURCES:
        rss_feed = fetch_with_retry(source["url"])

        with sqlite3.connect("News.db") as conn:
            cursor = conn.cursor()
            # Update the existing NewsSources entry for this source
            cursor.execute("""
                UPDATE NewsSources
                SET last_queried = ?, rss_content = ?
                WHERE name = ? AND url = ?
                """, (int(time.time()), rss_feed, source["name"], source["url"]))
            conn.commit()

client = None


def summarize(art: str) -> str:
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "Du fasst den dir übegerbenen Nachrichtenartikel so kurz wie nur möglich auf das wesentliche zusammen. Sollte der artikel in einer anderen sprache als deutsch vorliegen soll die zusammenfassung dennoch auf deutsch sein. Benutze keine emojis oder markdown. Einfach simpler text. Solltest du keine zusammenfassung erstellen können liefer einfach ein leerzeichen zurück"
            },
            {
                "role": "user",
                "content": art
            }
        ]
    )
    res = completion.choices[0].message.content
    return res


class QNewsBackend(QThread):
    results_ready = Signal(list)
    processing_complete = Signal()

    def __init__(self, settings):
        super().__init__()
        self.settings = settings

    def run(self):
        results = main(self.settings)  # main returns the summary/results
        pprint(results)
        self.results_ready.emit(results)
        self.processing_complete.emit()

SUMMARY_LEN = {
    1: "1 bis 2 Sätze",
    2: "2 bis 3 Sätze",
    3: "4 bis 5 Sätze",
    4: "6 bis 8 Sätze"
}

@Slot(dict)
def main(settings: dict) -> list:
    pprint(settings["model_id"])
    global MODEL
    MODEL = settings["model_id"]
    global client
    client = OpenAI(
        base_url=settings["ai_provider"],
        api_key=settings["api_key"]
    )
    #setup_db()
    rss_fetch()
    news_providers = {
        "tagesschau": NewsSite(1),
        "welt": NewsSite(2),
        "good_news": NewsSite(3),
        "swr": NewsSite(4)
    }
    news_providers["tagesschau"].addArticleProcessor(TagesschauProcessor)
    news_providers["welt"].addArticleProcessor(WeltProcessor)
    news_providers["good_news"].addArticleProcessor(GoodNewsProcessor)
    news_providers["swr"].addArticleProcessor(SWRProcessor)

    print_article_ids_for_date(settings["date"])

    summaries = []
    sources = []
    for provider in news_providers.keys():
        if settings[provider]:
            sources.append(news_providers[provider])

    pprint(sources)

    for source in sources:
        with sqlite3.connect("News.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT article_id FROM NewsArticles WHERE source_id = ? AND date = ?", (source.source_index, settings["date"]))
            article_ids_for_date = [row[0] for row in cursor.fetchall()]

        for article_id in article_ids_for_date:
            article = source.article_processor(article_id, source)
            with sqlite3.connect("News.db") as conn:
                cursor = conn.cursor()
                #only summarize if a summary doesn't already exist
                cursor.execute("SELECT summary FROM NewsArticles WHERE article_id = ?", (article.id,))
                result = cursor.fetchone()

                if result and result[0]:
                    summary = result[0]
                else:
                    content = article.content()
                    if content and content != "skip":
                        summary = summarize(content)
                        cursor.execute("UPDATE NewsArticles SET summary = ? WHERE article_id = ?", (summary, article.id))
                        conn.commit()
                    else:
                        summary = ""
            
            if summary:
                summaries.append(summary)
    
    whole = "<SYSTEM:NEWARTICLE>".join(summaries)
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": f"Du erstellst aus den dir übergebenen Nachrichten des Tages eine Zusammenfassung. Jedes <SYSTEM:NEWARTICLE> markiert den beginn eines neuen artikels. Es müssen alle artikel zusammengefasst werden. Die zusammenfassung sollte pro artikel in etwa ungefähr {SUMMARY_LEN[settings["length"]]} betragen."
            },
            {
                "role": "user",
                "content": whole
            }
        ]
    )

    return completion.choices[0].message.content
    #return whole

def print_article_ids_for_date(date_str):
    with sqlite3.connect("News.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT article_id FROM NewsArticles WHERE date = ?", (date_str,))
        article_ids = [row[0] for row in cursor.fetchall()]
        print(f"Article IDs for date {date_str}: {article_ids}")

if __name__ == "__main__":
    pass
