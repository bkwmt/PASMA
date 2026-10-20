"""check.py 的單元測試：用暫存站根驗證守門規則。"""
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import check  # noqa: E402

SITE = {"large_files": ["assets/pdf/big.pdf"], "allowed_external": []}
GOOD = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>T</title><meta name="description" content="d"><link rel="stylesheet" href="assets/css/site.css"></head>
<body><a href="history.html">h</a><a href="https://pmdb.taipei/x">p</a><img src="assets/img/a.jpg"></body></html>"""


def make_site(d: Path, html: str = GOOD):
    (d / ".nojekyll").touch()
    (d / "assets" / "css").mkdir(parents=True)
    (d / "assets" / "css" / "site.css").write_text("")
    (d / "assets" / "img").mkdir()
    (d / "assets" / "img" / "a.jpg").write_bytes(b"x")
    (d / "index.html").write_text(html)
    (d / "history.html").write_text(html)


class CheckSite(unittest.TestCase):
    def test_clean_site_passes(self):
        with tempfile.TemporaryDirectory() as t:
            d = Path(t); make_site(d)
            problems, external = check.check_site(d, SITE)
            self.assertEqual(problems, [])
            self.assertEqual(external, ["https://pmdb.taipei/x"])

    def test_anchor_checked(self):
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            make_site(d, GOOD.replace('href="history.html"', 'href="history.html#sec-2"'))
            problems, _ = check.check_site(d, SITE)
            self.assertTrue(any("missing anchor history.html#sec-2" in p for p in problems))
            (d / "history.html").write_text(GOOD + '<h2 id="sec-2">x</h2>')
            problems, _ = check.check_site(d, SITE)
            self.assertFalse(any("missing anchor" in p for p in problems))

    def test_missing_target_and_root_relative(self):
        with tempfile.TemporaryDirectory() as t:
            d = Path(t); make_site(d, GOOD.replace('href="history.html"', 'href="nope.html"').replace('src="assets/img/a.jpg"', 'src="/assets/img/a.jpg"'))
            problems, _ = check.check_site(d, SITE)
            self.assertTrue(any("missing target nope.html" in p for p in problems))
            self.assertTrue(any("root-relative" in p for p in problems))

    def test_external_resource_and_placeholder(self):
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            make_site(d, GOOD.replace('<img src="assets/img/a.jpg">', '<script src="https://cdn.x/y.js"></script><p>{唱片數}</p>'))
            problems, _ = check.check_site(d, SITE)
            self.assertTrue(any("external script resource" in p for p in problems))
            self.assertTrue(any("unresolved placeholder {唱片數}" in p for p in problems))

    def test_data_guard(self):
        with tempfile.TemporaryDirectory() as t:
            d = Path(t); make_site(d)
            (d / "data").mkdir()
            (d / "data" / "albums.json").write_text("{}")
            (d / "assets" / "network_full_deid.csv").write_text("x")
            problems, _ = check.check_site(d, SITE)
            self.assertTrue(any("data directory present" in p for p in problems))
            self.assertTrue(any("json file present" in p for p in problems))
            self.assertTrue(any("looks like dataset material" in p for p in problems))

    def test_large_file_whitelist(self):
        with tempfile.TemporaryDirectory() as t:
            d = Path(t); make_site(d)
            (d / "assets" / "pdf").mkdir()
            big = b"0" * (check.LIMIT + 1)
            (d / "assets" / "pdf" / "big.pdf").write_bytes(big)
            (d / "assets" / "pdf" / "other.pdf").write_bytes(big)
            problems, _ = check.check_site(d, SITE)
            self.assertTrue(any("other.pdf" in p for p in problems))
            self.assertFalse(any("big.pdf" in p for p in problems))


if __name__ == "__main__":
    unittest.main()
