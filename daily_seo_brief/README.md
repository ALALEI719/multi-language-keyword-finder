# 每日 SEO 热帖 → 中文摘要 → 飞书（全自动）

这条流水线会做 5 件事：

1. **按你选的抓取方式**拉取 **X**、**LinkedIn**（及任意 **RSS** 源）上的内容。
2. 按互动 + 关键词 **排序**（并为 LinkedIn/RSS 预留名额，避免只有 X 高赞帖），取 **Top 10**。
3. 调用 **大模型（OpenAI 兼容接口）** 生成 **中文短摘要**。
4. 通过 **飞书群机器人 Webhook** 推送纯文本消息。
5. 若运行崩溃，会尽量往飞书推一条「失败说明」。

---

## 不想用 Apify？可以

### ① X：Twitter / X 官方 API + 你关注的 KOL 主页

- 在 [X Developer Portal](https://developer.twitter.com/) 建应用，申请能 **读用户时间线** 的权限与 **Bearer Token**（具体套餐与配额以官方为准；免费档若受限，需升级到付费档）。
- 在 `.env` 填写：
  - `TWITTER_BEARER_TOKEN`
  - `X_KOL_PROFILE_URLS`：多个主页链接，英文逗号分隔即可，例如 `https://x.com/ahrefs,https://x.com/rustybrick`
- 默认只会保留正文中包含 `SEO_KEYWORDS` 的推文；若你希望「KOL 发什么都进候选」，设 `X_KOL_SKIP_KEYWORD_FILTER=true`。

### ② LinkedIn：没有稳定的「免费官方读好友动态 API」

常见做法是：

- 使用第三方 **「LinkedIn 动态 → RSS」** 服务（商业/合规风险自行评估），把得到的 **RSS 地址**填进 `RSS_FEED_URLS`；
- 或继续用 Apify 等工具只抓 LinkedIn；
- 或手工/mvp 阶段只盯 **X + RSS**，暂不抓原生 LinkedIn API。

### ③ 任意 RSS（博客、栏目、聚合源）

- `RSS_FEED_URLS`：多个订阅地址，逗号或换行均可。
- 若链接域名含 `linkedin.com`，展示来源会标成 **LinkedIn**（方便你区分）。

### ④ 仍可用 Apify（关键词刷「全站热帖」）

不配 KOL、想按关键词搜全天热点时，`APIFY_API_TOKEN` 依然可用（与上面几种方式可并存；**自建 HTTP 接口 URL 优先级最高**）。

---

## 至少要准备的两样东西（无论什么抓取方式）

| 物品 | 用途 | 怎么拿 |
|------|------|--------|
| **飞书 Webhook** | 推送到你的群 | 飞书群 → **设置 → 群机器人 → 自定义机器人** → 复制 **Webhook** |
| **LLM API Key** | 中文总结 | OpenAI 或兼容接口（`LLM_BASE_URL` + `LLM_API_KEY`） |

**再加「数据」任选其一：** `TWITTER_BEARER_TOKEN` + `X_KOL_PROFILE_URLS`，和/或 `RSS_FEED_URLS`，和/或 `APIFY_API_TOKEN`，和/或自建 `X_POSTS_API_URL` / `LINKEDIN_POSTS_API_URL`。

---

## 第一步：安装依赖

在**项目根目录** `seo-intent-tool` 下执行：

```bash
cd /Users/issuser/Developer/micro-saas-apps/seo-intent-tool
python3 -m pip install -r requirements.txt
```

---

## 第二步：配置 `.env`

把模板复制到**项目根目录**（与 `app.py` 同级）：

```bash
cd /Users/issuser/Developer/micro-saas-apps/seo-intent-tool
cp daily_seo_brief/.env.example .env
```

编辑 `.env`，**至少**填：

- `FEISHU_WEBHOOK_URL`
- `LLM_API_KEY`

并至少启用一种数据源，例如：

- **KOL 模式：** `TWITTER_BEARER_TOKEN` + `X_KOL_PROFILE_URLS`
- **RSS 模式：** `RSS_FEED_URLS`
- **关键词刷热点：** `APIFY_API_TOKEN`

其他常用参数：

- `SEO_KEYWORDS`：英文关键词，逗号分隔（用于过滤与加权）
- `POSTS_HOURS_WINDOW`：时间窗（小时）
- Apify 专用：`TWITTER_MAX_ITEMS` / `LINKEDIN_MAX_POSTS`

---

## 第三步：手动试跑

仍在 `seo-intent-tool` 目录：

```bash
python3 daily_seo_brief/main.py
```

成功时：飞书群会收到 **「SEO 热门帖日报 Top 10」**；终端有 `Fetched ... posts`。

若 **走 Apify 时 X 结果为 0**：可尝试 `apidojo/twitter-scraper-lite`，或改用 **官方 API + KOL 主页**。

若 **官方 API 403**：多半是开发者项目权限、套餐或配额不足，需在 X Developer Portal 核对。

---

## 第四步：每天 9:30 定时运行（macOS）

1. 确认 Python 路径：

```bash
which python3
```

2. 打开定时任务表：

```bash
crontab -e
```

3. 追加一行（把 `python3` 换成上一步的**完整路径**；目录按你本机实际为准）：

```cron
30 9 * * * TZ=Asia/Shanghai cd /Users/issuser/Developer/micro-saas-apps/seo-intent-tool && /usr/bin/env python3 daily_seo_brief/main.py >> /Users/issuser/Developer/micro-saas-apps/seo-intent-tool/daily_seo_brief/cron.log 2>&1
```

也可运行辅助脚本，它会打印一行**几乎可直接粘贴**的 cron（请仍核对路径）：

```bash
bash daily_seo_brief/print_cron_line.sh
```

**macOS 提醒：** 若发现定时任务不读 `.env` 或写不了日志，请在 **系统设置 → 隐私与安全性 → 完全磁盘访问** 中按官方说明授予 `cron`/`Terminal` 相应权限。

---

## 进阶：自建 HTTP 数据源（可选）

若你已有内部接口，可在 `.env` 填写：

- `X_POSTS_API_URL` / `X_POSTS_API_KEY`
- `LINKEDIN_POSTS_API_URL` / `LINKEDIN_POSTS_API_KEY`

脚本会 **优先走你的 URL**，而不再对该平台调用 Apify。

---

## 常见问题

1. **飞书没消息**：检查 Webhook 是否失效、机器人是否还在群里；脚本用的是 `msg_type: text`。
2. **只有 LinkedIn 没有 X**：多为 X 搜索词太窄或触达 Actor 最小条数限制，尝试加宽 `SEO_KEYWORDS`、增大 `TWITTER_MAX_ITEMS` 或换 Lite Actor。
3. **摘要全是降级文案**：检查 `LLM_API_KEY`、网络能否访问 `LLM_BASE_URL`、模型名是否在该服务商下可用。
