"""On the rented machine: download Qwen/Qwen3-VL-2B-Instruct + naver-clova-ix/cord-v2 from Hugging Face,
count receipts per split, and write counts.json. HF token (if any) comes from the HF cache file, never printed."""
import json, os, time
from huggingface_hub import snapshot_download
from datasets import load_dataset

ROOT = "/workspace/e2e_receipt"
t0 = time.time()
mdir = snapshot_download("Qwen/Qwen3-VL-2B-Instruct", local_dir=f"{ROOT}/models/Qwen3-VL-2B-Instruct")
msize = sum(os.path.getsize(os.path.join(d, f)) for d, _, fs in os.walk(mdir) for f in fs) / 1e9
print(f"model done: {mdir} {msize:.2f} GB in {time.time()-t0:.0f}s", flush=True)

t1 = time.time()
ddir = snapshot_download("naver-clova-ix/cord-v2", repo_type="dataset", local_dir=f"{ROOT}/data/cord-v2")
ds = load_dataset(ddir)
print(ds, flush=True)
names = {"train": "Training", "validation": "Validation", "test": "Test"}
counts = {names.get(k, k): len(v) for k, v in ds.items()}
dsize = sum(os.path.getsize(os.path.join(d, f)) for d, _, fs in os.walk(ddir) for f in fs) / 1e9
out = {"model": "Qwen/Qwen3-VL-2B-Instruct", "model_dir": mdir, "model_size_gb": round(msize, 2),
       "dataset": "naver-clova-ix/cord-v2", "dataset_dir": ddir, "dataset_size_gb": round(dsize, 2),
       "columns": ds["train"].column_names, "counts": counts, "total": sum(counts.values()),
       "seconds": round(time.time() - t0)}
json.dump(out, open(f"{ROOT}/counts.json", "w"), indent=1)
print(json.dumps(out, indent=1))
print("ALL_DONE", flush=True)
