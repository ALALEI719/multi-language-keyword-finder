from __future__ import annotations

from datetime import datetime, timedelta, timezone
from time import mktime
from typing import Any, Dict, List
from urllib.parse import urlparse

import feedparser
import requests


def _is_recent(dt: datetime | None, hours_window: int) -> bool:
    if dt is None:
        return True
    return dt >= datetime.now(timezone.utc) - timedelta(hours=hours_window)


def _entry_datetime(entry: Any) -> datetime | None:
    for attr in ("published_parsed", "updated_parsed"):
        struct = getattr(entry, attr, None)
        if struct:
            try:
                return datetime.fromtimestamp(mktime(struct), tz=timezone.utc)
            except (OverflowError, ValueError, TypeError):
                continue
    return None


def _entry_text(entry: Any) -> str:
    title = getattr(entry, "title", "") or ""
    summary = getattr(entry, "summary", "") or getattr(entry, "description", "") or ""
    return f"{title}\n{summary}".strip()


def _matches_keywords(text: str, keywords: List[str]) -> bool:
    if not keywords:
        return True
    lower = text.lower()
    return any(k.strip() and k.strip().lower() in lower for k in keywords)


def _platform_from_link(link: str) -> str:
    host = (urlparse(link).netloc or "").lower()
    if "linkedin.com" in host:
        return "LinkedIn"
    return "RSS"


def _author_from_feed(feed: Any, entry: Any) -> str:
    ea = getattr(entry, "author", None)
    if ea:
        return str(ea)
    fd = getattr(feed, "feed", None)
    if fd is not None:
        t = getattr(fd, "title", None) or getattr(fd, "author", None)
        if t:
            return str(t)
    return "RSS"


def fetch_rss_posts(
    feed_urls: List[str],
    hours_window: int,
    keywords: List[str],
    require_keyword_match: bool,
    max_entries_per_feed: int = 40,
) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for raw in feed_urls:
        url = raw.strip()
        if not url:
            continue
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https"):
                continue
        except Exception:
            continue

        try:
            # 显式用 requests 取 XML，避免部分服务对默认 UA 不友好
            resp = requests.get(url, timeout=25, headers={"User-Agent": "SEO-Brief-Bot/1.0"})
            resp.raise_for_status()
            feed = feedparser.parse(resp.content)
        except requests.RequestException as exc:
            print(f"[ERROR] RSS 下载失败 {url}: {exc}")
            continue

        if feed.bozo and not feed.entries:
            print(f"[WARN] RSS 可能解析失败 {url}: {getattr(feed, 'bozo_exception', '')}")

        for entry in feed.entries[:max_entries_per_feed]:
            link = getattr(entry, "link", "") or ""
            text = _entry_text(entry)
            if not link or not text:
                continue
            if require_keyword_match and not _matches_keywords(text, keywords):
                continue
            edt = _entry_datetime(entry)
            if not _is_recent(edt, hours_window):
                continue
            created = edt.isoformat() if edt else ""
            plat = _platform_from_link(link)
            author = _author_from_feed(feed, entry)
            out.append(
                {
                    "platform": plat,
                    "author": author,
                    "text": text[:4000],
                    "url": link,
                    "likes": 0,
                    "comments": 0,
                    "reposts": 0,
                    "created_at": created,
                }
            )
    return out
