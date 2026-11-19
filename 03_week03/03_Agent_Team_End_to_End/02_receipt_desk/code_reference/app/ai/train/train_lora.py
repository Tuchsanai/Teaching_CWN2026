#!/usr/bin/env python3
"""LoRA fine-tuning of the ReceiptDesk Vision-Language model (receipt image -> 5-field JSON).

The same command line works on 1 GPU and on 2 GPUs. Only the launcher changes:

    # 1 GPU
    python ai/train/train_lora.py  --train-file data/train.jsonl --eval-file data/val.jsonl --output-dir runs/r1
    # 2 GPUs (DDP), identical arguments
    torchrun --standalone --nproc_per_node 2 ai/train/train_lora.py  --train-file ... --output-dir runs/r1
    accelerate launch --num_processes 2       ai/train/train_lora.py  --train-file ... --output-dir runs/r1
    # CPU-only smoke test (tiny offline random VLM + synthetic receipts, no download, no GPU)
    python ai/train/train_lora.py --dry-run
    torchrun --nproc_per_node 2 ai/train/train_lora.py --dry-run      # 2 CPU processes (gloo DDP)

``--global-batch-size`` is the effective batch per optimizer step. Gradient accumulation is derived as
global / (per-device batch x number of processes), so 1 GPU and 2 GPUs train with the same effective
batch, learning-rate schedule and number of optimizer steps — 2 GPUs just finish sooner.

Data: JSONL, one receipt per line (see receipt_common.load_jsonl). Readable receipts carry the 5
ground-truth fields, unreadable ones (blurred / cut off) carry ``"unreadable": true`` and teach the model
to answer ``{"unreadable": true}`` instead of guessing a total (NFR-01 M5).

Output (``--output-dir``): the LoRA adapter + processor + ``receiptdesk_train_meta.json``. Serve it with
``vllm serve <base> --enable-lora --lora-modules receipt-vlm=<output-dir>`` or merge it with
``--merge-output DIR`` and serve the merged weights as ``--served-model-name receipt-vlm``.
Then gate the model with ``ai/train/evaluate.py`` (M1–M6 must all pass).
"""

from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import logging
import math
import os
import sys
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import receipt_common as rc  # noqa: E402

LOG = logging.getLogger("train_lora")
DEFAULT_MODEL = "Qwen/Qwen2.5-VL-7B-Instruct"

# LoRA on the language model only (vision tower stays frozen and un-adapted) — matches names in both
# transformers 4.x (model.layers.N...) and 5.x (model.language_model.layers.N...).
LORA_TARGETS = {
    "language": r"^(?!.*(?:visual|vision)).*\.(?:q_proj|k_proj|v_proj|o_proj|gate_proj|up_proj|down_proj)$",
    "all": r"^(?!.*lm_head).*\.(?:q_proj|k_proj|v_proj|o_proj|gate_proj|up_proj|down_proj|qkv|attn\.proj|fc1|fc2)$",
}


# ----------------------------------------------------------------------------------------------
# Arguments
# ----------------------------------------------------------------------------------------------
def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = p.add_argument_group("data / model")
    g.add_argument("--model", default=DEFAULT_MODEL, help="HF id or local path of the base VLM")
    g.add_argument("--train-file", help="training JSONL")
    g.add_argument("--eval-file", help="validation JSONL (loss only; use evaluate.py for M1–M6)")
    g.add_argument("--output-dir", default=str(Path(__file__).resolve().parent / "runs" / "receipt-lora"))
    g.add_argument("--image-max-side", type=int, default=1600, help="downscale so the longest side <= this")
    g.add_argument("--min-pixels", type=int, default=256 * 28 * 28, help="Qwen-VL processor min_pixels")
    g.add_argument("--max-pixels", type=int, default=1280 * 28 * 28, help="Qwen-VL processor max_pixels")
    g.add_argument("--attn-implementation", default="sdpa", help="sdpa | flash_attention_2 | eager")

    g = p.add_argument_group("optimisation (identical meaning on 1 or 2 GPUs)")
    g.add_argument("--epochs", type=float, default=3.0)
    g.add_argument("--max-steps", type=int, default=-1, help=">0 overrides --epochs")
    g.add_argument("--global-batch-size", type=int, default=16, help="effective batch per optimizer step")
    g.add_argument("--per-device-batch-size", type=int, default=1)
    g.add_argument("--learning-rate", type=float, default=1e-4)
    g.add_argument("--weight-decay", type=float, default=0.0)
    g.add_argument("--warmup-ratio", type=float, default=0.03)
    g.add_argument("--lr-scheduler", default="cosine")
    g.add_argument("--precision", choices=["auto", "bf16", "fp16", "fp32"], default="auto")
    g.add_argument("--no-gradient-checkpointing", dest="gradient_checkpointing", action="store_false")
    g.add_argument("--load-in-4bit", action="store_true", help="QLoRA (needs bitsandbytes)")
    g.add_argument("--seed", type=int, default=42)
    g.add_argument("--num-workers", type=int, default=2, help="dataloader workers per process")
    g.add_argument("--logging-steps", type=int, default=10)
    g.add_argument("--save-steps", type=int, default=0, help="0 = save/eval once per epoch")
    g.add_argument("--save-total-limit", type=int, default=2)
    g.add_argument("--resume", action="store_true", help="resume from the last checkpoint in --output-dir")
    g.add_argument("--report-to", default="none", help="none | tensorboard | wandb ...")

    g = p.add_argument_group("LoRA")
    g.add_argument("--lora-r", type=int, default=16)
    g.add_argument("--lora-alpha", type=int, default=32)
    g.add_argument("--lora-dropout", type=float, default=0.05)
    g.add_argument("--lora-target", default="language",
                   help="'language' (default), 'all' (also vision tower) or a regex over module names")

    g = p.add_argument_group("export / smoke test")
    g.add_argument("--merge-output", help="also write base+LoRA merged weights here (for plain vLLM serving)")
    g.add_argument("--dry-run", action="store_true",
                   help="CPU smoke test: tiny offline random VLM + synthetic receipts, a few steps")
    args = p.parse_args(argv)

    if args.dry_run:
        if args.max_steps <= 0:
            args.max_steps = 3
        if args.global_batch_size == 16:
            args.global_batch_size = 4
        args.precision = "fp32"
        args.num_workers = 0
        args.logging_steps = 1
        args.save_total_limit = 1
        args.image_max_side = 320
        args.min_pixels, args.max_pixels = 56 * 56, 224 * 308
        args.attn_implementation = "sdpa"
        args.load_in_4bit = False
    elif not args.train_file:
        p.error("--train-file is required (or use --dry-run)")
    return args


def dist_info() -> tuple[int, int, int]:
    """(world_size, rank, local_rank) as set by torchrun / accelerate launch; 1 process otherwise."""
    return (int(os.environ.get("WORLD_SIZE", 1)), int(os.environ.get("RANK", 0)),
            int(os.environ.get("LOCAL_RANK", 0)))


def grad_accum_steps(global_bs: int, per_device_bs: int, world: int) -> int:
    per_step = per_device_bs * world
    if global_bs < per_step or global_bs % per_step:
        raise SystemExit(
            f"--global-batch-size {global_bs} must be a multiple of per-device {per_device_bs} x "
            f"{world} process(es) = {per_step}. Pick a value divisible by both 1- and 2-GPU layouts "
            f"(e.g. 16) so the same arguments work on 1 and 2 GPUs."
        )
    return global_bs // per_step


def _filter_kwargs(fn, kwargs: dict[str, Any]) -> dict[str, Any]:
    params = inspect.signature(fn).parameters
    return {k: v for k, v in kwargs.items() if k in params}


# ----------------------------------------------------------------------------------------------
# Data
# ----------------------------------------------------------------------------------------------
class ReceiptDataset:
    """Map-style dataset: JSONL row -> {"image", "prompt_text", "full_text"} (chat template applied)."""

    def __init__(self, rows: list[dict[str, Any]], processor, image_max_side: int):
        self.rows = rows
        self.image_max_side = image_max_side
        self.prompt_text = processor.apply_chat_template(
            rc.build_messages(), tokenize=False, add_generation_prompt=True)
        self.processor = processor

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, idx: int) -> dict[str, Any]:
        row = self.rows[idx]
        full_text = self.processor.apply_chat_template(
            rc.build_messages(rc.target_text(row)), tokenize=False, add_generation_prompt=False)
        if not full_text.startswith(self.prompt_text):
            raise ValueError("chat template: prompt is not a prefix of prompt+answer; "
                             "this model family needs a custom collator")
        return {"image": rc.load_image(row["image"], self.image_max_side),
                "prompt_text": self.prompt_text, "full_text": full_text}


class ReceiptCollator:
    """Batch images + texts through the processor; loss only on the assistant answer (+ end token)."""

    def __init__(self, processor):
        self.processor = processor
        self.tok = processor.tokenizer
        self.tok.padding_side = "right"
        if self.tok.pad_token is None:
            self.tok.pad_token = self.tok.eos_token

    def __call__(self, batch: list[dict[str, Any]]) -> dict[str, Any]:
        import torch

        enc = self.processor(text=[b["full_text"] for b in batch], images=[b["image"] for b in batch],
                             padding=True, return_tensors="pt")
        labels = enc["input_ids"].clone()
        labels[enc["attention_mask"] == 0] = -100
        for i, b in enumerate(batch):
            suffix = b["full_text"][len(b["prompt_text"]):]
            suffix_ids = self.tok(suffix, add_special_tokens=False)["input_ids"]
            length = int(enc["attention_mask"][i].sum())
            start = length - len(suffix_ids)
            if start <= 0 or enc["input_ids"][i, start:length].tolist() != suffix_ids:
                # tokenizer merged across the prompt/answer boundary: measure the prompt directly
                start = self.processor(text=[b["prompt_text"]], images=[b["image"]],
                                       return_tensors="pt")["input_ids"].shape[1]
            labels[i, :start] = -100
        enc["labels"] = labels
        if not torch.any(labels != -100):
            raise ValueError("batch has no supervised tokens")
        return dict(enc)


# ----------------------------------------------------------------------------------------------
# Model
# ----------------------------------------------------------------------------------------------
def resolve_dtype(precision: str):
    import torch

    if precision == "auto":
        if torch.cuda.is_available():
            return torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
        return torch.float32
    return {"bf16": torch.bfloat16, "fp16": torch.float16, "fp32": torch.float32}[precision]


def load_processor(model_path: str, args: argparse.Namespace):
    from transformers import AutoProcessor

    try:  # Qwen-VL family bounds the number of visual tokens with min/max_pixels
        return AutoProcessor.from_pretrained(model_path, min_pixels=args.min_pixels,
                                             max_pixels=args.max_pixels, trust_remote_code=True)
    except (TypeError, ValueError):
        return AutoProcessor.from_pretrained(model_path, trust_remote_code=True)


def load_base_model(model_path: str, args: argparse.Namespace, dtype, local_rank: int, for_training: bool):
    import transformers

    try:
        from transformers import AutoModelForImageTextToText as AutoVLM
    except ImportError:  # transformers < 4.46
        from transformers import AutoModelForVision2Seq as AutoVLM

    kwargs: dict[str, Any] = {"trust_remote_code": True, "attn_implementation": args.attn_implementation}
    major = int(transformers.__version__.split(".")[0])
    kwargs["dtype" if major >= 5 else "torch_dtype"] = dtype
    if args.load_in_4bit and for_training:
        import torch
        from transformers import BitsAndBytesConfig

        kwargs["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=dtype)
        kwargs["device_map"] = {"": local_rank if torch.cuda.is_available() else "cpu"}
    model = AutoVLM.from_pretrained(model_path, **kwargs)
    for cfg in (model.config, getattr(model.config, "text_config", None)):
        if cfg is not None and for_training:
            cfg.use_cache = False
    return model


def add_lora(model, args: argparse.Namespace):
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

    if args.load_in_4bit:
        model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=args.gradient_checkpointing)
    target = LORA_TARGETS.get(args.lora_target, args.lora_target)
    config = LoraConfig(r=args.lora_r, lora_alpha=args.lora_alpha, lora_dropout=args.lora_dropout,
                        target_modules=target, bias="none", task_type="CAUSAL_LM")
    model = get_peft_model(model, config)
    if args.gradient_checkpointing:
        model.enable_input_require_grads()
    return model


# ----------------------------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------------------------
def prepare_dry_run(args: argparse.Namespace) -> None:
    """Build the tiny offline model and synthetic data under <output-dir>/_dryrun (rank 0 only)."""
    base = Path(args.output_dir) / "_dryrun"
    args.model = str(rc.build_tiny_vlm(base / "tiny-model", seed=args.seed))
    data = base / "data"
    if not (data / "train.jsonl").exists():
        rc.write_synthetic_dataset(data, n=16, n_unreadable=2, seed=1, name="train")
        rc.write_synthetic_dataset(data, n=4, n_unreadable=1, seed=2, name="val")
    args.train_file, args.eval_file = str(data / "train.jsonl"), str(data / "val.jsonl")


def prompt_fingerprint() -> str:
    return hashlib.sha256((rc.SYSTEM_PROMPT + "\n" + rc.USER_PROMPT).encode()).hexdigest()[:16]


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    world, rank, local_rank = dist_info()
    logging.basicConfig(level=logging.INFO if rank == 0 else logging.WARNING,
                        format=f"%(asctime)s [rank{rank}] %(levelname)s %(message)s")
    import torch
    from transformers import Trainer, TrainingArguments, set_seed

    accum = grad_accum_steps(args.global_batch_size, args.per_device_batch_size, world)
    dtype = resolve_dtype(args.precision)
    use_cpu = args.dry_run or not torch.cuda.is_available()
    if use_cpu and not args.dry_run:
        LOG.warning("CUDA not available: training on CPU (only sensible for tiny models)")
    if not use_cpu and world > torch.cuda.device_count():
        raise SystemExit(f"{world} processes but only {torch.cuda.device_count()} visible GPU(s)")

    strategy = "steps" if args.max_steps > 0 or args.save_steps > 0 else "epoch"
    has_eval = bool(args.eval_file) or args.dry_run
    every = args.save_steps if args.save_steps > 0 else max(args.max_steps, 1)
    ta_kwargs = dict(
        output_dir=args.output_dir,
        per_device_train_batch_size=args.per_device_batch_size,
        per_device_eval_batch_size=args.per_device_batch_size,
        gradient_accumulation_steps=accum,
        num_train_epochs=args.epochs,
        max_steps=args.max_steps,
        learning_rate=args.learning_rate,
        weight_decay=args.weight_decay,
        lr_scheduler_type=args.lr_scheduler,
        warmup_ratio=args.warmup_ratio,
        logging_steps=args.logging_steps,
        logging_first_step=True,
        save_strategy=strategy,
        save_steps=every,
        save_total_limit=args.save_total_limit,
        save_only_model=False,
        eval_steps=every,
        eval_strategy=strategy if has_eval else "no",
        evaluation_strategy=strategy if has_eval else "no",  # transformers 4.x name (filtered if unknown)
        bf16=dtype == torch.bfloat16 and not use_cpu,
        fp16=dtype == torch.float16 and not use_cpu,
        use_cpu=use_cpu,
        gradient_checkpointing=args.gradient_checkpointing,
        gradient_checkpointing_kwargs={"use_reentrant": False},
        ddp_find_unused_parameters=False,
        ddp_backend="gloo" if use_cpu and world > 1 else None,
        remove_unused_columns=False,  # keep image fields for the collator
        dataloader_num_workers=args.num_workers,
        report_to=args.report_to,
        seed=args.seed,
    )
    params = inspect.signature(TrainingArguments.__init__).parameters
    if "warmup_ratio" not in params:  # transformers >= 5: warmup_steps < 1 is a ratio
        ta_kwargs["warmup_steps"] = ta_kwargs.pop("warmup_ratio")
    training_args = TrainingArguments(**_filter_kwargs(TrainingArguments.__init__, ta_kwargs))
    set_seed(args.seed)

    with training_args.main_process_first(desc="prepare data/model", local=False):
        if args.dry_run:
            prepare_dry_run(args)
        processor = load_processor(args.model, args)
        train_rows = rc.load_jsonl(args.train_file)
        eval_rows = rc.load_jsonl(args.eval_file) if args.eval_file else []

    if has_eval and not eval_rows:
        raise SystemExit(f"--eval-file {args.eval_file} has no rows")

    n_unread = sum(r["unreadable"] for r in train_rows)
    LOG.info("processes=%d  per-device batch=%d  grad-accum=%d  -> global batch=%d",
             world, args.per_device_batch_size, accum, args.per_device_batch_size * accum * world)
    LOG.info("train=%d receipts (%d unreadable)  eval=%d  base=%s  dtype=%s  device=%s",
             len(train_rows), n_unread, len(eval_rows), args.model, dtype, "cpu" if use_cpu else "cuda")

    model = load_base_model(args.model, args, dtype, local_rank, for_training=True)
    model = add_lora(model, args)
    if rank == 0:
        model.print_trainable_parameters()

    train_ds = ReceiptDataset(train_rows, processor, args.image_max_side)
    eval_ds = ReceiptDataset(eval_rows, processor, args.image_max_side) if has_eval else None
    trainer = Trainer(model=model, args=training_args, train_dataset=train_ds, eval_dataset=eval_ds,
                      data_collator=ReceiptCollator(processor))
    t0 = time.time()
    result = trainer.train(resume_from_checkpoint=True if args.resume else None)
    elapsed = time.time() - t0
    metrics = dict(result.metrics)
    if has_eval:
        metrics.update(trainer.evaluate())

    trainer.save_model(args.output_dir)  # LoRA adapter only (rank 0 writes)
    if trainer.is_world_process_zero():
        processor.save_pretrained(args.output_dir)
        meta = {
            "base_model": args.model if not args.dry_run else "tiny-random-qwen2-vl (dry-run)",
            "served_model_name": rc.SERVED_MODEL_NAME,
            "prompt_sha256_16": prompt_fingerprint(),
            "system_prompt": rc.SYSTEM_PROMPT,
            "user_prompt": rc.USER_PROMPT,
            "world_size": world,
            "gradient_accumulation_steps": accum,
            "global_batch_size": args.global_batch_size,
            "train_receipts": len(train_rows),
            "train_seconds": round(elapsed, 1),
            "metrics": metrics,
            "args": {k: v for k, v in vars(args).items()},
        }
        Path(args.output_dir, "receiptdesk_train_meta.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        LOG.info("saved LoRA adapter to %s  (%.1fs, train_loss=%s)", args.output_dir, elapsed,
                 metrics.get("train_loss"))

        if args.merge_output:
            merge_adapter(args, dtype)
        if args.dry_run:
            smoke_generate(args, processor, eval_rows or train_rows)

    if world > 1 and torch.distributed.is_available() and torch.distributed.is_initialized():
        torch.distributed.barrier()
    return 0


def merge_adapter(args: argparse.Namespace, dtype) -> None:
    """Reload the base in full precision (not 4-bit) and fold the adapter in, for plain vLLM serving."""
    from peft import PeftModel

    args_noq = argparse.Namespace(**{**vars(args), "load_in_4bit": False})
    base = load_base_model(args.model, args_noq, dtype, 0, for_training=False)
    merged = PeftModel.from_pretrained(base, args.output_dir).merge_and_unload()
    merged.save_pretrained(args.merge_output)
    load_processor(args.output_dir, args).save_pretrained(args.merge_output)
    LOG.info("merged model written to %s (serve with --served-model-name %s)",
             args.merge_output, rc.SERVED_MODEL_NAME)


def smoke_generate(args: argparse.Namespace, processor, rows: list[dict[str, Any]]) -> None:
    """Dry-run only: reload base + saved adapter from disk and generate once (proves the adapter loads)."""
    import torch
    from peft import PeftModel

    base = load_base_model(args.model, args, torch.float32, 0, for_training=False)
    model = PeftModel.from_pretrained(base, args.output_dir).eval()
    processor.tokenizer.padding_side = "left"
    prompt = processor.apply_chat_template(rc.build_messages(), tokenize=False, add_generation_prompt=True)
    enc = processor(text=[prompt], images=[rc.load_image(rows[0]["image"], args.image_max_side)],
                    return_tensors="pt")
    with torch.no_grad():
        out = model.generate(**enc, max_new_tokens=16, do_sample=False)
    text = processor.tokenizer.decode(out[0, enc["input_ids"].shape[1]:], skip_special_tokens=True)
    parsed = rc.parse_model_output(text)
    LOG.info("dry-run smoke generate OK (random weights, so output is noise): %r -> valid=%s",
             text[:60], parsed.valid)
    LOG.info("DRY-RUN PASSED: LoRA trained %d step(s) on CPU, adapter saved and reloaded from %s",
             args.max_steps, args.output_dir)


if __name__ == "__main__":
    sys.exit(main())
