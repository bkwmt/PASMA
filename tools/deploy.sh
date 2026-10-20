#!/usr/bin/env bash
# PASMA 網站部署。
#   tools/deploy.sh "commit message"   建置 → 檢查 → commit → push → 線上驗證
#   tools/deploy.sh --init             只做一次：刪除並重建 GitHub repo bkwmt/PASMA（清掉含資料的舊歷史）、
#                                      推送、啟用 Pages、驗證；需要使用者輸入 DELETE-PASMA 才會執行。
set -euo pipefail
cd "$(dirname "$0")/.."

REPO="bkwmt/PASMA"
URL="https://bkwmt.github.io/PASMA/"
PY=".venv/bin/python"

build_and_check() {
  "$PY" tools/build.py
  "$PY" tools/check.py
  "$PY" -m unittest discover -s tools/tests >/dev/null
}

verify_online() {
  local expect_build; expect_build=$(grep -o 'name="build" content="[^"]*"' index.html | head -1)
  echo "waiting for Pages (up to 10 min)…"
  for i in $(seq 1 60); do
    code=$(curl -s -o /dev/null -w "%{http_code}" "$URL")
    old=$(curl -s -o /dev/null -w "%{http_code}" "${URL}data/albums.json")
    live=$(curl -s "$URL" | grep -o 'name="build" content="[^"]*"' | head -1 || true)
    if [[ "$code" == "200" && "$old" == "404" && "$live" == "$expect_build" ]]; then
      echo "online: $URL 200; old data path 404; build stamp matches."
      return 0
    fi
    sleep 10
  done
  echo "WARNING: could not confirm the live site (code=$code old=$old live='$live')." >&2
  return 1
}

if [[ "${1:-}" == "--init" ]]; then
  echo "This deletes the GitHub repo $REPO (its history holds the dataset) and recreates it."
  read -r -p "Type DELETE-PASMA to continue: " ans
  [[ "$ans" == "DELETE-PASMA" ]] || { echo "aborted"; exit 1; }
  build_and_check
  gh auth status >/dev/null
  gh auth refresh -h github.com -s delete_repo
  gh repo delete "$REPO" --yes
  gh repo create "$REPO" --public --disable-wiki \
    --description "PASMA: Private Archive of Scanned Music Artifacts — project site of the ISMIR 2026 paper (backstage networks in postwar Taiwanese popular music)"
  if [[ ! -d .git ]]; then git init -b main; fi
  git add -A
  git commit -m "PASMA project site" || true
  git remote remove origin 2>/dev/null || true
  git remote add origin "https://github.com/$REPO.git"
  git push -u origin main
  gh api -X POST "repos/$REPO/pages" -f "source[branch]=main" -f "source[path]=/" >/dev/null
  for i in $(seq 1 30); do
    st=$(gh api "repos/$REPO/pages" --jq .status 2>/dev/null || echo "")
    [[ "$st" == "built" ]] && break
    sleep 10
  done
  verify_online || true
  # 舊的資料庫瀏覽器留作內部工具，移除 remote 以免誤推資料
  if git -C /Users/hugowski/Developer/ghouse/web remote get-url origin >/dev/null 2>&1; then
    git -C /Users/hugowski/Developer/ghouse/web remote remove origin
    echo "removed origin from ghouse/web (internal tool only now)."
  fi
  exit 0
fi

msg="${1:-site update $(date +%F)}"
build_and_check
git add -A
git commit -m "$msg" || echo "nothing to commit"
git push
verify_online || true
