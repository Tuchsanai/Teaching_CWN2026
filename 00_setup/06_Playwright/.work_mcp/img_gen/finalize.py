#!/usr/bin/env python3
"""chosen.txt: '<name.png> <version>' → 01_playwright-mcp/img/<name.png> (1536px wide, 256-color palette) + compare/crop images."""
import shutil, glob, os
from PIL import Image
DST = "../../01_playwright-mcp/img"; os.makedirs(DST, exist_ok=True)
for line in open("chosen.txt"):
    if not line.strip(): continue
    name, ver = line.split()
    im = Image.open(f"raw/{name[:-4]}.{ver}.png").convert("RGB")
    if im.width > 1600: im = im.resize((1600, int(im.height * 1600 / im.width)), Image.LANCZOS)
    im.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(f"{DST}/{name}", optimize=True)
for f in glob.glob("../img_tools/cmp/*.png"):
    shutil.copy(f, DST)
for f in sorted(os.listdir(DST)): print(f, os.path.getsize(f"{DST}/{f}"))
