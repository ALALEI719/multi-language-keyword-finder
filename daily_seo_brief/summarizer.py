from __future__ import annotations

from typing import Dict, List

import requests

from config import get_config


def _build_prompt(post: Dict) -> str:
    return (
        "你是SEO分析助手。请把下面帖子用简体中文总结成1-2句话，"
        "强调对SEO从业者的实操价值，语气专业但易懂。\n\n"
        f"平台: {post['platform']}\n"
        f"作者: {post['author']}\n"
        f"正文: {post['text']}\n"
    )


def _call_llm(prompt: str) -> str:
    cfg = get_config()
    if not cfg.llm_api_key:
        return "未配置 LLM_API_KEY，暂时只展示原帖信息。"

    url = f"{cfg.llm_base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {cfg.llm_api_key}",
        "Content-Type": "application/json",
    }
    body = {
        "model": cfg.llm_model,
        "messages": [
            {"role": "system", "content": "你是一个专业SEO内容分析师。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
    }
    try:
        resp = requests.post(url, headers=headers, json=body, timeout=45)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
    except (requests.RequestException, KeyError, IndexError) as exc:
        print(f"[ERROR] LLM summary failed: {exc}")
        return "总结生成失败，已降级为原文链接。"


def summarize_posts_in_chinese(posts: List[Dict]) -> List[Dict]:
    output = []
    for post in posts:
        summary = _call_llm(_build_prompt(post))
        output.append(
            {
                "platform": post["platform"],
                "author": post["author"],
                "summary": summary,
                "likes": post["likes"],
                "comments": post["comments"],
                "reposts": post["reposts"],
                "url": post["url"],
            }
        )
    return output
