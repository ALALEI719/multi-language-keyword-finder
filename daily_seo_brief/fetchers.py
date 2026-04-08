from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

import requests

from apify_client import run_actor_sync
from config import get_config


def _safe_int(value: object) -> int:
    try:
        return int(value or 0)
    except (ValueError, TypeError):
        return 0


def _parse_twitter_created_at(raw: str) -> str:
    if not raw:
        return ""
    for fmt in ("%a %b %d %H:%M:%S %z %Y",):
        try:
            dt = datetime.strptime(raw, fmt)
            return dt.isoformat()
        except ValueError:
            continue
    return ""


def _parse_linkedin_created_at(item: Dict[str, Any]) -> str:
    posted = item.get("posted_at") or {}
    if isinstance(posted, dict):
        ts = posted.get("timestamp")
        if ts:
            try_ms = int(ts)
            return datetime.fromtimestamp(try_ms / 1000, tz=timezone.utc).isoformat()
        date_s = posted.get("date") or ""
        if date_s:
            try:
                dt = datetime.strptime(date_s, "%Y-%m-%d %H:%M:%S")
                return dt.replace(tzinfo=timezone.utc).isoformat()
            except ValueError:
                return date_s
    return ""


def _is_recent(created_at: str, hours_window: int) -> bool:
    if not created_at:
        return True
    try:
        dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    except ValueError:
        return True
    return dt >= datetime.now(timezone.utc) - timedelta(hours=hours_window)


def _request_json(url: str, api_key: str, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not url:
        return []
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return data.get("items", []) or data.get("data", [])
        return []
    except requests.RequestException as exc:
        print(f"[ERROR] Failed requesting {url}: {exc}")
        return []


def _normalize_generic(raw: Dict[str, Any], platform: str) -> Dict[str, Any]:
    return {
        "platform": platform,
        "author": raw.get("author") or raw.get("username") or "Unknown",
        "text": raw.get("text") or raw.get("content") or "",
        "url": raw.get("url") or "",
        "likes": _safe_int(raw.get("likes")),
        "comments": _safe_int(raw.get("comments")),
        "reposts": _safe_int(
            raw.get("reposts") or raw.get("retweets") or raw.get("shares")
        ),
        "created_at": raw.get("created_at") or raw.get("published_at") or "",
    }


def _normalize_apify_twitter(item: Dict[str, Any]) -> Dict[str, Any]:
    author = item.get("author") or {}
    if isinstance(author, dict):
        author_name = author.get("name") or author.get("userName") or "Unknown"
    else:
        author_name = str(author)
    created = _parse_twitter_created_at(item.get("createdAt") or "")
    return {
        "platform": "X",
        "author": author_name,
        "text": item.get("text") or "",
        "url": item.get("url") or item.get("twitterUrl") or "",
        "likes": _safe_int(item.get("likeCount")),
        "comments": _safe_int(item.get("replyCount")),
        "reposts": _safe_int(item.get("retweetCount")),
        "created_at": created,
    }


def _normalize_apify_linkedin(item: Dict[str, Any]) -> Dict[str, Any]:
    author = item.get("author") or {}
    if isinstance(author, dict):
        name = (
            f"{author.get('first_name', '')} {author.get('last_name', '')}".strip()
            or author.get("username")
            or "Unknown"
        )
    else:
        name = "Unknown"
    stats = item.get("stats") or {}
    return {
        "platform": "LinkedIn",
        "author": name,
        "text": item.get("text") or "",
        "url": item.get("url") or "",
        "likes": _safe_int(stats.get("like") or stats.get("total_reactions")),
        "comments": _safe_int(stats.get("comments")),
        "reposts": _safe_int(stats.get("reposts")),
        "created_at": _parse_linkedin_created_at(item),
    }


def _fetch_custom_http(platform: str, url: str, key: str) -> List[Dict[str, Any]]:
    cfg = get_config()
    items = _request_json(
        url=url,
        api_key=key,
        payload={
            "keywords": cfg.keywords,
            "hours_window": cfg.hours_window,
            "limit": 100,
            "sort_by": "engagement",
        },
    )
    normalized = [_normalize_generic(item, platform) for item in items]
    return [
        p
        for p in normalized
        if p["text"] and p["url"] and _is_recent(p["created_at"], cfg.hours_window)
    ]


def _twitter_since_day(hours_window: int) -> str:
    day = (datetime.now(timezone.utc) - timedelta(hours=hours_window)).date().isoformat()
    return day


def _build_twitter_search_terms(keywords: List[str], hours_window: int) -> List[str]:
    parts: List[str] = []
    for k in keywords:
        k = k.strip()
        if not k:
            continue
        if " " in k:
            parts.append(f'"{k}"')
        else:
            parts.append(k)
    if not parts:
        parts = ["seo"]
    or_expr = " OR ".join(parts)
    since = _twitter_since_day(hours_window)
    # Top 排序在 input.sort；排除转发减少噪音
    query = f"({or_expr}) since:{since} -is:retweet"
    return [query]


def _linkedin_keywords_string(keywords: List[str]) -> str:
    """LinkedIn 搜索用若干词组合即可；空格分隔比手写 OR 更稳妥。"""
    cleaned = [k.strip() for k in keywords if k.strip()]
    if not cleaned:
        return "seo"
    return " ".join(cleaned[:8])


def _linkedin_date_posted_filter(hours_window: int) -> str:
    if hours_window <= 24:
        return "past-24h"
    if hours_window <= 168:
        return "past-week"
    return "past-month"


def _fetch_x_apify() -> List[Dict[str, Any]]:
    cfg = get_config()
    run_input = {
        "searchTerms": _build_twitter_search_terms(cfg.keywords, cfg.hours_window),
        "maxItems": cfg.twitter_max_items,
        "sort": "Top",
    }
    raw_items = run_actor_sync(
        cfg.apify_twitter_actor,
        run_input,
        cfg.apify_token,
        wait_for_finish_sec=cfg.apify_wait_sec,
    )
    posts = [_normalize_apify_twitter(it) for it in raw_items if isinstance(it, dict)]
    return [
        p
        for p in posts
        if p["text"] and p["url"] and _is_recent(p["created_at"], cfg.hours_window)
    ]


def _fetch_linkedin_apify() -> List[Dict[str, Any]]:
    cfg = get_config()
    run_input = {
        "keywords": _linkedin_keywords_string(cfg.keywords),
        "maxPosts": cfg.linkedin_max_posts,
        "sortBy": "relevance",
        "datePosted": _linkedin_date_posted_filter(cfg.hours_window),
        "profileScrapingMode": "short",
    }
    raw_items = run_actor_sync(
        cfg.apify_linkedin_actor,
        run_input,
        cfg.apify_token,
        wait_for_finish_sec=cfg.apify_wait_sec,
    )
    posts = [_normalize_apify_linkedin(it) for it in raw_items if isinstance(it, dict)]
    return [
        p
        for p in posts
        if p["text"] and p["url"] and _is_recent(p["created_at"], cfg.hours_window)
    ]


def fetch_posts() -> List[Dict[str, Any]]:
    cfg = get_config()
    x_posts: List[Dict[str, Any]] = []
    linkedin_posts: List[Dict[str, Any]] = []
    rss_posts: List[Dict[str, Any]] = []

    if cfg.x_api_url:
        x_posts = _fetch_custom_http("X", cfg.x_api_url, cfg.x_api_key)
    elif cfg.twitter_bearer_token and cfg.x_kol_profile_urls:
        from twitter_official import fetch_x_via_official_api

        print("[INFO] Fetching X via Twitter API v2（你配置的 KOL 主页）...")
        x_posts = fetch_x_via_official_api(
            cfg.twitter_bearer_token,
            cfg.x_kol_profile_urls,
            cfg.twitter_tweets_per_kol,
            cfg.hours_window,
            cfg.keywords,
            cfg.x_kol_skip_keyword_filter,
        )
    elif cfg.apify_token:
        print("[INFO] Fetching X via Apify...")
        x_posts = _fetch_x_apify()

    if cfg.linkedin_api_url:
        linkedin_posts = _fetch_custom_http(
            "LinkedIn", cfg.linkedin_api_url, cfg.linkedin_api_key
        )
    elif cfg.apify_token:
        print("[INFO] Fetching LinkedIn via Apify...")
        linkedin_posts = _fetch_linkedin_apify()

    if cfg.rss_feed_urls:
        from rss_fetcher import fetch_rss_posts

        print("[INFO] Fetching RSS（含可将 LinkedIn 转为订阅源）...")
        rss_posts = fetch_rss_posts(
            cfg.rss_feed_urls,
            cfg.hours_window,
            cfg.keywords,
            cfg.rss_match_keywords,
        )

    li_from_rss = [p for p in rss_posts if p.get("platform") == "LinkedIn"]
    rss_other = [p for p in rss_posts if p.get("platform") != "LinkedIn"]
    linkedin_posts = linkedin_posts + li_from_rss

    all_posts = x_posts + linkedin_posts + rss_other

    if not all_posts:
        print(
            "[WARN] 未抓到帖子。可选配置："
            "① Apify `APIFY_API_TOKEN`；"
            "② X 官方接口 `TWITTER_BEARER_TOKEN` + `X_KOL_PROFILE_URLS`；"
            "③ `RSS_FEED_URLS`；④ 自建 `X_POSTS_API_URL` / `LINKEDIN_POSTS_API_URL`。"
        )
    else:
        print(
            f"[INFO] Fetched {len(all_posts)} posts "
            f"(X: {len(x_posts)}, LinkedIn 合计: {len(linkedin_posts)}, 其他 RSS: {len(rss_other)})."
        )
    return all_posts
