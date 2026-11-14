"""Trend research feeds. Fetches real headlines over plain HTTPS."""
from __future__ import annotations

import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from html import unescape

from . import config

FEEDS: list[tuple[str, str, str]] = [
    # (source, region, url)
    ("BBC World", "international", "https://feeds.bbci.co.uk/news/world/rss.xml"),
    ("BBC Technology", "international", "https://feeds.bbci.co.uk/news/technology/rss.xml"),
    ("BBC Business", "international", "https://feeds.bbci.co.uk/news/business/rss.xml"),
    ("BBC Entertainment", "international", "https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml"),
    ("Guardian World", "uk", "https://www.theguardian.com/world/rss"),
    ("Guardian Culture", "uk", "https://www.theguardian.com/uk/culture/rss"),
    ("Al Jazeera", "international", "https://www.aljazeera.com/xml/rss/all.xml"),
    ("Hacker News", "tech", "https://hnrss.org/frontpage"),
    ("Reddit WorldNews", "internet", "https://www.reddit.com/r/worldnews/.rss"),
    ("Reddit NotTheOnion", "absurd", "https://www.reddit.com/r/nottheonion/.rss"),
    ("Reddit Offbeat", "absurd", "https://www.reddit.com/r/offbeat/.rss"),
    ("DW Europe", "europe", "https://rss.dw.com/rdf/rss-en-eu"),
    ("France24", "europe", "https://www.france24.com/en/rss"),
    ("NPR", "us", "https://feeds.npr.org/1001/rss.xml"),
    ("Sky Sports", "sports", "https://www.skysports.com/rss/12040"),
    ("ESPN", "sports", "https://www.espn.com/espn/rss/news"),
]


def _fetch(url: str, timeout: int = 15) -> bytes | None:
    req = urllib.request.Request(url, headers={"User-Agent": config.USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read(2_000_000)
    except Exception:
        return None


def _clean(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", unescape(text)).strip()


def _parse_rss(data: bytes, source: str, region: str) -> list[dict]:
    items: list[dict] = []
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return items

    ns = {"atom": "http://www.w3.org/2005/Atom"}
    # RSS 2.0 items
    for item in root.iter("item"):
        title = item.findtext("title") or ""
        link = item.findtext("link") or ""
        desc = item.findtext("description") or ""
        pub = item.findtext("pubDate") or item.findtext(
            "{http://purl.org/dc/elements/1.1/}date"
        ) or ""
        if title and link:
            items.append({
                "title": _clean(title),
                "summary": _clean(desc)[:600],
                "url": link.strip(),
                "published": pub.strip(),
                "source": source,
                "region": region,
            })
    # Atom entries
    for entry in root.iter("{http://www.w3.org/2005/Atom}entry"):
        title = entry.findtext("atom:title", "", ns)
        link = ""
        for l in entry.iter("{http://www.w3.org/2005/Atom}link"):
            if l.get("rel") in (None, "alternate"):
                link = l.get("href", "")
                break
        desc = entry.findtext("atom:summary", "", ns) or entry.findtext("atom:content", "", ns)
        pub = entry.findtext("atom:published", "", ns) or entry.findtext("atom:updated", "", ns)
        if title and link:
            items.append({
                "title": _clean(title),
                "summary": _clean(desc)[:600],
                "url": link.strip(),
                "published": pub.strip(),
                "source": source,
                "region": region,
            })
    return items


def fetch_trends(limit_per_feed: int = 15) -> list[dict]:
    out: list[dict] = []
    for source, region, url in FEEDS:
        data = _fetch(url)
        if not data:
            continue
        out.extend(_parse_rss(data, source, region)[:limit_per_feed])
    return out
