#!/usr/bin/env python3
"""Render the news-image-20261119-v2 poster (1024x1024 PNG) with pure stdlib.

No Pillow, no network, no third-party packages.  Text is drawn with an
embedded 5x7 bitmap font; the PNG is written with a zlib-based encoder.
Running this file writes news.png next to it.  Output is deterministic:
rendering twice produces byte-identical files.
"""
import os
import struct
import sys
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- font
# 5x7 bitmap font.  Each glyph is 7 strings of 5 chars ('#' on, '.' off).
# '.' rows are blank so the font stays compact.
FONT = {
' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
'G': (".####", "#....", "#....", "#..##", "#...#", "#...#", ".###."),
'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
'I': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
'N': ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
'0': (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
'1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
'2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
'3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
'4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
'5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
'6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
'7': ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
'8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
'9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
'a': (".....", ".....", ".###.", "....#", ".####", "#...#", ".####"),
'b': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
'c': (".....", ".....", ".####", "#....", "#....", "#....", ".####"),
'd': ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
'e': (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
'f': ("..##.", ".#..#", ".#...", "####.", ".#...", ".#...", ".#..."),
'g': (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
'h': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
'i': ("..#..", ".....", ".##..", "..#..", "..#..", "..#..", ".###."),
'j': ("...#.", ".....", "..##.", "...#.", "...#.", "...#.", "...#.", "##..."),
'k': ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
'l': (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
'm': (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
'n': (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
'o': (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
'p': (".....", ".....", "####.", "#...#", "#...#", "####.", "#...."),
'q': (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
'r': (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
's': (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
't': (".#...", ".#...", "####.", ".#...", ".#...", ".#...", "..##."),
'u': (".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"),
'v': (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
'w': (".....", ".....", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
'x': (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
'y': (".....", ".....", "#...#", "#...#", ".####", "....#", ".###."),
'z': (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
'.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
',': (".....", ".....", ".....", ".....", ".##..", ".##..", ".#...", "#...."),
':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#...", "#...."),
'!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
'?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
"'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
'"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
'(': ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
')': (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
'-': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
'_': (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
'=': (".....", ".....", "#####", ".....", "#####", ".....", "....."),
'+': (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
'/': ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
'\\': ("#....", "#....", ".#...", "..#..", "...#.", "....#", "....#"),
'|': ("..#..", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
'*': (".....", "#...#", ".#.#.", "#####", ".#.#.", "#...#", "....."),
'%': ("#...#", "#..#.", "...#.", "..#..", ".#...", "#..#.", "#...#"),
'$': ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
'#': (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
'&': (".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"),
'@': (".###.", "#...#", "#.###", "#.#.#", "#.###", "#....", ".###."),
'<': ("...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."),
'>': (".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."),
'[': (".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".###."),
']': (".###.", "...#.", "...#.", "...#.", "...#.", "...#.", ".###."),
'^': ("..#..", ".#.#.", ".....", ".....", ".....", ".....", "....."),
'`': (".#...", "..#..", "...#.", ".....", ".....", ".....", "....."),
'~': (".....", ".....", ".##.#", "#.#.#", ".....", ".....", "....."),
'°': (".##..", "#..#.", "#..#.", ".##..", ".....", ".....", "....."),
'·': (".....", ".....", ".....", ".##..", ".##..", ".....", "....."),
}
# Aliases for typographic characters (rendered with their ASCII twin).
FONT['–'] = FONT['-']
FONT['—'] = FONT['-']
FONT['’'] = FONT["'"]
FONT['‘'] = FONT["'"]
FONT['“'] = FONT['"']
FONT['”'] = FONT['"']
FONT['•'] = FONT['·']
FONT['…'] = FONT['.']

# Fix the two glyphs above that were accidentally given 8 rows.
FONT['j'] = ("...#.", ".....", "..##.", "...#.", "...#.", "...#.", "##...")
FONT[','] = (".....", ".....", ".....", ".....", ".##..", ".##..", ".#...")
FONT[';'] = (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#...")


def _font_ok():
    for ch, rows in FONT.items():
        assert len(rows) == 7, "glyph %r has %d rows" % (ch, len(rows))
        for r in rows:
            assert len(r) == 5, "glyph %r row %r" % (ch, r)
            assert set(r) <= set(".#"), "glyph %r row %r" % (ch, r)


_font_ok()

CHAR_W = 6  # glyph advance in font units (5 px glyph + 1 px gap)


def text_w(s, scale):
    return len(s) * CHAR_W * scale


# ---------------------------------------------------------------- canvas
class Canvas(object):
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i] = c[0]
            self.buf[i + 1] = c[1]
            self.buf[i + 2] = c[2]

    def fill_rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.buf[i:i + (x1 - x0) * 3] = row

    def rect(self, x, y, w, h, c, t=1):
        self.fill_rect(x, y, w, t, c)
        self.fill_rect(x, y + h - t, w, t, c)
        self.fill_rect(x, y, t, h, c)
        self.fill_rect(x + w - t, y, t, h, c)

    def hline(self, x, y, w, c):
        self.fill_rect(x, y, w, 1, c)

    def vline(self, x, y, h, c):
        self.fill_rect(x, y, 1, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.px(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def fill_circle(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            dx = int((r * r - (yy - cy) * (yy - cy)) ** 0.5) if abs(yy - cy) <= r else -1
            if dx >= 0:
                self.fill_rect(cx - dx, yy, 2 * dx + 1, 1, c)

    def circle(self, cx, cy, r, c):
        # Midpoint circle outline (1 px).
        x, y, d = r, 0, 1 - r
        while x >= y:
            for sx, sy in ((x, y), (y, x), (-x, y), (-y, x),
                           (x, -y), (y, -x), (-x, -y), (-y, -x)):
                self.px(cx + sx, cy + sy, c)
            y += 1
            if d <= 0:
                d += 2 * y + 1
            else:
                x -= 1
                d += 2 * (y - x) + 1

    def fill_triangle(self, x0, y0, x1, y1, x2, y2, c):
        # Scanline fill of a triangle.
        pts = sorted([(x0, y0), (x1, y1), (x2, y2)], key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = pts
        if ay == cy:
            return
        def edge_x(xa, ya, xb, yb, y):
            if yb == ya:
                return xa
            return xa + (xb - xa) * (y - ya) / (yb - ya)
        for y in range(ay, cy + 1):
            if y < by:
                xa = edge_x(ax, ay, bx, by, y)
                xb = edge_x(ax, ay, cx, cy, y)
            else:
                xa = edge_x(bx, by, cx, cy, y)
                xb = edge_x(ax, ay, cx, cy, y)
            self.fill_rect(int(min(xa, xb)), y, int(abs(xb - xa)) + 1, 1, c)

    # ------------------------------------------------------------ text
    def text(self, x, y, s, scale, color, bold=False):
        cx = x
        for ch in s:
            g = FONT.get(ch)
            if g is None:
                raise ValueError("no glyph for %r" % ch)
            for row in range(7):
                bits = g[row]
                for col in range(5):
                    if bits[col] == '#':
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       scale, scale, color)
                        if bold:
                            self.fill_rect(cx + col * scale + 1,
                                           y + row * scale, scale, scale, color)
            cx += CHAR_W * scale
        return cx

    def text_center(self, cx, y, s, scale, color, bold=False):
        self.text(cx - text_w(s, scale) // 2, y, s, scale, color, bold)

    def text_right(self, x, y, s, scale, color, bold=False):
        self.text(x - text_w(s, scale), y, s, scale, color, bold)


def wrap(text, max_w, scale):
    """Greedy word wrap.  Returns a list of lines that fit max_w px."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if text_w(trial, scale) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- PNG
def write_png(path, cv):
    def chunk(typ, data):
        out = struct.pack(">I", len(data)) + typ + data
        out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
        return out
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.buf[y * stride:(y + 1) * stride]
    idat = zlib.compress(bytes(raw), 6)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(chunk(b"IHDR", ihdr))
        f.write(chunk(b"IDAT", idat))
        f.write(chunk(b"IEND", b""))


# ---------------------------------------------------------------- palette
PAPER = (250, 243, 224)
INK = (26, 32, 44)
RED = (176, 32, 32)
NAVY = (31, 58, 95)
BLUE = (41, 98, 168)
SKY = (178, 214, 235)
SEA = (64, 130, 180)
GOLD = (201, 162, 39)
TEAL = (20, 143, 119)
GREEN = (30, 132, 73)
ORANGE = (202, 111, 30)
PURPLE = (125, 60, 152)
GRAY = (93, 109, 126)
LINE = (198, 182, 158)
WHITE = (255, 255, 255)
CREAM2 = (238, 228, 203)
SAND = (226, 205, 160)
DARK = (20, 24, 34)

REGION_COLORS = {
    "ASIA": (176, 58, 46),
    "MIDDLE EAST": (202, 111, 30),
    "EUROPE": (31, 97, 141),
    "AMERICAS": (30, 132, 73),
    "AFRICA": (125, 60, 152),
    "OCEANIA": (20, 143, 119),
    "GLOBAL": (93, 109, 126),
}
REGION_ORDER = ["ASIA", "MIDDLE EAST", "EUROPE", "AMERICAS",
                "AFRICA", "OCEANIA", "GLOBAL"]
REGION_COUNTS = {"ASIA": 8, "MIDDLE EAST": 7, "EUROPE": 9, "AMERICAS": 11,
                 "AFRICA": 5, "OCEANIA": 2, "GLOBAL": 8}

# ---------------------------------------------------------------- data
# All 50 stories happened or were first reported on Thu 19 Nov 2026.

HEROES = [
    {"n": 1, "region": "ASIA", "tag": "APEC - SHENZHEN",
     "headline": "TRUMP, XI AND PUTIN HOLD FIRST THREE-WAY SUMMIT",
     "body": "Leaders meet in Shenzhen as APEC opens. Agenda: Ukraine, Iran, "
             "nuclear arms, trade and AI. Xi pledges $20m to the bloc.",
     "source": "CONFIRMED - BBC / CBS / Japan Times", "art": "summit"},
    {"n": 2, "region": "MIDDLE EAST", "tag": "GULF CRISIS",
     "headline": "IRAN HITS GULF STATES AFTER US STRIKE ON QESHM",
     "body": "Tehran fired at US bases in Kuwait and Bahrain. The US hit a "
             "Guard missile site on Qeshm. A tanker was struck in the "
             "Strait of Hormuz.",
     "source": "CONFIRMED - Reuters / AP", "art": "gulf"},
    {"n": 3, "region": "EUROPE", "tag": "KERCH - 00:50",
     "headline": "UKRAINE STRIKES CRIMEAN BRIDGE A THIRD TIME",
     "body": "Overnight blast at about 00:50 in Kerch. Aksyonov confirmed "
             "the strike; traffic suspended. The 17 Nov strike collapsed a "
             "227 m road section.",
     "source": "CONFIRMED - BBC / Reuters - CLAIM KYIV: Kyiv silent",
     "art": "bridge"},
]

SMALLS = [
    {"n": 4, "region": "MIDDLE EAST",
     "headline": "Israel pushes beyond Yellow Line in central Gaza",
     "source": "CONFIRMED - Reuters. Tanks into Nuseirat; 3 dead.",
     "art": "tank"},
    {"n": 5, "region": "ASIA",
     "headline": "UN court to rule on Myanmar Rohingya genocide case",
     "source": "CONFIRMED - ICJ / HRW. Judgment 10:00, The Hague.",
     "art": "court"},
    {"n": 6, "region": "AMERICAS",
     "headline": "Anthropic begins trading after record $81.3bn IPO",
     "source": "CONFIRMED - Reuters. Priced $83; Nasdaq: ANT.",
     "art": "ipo"},
    {"n": 7, "region": "EUROPE",
     "headline": "EU proposes 45bn euro loan for Ukraine",
     "source": "CONFIRMED - Reuters. Allies meet in Berlin.",
     "art": "eu"},
    {"n": 8, "region": "GLOBAL",
     "headline": "COP31 deadlock persists as climate check launches",
     "source": "Antalya, Turkey.",
     "art": "cop"},
    {"n": 9, "region": "AFRICA",
     "headline": "Ethiopia and Eritrea mass forces along the border",
     "source": "CLAIM monitors. Troops massed; clashes near Badme unconfirmed.",
     "art": "border"},
    {"n": 10, "region": "ASIA",
     "headline": "Cyclone Aqwan to hit India's east coast",
     "source": "Bay of Bengal. Landfall forecast between Narsapur and Puri.",
     "art": "cyclone"},
    {"n": 11, "region": "OCEANIA",
     "headline": "Fiji and Tonga declare emergencies over El Nino drought",
     "source": "Drought emergency declared in both island nations.",
     "art": "drought"},
    {"n": 12, "region": "AMERICAS",
     "headline": "Grand Theft Auto VI goes on sale after 13-year wait",
     "source": "Rockstar's sequel launches worldwide.",
     "art": "gta"},
    {"n": 13, "region": "AFRICA",
     "headline": "Strain-specific Ebola vaccines to be trialled in DR Congo",
     "source": "Trial to test vaccines matched to the strain.",
     "art": "ebola"},
]

# Numbered list 14-50, one line each.
ALSO = [
    (14, "Houthi missile aimed at Riyadh; Saudis plan long Yemen campaign."),
    (15, "Israel delays E1 settlement; settler kills woman near Jericho."),
    (16, "Trump says Iran is exploring chemical and biological weapons. CLAIM TRUMP."),
    (17, "Knesset elects Matan Kahana speaker with 66 votes."),
    (18, "Australia, Canada, Italy, UK urge Israel to let aid reach flooded Gaza."),
    (19, "IAEA says North Korea expanded uranium enrichment (Yongbyon)."),
    (20, "Xi, Japan's Takaichi shake hands in Shenzhen, first since Taiwan row."),
    (21, "South Korea and China agree to expand cultural exchange."),
    (22, "EU governments approve Indonesia trade pact to counter US tariffs."),
    (23, "Court sentences Imamoglu and eight others in CHP case (Ankara)."),
    (24, "France sees fourth weekend of protests over rising living costs."),
    (25, "Israel's president taps Eisenkot to try to form next government."),
    (26, "Russian military plane crash in Siberia kills 19."),
    (27, "Zelensky urges Washington to lift limits on Starshield satellite links."),
    (28, "US and Venezuela restore military cooperation (Hegseth visit)."),
    (29, "Milei's bill to suspend primaries advances (Argentina)."),
    (30, "Isolated Awa group makes rare contact in Brazil."),
    (31, "Pastor convicted over Haitian president's 2021 assassination."),
    (32, "Record rain from atmospheric river hits California."),
    (33, "AI worries weigh on stocks: Hang Seng -2.78%, FTSE 100 -1.30%."),
    (34, "Gold, copper and bitcoin slide as markets weigh war and AI."),
    (35, "Australia's unemployment rises to 4.9%."),
    (36, "IMF reaches deal to unlock $2.3bn for Egypt."),
    (37, "Sudan: aid for displaced as drones drive civilian toll (El Dabba)."),
    (38, "Five EU nations plan to send asylum seekers to Rwanda."),
    (39, "Nearly 1 in 4 children live in conflict zones (UNICEF)."),
    (40, "Pew projects Islam to pass Christianity by 2035."),
    (41, "South Korea college exam held under AI cheating curbs."),
    (42, "Unrest in Bangladesh over Hasina's return and wage demands."),
    (43, "Estonia plans to close road border crossings with Russia from 1 Dec."),
    (44, "Washington sanctions a Hezbollah-linked charity and two gold firms."),
    (45, "Yemen's government designates the Houthis a terrorist group."),
    (46, "US State Dept details $12bn in Venezuelan oil and mineral revenue."),
    (47, "Voyager 1 reaches one light-day from Earth (NASA)."),
    (48, "Alcaraz beats Medvedev at ATP Finals (Turin)."),
    (49, "Waymo pulls driverless taxis from US freeways."),
    (50, "Webb confirms rare merger of a supergiant and a sun-like star."),
]

TIMELINE = [
    ("OVERNIGHT ~00:50", "Crimean Bridge struck again, Kerch"),
    ("~02:00 UTC", "APEC opens in Shenzhen; Xi pledges $20m"),
    ("09:00 UTC", "ICJ judgment due in The Hague"),
    ("14:30 UTC", "Anthropic shares begin trading, Nasdaq"),
    ("DAY", "EU proposes 45bn euro Ukraine loan, Berlin"),
    ("EVENING", "Trump, Xi, Putin hold first trilateral summit"),
]

NUMBERS = [
    ("$81.3bn", "Anthropic IPO, biggest ever"),
    ("-2.78%", "Hang Seng falls on AI worries"),
    ("46,000", "Gaza households displaced by rain"),
    ("45bn euro", "EU loan proposed for Ukraine"),
    ("$2.3bn", "IMF deal unlocks funds for Egypt"),
    ("1 in 4", "children live in conflict zones"),
]

DATE_LEFT = [
    "Alaska Senate race called (AP called it Tue 17 Nov, reported 18 Nov).",
    "US measles elimination status lost (PAHO announced Tue 17 Nov).",
    "Fed minutes (released 18 Nov).",
]
DATE_NOTYET = [
    "Estonia road-border closure (takes effect 1 December).",
    "Anthropic IPO closing (20 Nov).",
    "Trilateral joint statement (none issued by press time).",
]

# Map pins 1-13: (number, lon, lat).  Dots 14-50: (number, lon, lat).
MAP_PINS = [
    (1, 114.0, 22.5), (2, 56.0, 27.0), (3, 38.0, 47.0),
    (4, 35.0, 30.0), (5, 2.0, 54.0), (6, -74.0, 40.7),
    (7, 15.0, 54.0), (8, 24.0, 40.0), (9, 44.0, 11.0),
    (10, 85.0, 18.0), (11, 172.0, -18.0), (12, -84.0, 22.0),
    (13, 23.0, -2.0),
]
MAP_DOTS = [
    (14, 46.7, 24.6), (15, 35.4, 31.9), (16, -77.0, 38.9),
    (17, 35.2, 31.8), (18, 34.5, 31.5), (19, 126.0, 39.8),
    (20, 114.5, 22.8), (21, 127.0, 37.5), (22, 106.8, -6.2),
    (23, 32.9, 39.9), (24, 2.35, 48.85), (25, 35.3, 31.7),
    (26, 103.0, 53.0), (27, 30.5, 50.45), (28, -66.9, 10.5),
    (29, -58.4, -34.6), (30, -45.0, -4.0), (31, -72.3, 18.5),
    (32, -120.0, 37.0), (33, 114.2, 22.3), (34, -0.1, 51.5),
    (35, 149.0, -35.3), (36, 31.2, 30.0), (37, 30.5, 18.0),
    (38, 30.0, -2.0), (39, 6.1, 46.2), (40, -77.5, 38.5),
    (41, 127.5, 37.0), (42, 90.4, 23.8), (43, 24.7, 59.4),
    (44, -76.5, 39.3), (45, 44.2, 15.35), (46, -67.5, 10.0),
    (47, 170.0, 75.0), (48, 7.7, 45.0), (49, -122.4, 37.8),
    (50, -170.0, -75.0),
]
PIN_REGION = {1: "ASIA", 2: "MIDDLE EAST", 3: "EUROPE", 4: "MIDDLE EAST",
              5: "EUROPE", 6: "AMERICAS", 7: "EUROPE", 8: "GLOBAL",
              9: "AFRICA", 10: "ASIA", 11: "OCEANIA", 12: "AMERICAS",
              13: "AFRICA"}

# Rough continent outlines (lon, lat) for the dotted world map.
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-85, 70), (-75, 62),
     (-55, 47), (-60, 45), (-70, 42), (-75, 35), (-80, 25), (-85, 20),
     (-90, 15), (-95, 18), (-105, 20), (-115, 28), (-125, 40), (-125, 49),
     (-140, 60), (-165, 60), (-168, 66)],
    # Greenland
    [(-58, 64), (-45, 60), (-30, 68), (-25, 76), (-40, 80), (-58, 76),
     (-58, 64)],
    # South America
    [(-79, 9), (-72, 12), (-60, 8), (-50, 4), (-35, -8), (-40, -20),
     (-48, -28), (-58, -38), (-65, -45), (-68, -52), (-70, -55),
     (-73, -40), (-72, -20), (-80, -5), (-81, 0), (-79, 9)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 48), (0, 51), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 58), (28, 60), (30, 62), (32, 70), (40, 68),
     (45, 66), (40, 60), (35, 55), (30, 50), (28, 45), (23, 40), (19, 42),
     (12, 44), (8, 44), (3, 42), (-2, 37), (-10, 36)],
    # Africa
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (32, 31), (35, 28),
     (43, 12), (51, 11), (48, 0), (40, -10), (35, -18), (32, -28),
     (26, -34), (20, -35), (15, -27), (12, -18), (9, -1), (4, 6), (-8, 5),
     (-17, 15)],
    # Asia
    [(40, 68), (50, 70), (60, 70), (70, 72), (80, 73), (100, 76),
     (120, 73), (140, 72), (160, 70), (178, 66), (170, 60), (162, 55),
     (158, 50), (150, 45), (142, 40), (140, 35), (135, 33), (130, 32),
     (127, 35), (122, 38), (120, 30), (115, 22), (108, 18), (105, 10),
     (100, 8), (98, 15), (95, 20), (90, 22), (85, 19), (80, 15), (77, 8),
     (75, 12), (70, 20), (65, 25), (60, 25), (55, 26), (50, 29), (48, 30),
     (44, 29), (40, 32), (38, 36), (36, 36), (40, 40), (40, 45), (42, 50),
     (40, 55), (40, 60), (40, 68)],
    # SE Asia / Indonesia
    [(95, 5), (98, 0), (100, -5), (105, -5), (110, -7), (115, -8),
     (120, -10), (125, -8), (130, -3), (135, -2), (140, -4), (138, 0),
     (132, 0), (128, 2), (125, 5), (120, 2), (115, 0), (110, 5), (105, 2),
     (100, 5), (95, 5)],
    # Japan
    [(130, 31), (133, 34), (137, 35), (140, 38), (141, 42), (143, 44),
     (145, 44), (142, 40), (140, 36), (136, 33), (132, 33), (130, 31)],
    # UK
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51),
     (-5, 50)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (120, -34), (124, -33),
     (129, -32), (132, -32), (135, -35), (138, -35), (140, -38),
     (145, -38), (150, -37), (153, -32), (153, -27), (150, -22),
     (146, -19), (142, -15), (142, -11), (137, -12), (135, -15),
     (132, -12), (130, -13), (126, -14), (122, -17), (118, -20),
     (113, -22)],
    # New Zealand
    [(167, -45), (170, -42), (174, -39), (177, -38), (178, -37),
     (175, -40), (172, -42), (168, -46), (167, -45)],
]


def _inside_poly(x, y, poly):
    ins = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and \
                (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            ins = not ins
        j = i
    return ins


def on_land(lon, lat):
    return any(_inside_poly(lon, lat, p) for p in CONTINENTS)


# ---------------------------------------------------------------- art
def _flag_us(cv, x, y, w, h):
    # 13 stripes + blue canton with white dots.
    for i in range(13):
        c = RED if i % 2 == 0 else WHITE
        cv.fill_rect(x, y + i * h // 13, w, h // 13 + 1, c)
    cw, ch = w * 2 // 5, h * 7 // 13
    cv.fill_rect(x, y, cw, ch, NAVY)
    for r in range(4):
        for cc in range(5):
            cv.fill_rect(x + 3 + cc * (cw - 6) // 4,
                         y + 3 + r * (ch - 6) // 3, 2, 2, WHITE)


def _flag_cn(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, RED)
    cv.fill_circle(x + w // 5, y + h // 4, max(3, h // 8), GOLD)
    for dx, dy in ((w // 2, h // 6), (w * 3 // 5, h // 3),
                   (w * 3 // 5, h // 2), (w // 2, h * 2 // 3)):
        cv.fill_circle(x + dx, y + dy, max(2, h // 16), GOLD)


def _flag_ru(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h // 3 + 1, WHITE)
    cv.fill_rect(x, y + h // 3, w, h // 3 + 1, BLUE)
    cv.fill_rect(x, y + 2 * h // 3, w, h - 2 * h // 3, RED)


def _starburst(cv, cx, cy, r, c1, c2):
    for i in range(8):
        import math
        a = i * math.pi / 4
        x2 = int(cx + r * math.cos(a))
        y2 = int(cy + r * math.sin(a))
        a2 = a + math.pi / 8
        x3 = int(cx + r * 0.45 * math.cos(a2))
        y3 = int(cy + r * 0.45 * math.sin(a2))
        a3 = a - math.pi / 8
        x4 = int(cx + r * 0.45 * math.cos(a3))
        y4 = int(cy + r * 0.45 * math.sin(a3))
        cv.fill_triangle(cx, cy, x2, y2, x3, y3, c1)
        cv.fill_triangle(cx, cy, x2, y2, x4, y4, c1)
    cv.fill_circle(cx, cy, max(2, r // 3), c2)


def _skyline(cv, x, y, w, h, color):
    # Flat blocky skyline silhouettes.
    import random
    rnd = random.Random(19)
    bx = x
    while bx < x + w - 8:
        bw = rnd.randint(10, 22)
        bh = rnd.randint(h // 3, h)
        cv.fill_rect(bx, y + h - bh, bw, bh, color)
        bx += bw + 3


def draw_art(cv, kind, x, y, w, h):
    """Flat vector-style illustration inside box (x, y, w, h)."""
    if kind == "summit":
        cv.fill_rect(x, y, w, h, SKY)
        _skyline(cv, x, y + h // 2, w, h // 2, (120, 150, 180))
        cv.fill_rect(x, y + h - 8, w, 8, (90, 110, 140))
        fw, fh = w // 4, h // 2
        for i, fn in enumerate((_flag_us, _flag_cn, _flag_ru)):
            fx = x + 12 + i * (w - 24) // 3
            cv.fill_rect(fx + fw // 2 - 1, y + 6, 2, fh + 8, INK)
            fn(cv, fx, y + 6, fw, fh)
        cv.fill_rect(x, y + h - 14, w, 4, RED)
    elif kind == "gulf":
        cv.fill_rect(x, y, w, h, (232, 214, 170))
        cv.fill_rect(x, y + h * 2 // 5, w, h * 3 // 5, SEA)
        cv.fill_rect(x + w // 3, y + h // 3, w // 3, h // 6, SAND)
        # tanker
        cv.fill_rect(x + w // 8, y + h // 2, w // 4, h // 8, DARK)
        cv.fill_rect(x + w // 8 + 6, y + h // 2 - 8, 8, 8, DARK)
        cv.fill_circle(x + w // 8 + 10, y + h // 2 - 12, 4, GRAY)
        # missile arc
        cv.line(x + w * 3 // 4, y + h - 6, x + w * 5 // 6, y + h // 4,
                WHITE)
        cv.fill_triangle(x + w * 5 // 6 - 4, y + h // 4 + 6,
                         x + w * 5 // 6 + 4, y + h // 4 + 6,
                         x + w * 5 // 6, y + h // 4 - 4, WHITE)
        _starburst(cv, x + w // 2, y + h // 3, 12, GOLD, RED)
        for i in range(4):
            cv.hline(x + 8 + i * 30, y + h - 12 - i * 4, 18, WHITE)
    elif kind == "bridge":
        cv.fill_rect(x, y, w, h, SKY)
        cv.fill_rect(x, y + h * 3 // 5, w, h * 2 // 5, SEA)
        # deck with a broken gap in the middle
        cv.fill_rect(x + 6, y + h // 2, w // 2 - 22, 6, WHITE)
        cv.fill_rect(x + w // 2 + 16, y + h // 2, w // 2 - 22, 6, WHITE)
        cv.fill_rect(x + w // 2 - 18, y + h // 2 + 8, 12, 4, WHITE)
        for tx in (x + w // 4, x + w * 3 // 4):
            cv.fill_rect(tx - 2, y + h // 4, 4, h // 4 + 6, WHITE)
            cv.line(tx - 2, y + h // 4, x + 6, y + h // 2, WHITE)
            cv.line(tx + 2, y + h // 4, x + w - 6, y + h // 2, WHITE)
        _starburst(cv, x + w // 2, y + h // 2 - 6, 13, GOLD, RED)
        for i in range(3):
            cv.hline(x + 10 + i * 40, y + h - 10 - i * 5, 26, WHITE)
    elif kind == "tank":
        cv.fill_rect(x, y, w, h, (214, 196, 150))
        cv.fill_rect(x, y + h - 12, w, 12, (150, 128, 84))
        cv.hline(x, y + h // 3, w, GOLD)
        # tank silhouette
        tx, ty = x + w // 2 - 34, y + h // 2
        cv.fill_rect(tx, ty, 68, 16, DARK)
        cv.fill_rect(tx + 18, ty - 10, 30, 12, DARK)
        cv.fill_rect(tx + 48, ty - 7, 34, 4, DARK)
        for wx in range(tx + 6, tx + 64, 12):
            cv.fill_circle(wx, ty + 16, 4, INK)
        # buildings
        cv.fill_rect(x + 8, y + h - 34, 16, 22, (120, 100, 70))
        cv.fill_rect(x + w - 26, y + h - 30, 18, 18, (120, 100, 70))
    elif kind == "court":
        cv.fill_rect(x, y, w, h, CREAM2)
        cx = x + w // 2
        cv.fill_triangle(cx - 34, y + 12, cx + 34, y + 12, cx, y + 2,
                         NAVY)
        for px in (cx - 26, cx - 9, cx + 7, cx + 24):
            cv.fill_rect(px, y + 14, 5, h - 26, NAVY)
        cv.fill_rect(x + 8, y + h - 12, w - 16, 4, NAVY)
        cv.fill_rect(x + 4, y + h - 8, w - 8, 4, NAVY)
        # clock
        cv.fill_circle(x + w - 16, y + 12, 9, WHITE)
        cv.circle(x + w - 16, y + 12, 9, INK)
        cv.line(x + w - 16, y + 12, x + w - 16, y + 5, INK)
        cv.line(x + w - 16, y + 12, x + w - 11, y + 12, INK)
    elif kind == "ipo":
        cv.fill_rect(x, y, w, h, CREAM2)
        bars = [12, 18, 15, 26, 22, 34, 30, 44]
        bw = (w - 20) // len(bars)
        for i, bh in enumerate(bars):
            cv.fill_rect(x + 10 + i * bw, y + h - 8 - bh, bw - 3, bh,
                         GREEN if i % 2 == 0 else TEAL)
        cv.line(x + 8, y + h - 8, x + w - 8, y + 6, RED)
        cv.fill_triangle(x + w - 8, y + 6, x + w - 18, y + 6,
                         x + w - 8, y + 16, RED)
        cv.text(x + 10, y + 4, "ANT", 1, INK, bold=True)
    elif kind == "eu":
        cv.fill_rect(x, y, w, h, NAVY)
        import math
        cx, cy = x + w // 2, y + h // 2
        for i in range(12):
            a = i * math.pi / 6
            cv.fill_circle(int(cx + (w // 3) * math.cos(a)),
                           int(cy + (h // 3) * math.sin(a)), 3, GOLD)
        cv.text(x + w // 2 - 18, y + h // 2 - 4, "45bn", 1, WHITE, bold=True)
    elif kind == "cop":
        cv.fill_rect(x, y, w, h, SKY)
        cx, cy = x + w // 2, y + h // 2
        cv.fill_circle(cx, cy, h // 3 + 4, BLUE)
        cv.fill_circle(cx - 8, cy - 4, 6, GREEN)
        cv.fill_circle(cx + 8, cy + 6, 5, GREEN)
        cv.fill_circle(cx + 2, cy - 10, 4, GREEN)
        cv.fill_circle(cx + w // 3, y + 10, 7, GOLD)
        cv.line(x + 8, y + h - 10, x + w - 8, y + h - 26, RED)
        cv.fill_triangle(x + w - 8, y + h - 26, x + w - 18, y + h - 26,
                         x + w - 8, y + h - 16, RED)
    elif kind == "border":
        cv.fill_rect(x, y, w, h, SAND)
        cv.fill_rect(x, y, w // 2, h, (196, 170, 120))
        for i in range(0, h, 8):
            cv.fill_rect(x + w // 2 - 1, y + i, 3, 4, RED)
        for tx in (x + w // 4, x + w * 3 // 4):
            cv.fill_triangle(tx - 8, y + h - 10, tx + 8, y + h - 10,
                             tx, y + h - 26, DARK)
            cv.fill_rect(tx - 1, y + h - 26, 2, 8, DARK)
        cv.fill_triangle(x + w // 2, y + 4, x + w // 2 + 16, y + 24,
                         x + w // 2 - 16, y + 24, GOLD)
        cv.text(x + w // 2 - 2, y + 12, "!", 1, INK, bold=True)
    elif kind == "cyclone":
        cv.fill_rect(x, y, w, h, (206, 224, 238))
        cx, cy = x + w // 2, y + h // 2
        for r in (26, 20, 14, 8):
            cv.circle(cx, cy, r, SEA)
            cv.fill_rect(cx + r - 2, cy - 1, 4, 2, (206, 224, 238))
        cv.fill_circle(cx, cy, 4, WHITE)
        for i in range(6):
            cv.line(x + 10 + i * 12, y + h - 6, x + 8 + i * 12, y + h - 14,
                    BLUE)
        cv.fill_rect(x, y + h - 4, w, 4, GREEN)
    elif kind == "drought":
        cv.fill_rect(x, y, w, h, (246, 222, 160))
        cv.fill_circle(x + w - 22, y + 14, 10, GOLD)
        for a in range(8):
            import math
            ang = a * math.pi / 4
            cv.line(x + w - 22 + int(13 * math.cos(ang)),
                    y + 14 + int(13 * math.sin(ang)),
                    x + w - 22 + int(19 * math.cos(ang)),
                    y + 14 + int(19 * math.sin(ang)), GOLD)
        # cracked earth
        cv.fill_rect(x, y + h * 2 // 3, w, h // 3, (176, 138, 84))
        cv.line(x + 10, y + h * 2 // 3, x + 26, y + h - 4, (120, 86, 40))
        cv.line(x + 26, y + h - 4, x + 44, y + h * 2 // 3 + 6, (120, 86, 40))
        cv.line(x + w - 40, y + h * 2 // 3, x + w - 20, y + h - 6,
                (120, 86, 40))
        # palm
        cv.line(x + 24, y + h * 2 // 3, x + 20, y + h // 4, GREEN)
        for dx, dy in ((-12, -4), (12, -4), (-8, -10), (8, -10)):
            cv.line(x + 20, y + h // 4, x + 20 + dx, y + h // 4 + dy, GREEN)
    elif kind == "gta":
        cv.fill_rect(x, y, w, h, (250, 170, 90))
        cv.fill_rect(x, y + h // 3, w, h * 2 // 3, (240, 120, 90))
        cv.fill_circle(x + w // 2, y + h // 3, 12, (255, 220, 130))
        _skyline(cv, x, y + h // 2, w, h // 2, DARK)
        cv.fill_rect(x, y + h - 6, w, 6, (40, 60, 90))
        cv.text(x + 8, y + 6, "VI", 2, WHITE, bold=True)
    elif kind == "ebola":
        cv.fill_rect(x, y, w, h, CREAM2)
        # vial
        vx, vy = x + w // 2 - 30, y + 10
        cv.fill_rect(vx, vy, 20, h - 20, WHITE)
        cv.rect(vx, vy, 20, h - 20, INK)
        cv.fill_rect(vx - 2, vy - 6, 24, 6, RED)
        cv.fill_rect(vx + 2, vy + 10, 16, h - 30, (120, 200, 120))
        # syringe
        cv.line(x + w - 40, y + h - 10, x + w - 12, y + 12, INK)
        cv.fill_rect(x + w - 16, y + 10, 8, 8, GRAY)
        # virus dots with spikes
        for (dx, dy) in ((w - 60, 14), (w - 70, 30), (30, h - 14)):
            cv.fill_circle(x + dx, y + dy, 5, RED)
            cv.line(x + dx - 7, y + dy, x + dx + 7, y + dy, RED)
            cv.line(x + dx, y + dy - 7, x + dx, y + dy + 7, RED)
    else:
        cv.fill_rect(x, y, w, h, CREAM2)
        cv.rect(x, y, w, h, LINE)

# ---------------------------------------------------------------- layout
X0, X1 = 24, 1000
CW = X1 - X0  # 976


def _num_chip(cv, x, y, n, color, scale=1):
    """Numbered story badge: coloured square + white number."""
    s = 16 if scale == 1 else 20
    cv.fill_rect(x, y, s, s, color)
    t = str(n)
    cv.text(x + (s - text_w(t, 1)) // 2, y + (s - 7) // 2, t, 1, WHITE,
            bold=True)


def draw_header(cv, y):
    cv.text_center(512, y, "THE WORLD'S NEWS IN ONE PICTURE", 2, RED,
                   bold=True)
    y += 18
    cv.text_center(512, y, "THURSDAY 19 NOVEMBER 2026", 5, INK, bold=True)
    y += 40
    cv.text_center(512, y, "50 STORIES  ·  7 REGIONS  ·  ALL FROM THURSDAY",
                   2, NAVY, bold=True)
    y += 18
    cv.fill_rect(X0, y, CW, 2, RED)
    cv.fill_rect(X0, y + 3, CW, 1, INK)
    return y + 8


def draw_timeline(cv, y):
    cv.text(X0, y, "THURSDAY IN SIX MOMENTS", 1, RED, bold=True)
    cv.text_right(X1, y, "ALL TIMES UTC", 1, GRAY)
    y += 11
    slot_w = (CW - 5 * 8) // 6
    for i, (t, txt) in enumerate(TIMELINE):
        sx = X0 + i * (slot_w + 8)
        cv.fill_rect(sx, y, slot_w, 1, LINE)
        cv.text(sx, y + 4, t, 1, RED, bold=True)
        lines = wrap(txt, slot_w, 1)
        ly = y + 14
        for ln in lines[:3]:
            cv.text(sx, ly, ln, 1, INK)
            ly += 9
        if i < 5:
            cv.vline(sx + slot_w + 4, y, 30, LINE)
    return y + 34


def draw_heroes(cv, y):
    gap = 12
    hw = (CW - 2 * gap) // 3
    top = y
    for i, st in enumerate(HEROES):
        hx = X0 + i * (hw + gap)
        color = REGION_COLORS[st["region"]]
        # art
        cv.fill_rect(hx, y, hw, 78, CREAM2)
        draw_art(cv, st["art"], hx + 2, y + 2, hw - 4, 74)
        _num_chip(cv, hx + 4, y + 4, st["n"], color)
        yy = y + 82
        # region tag chip
        tag = st["n"] and "%s - %s" % (st["region"], st["tag"])
        cv.fill_rect(hx, yy, text_w(tag, 1) + 8, 12, color)
        cv.text(hx + 4, yy + 2, tag, 1, WHITE, bold=True)
        yy += 16
        # headline, scale 2 bold, max 3 lines
        for ln in wrap(st["headline"], hw, 2)[:3]:
            cv.text(hx, yy, ln, 2, INK, bold=True)
            yy += 16
        yy += 2
        # body, scale 1, max 4 lines
        for ln in wrap(st["body"], hw, 1)[:4]:
            cv.text(hx, yy, ln, 1, INK)
            yy += 10
        yy += 2
        # source line, red CLAIM/CONFIRMED lead
        for ln in wrap(st["source"], hw, 1)[:2]:
            cv.text(hx, yy, ln, 1, RED, bold=True)
            yy += 10
        top = max(top, yy)
    return top + 6


def draw_smalls(cv, y):
    gap = 8
    cols, rows = 5, 2
    cw_ = (CW - (cols - 1) * gap) // cols
    rh = 80
    for idx, st in enumerate(SMALLS):
        r, c = divmod(idx, cols)
        sx = X0 + c * (cw_ + gap)
        sy = y + r * (rh + gap)
        color = REGION_COLORS[st["region"]]
        # mini art banner
        draw_art(cv, st["art"], sx, sy, cw_, 32)
        _num_chip(cv, sx + 3, sy + 3, st["n"], color)
        yy = sy + 36
        for ln in wrap(st["headline"], cw_, 1)[:2]:
            cv.text(sx, yy, ln, 1, INK, bold=True)
            yy += 10
        for ln in wrap(st["source"], cw_, 1)[:2]:
            cv.text(sx, yy, ln, 1, GRAY)
            yy += 9
    return y + rows * rh + (rows - 1) * gap + 4


def draw_numbers(cv, y):
    bw = (CW - 5 * 8) // 6
    for i, (fig, label) in enumerate(NUMBERS):
        bx = X0 + i * (bw + 8)
        cv.fill_rect(bx, y, bw, 46, CREAM2)
        cv.rect(bx, y, bw, 46, LINE)
        cv.text_center(bx + bw // 2, y + 5, fig, 2, RED, bold=True)
        for j, ln in enumerate(wrap(label, bw - 8, 1)[:2]):
            cv.text_center(bx + bw // 2, y + 24 + j * 9, ln, 1, INK)
    return y + 50


def draw_regions(cv, y):
    x = X0
    cv.text(x, y + 2, "REGIONS:", 1, INK, bold=True)
    x += text_w("REGIONS: ", 1) + 4
    for name in REGION_ORDER:
        color = REGION_COLORS[name]
        cv.fill_rect(x, y, 12, 12, color)
        x += 15
        t = "%s %d" % (name, REGION_COUNTS[name])
        cv.text(x, y + 2, t, 1, INK, bold=True)
        x += text_w(t, 1) + 14
    cv.text_right(X1, y + 2, "TOTAL 50", 1, RED, bold=True)
    return y + 16


def draw_map(cv, y):
    # panel frame + title
    cv.fill_rect(X0, y, CW, 2, RED)
    cv.text(X0, y + 6, "WHERE IT HAPPENED", 2, INK, bold=True)
    cv.text_right(X1, y + 6, "PINS 1-13 FEATURED STORIES - DOTS 14-50",
                  1, GRAY)
    y += 26
    map_x, map_y, map_w, map_h = X0, y, 600, 110
    leg_x = X0 + map_w + 16
    leg_w = X1 - leg_x
    # dotted land
    for gy in range(map_y, map_y + map_h, 5):
        for gx in range(map_x, map_x + map_w, 5):
            lon = (gx - map_x) / float(map_w) * 360.0 - 180.0
            lat = 90.0 - (gy - map_y) / float(map_h) * 180.0
            if on_land(lon, lat):
                cv.fill_rect(gx, gy, 3, 3, (150, 138, 110))
    # graticule hint
    cv.rect(map_x, map_y, map_w, map_h, LINE)
    # dots 14-50 first (under pins)
    for (n, lon, lat) in MAP_DOTS:
        px = int(map_x + (lon + 180.0) / 360.0 * map_w)
        py = int(map_y + (90.0 - lat) / 180.0 * map_h)
        if n in (47, 50):
            cv.fill_rect(px - 3, py - 1, 7, 2, GOLD)
            cv.fill_rect(px - 1, py - 3, 2, 7, GOLD)
        else:
            cv.fill_circle(px, py, 2, INK)
    # numbered pins 1-13
    for (n, lon, lat) in MAP_PINS:
        px = int(map_x + (lon + 180.0) / 360.0 * map_w)
        py = int(map_y + (90.0 - lat) / 180.0 * map_h)
        color = REGION_COLORS[PIN_REGION[n]]
        cv.fill_circle(px, py, 8, color)
        cv.circle(px, py, 8, WHITE)
        t = str(n)
        cv.text(px - text_w(t, 1) // 2, py - 3, t, 1, WHITE, bold=True)
    # legend (right column, two sub-columns so it fits the map height)
    ly = map_y
    cv.text(leg_x, ly, "REGIONS", 1, RED, bold=True)
    ly += 12
    col2_x = leg_x + 180
    for i, name in enumerate(REGION_ORDER):
        lx = leg_x if i < 4 else col2_x
        lyy = ly + (i if i < 4 else i - 4) * 13
        cv.fill_rect(lx, lyy, 10, 10, REGION_COLORS[name])
        cv.text(lx + 13, lyy + 1,
                "%s %d" % (name, REGION_COUNTS[name]), 1, INK)
    ly += 4 * 13 + 2
    cv.text(leg_x, ly, "PIN KEY", 1, RED, bold=True)
    ly += 11
    key = [(1, "Summit"), (2, "Gulf strikes"), (3, "Crimean Bridge"),
           (6, "Anthropic IPO"), (9, "Border build-up"),
           (10, "Cyclone Aqwan")]
    for i, (n, label) in enumerate(key):
        lx = leg_x if i < 3 else col2_x
        lyy = ly + (i if i < 3 else i - 3) * 11
        cv.fill_circle(lx + 5, lyy + 4, 5, REGION_COLORS[PIN_REGION[n]])
        t = str(n)
        cv.text(lx + 5 - text_w(t, 1) // 2, lyy + 1, t, 1, WHITE, bold=True)
        cv.text(lx + 14, lyy + 1, label, 1, INK)
    return y + map_h + 4


def draw_also(cv, y):
    cv.fill_rect(X0, y, CW, 2, RED)
    cv.text(X0, y + 6, "ALSO ON THURSDAY", 2, INK, bold=True)
    cv.text_right(X1, y + 6, "STORIES 14-50", 1, GRAY)
    y += 24
    col_w = (CW - 24) // 2
    rows = (len(ALSO) + 1) // 2  # 19
    for i, (n, txt) in enumerate(ALSO):
        col = 0 if i < rows else 1
        row = i if col == 0 else i - rows
        lx = X0 + col * (col_w + 24)
        ly = y + row * 8
        line = "%d. %s" % (n, txt)
        assert text_w(line, 1) <= col_w, "also line too long: %r" % line
        cv.text(lx, ly, line, 1, INK)
    return y + rows * 8 + 4


def draw_datecheck(cv, y):
    cv.fill_rect(X0, y, CW, 2, RED)
    cv.text(X0, y + 6, "DATE CHECK", 2, RED, bold=True)
    cv.text(X0 + text_w("DATE CHECK ", 2) + 4, y + 6,
            "- WHAT WE LEFT OUT, AND WHAT HAS NOT HAPPENED YET", 1, INK)
    y += 22
    col_w = (CW - 24) // 2
    cv.text(X0, y, "LEFT OUT - NOT 19 NOVEMBER:", 1, RED, bold=True)
    cv.text(X0 + col_w + 24, y, "NOT YET HAPPENED:", 1, RED, bold=True)
    y += 11
    ly = y
    for item in DATE_LEFT:
        for ln in wrap("- " + item, col_w, 1):
            cv.text(X0, ly, ln, 1, INK)
            ly += 9
    ry = y
    for item in DATE_NOTYET:
        for ln in wrap("- " + item, col_w, 1):
            cv.text(X0 + col_w + 24, ry, ln, 1, INK)
            ry += 9
    return max(ly, ry) + 4


def draw_footer(cv, y):
    cv.fill_rect(X0, y, CW, 1, INK)
    y += 5
    cv.text(X0, y,
            "Every story here happened or was first reported on Thursday "
            "19 November 2026. Contested claims are marked as claims.",
            1, INK)
    y += 10
    cv.text(X0, y,
            "Sources: Reuters, AP, AFP, BBC, Al Jazeera, WHO, UN, PAHO, "
            "NASA. Original drawings.",
            1, GRAY)
    return y + 10


def build_poster():
    cv = Canvas(W, H, PAPER)
    y = 10
    y = draw_header(cv, y)
    y = draw_timeline(cv, y + 4)
    y = draw_heroes(cv, y + 4)
    y = draw_smalls(cv, y + 4)
    y = draw_numbers(cv, y + 4)
    y = draw_regions(cv, y + 4)
    y = draw_map(cv, y + 4)
    y = draw_also(cv, y + 4)
    y = draw_datecheck(cv, y + 4)
    y = draw_footer(cv, y + 4)
    return cv, y


def all_poster_text():
    """Every string printed on the poster (for font-coverage tests)."""
    out = ["THE WORLD'S NEWS IN ONE PICTURE", "THURSDAY 19 NOVEMBER 2026",
           "50 STORIES  ·  7 REGIONS  ·  ALL FROM THURSDAY",
           "THURSDAY IN SIX MOMENTS", "ALL TIMES UTC",
           "WHERE IT HAPPENED", "PINS 1-13 FEATURED STORIES - DOTS 14-50",
           "REGIONS", "TOTAL 50", "PIN KEY",
           "ALSO ON THURSDAY", "STORIES 14-50", "DATE CHECK",
           "- WHAT WE LEFT OUT, AND WHAT HAS NOT HAPPENED YET",
           "LEFT OUT - NOT 19 NOVEMBER:", "NOT YET HAPPENED:",
           "Every story here happened or was first reported on Thursday "
           "19 November 2026. Contested claims are marked as claims.",
           "Sources: Reuters, AP, AFP, BBC, Al Jazeera, WHO, UN, PAHO, "
           "NASA. Original drawings.",
           "REGIONS:"]
    for t, txt in TIMELINE:
        out += [t, txt]
    for fig, label in NUMBERS:
        out += [fig, label]
    for name in REGION_ORDER:
        out.append("%s %d" % (name, REGION_COUNTS[name]))
    for st in HEROES:
        out += ["%s - %s" % (st["region"], st["tag"]), st["headline"],
                st["body"], st["source"]]
    for st in SMALLS:
        out += [st["headline"], st["source"]]
    for n, txt in ALSO:
        out.append("%d. %s" % (n, txt))
    for item in DATE_LEFT + DATE_NOTYET:
        out.append("- " + item)
    return out


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "news.png")
    cv, bottom = build_poster()
    print("poster bottom y = %d / %d" % (bottom, H))
    if bottom > H - 4:
        print("WARNING: poster overflows by %d px" % (bottom - (H - 4)))
    write_png(out, cv)
    print("wrote %s (%d bytes)" % (out, os.path.getsize(out)))


if __name__ == "__main__":
    main()
