"""LAB 9 step 3: time SDXL-Turbo text-to-image on one GPU (512x512, 4 steps) for batch sizes 1, 2, 4, 8."""
import json, os, sys, time
import torch
from diffusers import AutoPipelineForText2Image

MODEL = "stabilityai/sdxl-turbo"
SIZE, STEPS, REPEATS = 512, 4, 3
PROMPTS = [l.strip() for l in open(sys.argv[1]) if l.strip()] if len(sys.argv) > 1 else ["a red lighthouse on a cliff at sunset"] * 8

pipe = AutoPipelineForText2Image.from_pretrained(MODEL, torch_dtype=torch.float16, variant="fp16").to("cuda:0")
pipe.set_progress_bar_config(disable=True)

def gen(prompts, seed=0):
    g = torch.Generator("cuda:0").manual_seed(seed)
    return pipe(prompt=prompts, num_inference_steps=STEPS, guidance_scale=0.0,
                height=SIZE, width=SIZE, generator=g).images

gen(PROMPTS[:1]); gen(PROMPTS[:8])  # warm-up (CUDA kernels, memory)
rows = []
for bs in (1, 2, 4, 8):
    batch = (PROMPTS * 8)[:bs]
    times = []
    for r in range(REPEATS):
        torch.cuda.synchronize(); t = time.perf_counter()
        gen(batch, seed=r)
        torch.cuda.synchronize(); times.append(time.perf_counter() - t)
    t = sorted(times)[len(times) // 2]  # median
    rows.append({"batch": bs, "sec_per_batch": round(t, 3), "sec_per_image": round(t / bs, 3),
                 "images_per_sec": round(bs / t, 2), "peak_vram_gb": round(torch.cuda.max_memory_allocated(0) / 1e9, 2)})
    print(rows[-1], flush=True)

out = {"model": MODEL, "gpu": torch.cuda.get_device_name(0), "size": SIZE, "steps": STEPS,
       "repeats": REPEATS, "torch": torch.__version__, "results": rows}
json.dump(out, open("bench_single_gpu.json", "w"), indent=2)
