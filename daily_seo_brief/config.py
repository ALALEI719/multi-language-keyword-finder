from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List

from dotenv import load_dotenv

load_dotenv()


def _split_multi_value(raw: str) -> List[str]:
    """支持逗号分隔或换行分隔。"""
    text = (raw or "").strip()
    if not text:
        return []
    normalized = text.replace("\n", ",")
    return [s.strip() for s in normalized.split(",") if s.strip()]


@dataclass
class AppConfig:
    # 可选：自建 HTTP 接口（若填写则优先于其他抓取方式）
    x_api_url: str
    x_api_key: str
    linkedin_api_url: str
    linkedin_api_key: str
    # 免 Apify：X 官方 API + KOL 主页
    twitter_bearer_token: str
    x_kol_profile_urls: List[str]
    twitter_tweets_per_kol: int
    x_kol_skip_keyword_filter: bool
    # 免 Apify：RSS（可把 LinkedIn/其他平台「转成 RSS」后填入）
    rss_feed_urls: List[str]
    rss_match_keywords: bool
    # Apify
    apify_token: str
    apify_twitter_actor: str
    apify_linkedin_actor: str
    apify_wait_sec: int
    twitter_max_items: int
    linkedin_max_posts: int
    # 飞书 + LLM
    feishu_webhook_url: str
    llm_api_key: str
    llm_base_url: str
    llm_model: str
    # 业务
    keywords: List[str]
    hours_window: int


def _split_keywords(raw: str) -> List[str]:
    return [k.strip() for k in raw.split(",") if k.strip()]


def get_config() -> AppConfig:
    return AppConfig(
        x_api_url=os.getenv("X_POSTS_API_URL", ""),
        x_api_key=os.getenv("X_POSTS_API_KEY", ""),
        linkedin_api_url=os.getenv("LINKEDIN_POSTS_API_URL", ""),
        linkedin_api_key=os.getenv("LINKEDIN_POSTS_API_KEY", ""),
        twitter_bearer_token=os.getenv("TWITTER_BEARER_TOKEN", ""),
        x_kol_profile_urls=_split_multi_value(os.getenv("X_KOL_PROFILE_URLS", "")),
        twitter_tweets_per_kol=int(os.getenv("TWITTER_TWEETS_PER_KOL", "30")),
        x_kol_skip_keyword_filter=os.getenv("X_KOL_SKIP_KEYWORD_FILTER", "false").lower()
        in ("1", "true", "yes"),
        rss_feed_urls=_split_multi_value(os.getenv("RSS_FEED_URLS", "")),
        rss_match_keywords=os.getenv("RSS_MATCH_KEYWORDS", "true").lower() in ("1", "true", "yes"),
        apify_token=os.getenv("APIFY_API_TOKEN", ""),
        apify_twitter_actor=os.getenv(
            "APIFY_TWITTER_ACTOR",
            "apidojo/tweet-scraper",
        ),
        apify_linkedin_actor=os.getenv(
            "APIFY_LINKEDIN_ACTOR",
            "benjarapi/linkedin-post-search",
        ),
        apify_wait_sec=int(os.getenv("APIFY_WAIT_SEC", "300")),
        twitter_max_items=int(os.getenv("TWITTER_MAX_ITEMS", "120")),
        linkedin_max_posts=int(os.getenv("LINKEDIN_MAX_POSTS", "80")),
        feishu_webhook_url=os.getenv("FEISHU_WEBHOOK_URL", ""),
        llm_api_key=os.getenv("LLM_API_KEY", ""),
        llm_base_url=os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"),
        llm_model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        keywords=_split_keywords(
            os.getenv(
                "SEO_KEYWORDS",
                "seo,technical seo,international seo,search intent,google updates",
            )
        ),
        hours_window=int(os.getenv("POSTS_HOURS_WINDOW", "24")),
    )
