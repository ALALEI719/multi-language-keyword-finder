from __future__ import annotations

from typing import Any, Dict, List

import requests


def actor_slug(actor_id: str) -> str:
    """Apify REST API 使用 owner~name，例如 apidojo/tweet-scraper -> apidojo~tweet-scraper。"""
    return actor_id.strip().replace("/", "~")


def run_actor_sync(
    actor_id: str,
    run_input: Dict[str, Any],
    token: str,
    wait_for_finish_sec: int = 300,
) -> List[Dict[str, Any]]:
    """
    同步运行 Actor（带 waitForFinish），返回 default dataset 中的全部 items。
    文档：https://docs.apify.com/api/v2/act-runs-post
    """
    if not token or not actor_id:
        return []

    url = f"https://api.apify.com/v2/acts/{actor_slug(actor_id)}/runs"
    params = {"token": token, "waitForFinish": wait_for_finish_sec}
    try:
        resp = requests.post(
            url,
            params=params,
            json=run_input,
            timeout=wait_for_finish_sec + 90,
        )
        resp.raise_for_status()
        payload = resp.json()
    except requests.RequestException as exc:
        print(f"[ERROR] Apify run failed to start/finish: {exc}")
        return []

    data = payload.get("data") or {}
    dataset_id = data.get("defaultDatasetId")
    status = data.get("status")
    if status and status not in ("SUCCEEDED", "READY"):
        print(f"[WARN] Apify run status={status}, run_id={data.get('id')}")

    if not dataset_id:
        print("[ERROR] Apify response missing defaultDatasetId.")
        return []

    return fetch_dataset_items(dataset_id, token)


def fetch_dataset_items(dataset_id: str, token: str, limit: int = 5000) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    offset = 0
    page = 500

    while offset < limit:
        url = f"https://api.apify.com/v2/datasets/{dataset_id}/items"
        params = {"token": token, "clean": "true", "limit": page, "offset": offset}
        try:
            resp = requests.get(url, params=params, timeout=60)
            resp.raise_for_status()
            batch = resp.json()
        except (requests.RequestException, ValueError) as exc:
            print(f"[ERROR] Apify dataset fetch failed: {exc}")
            break

        if not isinstance(batch, list) or not batch:
            break
        items.extend(batch)
        if len(batch) < page:
            break
        offset += page

    return items
