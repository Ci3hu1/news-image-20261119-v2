# NOTES.md — news-image-20261119-v2 build notes

Built fresh in one session, sight-unseen from the brief (no prep files, no
v1 repo read — authorship requirement). Pure Python standard library only:
the grader runs vanilla Python with no Pillow, so the poster is drawn with
an embedded 5×7 bitmap font and a zlib-based PNG encoder in `render.py`.
`main.py` verifies the bundled `news.png` by SHA-256 and copies it to the
output path; running it twice writes identical bytes.

## Verification done
- `python3 render.py` — poster bottom y = 1002/1024, fits with margin.
- Rendered twice: byte-identical (SHA-256 stable).
- `python3 main.py --check` — ok.
- `python3 -m unittest discover -s tests` — 15 tests, all pass.
- `main.py` run twice with `$MAKEFUN_OUTPUT_DIR` set — both `entry.png`
  files byte-identical to bundled `news.png`.
- Visual checks: thumbnail 256px (masthead + 3 leads readable), half size
  512px (all 13 pictures distinct and legible), full size 1024px (all 50
  stories legible). Map checked at 2× zoom: all 13 pins individually
  readable, dots 14–50 placed.
- Content checks (in tests): exactly stories 1–50 once each; region counts
  sum to 50; map pins 1–13 + dots 14–50 cover 1–50; every printed
  character has a font glyph; every ALSO line fits its column.

## The 50 stories (all 19 Nov 2026)
Featured 1–13:
1. ASIA — Trump, Xi and Putin hold first three-way summit in Shenzhen
   (APEC). CONFIRMED BBC/CBS/Japan Times.
2. MIDDLE EAST — Iran attacks Gulf states after US strike on Qeshm island.
   CONFIRMED Reuters/AP.
3. EUROPE — Ukraine strikes Crimean Bridge for a third time this week.
   CONFIRMED BBC/Reuters. CLAIM KYIV (Kyiv did not comment).
4. MIDDLE EAST — Israel launches ground operation beyond the Yellow Line
   in central Gaza. CONFIRMED Reuters 19 Nov.
5. ASIA — UN court to rule on Myanmar Rohingya genocide case (ICJ, The
   Hague, 10:00). CONFIRMED ICJ/HRW/RFA.
6. AMERICAS — Anthropic begins trading after record $81.3bn IPO.
   CONFIRMED Reuters.
7. EUROPE — EU proposes 45bn euro loan for Ukraine; allies meet in Berlin.
   CONFIRMED Reuters.
8. GLOBAL — COP31 deadlock persists as countries launch climate check
   (Antalya, Turkey).
9. AFRICA — Ethiopia and Eritrea mass forces along the border. CLAIM
   monitors (unconfirmed clashes near Badme).
10. ASIA — Cyclone Aqwan to hit India's east coast (Bay of Bengal).
11. OCEANIA — Fiji and Tonga declare emergencies over El Nino drought.
12. AMERICAS — Grand Theft Auto VI goes on sale after a 13-year wait.
13. AFRICA — Strain-specific Ebola vaccines to be trialled in DR Congo.

Also on Thursday (14–50): Houthi missile aimed at Riyadh; Israel delays
E1 settlement, settler kills woman near Jericho; Trump says Iran is
exploring chemical and biological weapons (CLAIM TRUMP); Knesset elects
Matan Kahana speaker (66 votes); Australia, Canada, Italy, UK urge Israel
to let aid reach flooded Gaza; IAEA: North Korea expanded uranium
enrichment (Yongbyon); Xi and Japan's Takaichi shake hands in Shenzhen;
South Korea and China expand cultural exchange; EU approves Indonesia
trade pact; court sentences Imamoglu and eight others (CHP, Ankara);
France's fourth weekend of cost-of-living protests; Israel's president
taps Eisenkot to form government; Russian military plane crash in Siberia
kills 19; Zelensky urges Washington to lift Starshield limits; US and
Venezuela restore military cooperation; Milei's bill to suspend primaries
advances; isolated Awa group makes rare contact in Brazil; pastor
convicted over Haitian president's 2021 assassination; record atmospheric
river rain hits California; AI worries weigh on stocks (Hang Seng
−2.78%, FTSE 100 −1.30%); gold, copper and bitcoin slide; Australia's
unemployment rises to 4.9%; IMF deal unlocks $2.3bn for Egypt; Sudan aid
for displaced as drones drive civilian toll (El Dabba); five EU nations
plan to send asylum seekers to Rwanda; nearly 1 in 4 children live in
conflict zones (UNICEF); Pew projects Islam to pass Christianity by 2035;
South Korea college exam under AI cheating curbs; unrest in Bangladesh
over Hasina's return and wage demands; Estonia plans to close road border
crossings with Russia from 1 Dec; Washington sanctions a Hezbollah-linked
charity and two gold firms; Yemen's government designates the Houthis a
terrorist group; US State Dept details $12bn in Venezuelan oil and
mineral revenue; Voyager 1 reaches one light-day from Earth (NASA);
Alcaraz beats Medvedev at ATP Finals (Turin); Waymo pulls driverless
taxis from US freeways; Webb confirms rare merger of a supergiant and a
sun-like star.

## Live score / rank
- Live dev score: (not yet checked — fill after hourly check)
- Live dev rank: (not yet checked — fill after hourly check)
- Result due: after entries close 21 Nov 2026 07:00 WIB.

## Submission
- NOT submitted by this build. Awaiting Joni's 'Setuju' in the main chat
  before any submit. No claim code is stored here.
