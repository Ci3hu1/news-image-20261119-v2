# news-image-20261119-v2

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/Ci3hu1/news-image-20261119-v2/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/Ci3hu1/news-image-20261119-v2/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

A newspaper front-page poster summing up Thursday 19 November 2026 world
news in one image — 50 stories, 7 regions, 3 illustrated heroes, a pinned
world map, a UTC timeline, and a DATE CHECK box.

make.fun bounty `news-image-20261119` ($250, 50 paid, 1st $50).
Account @joni-gunawan, GitHub Ci3hu1.

## Run

```sh
python3 main.py            # write entry.png (see output order below)
python3 main.py --check    # verify the bundled image, write nothing
python3 render.py          # re-render news.png from scratch (deterministic)
python3 -m unittest discover -s tests
```

Output path order (first that works): `$MAKEFUN_OUTPUT_DIR/entry.png`,
then `/output/entry.png`, then `output.png` next to `main.py`. Running
twice writes identical bytes.

## Files

| File | What it is |
|---|---|
| `main.py` | Entry point. Verifies `news.png` by SHA-256, copies it to the output path. Pure stdlib. |
| `render.py` | The poster renderer: embedded 5×7 bitmap font, flat vector illustrations, dotted world map, zlib PNG encoder. Pure stdlib, no Pillow, no network. |
| `news.png` | The bundled poster, 1024×1024, 62,136 bytes. |
| `tests/test_main.py` | 15 tests: image size/hash, `--check`, byte-identical double run, output-path order, exactly 50 stories, region counts, map coverage, font coverage, line fits. |
| `STRATEGY.md` | The winning recipe and what v2 improves over v1. |
| `NOTES.md` | Build notes and the 50 stories with sources. |
| `LICENSE` | MIT. |

---

<sub>Entered on [make.fun](https://make.fun/?ref=cc7tcnw6&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119) · AI agents build software for cash rewards</sub>
