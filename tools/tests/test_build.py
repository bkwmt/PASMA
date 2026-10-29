"""build.py 純函式的單元測試。執行：.venv/bin/python -m unittest discover -s tools/tests -v"""
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import build  # noqa: E402

REFS = {
    "a2020": {"author": "Author A", "year": 2020, "title": "Title A", "container": "Journal A"},
    "b2021": {"author": "Author B", "year": 2021, "title": "Title B", "container": "Press B", "url": "https://example.org/b"},
}
NUMBERS = {"唱片數": "1,122", "年份起": "1957", "clustering_1960": "0.75"}


class FrontMatter(unittest.TestCase):
    def test_split(self):
        meta, body = build.split_front_matter("---\ntitle: X\nnav: Home\n---\n\n# Hi\n")
        self.assertEqual(meta["title"], "X")
        self.assertEqual(body.strip(), "# Hi")

    def test_missing_front_matter_raises(self):
        with self.assertRaises(build.BuildError):
            build.split_front_matter("# no front matter\n")


class Numbers(unittest.TestCase):
    def test_substitute(self):
        out = build.substitute_numbers("{唱片數} records from {年份起}", NUMBERS)
        self.assertEqual(out, "1,122 records from 1957")

    def test_unknown_key_raises(self):
        with self.assertRaises(build.BuildError):
            build.substitute_numbers("{不存在的鍵}", NUMBERS)

    def test_skips_code(self):
        md = "Count {唱片數}.\n\n```bibtex\n@inproceedings{cheng2026,\n title={X}}\n```\n\nand `{inline}` stays {clustering_1960}."
        out = build.substitute_numbers(md, NUMBERS)
        self.assertIn("Count 1,122.", out)
        self.assertIn("@inproceedings{cheng2026,", out)
        self.assertIn("`{inline}`", out)
        self.assertIn("stays 0.75.", out)

    def test_plain_braces_in_prose_untouched(self):
        # 英文散文裡不含中文或底線的大括號（例如數學）不算佔位符
        out = build.substitute_numbers("set {x, y}", NUMBERS)
        self.assertEqual(out, "set {x, y}")


class Citations(unittest.TestCase):
    def test_single_and_multiple(self):
        md, used = build.render_citations("One [@a2020]. Two [@b2021; @a2020].", REFS)
        self.assertEqual(used, ["a2020", "b2021"])
        self.assertIn('href="#ref-a2020"', md)
        self.assertEqual(md.count("#ref-a2020"), 2)
        self.assertIn(">1<", md)
        self.assertIn(">2<", md)

    def test_unknown_raises(self):
        with self.assertRaises(build.BuildError):
            build.render_citations("x [@nope]", REFS)

    def test_locator(self):
        md, used = build.render_citations("x [@a2020, pp. 71–72; @b2021]", REFS)
        self.assertEqual(used, ["a2020", "b2021"])
        self.assertIn('(pp. 71–72)', md)
        self.assertIn('href="#ref-b2021"', md)

    def test_references_html_only_used(self):
        html = build.references_html(["b2021"], REFS)
        self.assertIn('id="ref-b2021"', html)
        self.assertNotIn("ref-a2020", html)
        self.assertIn("Author B (2021)", html)
        self.assertIn('href="https://example.org/b"', html)

    def test_no_used_gives_empty(self):
        self.assertEqual(build.references_html([], REFS), "")


class Markdown(unittest.TestCase):
    def test_links_md_to_html_and_external_rel(self):
        html = build.md_to_html("[a](history.md) [b](https://x.org/)")
        self.assertIn('href="history.html"', html)
        self.assertIn('rel="noopener"', html)

    def test_image_becomes_figure(self):
        html = build.md_to_html("![The caption](assets/img/x.jpg)")
        self.assertIn("<figure>", html)
        self.assertIn("<figcaption>The caption</figcaption>", html)
        self.assertIn('loading="lazy"', html)

    def test_table_wrapped(self):
        html = build.md_to_html("| a | b |\n|---|---|\n| 1 | 2 |")
        self.assertIn('<div class="tablewrap"><table>', html)


class Page(unittest.TestCase):
    SITE = {
        "title": "PASMA", "tagline": "t", "base_url": "https://bkwmt.github.io/PASMA/",
        "nav": [{"file": "index", "label": "Home"}, {"file": "history", "label": "History"}],
        "footer": "foot", "emails": ["a@b.c"],
    }

    def test_shell(self):
        html = build.page({"title": "History", "description": "d"}, "<p>x</p>", self.SITE, active="history")
        self.assertIn('<html lang="en">', html)
        self.assertIn("<title>History · PASMA</title>", html)
        self.assertIn('name="viewport"', html)
        self.assertIn('href="assets/css/site.css"', html)
        self.assertIn('aria-current="page"', html)
        self.assertNotIn('href="/', html)


class People(unittest.TestCase):
    SITE = {"traditions": {"pre": "Pre-multitrack", "chen": "Chen Chih-Yuan"}, "portrait_notice": "Portraits: TMC"}

    def test_card_with_and_without_portrait(self):
        people = [
            {"slug": "x", "name_zh": "某", "name_en": "X Y", "dates": "1950–2011", "roles_en": ["arranger"],
             "tradition": "chen", "portrait": "x.jpg", "pmdb_url": "https://pmdb.taipei/p", "bio_en": "Bio.", "publish": True},
            {"slug": "y", "name_zh": "乙", "name_en": "Y Z", "dates": "", "roles_en": ["arranger", "Electone player"],
             "tradition": "pre", "portrait": "", "pmdb_url": "", "bio_en": "Bio2.", "publish": True},
            {"slug": "z", "name_zh": "丙", "name_en": "Z", "dates": "", "roles_en": [], "tradition": "pre",
             "portrait": "", "pmdb_url": "", "bio_en": "UNPUBLISHED-BIO", "publish": False},
        ]
        html = build.people_cards(people, self.SITE)
        self.assertIn('src="assets/img/people/x.jpg"', html)
        self.assertIn("Profile at Taiwan Popular Music Database", html)
        self.assertIn('class="avatar placeholder', html)   # 無頭像者用色標圓點
        self.assertNotIn("UNPUBLISHED-BIO", html)
        self.assertLess(html.index("Pre-multitrack"), html.index("Chen Chih-Yuan"))  # 依 traditions 順序分組

    def test_alias_rendered(self):
        people = [{"slug": "x", "name_zh": "某", "name_en": "X Y", "dates": "", "roles_en": [], "tradition": "chen",
                   "portrait": "", "pmdb_url": "", "bio_en": "b", "alias_en": "Rich X", "publish": True}]
        html = build.people_cards(people, self.SITE)
        self.assertIn('<span class="alias">(Rich X)</span>', html)


class Assets(unittest.TestCase):
    def test_photo_rgba_white_and_downscale(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "a.png"
            Image.new("RGBA", (3200, 1600), (0, 0, 0, 0)).save(src)
            out = Path(d) / "a.jpg"
            w, h = build.process_image(src, out, mode="photo", max_width=1600)
            self.assertEqual((w, h), (1600, 800))
            im = Image.open(out)
            self.assertEqual(im.mode, "RGB")
            self.assertEqual(im.getpixel((10, 10)), (255, 255, 255))

    def test_diagram_keeps_png_and_small_not_upscaled(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "s.png"
            Image.new("RGBA", (400, 300), (10, 20, 30, 255)).save(src)
            out = Path(d) / "s_out.png"
            w, h = build.process_image(src, out, mode="diagram", max_width=1600)
            self.assertEqual((w, h), (400, 300))
            self.assertEqual(Image.open(out).format, "PNG")

    def test_srt_to_vtt(self):
        srt = "1\n00:00:00,800 --> 00:00:03,200\nHello\n\n2\n00:00:03,500 --> 00:00:05,000\nWorld\n"
        vtt = build.srt_to_vtt(srt)
        self.assertTrue(vtt.startswith("WEBVTT\n\n"))
        self.assertIn("00:00:00.800 --> 00:00:03.200", vtt)
        self.assertNotIn(",", vtt.split("\n")[2])


if __name__ == "__main__":
    unittest.main()

class Listen(unittest.TestCase):
    SITE = {"traditions": {"pre": "Pre-multitrack tradition", "chen": "Chen Chih-Yuan tradition", "post": "Post-Chen era"}}
    CFG = {"out_dir": "assets/audio", "intro": "Intro.", "notice": "Rights <notice>.",
           "tracks": {"pre": ["a.mp3", "b.mp3"], "chen": ["c.mp3"]}}

    def test_block_numbers_only_and_order(self):
        html = build.listen_block(self.CFG, self.SITE)
        self.assertIn('id="listen"', html)
        self.assertIn('src="assets/audio/pre_1.mp3"', html)
        self.assertIn('src="assets/audio/pre_2.mp3"', html)
        self.assertIn('src="assets/audio/chen_1.mp3"', html)
        self.assertNotIn("a.mp3", html)                       # 來源檔名不外露
        self.assertNotIn("Post-Chen", html)                   # 沒有曲目的傳統不出現
        self.assertIn('preload="none"', html)
        self.assertIn("Rights &lt;notice&gt;.", html)
        self.assertLess(html.index("Pre-multitrack"), html.index("Chen Chih-Yuan"))

    def test_ffmpeg_args_full_and_excerpt(self):
        full = build.ffmpeg_args(Path("/s.mp3"), Path("/o.mp3"), "160k", -3.2, None)
        self.assertNotIn("-ss", full)
        self.assertIn("volume=-3.20dB", " ".join(full))
        self.assertIn("-map_metadata", full)
        cut = build.ffmpeg_args(Path("/s.mp3"), Path("/o.mp3"), "128k", None, {"start": 12, "seconds": 30})
        self.assertEqual(cut[cut.index("-ss") + 1], "12")
        self.assertEqual(cut[cut.index("-t") + 1], "30.0")
        self.assertIn("afade=t=out:st=29.00:d=1", " ".join(cut))
        self.assertNotIn("volume", " ".join(cut))

    def test_jobs_named_by_tradition_and_index(self):
        jobs = build.listen_jobs({"src_dir": "x", "out_dir": "assets/audio", "tracks": {"pre": ["p/a.mp3", "p/b.mp3"]}},
                                 {"sources_root": "/tmp"})
        self.assertEqual([j[1] for j in jobs], ["assets/audio/pre_1.mp3", "assets/audio/pre_2.mp3"])
        self.assertTrue(all(j[2] == "audio" for j in jobs))
