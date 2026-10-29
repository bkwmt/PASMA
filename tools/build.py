#!/usr/bin/env python3
"""PASMA 專案網站建置器。

資料流：content/*.md（YAML front matter＋Markdown）
      ＋ tools/site.yaml（站名、導覽、信箱、頁尾）
      ＋ presentation/numbers.json（論文數字，{鍵} 代入，不手打數字）
      ＋ content/references.yaml（書目，[@鍵] 引用）
      ＋ content/people.yaml（人物卡資料）
      ＋ tools/manifest.yaml（圖、PDF、影片、頭像、試聽音訊的來源與處理模式）
      → 站根 *.html ＋ assets/ ＋ manifest.lock.json

用法：.venv/bin/python tools/build.py [--out DIR] [--no-assets]
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html as htmlmod
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import markdown
import yaml

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
CONTENT = ROOT / "content"

MAX_WIDTH = {"photo": 1600, "diagram": 1600, "scan": 600, "portrait": 480}
MD_EXTENSIONS = ["tables", "fenced_code", "sane_lists", "toc", "attr_list", "md_in_html", "footnotes"]


class BuildError(Exception):
    """任何會讓網站內容不正確的狀況都直接中止建置。"""


# ---------------------------------------------------------------- 讀檔
def load_yaml(path: Path) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}


def load_numbers(path: Path) -> dict[str, str]:
    """presentation/numbers.json：{鍵: {"值": …, "tex": …}} → {鍵: 值}。"""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return {k: str(v["值"]) for k, v in data.items()}


FRONT_MATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)


def split_front_matter(text: str) -> tuple[dict, str]:
    m = FRONT_MATTER.match(text)
    if not m:
        raise BuildError("content file lacks YAML front matter (--- … ---)")
    meta = yaml.safe_load(m.group(1)) or {}
    return meta, text[m.end():]


# ---------------------------------------------------------------- 數字代換
# 程式碼區塊（fenced 與 inline）切出來不處理：paper.md 的 BibTeX 有大括號。
CODE_SPLIT = re.compile(r"(```.*?```|`[^`\n]*`)", re.S)
PLACEHOLDER = re.compile(r"\{([^\s{}]{1,40})\}")


def _looks_like_key(key: str) -> bool:
    """含中文或底線的 {…} 才視為數字佔位符；{x, y} 這種英文散文不算。"""
    return bool(re.search(r"[一-鿿_]", key))


def _map_outside_code(text: str, fn) -> str:
    parts = CODE_SPLIT.split(text)
    return "".join(part if i % 2 else fn(part) for i, part in enumerate(parts))


def substitute_numbers(md: str, numbers: dict[str, str]) -> str:
    def repl(m: re.Match) -> str:
        key = m.group(1)
        if key in numbers:
            return numbers[key]
        if _looks_like_key(key):
            raise BuildError(f"unknown number key {{{key}}} (not in numbers.json)")
        return m.group(0)

    return _map_outside_code(md, lambda s: PLACEHOLDER.sub(repl, s))


# ---------------------------------------------------------------- 引用
CITATION = re.compile(r"\[(@[^\]]+)\]")


def render_citations(md: str, refs: dict) -> tuple[str, list[str]]:
    """[@a; @b, p. 7] → <sup class="cite"><a href="#ref-a">1</a>, <a href="#ref-b">2</a> (p. 7)</sup>；編號依每頁首次出現。

    每個項目是 `@鍵` 後面可接逗號與頁碼等定位詞（locator），定位詞原樣放在連結之後。"""
    used: list[str] = []

    def repl(m: re.Match) -> str:
        links = []
        for raw in m.group(1).split(";"):
            raw = raw.strip()
            key, _, locator = raw.partition(",")
            key = key.strip().lstrip("@")
            if key not in refs:
                raise BuildError(f"unknown reference key @{key} (not in references.yaml)")
            if key not in used:
                used.append(key)
            loc = f' <span class="loc">({htmlmod.escape(locator.strip())})</span>' if locator.strip() else ""
            links.append(f'<a href="#ref-{key}">{used.index(key) + 1}</a>{loc}')
        return '<sup class="cite">' + ", ".join(links) + "</sup>"

    return _map_outside_code(md, lambda s: CITATION.sub(repl, s)), used


def format_reference(key: str, r: dict) -> str:
    esc = htmlmod.escape
    s = f'{esc(str(r["author"]))} ({esc(str(r["year"]))}). {esc(str(r["title"]))}.'
    if r.get("container"):
        s += f' {esc(str(r["container"]))}.'
    if r.get("note"):
        s += f' {esc(str(r["note"]))}'
    if r.get("url"):
        url = esc(str(r["url"]))
        s += f' <a href="{url}" rel="noopener">{url}</a>'
    return f'<li id="ref-{esc(key)}">{s}</li>'


def references_html(used: list[str], refs: dict) -> str:
    if not used:
        return ""
    items = "".join(format_reference(k, refs[k]) for k in used)
    return f'<section id="references" class="references"><h2>References</h2><ol>{items}</ol></section>'


# ---------------------------------------------------------------- Markdown → HTML
def _figure(m: re.Match) -> str:
    img = m.group(1)
    alt = re.search(r'alt="([^"]*)"', img)
    img = img.replace("<img ", '<img loading="lazy" ', 1)
    caption = f"<figcaption>{alt.group(1)}</figcaption>" if alt and alt.group(1) else ""
    return f"<figure>{img}{caption}</figure>"


def md_to_html(body: str) -> str:
    md = markdown.Markdown(extensions=MD_EXTENSIONS, extension_configs={"toc": {"permalink": False}})
    html = md.convert(body)
    html = re.sub(r'href="([^"#:]+)\.md(#[^"]*)?"', lambda m: f'href="{m.group(1)}.html{m.group(2) or ""}"', html)
    html = re.sub(r'<a href="(https?://[^"]+)"(?![^>]*\brel=)', r'<a href="\1" rel="noopener"', html)
    html = re.sub(r"<p>(<img [^>]*>)</p>", _figure, html)
    html = html.replace("<table>", '<div class="tablewrap"><table>').replace("</table>", "</table></div>")
    return html


# ---------------------------------------------------------------- 人物卡
def people_cards(people: list[dict], site: dict) -> str:
    esc = htmlmod.escape
    traditions: dict = site.get("traditions", {})
    groups: dict[str, list[dict]] = {t: [] for t in traditions}
    for p in people:
        if not p.get("publish", True):
            continue
        groups.setdefault(p["tradition"], []).append(p)
    out = []
    for t, label in traditions.items():
        members = groups.get(t, [])
        if not members:
            continue
        out.append(f'<h2 id="tradition-{esc(t)}">{esc(label)}</h2>\n<div class="people-grid">')
        for p in members:
            slug = esc(p["slug"])
            if p.get("portrait"):
                avatar = (f'<img class="avatar" src="assets/img/people/{slug}.jpg" '
                          f'alt="Portrait of {esc(p["name_en"])}" loading="lazy" width="160" height="160">')
            else:
                avatar = f'<div class="avatar placeholder placeholder-{esc(t)}" aria-hidden="true"></div>'
            meta_bits = [b for b in (p.get("dates", ""), ", ".join(p.get("roles_en", []))) if b]
            alias = f' <span class="alias">({esc(p["alias_en"])})</span>' if p.get("alias_en") else ""
            meta = " · ".join(esc(b) for b in meta_bits)
            in_study = f'<p class="in-study">{esc(p["role_in_study"])}</p>' if p.get("role_in_study") else ""
            link = (f'<p class="more"><a href="{esc(p["pmdb_url"])}" rel="noopener">Profile at Taiwan Popular Music Database →</a></p>'
                    if p.get("pmdb_url") else "")
            out.append(
                f'<article class="person" id="{slug}">{avatar}'
                f'<h3>{esc(p["name_en"])} <span class="zh">{esc(p["name_zh"])}</span>{alias}</h3>'
                f'<p class="meta">{meta}</p><p class="bio">{esc(p["bio_en"]).strip()}</p>{in_study}{link}</article>'
            )
        out.append("</div>")
    if site.get("portrait_notice"):
        out.append(f'<p class="notice">{esc(site["portrait_notice"])}</p>')
    return "\n".join(out)


# ---------------------------------------------------------------- 版本
def site_version(site: dict) -> str:
    """頁尾的網站版本字串：「Companion site v1.2 (30 October 2026) · 」；site.yaml 無 version 則為空。"""
    v = site.get("version")
    if not v:
        return ""
    esc = htmlmod.escape
    date = f' ({esc(str(site["version_date"]))})' if site.get("version_date") else ""
    return f'Companion site v{esc(str(v))}{date} · '


def versions_block(site: dict) -> str:
    """Paper 頁 <!-- versions -->：網站版本紀錄，最新在前；論文本身不變，差異由版本承擔。"""
    esc = htmlmod.escape
    items = site.get("versions") or []
    if not items:
        return ""
    out = ['<ul class="versions">']
    for it in sorted(items, key=lambda x: str(x["v"]), reverse=True):
        out.append(f'<li><b>v{esc(str(it["v"]))}</b> <span class="muted">({esc(str(it["date"]))})</span> {esc(it["note"])}</li>')
    out.append("</ul>")
    return "\n".join(out)


# ---------------------------------------------------------------- 頁面外殼
def page(meta: dict, body_html: str, site: dict, active: str, build_time: str = "") -> str:
    esc = htmlmod.escape
    title = meta["title"]
    full_title = f'{site["title"]} · {site.get("tagline", "")}'.strip(" ·") if active == "index" else f'{title} · {site["title"]}'
    nav = "".join(
        f'<a href="{esc(item["file"])}.html"{" aria-current=\"page\"" if item["file"] == active else ""}>{esc(item["label"])}</a>'
        for item in site["nav"]
    )
    desc = esc(meta.get("description") or site.get("tagline", ""))
    emails = " · ".join(f'<a href="mailto:{esc(e)}">{esc(e)}</a>' for e in site.get("emails", []))
    build_time = build_time or dt.datetime.now().isoformat(timespec="minutes")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full_title)}</title>
<meta name="description" content="{desc}">
<meta name="build" content="{esc(build_time)}">
<link rel="stylesheet" href="assets/css/site.css">
<link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
</head>
<body class="page-{esc(active)}">
<header class="site-head"><div class="wrap">
<a class="brand" href="index.html"><span class="brand-main">{esc(site["title"])}</span><span class="brand-sub">{esc(site.get("brand_sub", ""))}</span></a>
<nav class="site-nav" aria-label="Site">{nav}</nav>
</div></header>
<main class="wrap">
{body_html}
</main>
<footer class="site-foot"><div class="wrap">
<p>{site.get("footer", "")}</p>
<p>Contact: {emails}</p>
<p class="small">{site_version(site)}Built {esc(build_time[:10])}.</p>
</div></footer>
</body>
</html>
"""


# ---------------------------------------------------------------- 資產
def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def process_image(src: Path, out: Path, mode: str, max_width: int | None = None, quality: int = 85) -> tuple[int, int]:
    """photo/portrait/scan → JPEG（RGBA 鋪白）；diagram → PNG。只縮不放。"""
    from PIL import Image

    max_width = max_width or MAX_WIDTH[mode]
    im = Image.open(src)
    if im.width > max_width:
        im = im.resize((max_width, round(im.height * max_width / im.width)), Image.LANCZOS)
    out.parent.mkdir(parents=True, exist_ok=True)
    if mode == "diagram":
        im.save(out, "PNG", optimize=True)
    else:
        if im.mode in ("RGBA", "LA", "P"):
            im = im.convert("RGBA")
            bg = Image.new("RGB", im.size, (255, 255, 255))
            bg.paste(im, mask=im.split()[-1])
            im = bg
        elif im.mode != "RGB":
            im = im.convert("RGB")
        im.save(out, "JPEG", quality=quality, optimize=True, subsampling=0)
    return im.size


def srt_to_vtt(srt: str) -> str:
    body = re.sub(r"(\d{2}:\d{2}:\d{2}),(\d{3})", r"\1.\2", srt.strip().replace("\r\n", "\n"))
    return "WEBVTT\n\n" + body + "\n"


# ---------------------------------------------------------------- 音訊（試聽）
def ffmpeg_args(src: Path, out: Path, bitrate: str, gain_db: float | None, excerpt: dict | None) -> list[str]:
    """組 ffmpeg 參數（純函式，可測）。gain_db 為線性增益；excerpt={start, seconds} 時切片並淡入淡出。"""
    args = ["ffmpeg", "-y", "-v", "error"]
    filters = []
    if excerpt:
        args += ["-ss", str(excerpt.get("start", 0))]
    args += ["-i", str(src)]
    if excerpt:
        sec = float(excerpt["seconds"])
        args += ["-t", str(sec)]
        filters += ["afade=t=in:d=1", f"afade=t=out:st={sec - 1:.2f}:d=1"]
    if gain_db is not None and abs(gain_db) > 0.05:
        filters.insert(0, f"volume={gain_db:.2f}dB")
    if filters:
        args += ["-af", ",".join(filters)]
    args += ["-vn", "-map_metadata", "-1", "-codec:a", "libmp3lame", "-b:a", bitrate, str(out)]
    return args


def measure_loudness(src: Path) -> tuple[float, float, float]:
    """以 loudnorm 量測：回傳 (integrated LUFS, true peak dBTP, duration s)。"""
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", str(src), "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True)
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr, re.S)
    if not m:
        raise BuildError(f"loudness measurement failed for {src.name}: {r.stderr[-400:]}")
    j = json.loads(m.group(0))
    d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(src)],
                       capture_output=True, text=True)
    return float(j["input_i"]), float(j["input_tp"]), float(d.stdout.strip() or 0)


def transcode_audio(src: Path, out: Path, cfg: dict) -> dict:
    """整首或片段轉成 mp3；線性增益把整體響度拉到 target_lufs，真峰值不超過 -1 dBTP。回傳 lock 用的描述。"""
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise BuildError("ffmpeg/ffprobe not found; needed for listen tracks")
    target = cfg.get("target_lufs")
    gain = None
    lufs, tp, dur = measure_loudness(src)
    if target is not None:
        gain = min(float(target) - lufs, -1.0 - tp)
    excerpt = cfg.get("excerpt") or None
    subprocess.run(ffmpeg_args(src, out, cfg.get("bitrate", "160k"), gain, excerpt), check=True)
    return {"seconds": round(float(excerpt["seconds"]) if excerpt else dur, 1), "gain_db": round(gain, 2) if gain is not None else None,
            "params": {"bitrate": cfg.get("bitrate", "160k"), "target_lufs": target, "excerpt": excerpt}}


def listen_jobs(listen: dict, manifest: dict) -> list[tuple[Path, str, str]]:
    """manifest.listen.tracks → [(src, out_rel, "audio")]，輸出檔名只帶傳統代碼與編號。"""
    src_dir = resolve_src(manifest, listen["src_dir"])
    jobs = []
    for t, files in (listen.get("tracks") or {}).items():
        for i, f in enumerate(files, 1):
            jobs.append((src_dir / f, f'{listen["out_dir"]}/{t}_{i}.mp3', "audio"))
    return jobs


def listen_block(listen: dict, site: dict) -> str:
    """Paper 頁的試聽區塊：每個傳統一欄，曲目只給編號。"""
    esc = htmlmod.escape
    traditions: dict = site.get("traditions", {})
    out = [f'<section class="listen" id="listen">']
    if listen.get("intro"):
        out.append(f'<p>{esc(listen["intro"])}</p>')
    out.append('<div class="listen-grid">')
    for t, label in traditions.items():
        files = (listen.get("tracks") or {}).get(t) or []
        if not files:
            continue
        out.append(f'<div class="listen-group t-{esc(t)}"><h3>{esc(label)}</h3>')
        for i in range(1, len(files) + 1):
            out.append(f'<div class="track"><span class="n">{i}</span>'
                       f'<audio controls preload="none" src="{esc(listen["out_dir"])}/{esc(t)}_{i}.mp3"></audio></div>')
        out.append("</div>")
    out.append("</div>")
    if listen.get("notice"):
        out.append(f'<p class="notice">{esc(listen["notice"])}</p>')
    out.append("</section>")
    return "\n".join(out)


def resolve_src(manifest: dict, rel: str) -> Path:
    root = Path(manifest.get("sources_root", "~")).expanduser()
    return (root / rel).resolve()


def sync_assets(manifest: dict, people: list[dict], out_root: Path, lock: dict) -> dict:
    """依 manifest 複製／轉檔資產到 out_root/assets；來源 sha256 與 lock 相同且輸出存在就跳過。"""
    new_lock: dict = {}
    jobs: list[tuple[Path, str, str]] = []  # (src, out_rel, mode)
    for a in manifest.get("assets", []):
        jobs.append((resolve_src(manifest, a["src"]), a["out"], a.get("mode", "copy")))
    pt = manifest.get("portraits")
    if pt:
        src_dir = resolve_src(manifest, pt["src_dir"])
        for p in people:
            if p.get("publish", True) and p.get("portrait"):
                jobs.append((src_dir / p["portrait"], f'{pt["out_dir"]}/{p["slug"]}.jpg', "portrait"))
    listen = manifest.get("listen") or {}
    if listen:
        jobs += listen_jobs(listen, manifest)
    audio_params = {"bitrate": listen.get("bitrate", "160k"), "target_lufs": listen.get("target_lufs"), "excerpt": listen.get("excerpt") or None}
    for src, out_rel, mode in jobs:
        if not src.exists():
            raise BuildError(f"asset source missing: {src}")
        out = out_root / out_rel
        digest = sha256(src)
        prev = lock.get(out_rel)
        same_params = mode != "audio" or (prev or {}).get("params") == audio_params
        if prev and prev.get("sha256") == digest and out.exists() and same_params and (mode != "subtitles" or out.with_suffix(".vtt").exists()):
            new_lock[out_rel] = prev
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        entry = {"src": str(src), "sha256": digest, "mode": mode, "built": dt.datetime.now().isoformat(timespec="minutes")}
        if mode == "copy":
            shutil.copy2(src, out)
        elif mode == "subtitles":
            shutil.copy2(src, out)
            out.with_suffix(".vtt").write_text(srt_to_vtt(src.read_text(encoding="utf-8")), encoding="utf-8")
        elif mode in MAX_WIDTH:
            entry["size"] = list(process_image(src, out, mode))
        elif mode == "audio":
            entry.update(transcode_audio(src, out, listen))
        else:
            raise BuildError(f"unknown asset mode {mode} for {out_rel}")
        entry["bytes"] = out.stat().st_size
        new_lock[out_rel] = entry
        print(f"  asset {mode:9s} {out_rel}")
    return new_lock


# ---------------------------------------------------------------- 建置
PEOPLE_MARK = "<!-- people -->"
LISTEN_MARK = "<!-- listen -->"
VERSIONS_MARK = "<!-- versions -->"


def render_page(name: str, site: dict, numbers: dict, refs: dict, people: list[dict], build_time: str,
                listen: dict | None = None) -> str:
    text = (CONTENT / f"{name}.md").read_text(encoding="utf-8")
    meta, body = split_front_matter(text)
    if PEOPLE_MARK in body:
        body = body.replace(PEOPLE_MARK, "\n" + people_cards(people, site) + "\n")
    if LISTEN_MARK in body:
        if not listen:
            raise BuildError(f"{name}.md has {LISTEN_MARK} but manifest has no listen section")
        body = body.replace(LISTEN_MARK, "\n" + listen_block(listen, site) + "\n")
    if VERSIONS_MARK in body:
        body = body.replace(VERSIONS_MARK, "\n" + versions_block(site) + "\n")
    body = substitute_numbers(body, numbers)   # 人物卡的 bio／role_in_study 也可用 {鍵}
    body, used = render_citations(body, refs)
    html = md_to_html(body) + references_html(used, refs)
    return page(meta, html, site, active=name, build_time=build_time)


def build(out_root: Path | None = None, assets: bool = True) -> Path:
    out_root = (out_root or ROOT).resolve()
    site = load_yaml(TOOLS / "site.yaml")
    manifest = load_yaml(TOOLS / "manifest.yaml")
    numbers = load_numbers(resolve_src(manifest, manifest["numbers"]))
    refs = load_yaml(CONTENT / "references.yaml")
    people = load_yaml(CONTENT / "people.yaml") if (CONTENT / "people.yaml").exists() else []
    lock_path = out_root / "manifest.lock.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8")) if lock_path.exists() else {}
    build_time = dt.datetime.now().isoformat(timespec="minutes")

    (out_root / "assets" / "css").mkdir(parents=True, exist_ok=True)
    shutil.copy2(TOOLS / "style.css", out_root / "assets" / "css" / "site.css")
    if (TOOLS / "favicon.svg").exists():
        (out_root / "assets" / "img").mkdir(parents=True, exist_ok=True)
        shutil.copy2(TOOLS / "favicon.svg", out_root / "assets" / "img" / "favicon.svg")
    (out_root / ".nojekyll").touch()

    if assets:
        lock = sync_assets(manifest, people, out_root, lock)
        lock_path.write_text(json.dumps(lock, ensure_ascii=False, indent=1), encoding="utf-8")

    for item in site["nav"]:
        name = item["file"]
        html = render_page(name, site, numbers, refs, people, build_time, listen=manifest.get("listen"))
        (out_root / f"{name}.html").write_text(html, encoding="utf-8")
        print(f"  page  {name}.html ({len(html):,} bytes)")
    return out_root


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, default=None, help="輸出目錄（預設站根）")
    ap.add_argument("--no-assets", action="store_true", help="不同步資產，只產 HTML")
    args = ap.parse_args(argv)
    try:
        out = build(args.out, assets=not args.no_assets)
    except BuildError as e:
        print(f"BUILD ERROR: {e}", file=sys.stderr)
        return 1
    print(f"built → {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
