#!/usr/bin/env python3
"""Sum up Tuesday 24 November 2026 world news in one image.

Pure Python standard library only. Draws a 1024x1024 news-front-page image
with a 5x7 bitmap font and encodes the PNG by hand (zlib + struct).
Deterministic: identical bytes on every run.
"""

import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- font ----
# 5x7 bitmap font. Each glyph is 7 rows of 5 bits ("1" = ink).
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    "%": ("11001", "10010", "00100", "01000", "01001", "10011", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
}

# ------------------------------------------------------------- palette ----
NAVY = (20, 38, 63)
GOLD = (201, 162, 39)
CREAM = (244, 241, 232)
WHITE = (255, 255, 255)
INK = (24, 28, 36)
GREY = (110, 116, 128)
RED = (178, 44, 38)
GREEN = (38, 122, 74)
BLUE = (36, 90, 168)
ORANGE = (214, 110, 30)
PURPLE = (104, 74, 158)
TEAL = (18, 128, 122)

# -------------------------------------------------------------- canvas ----
# Flat RGB bytearray, row-major.
PIX = bytearray(W * H * 3)


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        PIX[i], PIX[i + 1], PIX[i + 2] = c


def rect(x, y, w, h, c):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            PIX[i], PIX[i + 1], PIX[i + 2] = c


def disc(cx, cy, r, c):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                px(xx, yy, c)


def ring(cx, cy, r, t, c):
    for yy in range(cy - r - t, cy + r + t + 1):
        for xx in range(cx - r - t, cx + r + t + 1):
            d2 = (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy)
            if (r - t) * (r - t) <= d2 <= (r + t) * (r + t):
                px(xx, yy, c)


def hline(x, y, w, t, c):
    rect(x, y, w, t, c)


def vline(x, y, h, t, c):
    rect(x, y, t, h, c)


def triangle(x0, y0, x1, y1, x2, y2, c):
    # Scanline fill of a triangle.
    ys = sorted([y0, y1, y2])
    for yy in range(ys[0], ys[2] + 1):
        xs = []
        for (ax, ay), (bx, by) in (((x0, y0), (x1, y1)),
                                   ((x1, y1), (x2, y2)),
                                   ((x2, y2), (x0, y0))):
            if ay == by:
                continue
            if min(ay, by) <= yy <= max(ay, by):
                xs.append(ax + (yy - ay) * (bx - ax) / (by - ay))
        if len(xs) >= 2:
            xa, xb = int(min(xs)), int(max(xs))
            for xx in range(xa, xb + 1):
                px(xx, yy, c)


def text_width(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(x, y, s, scale, c):
    s = s.upper()
    cx = x
    for ch in s:
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "1":
                    rect(cx + col * scale, y + row * scale, scale, scale, c)
        cx += 6 * scale


def draw_text_center(cx, y, s, scale, c):
    draw_text(cx - text_width(s, scale) // 2, y, s, scale, c)


# ------------------------------------------------------------ PNG out -----
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(path):
    raw = bytearray()
    stride = W * 3
    for yy in range(H):
        raw.append(0)  # filter: none
        raw += PIX[yy * stride:(yy + 1) * stride]
    comp = zlib.compress(bytes(raw), 6)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += _chunk(b"IDAT", comp)
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)

# ---------------------------------------------------------- pictograms ----
# Each pictogram draws inside a ~120x120 box whose top-left is (x, y).

def pic_ship(x, y, c):
    # Hull, mast, sail, waves, and a small pennant on the mast.
    vline(x + 58, y + 8, 52, 6, c)
    rect(x + 64, y + 8, 20, 12, GOLD)
    triangle(x + 64, y + 12, x + 64, y + 56, x + 104, y + 56, c)
    triangle(x + 14, y + 62, x + 106, y + 62, x + 96, y + 88, c)
    rect(x + 14, y + 62, 92, 10, c)
    hline(x + 6, y + 96, 108, 5, c)
    hline(x + 20, y + 108, 80, 5, c)


def pic_globe(x, y, c):
    ring(x + 60, y + 60, 46, 5, c)
    vline(x + 60, y + 14, 92, 4, c)
    hline(x + 14, y + 60, 92, 4, c)
    hline(x + 26, y + 34, 68, 4, c)
    hline(x + 26, y + 86, 68, 4, c)
    # Crack: no-deal slash.
    for i in range(30):
        px(x + 78 + i, y + 22 + i, RED)
        px(x + 79 + i, y + 22 + i, RED)


def pic_chip(x, y, c):
    rect(x + 30, y + 30, 60, 60, c)
    rect(x + 44, y + 44, 32, 32, CREAM)
    rect(x + 52, y + 52, 16, 16, c)
    for i in range(4):
        rect(x + 34 + i * 14, y + 14, 6, 16, c)
        rect(x + 34 + i * 14, y + 90, 6, 16, c)
        rect(x + 14, y + 34 + i * 14, 16, 6, c)
        rect(x + 90, y + 34 + i * 14, 16, 6, c)


def pic_flame(x, y, c):
    disc(x + 60, y + 78, 30, c)
    triangle(x + 34, y + 76, x + 86, y + 76, x + 60, y + 18, c)
    disc(x + 60, y + 88, 16, GOLD)
    hline(x + 14, y + 108, 92, 5, c)


def pic_trophy(x, y, c):
    rect(x + 36, y + 18, 48, 44, c)
    rect(x + 24, y + 26, 12, 22, c)
    rect(x + 84, y + 26, 12, 22, c)
    rect(x + 56, y + 62, 8, 26, c)
    rect(x + 40, y + 88, 40, 10, c)
    disc(x + 60, y + 34, 10, GOLD)


def pic_chess(x, y, c):
    # 6x6 board, alternating squares, with a crown marker on top.
    for r in range(6):
        for col in range(6):
            if (r + col) % 2 == 0:
                rect(x + 18 + col * 14, y + 22 + r * 14, 14, 14, c)
    rect(x + 18, y + 22, 84, 4, c)
    rect(x + 18, y + 102, 84, 4, c)
    rect(x + 18, y + 22, 4, 84, c)
    rect(x + 98, y + 22, 4, 84, c)
    triangle(x + 46, y + 6, x + 74, y + 6, x + 60, y + 18, GOLD)


# -------------------------------------------------------------- panels ----
def panel(x, y, w, h, accent, tag, lines, pic):
    rect(x, y, w, h, WHITE)
    rect(x, y, w, 10, accent)
    rect(x, y + 10, w, 2, GOLD)
    draw_text(x + 18, y + 26, tag, 2, accent)
    pic(x + 18, y + 62, accent)
    tx = x + 158
    ty = y + 66
    for ln in lines:
        draw_text(tx, ty, ln, 2, INK)
        ty += 34
    # Thin frame.
    rect(x, y, w, 2, INK)
    rect(x, y + h - 2, w, 2, INK)
    rect(x, y, 2, h, INK)
    rect(x + w - 2, y, 2, h, INK)


def build():
    rect(0, 0, W, H, CREAM)
    # Masthead.
    rect(0, 0, W, 118, NAVY)
    rect(0, 118, W, 6, GOLD)
    draw_text_center(W // 2, 22, "TUESDAY 24 NOVEMBER 2026", 4, WHITE)
    draw_text_center(W // 2, 76, "WORLD NEWS IN ONE IMAGE", 2, GOLD)

    panels = [
        (16, 140, RED, "WAR AT SEA",
         ["UKRAINE SAYS IT SANK", "A RUSSIAN WARSHIP", "OFF LIBYA", "CORVETTE MERKURY", "HIT AT BENGHAZI"],
         pic_ship),
        (512, 140, GREEN, "CLIMATE",
         ["COP31 COLLAPSES", "NO DEAL IN ANTALYA", "LONGEST COP EVER", "EU REJECTS DRAFT"],
         pic_globe),
        (16, 424, BLUE, "TECH",
         ["NVIDIA BRINGS BACK", "JENSEN HUANG", "AS CEO, 11 DAYS", "AFTER HE QUIT", "SHARES JUMP 33%"],
         pic_chip),
        (512, 424, ORANGE, "DISASTER",
         ["FACTORY FIRE IN", "INDONESIA KILLS 24", "30 STILL MISSING", "CIKANDE, BANTEN"],
         pic_flame),
        (16, 708, PURPLE, "SPORT",
         ["ALCARAZ WINS FIRST", "ATP FINALS CROWN", "BEATS ZVEREV", "6-2, 7-6 IN TURIN"],
         pic_trophy),
        (512, 708, TEAL, "CHESS",
         ["CHESS CROWN FIGHT", "BEGINS IN GENEVA", "GUKESH V SINDAROV", "GAME 1 TODAY", "YOUNGEST MATCH EVER"],
         pic_chess),
    ]
    for (px0, py0, accent, tag, lines, pic) in panels:
        panel(px0, py0, 496, 268, accent, tag, lines, pic)

    # Footer.
    rect(0, 992, W, 32, NAVY)
    draw_text_center(W // 2, 1000, "SIX STORIES FROM ONE DAY - 24 NOVEMBER 2026", 2, WHITE)


def main():
    out_dir = os.environ.get("OUTPUT_DIR") or os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    build()
    path = os.path.join(out_dir, "entry.png")
    size = write_png(path)
    print("wrote %s (%d bytes)" % (path, size))


if __name__ == "__main__":
    main()
