from __future__ import annotations

from collections import OrderedDict
from typing import Dict, List


def _keyword_bonus(text: str) -> int:
    text_lower = text.lower()
    keywords = [
        "seo",
        "technical seo",
        "international seo",
        "search intent",
        "core web vitals",
        "google update",
    ]
    return sum(3 for kw in keywords if kw in text_lower)


def _score(post: Dict) -> int:
    return (
        post.get("likes", 0) * 1
        + post.get("comments", 0) * 2
        + post.get("reposts", 0) * 2
        + _keyword_bonus(post.get("text", ""))
    )


def _deduplicate(posts: List[Dict]) -> List[Dict]:
    unique = OrderedDict()
    for p in posts:
        key = p["url"].strip().lower()
        if key and key not in unique:
            unique[key] = p
    return list(unique.values())


def _reserved_li_rss_slots(top_k: int) -> int:
    """为 LinkedIn / RSS（常为 0 互动）预留名额，避免只有 X 大热门入选。"""
    if top_k <= 3:
        return 0
    return min(2, top_k // 3)


def pick_top_posts(posts: List[Dict], top_k: int = 10) -> List[Dict]:
    deduped = _deduplicate(posts)
    ranked = sorted(deduped, key=_score, reverse=True)
    reserve = _reserved_li_rss_slots(top_k)
    primary_budget = max(0, top_k - reserve)

    picked: List[Dict] = []
    used = set()

    for p in ranked:
        if len(picked) >= primary_budget:
            break
        key = p["url"].strip().lower()
        if key not in used:
            used.add(key)
            picked.append(p)

    li_rss_candidates = [
        p
        for p in deduped
        if p.get("platform") in ("LinkedIn", "RSS") and p["url"].strip().lower() not in used
    ]
    li_rss_sorted = sorted(
        li_rss_candidates,
        key=lambda x: x.get("created_at") or "",
        reverse=True,
    )
    for p in li_rss_sorted:
        if len(picked) >= top_k:
            break
        key = p["url"].strip().lower()
        if key not in used:
            used.add(key)
            picked.append(p)

    for p in ranked:
        if len(picked) >= top_k:
            break
        key = p["url"].strip().lower()
        if key not in used:
            used.add(key)
            picked.append(p)

    return picked[:top_k]
