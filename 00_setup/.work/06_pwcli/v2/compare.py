#!/usr/bin/env python3
"""compare.png = real screenshot (left, colored boxes + number badges from [box=...]) | same YAML lines (right).

usage: compare.py shot.png snap.yml out.png SPEC [SPEC ...] [--title T] [--pad N] [--width W]
SPEC = a ref (e107) or a regex prefixed with '/' (/option "One way") — first matching line of snap.yml.
The screenshot must be a --hires (2x) capture taken right after `snapshot --boxes` of the same page state.
"""
import argparse, re, textwrap
from PIL import Image, ImageDraw, ImageFont

COLORS = ["#e53935", "#1e88e5", "#43a047", "#fb8c00", "#8e24aa", "#00897b", "#d81b60", "#6d4c41"]
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BOX = re.compile(r"\[box=(-?\d+),(-?\d+),(\d+),(\d+)\]")


def find(lines, spec):
    rx = re.compile(re.escape(f"[ref={spec}]") if not spec.startswith("/") else spec[1:])
    for n, l in enumerate(lines, 1):
        if rx.search(l):
            return n, l
    raise SystemExit(f"not found: {spec}")


def shorten(line, maxlen):
    line = line.rstrip()
    if len(line) <= maxlen:
        return line
    m = re.match(r'^(\s*- \w+ ")(.*?)(".*)$', line)          # shorten the name, keep role/state/ref/box
    if m:
        keep = maxlen - len(m.group(1)) - len(m.group(3)) - 1
        if keep > 12:
            return m.group(1) + m.group(2)[:keep] + "…" + m.group(3)
    return line[:maxlen - 1] + "…"


def badge(d, x, y, r, n, color):
    d.ellipse([x - r, y - r, x + r, y + r], fill=color, outline="white", width=max(2, r // 6))
    f = ImageFont.truetype(SANS_B, int(r * 1.25))
    d.text((x, y), str(n), fill="white", font=f, anchor="mm")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("shot"); ap.add_argument("snap"); ap.add_argument("out"); ap.add_argument("specs", nargs="+")
    ap.add_argument("--title", default="Real page (screenshot --hires)   <->   accessibility snapshot (YAML)")
    ap.add_argument("--pad", type=int, default=60, help="css px around the union of boxes (x)")
    ap.add_argument("--pady", type=int, default=150, help="css px around the union of boxes (y)")
    ap.add_argument("--width", type=int, default=2200)
    ap.add_argument("--maxlen", type=int, default=62)
    a = ap.parse_args()

    lines = open(a.snap, encoding="utf-8").read().splitlines()
    items = []
    for i, spec in enumerate(a.specs):
        n, l = find(lines, spec)
        b = BOX.search(l)
        items.append(dict(n=i + 1, line_no=n, text=l, box=[int(v) for v in b.groups()] if b else None, color=COLORS[i % len(COLORS)]))

    shot = Image.open(a.shot).convert("RGB")
    S = shot.width / 1920                                   # 2.0 for --hires
    boxes = [it["box"] for it in items if it["box"] and it["box"][2] > 0]
    x0 = max(0, min(b[0] for b in boxes) - a.pad); y0 = max(0, min(b[1] for b in boxes) - a.pady)
    x1 = min(1920, max(b[0] + b[2] for b in boxes) + a.pad); y1 = min(shot.height / S, max(b[1] + b[3] for b in boxes) + a.pady)
    if (x1 - x0) < 520:                                      # keep some context
        cx = (x0 + x1) / 2; x0, x1 = max(0, cx - 260), min(1920, cx + 260)
    d = ImageDraw.Draw(shot)
    for it in items:
        if not it["box"]:
            continue
        x, y, w, h = [v * S for v in it["box"]]
        d.rectangle([x - 4, y - 4, x + w + 4, y + h + 4], outline=it["color"], width=int(3 * S))
    placed, r = [], int(13 * S)
    for it in items:                                         # badges on top of all rectangles, never on top of each other
        if it["box"]:
            x, y = it["box"][0] * S - 2, it["box"][1] * S - 2
            while any(abs(x - px) < 2.2 * r and abs(y - py) < 2.2 * r for px, py in placed):
                x += 2.4 * r
            placed.append((x, y))
            badge(d, x, y, r, it["n"], it["color"])
    left = shot.crop((int(x0 * S), int(y0 * S), int(x1 * S), int(y1 * S)))

    # right panel: YAML lines
    fs = 26; f = ImageFont.truetype(MONO, fs); fb = ImageFont.truetype(MONO_B, fs)
    indent = min(len(it["text"]) - len(it["text"].lstrip()) for it in items)
    rows = []
    for it in items:
        t = shorten(it["text"][indent:], a.maxlen * 2)
        ind = len(t) - len(t.lstrip()) + 2
        parts = textwrap.wrap(t, a.maxlen, subsequent_indent=" " * ind, drop_whitespace=False, break_on_hyphens=False) or [t]
        parts[0] = t[:len(parts[0])]                        # keep the real leading indent
        rows.append((it, parts))
    lh = int(fs * 1.45)
    rw = int(max(f.getlength(x) for _, ps in rows for x in ps) + 190)
    rh = sum(lh * len(ps) + 16 for _, ps in rows) + 90
    right = Image.new("RGB", (rw, rh), "#1e1e2e")
    rd = ImageDraw.Draw(right)
    rd.text((24, 18), f"{a.snap.split('/')[-1]}  (line: text)", fill="#9aa0b4", font=f)
    y = 70
    for it, ps in rows:
        badge(rd, 36, y + lh // 2, 18, it["n"], it["color"])
        rd.text((64, y + 4), f"{it['line_no']:>4}", fill="#7f849c", font=f)
        rd.rectangle([140, y, 146, y + lh * len(ps)], fill=it["color"])
        for k, x in enumerate(ps):
            rd.text((160, y + 4 + k * lh), x, fill="#f5f5f5", font=fb if it["box"] else f)
        y += lh * len(ps) + 16

    # compose: scale left to a sensible height, right keeps its size
    H = max(right.height, 760)
    lw = int(left.width * H / left.height)
    if lw + right.width > a.width * 1.6:
        lw = int(a.width * 1.6 - right.width); H2 = int(left.height * lw / left.width)
    else:
        H2 = H
    left = left.resize((lw, H2), Image.LANCZOS)
    title_h = 64
    W = lw + right.width + 30
    canvas = Image.new("RGB", (W, max(H2, right.height) + title_h + 10), "white")
    cd = ImageDraw.Draw(canvas)
    cd.text((16, 14), a.title, fill="#1a237e", font=ImageFont.truetype(SANS_B, 30))
    canvas.paste(left, (0, title_h))
    cd.rectangle([0, title_h, lw - 1, title_h + H2 - 1], outline="#90a4ae", width=2)
    canvas.paste(right, (lw + 30, title_h))
    if canvas.width > a.width:
        canvas = canvas.resize((a.width, int(canvas.height * a.width / canvas.width)), Image.LANCZOS)
    canvas.quantize(colors=200, method=Image.Quantize.MEDIANCUT).save(a.out, optimize=True)
    for it in items:
        print(f"# {it['n']}  line {it['line_no']}: {it['text'].strip()[:150]}")


if __name__ == "__main__":
    main()
