"""
Crypto & Macro News Bot
Fetch RSS feeds + CryptoPanic -> filter by keyword -> dedupe -> send to Telegram
100% free stack: GitHub Actions (scheduler) + RSS/CryptoPanic (source) + Telegram (delivery)
"""

import os
import json
import hashlib
import feedparser
import requests

# ---------- CONFIG ----------

RSS_FEEDS = [
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://cointelegraph.com/rss",
    "https://decrypt.co/feed",
    "https://www.investing.com/rss/news_301.rss",  # economic news
]

# CryptoPanic free tier (no key needed for public posts, but rate limited)
CRYPTOPANIC_URL = "https://cryptopanic.com/api/v1/posts/?public=true&kind=news"

KEYWORDS = [
    # macro
    "fed", "fomc", "interest rate", "rate cut", "rate hike", "inflation",
    "cpi", "jobs report", "nfp", "recession", "gdp", "yield", "treasury",
    "powell", "ecb", "boj",
    # crypto
    "bitcoin", "btc", "ethereum", "eth", "etf", "sec", "solana", "sol",
    "binance", "coinbase", "regulation", "hack", "exploit", "liquidation",
    "halving", "stablecoin", "defi",
]

STATE_FILE = "sent_news.json"
MAX_ITEMS_PER_RUN = 8  # avoid Telegram spam if many hits at once

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")


# ---------- HELPERS ----------

def load_sent_ids():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_sent_ids(ids):
    # keep only last 500 to avoid file growing forever
    trimmed = list(ids)[-500:]
    with open(STATE_FILE, "w") as f:
        json.dump(trimmed, f)


def make_id(title, link):
    return hashlib.sha256(f"{title}{link}".encode()).hexdigest()


def matches_keyword(text):
    text_lower = text.lower()
    return any(kw in text_lower for kw in KEYWORDS)


def fetch_rss_items():
    items = []
    for feed_url in RSS_FEEDS:
        try:
            parsed = feedparser.parse(feed_url)
            for entry in parsed.entries[:20]:
                title = entry.get("title", "")
                link = entry.get("link", "")
                if title and link:
                    items.append({"title": title, "link": link, "source": parsed.feed.get("title", feed_url)})
        except Exception as e:
            print(f"[warn] failed to fetch {feed_url}: {e}")
    return items


def fetch_cryptopanic_items():
    items = []
    try:
        resp = requests.get(CRYPTOPANIC_URL, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        for post in data.get("results", [])[:20]:
            title = post.get("title", "")
            link = post.get("url", "")
            if title and link:
                items.append({"title": title, "link": link, "source": "CryptoPanic"})
    except Exception as e:
        print(f"[warn] failed to fetch CryptoPanic: {e}")
    return items


def send_discord(text):
    if not DISCORD_WEBHOOK_URL:
        print("[error] DISCORD_WEBHOOK_URL not set")
        return False
    payload = {"content": text}
    resp = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
    # Discord webhook returns 204 No Content on success
    if resp.status_code not in (200, 204):
        print(f"[error] discord send failed: {resp.status_code} {resp.text}")
        return False
    return True


# ---------- MAIN ----------

def main():
    sent_ids = load_sent_ids()
    all_items = fetch_rss_items() + fetch_cryptopanic_items()

    new_items = []
    for item in all_items:
        item_id = make_id(item["title"], item["link"])
        if item_id in sent_ids:
            continue
        if not matches_keyword(item["title"]):
            continue
        item["id"] = item_id
        new_items.append(item)

    # dedupe within this run too (same news from multiple feeds)
    seen_titles = set()
    unique_items = []
    for item in new_items:
        key = item["title"].lower().strip()[:60]
        if key in seen_titles:
            continue
        seen_titles.add(key)
        unique_items.append(item)

    unique_items = unique_items[:MAX_ITEMS_PER_RUN]

    if not unique_items:
        print("No new relevant news this run.")
        return

    for item in unique_items:
        msg = f"📰 **{item['title']}**\nSource: {item['source']}\n{item['link']}"
        ok = send_discord(msg)
        if ok:
            sent_ids.add(item["id"])
            print(f"[sent] {item['title']}")

    save_sent_ids(sent_ids)


if __name__ == "__main__":
    main()
