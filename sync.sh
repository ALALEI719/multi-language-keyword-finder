#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./sync.sh "your commit message"
#   ./sync.sh

cd "$(dirname "$0")"

if [[ -n "${1:-}" ]]; then
  MSG="$1"
else
  MSG="chore: sync updates $(date '+%Y-%m-%d %H:%M:%S')"
fi

git add .

if git diff --cached --quiet; then
  echo "No changes to commit."
  exit 0
fi

git commit -m "$MSG"
git push

echo "Done: committed and pushed to origin/main"
