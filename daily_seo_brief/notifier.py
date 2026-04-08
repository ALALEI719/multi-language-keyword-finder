from __future__ import annotations

from typing import List

import requests

from config import get_config


def send_feishu_message(title: str, body_lines: List[str]) -> None:
    cfg = get_config()
    if not cfg.feishu_webhook_url:
        print("[WARN] FEISHU_WEBHOOK_URL not set. Skip send.")
        return

    # 飞书群机器人对「纯文本」兼容性最好，避免因 post 卡片段落过长被拒。
    body = "\n".join(body_lines).strip()
    text = f"{title}\n\n{body}" if body else title
    if len(text) > 15000:
        text = text[:14900] + "\n\n...(内容过长已截断)"

    payload = {
        "msg_type": "text",
        "content": {"text": text},
    }

    try:
        resp = requests.post(cfg.feishu_webhook_url, json=payload, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, dict) and data.get("code") not in (0, None):
            print(f"[WARN] Feishu API returned: {data}")
    except requests.RequestException as exc:
        print(f"[ERROR] Failed to send Feishu message: {exc}")
