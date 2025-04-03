import requests

NEWS_SOURCES = [
    "https://www.welt.de/",
    "https://www.zeit.de/index",
    "https://www.spiegel.de/",
    "https://www.kyivpost.com/",
    "https://brooklyneagle.com/"
    ]

NEWS_SOURCE_RETRY_COUNTS = {source: 0 for source in NEWS_SOURCES}
MAX_RETRIES = 5

def fetch_source(source):
    req = requests.get(source)
    req.raise_for_status()

def main():
    for source in NEWS_SOURCES:
        try:
            fetch_source(source)
        except requests.exceptions.ConnectionError:
            print(f"Connection to {source} failed. Retrying")
            if NEWS_SOURCE_RETRY_COUNTS[source] <= MAX_RETRIES:
                NEWS_SOURCE_RETRY_COUNTS[source] += 1
                main()

main()