#!/usr/bin/env python3
"""page.png crops for README (2x screenshots -> CSS coords * 2)."""
from PIL import Image
R = "ref/runs"; O = "img_tools/cmp"
def save(img, out, width=None):
    if width and img.width > width:
        img = img.resize((width, int(img.height * width / img.width)), Image.LANCZOS)
    img.convert("RGB").quantize(colors=200, method=Image.Quantize.MEDIANCUT).save(f"{O}/{out}", optimize=True)
def crop(src, out, x, y, w, h, width=1600):
    im = Image.open(src); save(im.crop((x*2, y*2, (x+w)*2, (y+h)*2)), out, width)
save(Image.open(f"{R}/lab5/step/page.png"), "lab5-page.png", 1600)
crop(f"{R}/lab5/step/page.png", "lab5-page-crop.png", 370, 200, 800, 310)
save(Image.open(f"{R}/full1/steps/12_results/page.png"), "lab6-results-page.png", 1600)
crop(f"{R}/full1/steps/12_results/page.png", "lab6-results-page-crop.png", 420, 340, 1500, 320)
crop(f"{R}/guardrail/A/steps/01_goal-click/page.png", "lab7-guardA-page-crop.png", 1320, 0, 600, 260, 1200)
crop(f"{R}/guardrail/B/steps/01_goal-click/page.png", "lab7-guardB-page-crop.png", 180, 40, 1400, 440)
