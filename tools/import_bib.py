#!/usr/bin/env python3
"""從 BibTeX 檔抽出指定鍵，印成 references.yaml 用的 YAML（author / year / title / container / url）。

用法：.venv/bin/python tools/import_bib.py path/to/file.bib KEY [KEY …]
      .venv/bin/python tools/import_bib.py path/to/file.bib --all-cited work/history_s*.md
只做粗略的 BibTeX 解析（大括號平衡），足夠應付 phd/mybib.bib 與 ISMIR 的 bib。
"""
from __future__ import annotations

import glob
import re
import sys
from pathlib import Path

import yaml


def parse_bib(text: str) -> dict[str, dict]:
    entries: dict[str, dict] = {}
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", text):
        kind, key = m.group(1).lower(), m.group(2)
        if kind in ("comment", "string", "preamble"):
            continue
        # 找到這筆的結尾：從 { 開始算括號平衡
        i = m.start() + text[m.start():].index("{")
        depth, j = 0, i
        while j < len(text):
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        body = text[m.end():j]
        fields: dict[str, str] = {"_type": kind}
        for fm in re.finditer(r"(\w+)\s*=\s*(\{(?:[^{}]|\{[^{}]*\})*\}|\"[^\"]*\"|[^,\n]+)", body):
            val = fm.group(2).strip().strip(",").strip()
            if val[:1] in "{\"":
                val = val[1:-1]
            fields[fm.group(1).lower()] = re.sub(r"\s+", " ", val.replace("{", "").replace("}", "")).strip()
        entries[key] = fields
    return entries


def to_ref(e: dict) -> dict:
    kind = e.get("_type", "")
    author = e.get("author") or e.get("editor") or ""
    author = " and ".join(a.strip() for a in author.split(" and ")) if author else ""
    author = re.sub(r"\\['`\"^~=.]", "", author)
    year = e.get("year") or e.get("date", "")[:4] or "n.d."
    title = e.get("title", "")
    if kind in ("article",):
        cont = e.get("journal") or e.get("journaltitle", "")
        vol = e.get("volume", "")
        num = e.get("number", "")
        pages = e.get("pages", "")
        cont = cont + (f" {vol}" if vol else "") + (f"({num})" if num else "") + (f": {pages}" if pages else "")
    elif kind in ("inproceedings", "incollection", "inbook"):
        cont = "In " + (e.get("booktitle", ""))
        if e.get("pages"):
            cont += f", {e['pages']}"
        if e.get("publisher"):
            cont += f". {e.get('address', '').strip()}{': ' if e.get('address') else ''}{e['publisher']}"
    elif kind in ("phdthesis", "mastersthesis", "thesis"):
        deg = {"phdthesis": "PhD dissertation", "mastersthesis": "Master's thesis"}.get(kind, e.get("type", "Thesis"))
        cont = f"{deg}, {e.get('school') or e.get('institution', '')}"
    elif kind == "book":
        cont = f"{e.get('address', '')}{': ' if e.get('address') else ''}{e.get('publisher', '')}"
    else:
        cont = e.get("howpublished") or e.get("publisher") or e.get("journal") or e.get("note", "")
    ref = {"author": author, "year": year, "title": title, "container": cont.strip(" .,")}
    url = e.get("url") or (f"https://doi.org/{e['doi']}" if e.get("doi") else "")
    if url:
        ref["url"] = url
    return ref


def cited_keys(paths: list[str]) -> list[str]:
    keys: set[str] = set()
    for p in paths:
        t = Path(p).read_text(encoding="utf-8").split("### Proposed references")[0]
        for m in re.finditer(r"\[(@[^\]]+)\]", t):
            for part in m.group(1).split(";"):
                keys.add(part.strip().partition(",")[0].strip().lstrip("@"))
    return sorted(keys)


def main(argv: list[str]) -> int:
    bib = Path(argv[0]).expanduser()
    entries = parse_bib(bib.read_text(encoding="utf-8"))
    if argv[1] == "--all-cited":
        keys = cited_keys([f for pat in argv[2:] for f in glob.glob(pat)])
    else:
        keys = argv[1:]
    out: dict[str, dict] = {}
    missing = []
    for k in keys:
        if k in entries:
            out[k] = to_ref(entries[k])
        else:
            missing.append(k)
    print(yaml.safe_dump(out, allow_unicode=True, sort_keys=False, width=120))
    if missing:
        print("# MISSING in bib: " + ", ".join(missing), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
