#!/usr/bin/env python3
"""PASMA 網站守門檢查。回傳非零即不得部署。

檢查站根：每個 *.html 可解析、lang="en"、<title>、viewport、description；
不引用外部 script/stylesheet/圖片/影片（site.yaml allowed_external 可放行網域）；
站內 href/src/poster 都存在且不以 / 開頭；無殘留數字佔位符；
資料守門：站內無 data/ 目錄、無 *.json（除 manifest.lock.json）、檔名不含 albums／ocr／network_full／sna；
>10 MB 的檔案須在 site.yaml large_files 白名單；.nojekyll 存在。
--links：另外測外部連結（HEAD，失敗再 GET）。
用法：.venv/bin/python tools/check.py [--root DIR] [--links]
"""
from __future__ import annotations

import argparse
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
LIMIT = 10 * 1024 * 1024
DATA_NAME = re.compile(r"albums|(^|[^a-z])ocr([^a-z]|$)|network_full|(^|[^a-z])sna([^a-z]|$)", re.I)
PLACEHOLDER = re.compile(r"\{[^\s{}]*[一-鿿_][^\s{}]*\}")
RESOURCE_ATTRS = {"script": "src", "link": "href", "img": "src", "iframe": "src", "video": "src", "source": "src",
                  "track": "src", "audio": "src"}


class Collector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.lang = None
        self.title = False
        self.viewport = False
        self.description = False
        self.resources: list[tuple[str, str]] = []   # (tag, url)
        self.links: list[str] = []
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        if tag == "title":
            self._in_title = True
        if tag == "meta":
            if a.get("name") == "viewport":
                self.viewport = True
            if a.get("name") == "description" and a.get("content"):
                self.description = True
        if tag in RESOURCE_ATTRS and a.get(RESOURCE_ATTRS[tag]):
            self.resources.append((tag, a[RESOURCE_ATTRS[tag]]))
        if tag == "video" and a.get("poster"):
            self.resources.append(("video-poster", a["poster"]))
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])

    def handle_data(self, data):
        if self._in_title and data.strip():
            self.title = True

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False


def is_external(url: str) -> bool:
    return url.startswith(("http://", "https://", "//"))


def check_site(root: Path, site: dict) -> tuple[list[str], list[str]]:
    """回傳 (問題清單, 外部連結清單)。"""
    problems: list[str] = []
    external: set[str] = set()
    allowed = set(site.get("allowed_external", []) or [])
    large_ok = set(site.get("large_files", []) or [])

    if not (root / ".nojekyll").exists():
        problems.append(".nojekyll missing")
    pages = sorted(root.glob("*.html"))
    if not pages:
        problems.append("no *.html at site root")

    for page in pages:
        text = page.read_text(encoding="utf-8")
        c = Collector()
        try:
            c.feed(text)
        except Exception as e:  # HTMLParser 幾乎不拋錯，保險
            problems.append(f"{page.name}: parse error {e}")
            continue
        if c.lang != "en":
            problems.append(f'{page.name}: <html lang> is {c.lang!r}, expected "en"')
        for ok, label in ((c.title, "<title>"), (c.viewport, "viewport meta"), (c.description, "description meta")):
            if not ok:
                problems.append(f"{page.name}: missing {label}")
        for m in PLACEHOLDER.finditer(text):
            problems.append(f"{page.name}: unresolved placeholder {m.group(0)}")
        for tag, url in c.resources:
            if is_external(url):
                host = re.sub(r"^(https?:)?//", "", url).split("/")[0]
                if host not in allowed:
                    problems.append(f"{page.name}: external {tag} resource {url}")
            else:
                _check_internal(page, url, root, problems)
        for href in c.links:
            if href.startswith(("mailto:", "#", "tel:")):
                continue
            if is_external(href):
                external.add(href)
            else:
                _check_internal(page, href, root, problems)

    # 資料守門與大檔
    for p in root.rglob("*"):
        rel = p.relative_to(root).as_posix()
        if p.is_dir():
            if p.name == "data" and not rel.startswith((".git", ".venv", "work", "content", "tools")):
                problems.append(f"data directory present: {rel}")
            continue
        if rel.startswith((".git/", ".venv/", "work/", "content/", "tools/", "build/")):
            continue
        if p.suffix == ".json" and rel != "manifest.lock.json":
            problems.append(f"json file present at site: {rel}")
        if DATA_NAME.search(p.name):
            problems.append(f"file name looks like dataset material: {rel}")
        if p.stat().st_size > LIMIT and rel not in large_ok:
            problems.append(f"file over 10 MB and not whitelisted: {rel} ({p.stat().st_size/1e6:.1f} MB)")
    return problems, sorted(external)


def _check_internal(page: Path, url: str, root: Path, problems: list[str]) -> None:
    if url.startswith("/"):
        problems.append(f"{page.name}: root-relative link breaks under /PASMA/: {url}")
        return
    target, _, frag = url.partition("#")
    target = target.split("?")[0]
    file = (root / target) if target else page
    if target and not file.exists():
        problems.append(f"{page.name}: missing target {url}")
        return
    if frag and file.suffix == ".html":
        if f'id="{frag}"' not in file.read_text(encoding="utf-8"):
            problems.append(f"{page.name}: missing anchor {url}")


def check_links(urls: list[str]) -> list[str]:
    def probe(u: str) -> str | None:
        for method in ("HEAD", "GET"):
            try:
                req = urllib.request.Request(u, method=method, headers={"User-Agent": "Mozilla/5.0 (PASMA link check)"})
                with urllib.request.urlopen(req, timeout=20) as r:
                    if r.status < 400:
                        return None
            except urllib.error.HTTPError as e:
                if method == "GET":
                    return f"{u} → HTTP {e.code}"
            except Exception as e:
                if method == "GET":
                    return f"{u} → {e}"
        return f"{u} → unreachable"

    with ThreadPoolExecutor(max_workers=8) as ex:
        return [r for r in ex.map(probe, urls) if r]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--links", action="store_true", help="也測外部連結")
    args = ap.parse_args(argv)
    site = yaml.safe_load((ROOT / "tools" / "site.yaml").read_text(encoding="utf-8"))
    problems, external = check_site(args.root.resolve(), site)
    if args.links:
        bad = check_links(external)
        problems += [f"external link failed: {b}" for b in bad]
        print(f"external links checked: {len(external)}, failed: {len(bad)}")
    for p in problems:
        print("PROBLEM:", p)
    print(f"check: {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
