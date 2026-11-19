#!/usr/bin/env python3
"""Tests for news-image-20261119-v2.  Pure stdlib, no network.

Run: python3 -m unittest discover -s tests
"""
import hashlib
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

import render  # noqa: E402
import main as entry  # noqa: E402


def _read(path):
    with open(path, "rb") as f:
        return f.read()


class TestBundledImage(unittest.TestCase):
    def test_png_exists_and_is_1024(self):
        path = os.path.join(ROOT, "news.png")
        self.assertTrue(os.path.exists(path), "news.png missing")
        data = _read(path)
        self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
        self.assertEqual(int.from_bytes(data[16:20], "big"), 1024)
        self.assertEqual(int.from_bytes(data[20:24], "big"), 1024)

    def test_sha_and_size_match_main(self):
        data = _read(os.path.join(ROOT, "news.png"))
        self.assertEqual(len(data), entry.IMAGE_SIZE)
        self.assertEqual(hashlib.sha256(data).hexdigest(),
                         entry.EXPECTED_SHA256)

    def test_check_mode(self):
        r = subprocess.run([sys.executable, "main.py", "--check"],
                           cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("check ok", r.stdout)

    def test_render_is_deterministic(self):
        before = hashlib.sha256(_read(os.path.join(ROOT, "news.png"))).hexdigest()
        r = subprocess.run([sys.executable, "render.py"],
                           cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        after = hashlib.sha256(_read(os.path.join(ROOT, "news.png"))).hexdigest()
        self.assertEqual(before, after, "render.py is not deterministic")


class TestMainOutput(unittest.TestCase):
    def test_writes_identical_bytes_twice(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ, MAKEFUN_OUTPUT_DIR=tmp)
            outs = []
            for _ in range(2):
                r = subprocess.run([sys.executable, "main.py"],
                                   cwd=ROOT, capture_output=True, text=True,
                                   env=env)
                self.assertEqual(r.returncode, 0, r.stderr)
                outs.append(_read(os.path.join(tmp, "entry.png")))
            src = _read(os.path.join(ROOT, "news.png"))
            self.assertEqual(outs[0], src)
            self.assertEqual(outs[0], outs[1], "two runs differ")

    def test_output_path_order(self):
        # $MAKEFUN_OUTPUT_DIR wins when set.
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ, MAKEFUN_OUTPUT_DIR=tmp)
            r = subprocess.run(
                [sys.executable, "-c",
                 "import main; print(main.output_path())"],
                cwd=ROOT, capture_output=True, text=True, env=env)
            self.assertEqual(r.stdout.strip(),
                             os.path.join(tmp, "entry.png"))
        # Without the env var it falls back to /output or local output.png.
        env = {k: v for k, v in os.environ.items()
               if k != "MAKEFUN_OUTPUT_DIR"}
        r = subprocess.run(
            [sys.executable, "-c", "import main; print(main.output_path())"],
            cwd=ROOT, capture_output=True, text=True, env=env)
        self.assertIn(r.stdout.strip(),
                      ("/output/entry.png",
                       os.path.join(ROOT, "output.png")))


class TestPosterContent(unittest.TestCase):
    def test_exactly_50_stories(self):
        nums = [s["n"] for s in render.HEROES]
        nums += [s["n"] for s in render.SMALLS]
        nums += [n for n, _ in render.ALSO]
        self.assertEqual(sorted(nums), list(range(1, 51)))

    def test_region_counts_add_to_50(self):
        self.assertEqual(sum(render.REGION_COUNTS.values()), 50)
        self.assertEqual(set(render.REGION_COUNTS),
                         set(render.REGION_ORDER))

    def test_map_pins_and_dots_cover_1_to_50(self):
        nums = [n for n, _, _ in render.MAP_PINS]
        nums += [n for n, _, _ in render.MAP_DOTS]
        self.assertEqual(sorted(nums), list(range(1, 51)))

    def test_all_text_has_glyphs(self):
        missing = set()
        for s in render.all_poster_text():
            for ch in s:
                if ch not in render.FONT:
                    missing.add(ch)
        self.assertEqual(missing, set(), "glyphs missing: %r" % missing)

    def test_also_lines_fit_one_line(self):
        col_w = (render.X1 - render.X0 - 24) // 2
        for n, txt in render.ALSO:
            line = "%d. %s" % (n, txt)
            self.assertLessEqual(render.text_w(line, 1), col_w, line)

    def test_timeline_has_six_slots(self):
        self.assertEqual(len(render.TIMELINE), 6)

    def test_numbers_strip_has_six_figures(self):
        self.assertEqual(len(render.NUMBERS), 6)

    def test_poster_fits_canvas(self):
        _, bottom = render.build_poster()
        self.assertLessEqual(bottom, 1024)

    def test_wrap_never_overflows(self):
        for st in render.HEROES:
            self.assertLessEqual(
                max(len(ln) for ln in render.wrap(st["headline"], 317, 2)),
                27)
            self.assertLessEqual(
                len(render.wrap(st["body"], 317, 1)), 4)


if __name__ == "__main__":
    unittest.main()
