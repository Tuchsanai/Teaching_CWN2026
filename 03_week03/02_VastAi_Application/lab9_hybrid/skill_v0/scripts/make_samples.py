"""LAB 9 step 4: generate the first 6 prompts and lay them out as one captioned grid (3 x 2)."""
import io, json, sys, textwrap, time
import torch
from diffusers import AutoPipelineForText2Image
from PIL import Image, ImageDraw, ImageFont

prompts = [l.strip() for l in open("prompts.txt") if l.strip()][:6]
pipe = AutoPipelineForText2Image.from_pretrained("stabilityai/sdxl-turbo", torch_dtype=torch.float16, variant="fp16").to("cuda:0")
pipe.set_progress_bar_config(disable=True)
g = torch.Generator("cuda:0").manual_seed(42)
imgs = pipe(prompt=prompts, num_inference_steps=4, guidance_scale=0.0, height=512, width=512, generator=g).images

# one sample "job": what goes in, what comes out
t = time.perf_counter()
one = pipe(prompt=prompts[2], num_inference_steps=4, guidance_scale=0.0, height=512, width=512,
           generator=torch.Generator("cuda:0").manual_seed(7)).images[0]
sec = time.perf_counter() - t
buf = io.BytesIO(); one.save(buf, format="PNG"); one.save("example_job.png")
json.dump({"job_in": {"prompt": prompts[2], "width": 512, "height": 512, "steps": 4, "seed": 7},
           "job_out": {"format": "PNG", "size_px": list(one.size), "bytes": buf.tell(), "gen_sec": round(sec, 3)}},
          open("example_job.json", "w"), indent=2)

COLS, CELL, CAP, PAD = 3, 512, 70, 12
font = None
for f in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",):
    try: font = ImageFont.truetype(f, 20)
    except OSError: pass
font = font or ImageFont.load_default(size=20)
rows = (len(imgs) + COLS - 1) // COLS
W = COLS * CELL + (COLS + 1) * PAD; H = rows * (CELL + CAP) + (rows + 1) * PAD
grid = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(grid)
for i, (im, p) in enumerate(zip(imgs, prompts)):
    x = PAD + (i % COLS) * (CELL + PAD); y = PAD + (i // COLS) * (CELL + CAP + PAD)
    grid.paste(im, (x, y))
    d.multiline_text((x + 4, y + CELL + 6), "\n".join(textwrap.wrap(f"{i+1}. {p}", 46)[:2]), fill="black", font=font, spacing=4)
grid.save("dataset_samples.jpg", quality=90)
print("done", grid.size)
