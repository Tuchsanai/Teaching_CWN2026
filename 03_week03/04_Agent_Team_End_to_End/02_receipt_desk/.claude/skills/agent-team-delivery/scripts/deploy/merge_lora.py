"""Step 11 · merge the best LoRA (2-GPU run) into Qwen3-VL-2B-Instruct so vLLM serves one plain model.
Run on the GPU machine with the vLLM venv:  python merge_lora.py <base> <lora> <out>"""
import shutil, sys
from pathlib import Path
import torch
from peft import PeftModel
from transformers import AutoModelForImageTextToText, AutoProcessor

base, lora, out = sys.argv[1:4]
model = AutoModelForImageTextToText.from_pretrained(base, torch_dtype=torch.bfloat16)
model = PeftModel.from_pretrained(model, lora).merge_and_unload()
model.save_pretrained(out, safe_serialization=True)
AutoProcessor.from_pretrained(base).save_pretrained(out)
for name in ("chat_template.jinja", "generation_config.json", "preprocessor_config.json", "video_preprocessor_config.json"):
    if (Path(base) / name).exists() and not (Path(out) / name).exists():
        shutil.copy(Path(base) / name, Path(out) / name)
print("MERGED", out)
