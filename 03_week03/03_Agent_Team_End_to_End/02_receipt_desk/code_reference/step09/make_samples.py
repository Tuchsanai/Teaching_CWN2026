"""On the rented machine: pick 6 Training receipts from CORD-v2 and draw each receipt next to its answer JSON (gt_parse).
Output: /workspace/e2e_receipt/dataset_samples.jpg + samples_info.json (full JSON of every pick)."""
import json, random, textwrap
from datasets import load_dataset
from PIL import Image, ImageDraw, ImageFont

ROOT = "/workspace/e2e_receipt"
ds = load_dataset(f"{ROOT}/data/cord-v2", split="train")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
try:
    font, bold = ImageFont.truetype(FONT, 15), ImageFont.truetype(FONT.replace("Mono.ttf", "Mono-Bold.ttf"), 18)
except OSError:
    font = bold = ImageFont.load_default()

random.seed(9)
idx = list(range(len(ds))); random.shuffle(idx)
picked = []
for i in idx:  # prefer readable receipts: 2-6 menu lines and a total.total_price
    gp = json.loads(ds[i]["ground_truth"])["gt_parse"]
    menu = gp.get("menu", []); menu = menu if isinstance(menu, list) else [menu]
    if 2 <= len(menu) <= 6 and isinstance(gp.get("total"), dict) and "total_price" in gp["total"]:
        picked.append((i, gp))
    if len(picked) == 6:
        break

H, IW, JW = 700, 420, 520          # tile height, receipt width, JSON panel width
grid = Image.new("RGB", (3 * (IW + JW), 2 * H), "white")
for k, (i, gp) in enumerate(picked):
    img = ds[i]["image"].convert("RGB"); img.thumbnail((IW, H - 10))
    tile = Image.new("RGB", (IW + JW, H), "white")
    tile.paste(img, ((IW - img.width) // 2, (H - img.height) // 2))
    d = ImageDraw.Draw(tile)
    d.rectangle([IW, 0, IW + JW - 1, H - 1], fill="#f6f8fa", outline="#999")
    d.text((IW + 10, 8), f"#{k+1}  train[{i}]  gt_parse", font=bold, fill="#0b3d91")
    lines = []
    for ln in json.dumps(gp, ensure_ascii=False, indent=1).splitlines():
        lines += textwrap.wrap(ln, 54, subsequent_indent="    ") or [""]
    y = 36
    for ln in lines:
        if y > H - 24:
            d.text((IW + 10, y), "  ...", font=font, fill="#555"); break
        col = "#c00000" if '"total_price"' in ln else "#111"
        d.text((IW + 10, y), ln, font=font, fill=col); y += 18
    d.rectangle([0, 0, IW + JW - 1, H - 1], outline="#333", width=2)
    grid.paste(tile, ((k % 3) * (IW + JW), (k // 3) * H))
grid.save(f"{ROOT}/dataset_samples.jpg", quality=88)
json.dump([{"no": k + 1, "train_index": i, "image_size": ds[i]["image"].size,
            "ground_truth": json.loads(ds[i]["ground_truth"])} for k, (i, gp) in enumerate(picked)],
          open(f"{ROOT}/samples_info.json", "w"), indent=1, ensure_ascii=False)
print("saved", grid.size, "picked", [i for i, _ in picked])
