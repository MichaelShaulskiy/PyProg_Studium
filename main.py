import requests
from pprint import pprint
from openai import OpenAI
import openai
import os
from typing import List, Tuple, Optional, Any
from bs4 import BeautifulSoup
import sqlite3
import time
from PySide6.QtCore import QObject, Signal, Slot, QCoreApplication
from news_provider.rssparser import RSSItem, RSS
from news_provider.provider import NewsSite, NewsSourceIndex, TagesschauProcessor, WeltProcessor, SpiegelProcessor, SZProcessor

OPENROUTER = "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"
MODEL = "gemma-3-12b-it-qat"
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
        "name": "SZ",
        "url": "https://rss.sueddeutsche.de/rss/Topthemen"
    },
    {
        "name": "Spiegel",
        "url": "https://www.spiegel.de/schlagzeilen/tops/index.rss"
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

client = OpenAI(
    base_url="http://127.0.0.1:1234/v1",
    api_key=OPENROUTER
) 

def summarize(art: str) -> str:
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "Du fasst den dir übegerbenen Nachrichtenartikel so kurz wie nur möglich auf das wesentliche zusammen. Die zusammenfassung sollte kurz sein, höchstens 2 kurze abschnitte. Sollte der artikel in einer anderen sprache als deutsch vorliegen soll die zusammenfassung dennoch auf deutsch sein. Benutze keine emojis oder markdown. Einfach simpler text"
            },
            {
                "role": "user",
                "content": art
            }
        ]
    )
    res = completion.choices[0].message.content
    return res



def main():
    #setup_db()
    tagesschau = NewsSite(1)
    welt = NewsSite(2)
    sz = NewsSite(3)
    spiegel = NewsSite(4)

    pprint(len(welt))
    tagesschau.addArticleProcessor(TagesschauProcessor)
    welt.addArticleProcessor(WeltProcessor)
    spiegel.addArticleProcessor(SpiegelProcessor)
    sz.addArticleProcessor(SZProcessor)

    whole = []

    for article in tagesschau:
        with sqlite3.connect("News.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT summary FROM NewsArticles WHERE article_id = ?", (article.id,))
            result = cursor.fetchone()

            if result and result[0]:
                summary = result[0]
            else:
                summary = summarize(article.content())
                cursor.execute("UPDATE NewsArticles SET summary = ? WHERE article_id = ?", (summary, article.id))
                conn.commit()
        whole.append(summary)
    
    whole = " ".join(whole)
    print(len(whole))
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "Du fasst die dir hier übegebenen zusammenfassungen von Nachrichtenartikeln aus allerlei Quellen in einen kurzen bis mittellangen überblick zusammen"
            },
            {
                "role": "user",
                "content": whole
            }
        ]
    )

    print(completion.choices[0].message.content)


if __name__ == "__main__":
    main()