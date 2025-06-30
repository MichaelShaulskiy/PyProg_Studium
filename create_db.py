import sqlite3
import os
import requests
import time

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

if __name__ == "__main__":
    with sqlite3.connect("News.db") as conn:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS NewsSources (source_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, url TEXT, last_queried INTEGER, rss_content TEXT, hash TEXT);")
        cursor.execute("""CREATE TABLE IF NOT EXISTS NewsArticles (
                        article_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        source_id INTEGER,
                        title TEXT,
                        author TEXT,
                        summary TEXT,
                        article_text TEXT,
                        raw_article TEXT,
                        article_link TEXT,
                        category TEXT,
                        timestamp INTEGER,
                        date TEXT,
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