from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List
from urllib.parse import urlparse

import requests


def _parse_x_username(raw: str) -> str | None:
    s = raw.strip()
    if not s:
        return None
    if s.startswith("@"):
        return s[1:].split("/")[0].split("?")[0] or None
    if "http://" in s or "https://" in s:
        u = urlparse(s)
        host = (u.netloc or "").lower()
        if host not in ("x.com", "www.x.com", "twitter.com", "www.twitter.com", "mobile.twitter.com"):
            return None
        parts = [p for p in u.path.split("/") if p]
        if not parts:
            return None
        if parts[0] in ("intent", "search", "hashtag", "i", "settings"):
            return None
        if parts[0] == "status" or (len(parts) >= 2 and parts[1] == "status"):
            return None
        name = parts[0].lstrip("@")
        return name or None
    return s.lstrip("@").split("/")[0].split("?")[0] or None


def extract_x_usernames(urls_or_handles: List[str]) -> List[str]:
    seen: set[str] = set()
    out: List[str] = []
    for item in urls_or_handles:
        uname = _parse_x_username(item)
        if not uname:
            continue
        key = uname.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(uname)
    return out


def _headers(bearer: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {bearer}"}


def lookup_user_id(bearer: str, username: str) -> str | None:
    url = f"https://api.twitter.com/2/users/by/username/{username}"
    try:
        r = requests.get(url, headers=_headers(bearer), timeout=30)
        if r.status_code == 404:
            print(f"[WARN] X 用户不存在或已改名: @{username}")
            return None
        if r.status_code == 403:
            print(
                "[WARN] Twitter API 返回 403：当前开发者套餐可能无权读取用户资料，"
                "请检查 X Developer Portal 的项目权限与计费档位。"
            )
            return None
        r.raise_for_status()
        data = r.json().get("data") or {}
        uid = data.get("id")
        return str(uid) if uid else None
    except requests.RequestException as exc:
        print(f"[ERROR] Twitter user lookup failed @{username}: {exc}")
        return None


def _tweet_matches_keywords(text: str, keywords: List[str]) -> bool:
    if not keywords:
        return True
    lower = text.lower()
    return any(k.strip().lower() in lower for k in keywords if k.strip())


def fetch_user_tweets(
    bearer: str,
    username: str,
    user_id: str,
    max_results: int,
    hours_window: int,
    keywords: List[str],
    skip_keyword_filter: bool,
) -> List[Dict[str, Any]]:
    """调用 X API v2：用户时间线（需应用在开发者后台启用相应权限）。"""
    max_results = max(5, min(max_results, 100))
    url = f"https://api.twitter.com/2/users/{user_id}/tweets"
    params = {
        "max_results": max_results,
        "tweet.fields": "created_at,public_metrics",
        "exclude": "retweets,replies",
    }
    try:
        r = requests.get(url, headers=_headers(bearer), params=params, timeout=45)
        if r.status_code == 403:
            print(
                f"[WARN] 拉取 @{username} 时间线被拒 (403)："
                "请确认项目已申请读取推文权限，且账户有可用配额。"
            )
            return []
        r.raise_for_status()
        payload = r.json()
    except requests.RequestException as exc:
        print(f"[ERROR] Twitter timeline failed @{username}: {exc}")
        return []

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=hours_window)
    posts: List[Dict[str, Any]] = []

    for tw in payload.get("data") or []:
        if not isinstance(tw, dict):
            continue
        tid = tw.get("id")
        text = tw.get("text") or ""
        created = tw.get("created_at") or ""
        metrics = tw.get("public_metrics") or {}
        if not text or not tid:
            continue
        if not skip_keyword_filter and not _tweet_matches_keywords(text, keywords):
            continue
        try:
            cdt = datetime.fromisoformat(created.replace("Z", "+00:00"))
        except ValueError:
            cdt = now
        if cdt < cutoff:
            continue
        posts.append(
            {
                "platform": "X",
                "author": username,
                "text": text,
                "url": f"https://x.com/{username}/status/{tid}",
                "likes": int(metrics.get("like_count") or 0),
                "comments": int(metrics.get("reply_count") or 0),
                "reposts": int(metrics.get("retweet_count") or 0),
                "created_at": cdt.isoformat(),
            }
        )
    return posts


def fetch_x_via_official_api(
    bearer: str,
    profile_urls: List[str],
    tweets_per_kol: int,
    hours_window: int,
    keywords: List[str],
    skip_keyword_filter: bool,
) -> List[Dict[str, Any]]:
    users = extract_x_usernames(profile_urls)
    if not users:
        print("[WARN] X_KOL_PROFILE_URLS 为空或无法解析出用户名。")
        return []
    all_posts: List[Dict[str, Any]] = []
    for uname in users:
        uid = lookup_user_id(bearer, uname)
        if not uid:
            continue
        batch = fetch_user_tweets(
            bearer,
            uname,
            uid,
            tweets_per_kol,
            hours_window,
            keywords,
            skip_keyword_filter,
        )
        all_posts.extend(batch)
        print(f"[INFO] X API @{uname}: {len(batch)} 条符合条件推文")
    return all_posts
