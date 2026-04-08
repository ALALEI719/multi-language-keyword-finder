#!/usr/bin/env bash
# 在终端运行：bash daily_seo_brief/print_cron_line.sh
# 将输出的一行复制到 crontab -e 中（并核对 python3 路径）。

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="$(command -v python3 || true)"
if [[ -z "$PY" ]]; then
  echo "未找到 python3，请先安装 Python。" >&2
  exit 1
fi

echo "# 每天北京时间 9:30 运行（请整行复制到 crontab -e）："
echo "30 9 * * * TZ=Asia/Shanghai cd \"${ROOT}\" && \"${PY}\" daily_seo_brief/main.py >> \"${ROOT}/daily_seo_brief/cron.log\" 2>&1"
