"""Build dataset_samples.jpg: 6 CORD-v2 test receipts, each paired with its simplified ground-truth JSON."""
import json, os
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.dirname(HERE)
gt = json.load(open(os.path.join(HERE, "gt_samples.json")))

def simplify(p):
    menu = p.get("menu", [])
    menu = menu if isinstance(menu, list) else [menu]
    items = [[m.get("nm"), m.get("cnt"), m.get("price")] for m in menu]
    st, tt = p.get("sub_total", {}), p.get("total", {})
    return {"items": items, "subtotal": st.get("subtotal_price"),
            "tax": st.get("tax_price"), "total": tt.get("total_price")}

def render(sp):
    out = ["# items = [name, qty, price]", "{", ' "items": [']
    out += ["  " + json.dumps(i, ensure_ascii=False) + ("," if n < len(sp["items"]) - 1 else "") for n, i in enumerate(sp["items"])]
    out += [" ],"] + [f' "{f}": {json.dumps(sp[f])}' + ("," if f != "total" else "") for f in ("subtotal", "tax", "total")] + ["}"]
    return out

FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
mono = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 17)
bold = ImageFont.truetype(FB, 24)
IMG_H, TXT_W, PAD, HEAD, WRAP = 640, 520, 24, 44, 45
cells = []
for k in sorted(gt):
    im = Image.open(os.path.join(LAB, "samples", f"{k}.jpg")).convert("RGB")
    im = im.resize((int(im.width * IMG_H / im.height), IMG_H))
    sp = simplify(gt[k]["gt_parse"])
    lines = []
    for ln in render(sp):
        while len(ln) > WRAP: lines.append(ln[:WRAP]); ln = "    " + ln[WRAP:]
        lines.append(ln)
    w = im.width + TXT_W + 3 * PAD
    c = Image.new("RGB", (w, IMG_H + HEAD + 2 * PAD), "white")
    d = ImageDraw.Draw(c)
    n = len(sp["items"])
    d.text((PAD, 10), f"{k}  (test index {int(k[5:])}, {n} item{'s' if n > 1 else ''})", font=bold, fill="#1f2937")
    c.paste(im, (PAD, HEAD + PAD))
    d.rectangle([im.width + 2 * PAD - 8, HEAD + PAD, w - PAD, HEAD + PAD + IMG_H], fill="#f3f4f6", outline="#d1d5db")
    y = HEAD + PAD + 12
    for ln in lines:
        col = "#6b7280" if ln.startswith("#") else "#065f46" if '"total"' in ln else "#111827"
        d.text((im.width + 2 * PAD, y), ln, font=mono, fill=col); y += 24
    cells.append(c)
COLS = 3
cw = max(c.width for c in cells); ch = cells[0].height
title_h = 70
grid = Image.new("RGB", (cw * COLS + 8, title_h + ch * 2 + 8), "white")
ImageDraw.Draw(grid).text((PAD, 18), "CORD-v2 test set: receipt image + ground-truth JSON (items: name, qty, price | subtotal | tax | total)",
                          font=ImageFont.truetype(FB, 30), fill="#111827")
for i, c in enumerate(cells):
    grid.paste(c, ((i % COLS) * cw + 4, title_h + (i // COLS) * ch + 4))
grid.save(os.path.join(HERE, "dataset_samples.jpg"), quality=90)
print(grid.size)
