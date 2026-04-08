from __future__ import annotations

import sys
import traceback
from datetime import datetime

from fetchers import fetch_posts
from notifier import send_feishu_message
from ranking import pick_top_posts
from summarizer import summarize_posts_in_chinese


def run_daily_brief() -> None:
    now = datetime.now().strftime("%Y-%m-%d")
    print(f"[INFO] Starting daily SEO brief for {now}")

    posts = fetch_posts()
    if not posts:
        send_feishu_message(
            title=f"SEO 热门帖日报（{now}）",
            body_lines=["今天没有抓取到可用帖子，请检查 Apify Token、飞书 Webhook 或网络；也可调大 TWITTER_MAX_ITEMS。"],
        )
        print("[WARN] No posts fetched.")
        return

    top_posts = pick_top_posts(posts, top_k=10)
    summaries = summarize_posts_in_chinese(top_posts)

    body_lines = []
    for index, item in enumerate(summaries, start=1):
        body_lines.extend(
            [
                f"{index}. [{item['platform']}] {item['author']}",
                f"   中文总结：{item['summary']}",
                f"   热度：点赞 {item['likes']} | 评论 {item['comments']} | 转发 {item['reposts']}",
                f"   链接：{item['url']}",
                "",
            ]
        )

    send_feishu_message(
        title=f"SEO 热门帖日报 Top 10（{now}）",
        body_lines=body_lines or ["今天暂无可推送内容。"],
    )
    print("[INFO] Daily SEO brief sent to Feishu.")


if __name__ == "__main__":
    try:
        run_daily_brief()
    except Exception as exc:
        now = datetime.now().strftime("%Y-%m-%d")
        tb = traceback.format_exc()
        print(tb)
        try:
            send_feishu_message(
                title=f"SEO 日报运行失败（{now}）",
                body_lines=[
                    f"异常类型：{type(exc).__name__}",
                    f"简要说明：{exc}",
                    "完整堆栈已打印在运行日志（终端或 cron.log），请向上翻动查看。",
                ],
            )
        except Exception:
            pass
        sys.exit(1)
