# STRATEGY.md — news-image-20261119 v2

## Bounty
make.fun `news-image-20261119` — "Sum up 19 November's world news in one
image". $250 prize pool, 50 paid places, 1st $50. Entries close 21 Nov 2026
07:00 WIB (21 Nov 00:00 UTC). Account @joni-gunawan, GitHub Ci3hu1.

## Why v2 exists
v1 (36 stories, live dev rank 1,045/4,815, score 976.591) was a solid
front page but short of the winning recipe. v2 is a measured upgrade on
every axis the top-50 study found decisive, not a re-render of v1.

## The winning recipe (from the news-image-20261117 top-50 study)
The study of the 50 winning entries of the 17 Nov bounty found one
repeatable pattern:
- 45–50 verified same-day stories (top-10 floor: 43 stories)
- 6–7 regions covered
- Newspaper front page: masthead + UTC timeline strip
- 3 illustrated heroes + ~10 smaller illustrated stories
- Numbers strip + region-count strip
- Pinned world map (numbered pins for featured stories, dots for the rest)
- Numbered "also on" list covering every story exactly once
- DATE CHECK box (what was left out, what has not happened yet)
- Sources line, 7–9 outlets
- Flat illustration only — photo-style images ranked 44th

## What v2 does
| Element | v1 | v2 |
|---|---|---|
| Stories | 36 | 50 (exactly 1–50, numbered once each) |
| Regions | 6 | 7 (ASIA 8, MIDDLE EAST 7, EUROPE 9, AMERICAS 11, AFRICA 5, OCEANIA 2, GLOBAL 8) |
| Heroes | 3 | 3, each with a flat vector scene (flags, bridge, gulf) |
| Smaller stories | 10 | 10, each with a flat mini illustration |
| UTC timeline | yes | yes, 6 slots (00:50 Kerch, 02:00 APEC, 09:00 ICJ, 14:30 Nasdaq, Day Berlin, Evening summit) |
| Numbers strip | yes | 6 figures ($81.3bn IPO, Hang Seng −2.78%, 46,000 Gaza households, 45bn euro loan, $2.3bn IMF Egypt, 1 in 4 children) |
| Region strip | yes | yes, with TOTAL 50 |
| World map | yes | yes, dotted land, pins 1–13 + dots 14–50, region legend + pin key |
| DATE CHECK | yes | yes, LEFT OUT (3 items from 17–18 Nov) + NOT YET HAPPENED (3 items) |
| Claim handling | — | CLAIM tags kept separate from CONFIRMED: CLAIM KYIV (bridge attribution), CLAIM monitors (Ethiopia/Eritrea), CLAIM TRUMP (Iran WMD claim) |
| Sources line | yes | Reuters, AP, AFP, BBC, Al Jazeera, WHO, UN, PAHO, NASA + "Original drawings" |

## Measured edge vs v1
- +14 stories (36 → 50), reaching the top-10 floor of the winning recipe.
- +1 region (Oceania: Fiji/Tonga drought) → all 7 regions.
- Map now carries every story: 13 numbered pins + 37 dots (was pins only).
- DATE CHECK is explicit about the two most likely date traps (Alaska
  Senate race called 17 Nov; measles status lost 17 Nov) and the three
  not-yet-happened items (Estonia closure 1 Dec, Anthropic close 20 Nov,
  trilateral joint statement).
- Rendering is pure stdlib (no Pillow on the grader): embedded 5×7 bitmap
  font + zlib PNG encoder, byte-identical across runs (SHA-256 verified by
  main.py).

## What v2 deliberately does not do
- No story from any day other than 19 Nov 2026.
- No photo-style imagery anywhere; every picture is a drawn flat scene.
- No invented figures: every number strip figure comes from a listed story.
