# ai/train · LoRA fine-tuning + evaluation of the receipt VLM (block B10)

| File | What it does |
|---|---|
| `train_lora.py` | LoRA fine-tuning of a Vision-Language model (default `Qwen/Qwen2.5-VL-7B-Instruct`). The same arguments work on 1 GPU and on 2 GPUs (torchrun / accelerate). |
| `evaluate.py` | Model gate for NFR-01: M1–M6 must all pass, and M7 is reported only. It uses the same flag rules as the web (BR-04 `< 0.90`, BR-05 `> 1.00` baht). |
| `receipt_common.py` | Code shared with production: the prompt, the 5-field JSON contract, the flag rules, `total_confidence` from logprobs, the data loader, and the synthetic data and tiny model for `--dry-run`. |
| `requirements.txt` | Packages. `evaluate.py --backend vllm/predictions` needs only Python and Pillow. |

## Data (JSONL, one receipt per line, image paths relative to the JSONL file)

```json
{"id": "r0001", "image": "images/r0001.jpg", "merchant": "ร้านตัวอย่าง", "date": "2026-11-18",
 "items": [{"name": "ข้าวสาร 5 กก.", "price": "45.00"}], "total": "100.00"}
{"id": "u01", "image": "images/u01.jpg", "unreadable": true}
```

- Training: put some `unreadable` receipts in the training set (blurred or cut off). The model learns to answer `{"unreadable": true}` instead of guessing (M5).
- Test Set (NFR-01): at least 200 readable receipts that are **not in the training set**, plus at least 20 in the unreadable set. If it is smaller, `evaluate.py` exits with code 2 (pass `--allow-small-test-set` only for trial runs).

## Training · 1 GPU and 2 GPUs with the same arguments

```bash
ARGS="--train-file data/train.jsonl --eval-file data/val.jsonl --output-dir ai/train/runs/r1 \
      --epochs 3 --global-batch-size 16 --per-device-batch-size 1 --learning-rate 1e-4 --lora-r 16"
python  ai/train/train_lora.py $ARGS                                            # 1 GPU
torchrun --standalone --nproc_per_node 2 ai/train/train_lora.py $ARGS           # 2 GPUs (DDP)
accelerate launch --multi_gpu --num_processes 2 ai/train/train_lora.py $ARGS    # 2 GPUs (alternative)
```

- `--global-batch-size` is the effective batch per optimizer step. The script computes `grad_accum = global ÷ (per-device × number of processes)`. With 16, that is 16 on 1 GPU and 8 on 2 GPUs. The step count and LR schedule are identical; 2 GPUs just finish sooner.
- LoRA is applied only to the language model (`q/k/v/o/gate/up/down_proj`). The vision tower is frozen. `--lora-target all` also adapts the vision tower.
- Memory options: gradient checkpointing (on by default), `--load-in-4bit` (QLoRA), and `--max-pixels` to cap the visual tokens.
- Output: the LoRA adapter, the processor, and `receiptdesk_train_meta.json` (prompt hash, world size, loss).

Serving with vLLM (served name `receipt-vlm`, as in DESIGN 5.4):

```bash
vllm serve Qwen/Qwen2.5-VL-7B-Instruct --enable-lora --lora-modules receipt-vlm=ai/train/runs/r1 --port 8001
# or merge once:  train_lora.py ... --merge-output ai/train/runs/r1-merged
vllm serve ai/train/runs/r1-merged --served-model-name receipt-vlm --port 8001
```

## Evaluation (deploy only if exit code = 0)

```bash
# Through NGINX/vLLM on the GPU box (the same request the worker sends; the key comes from an env var)
VLLM_API_KEY=... python ai/train/evaluate.py --test-set data/test.jsonl --unreadable-set data/unreadable.jsonl \
    --backend vllm --vllm-url http://127.0.0.1:8080 --served-model receipt-vlm
# Local transformers model + adapter
python ai/train/evaluate.py --test-set data/test.jsonl --unreadable-set data/unreadable.jsonl \
    --backend hf --model Qwen/Qwen2.5-VL-7B-Instruct --adapter ai/train/runs/r1
# Score results collected elsewhere ({"id","output","total_confidence"} or {"id","result":{...}})
python ai/train/evaluate.py --test-set ... --backend predictions --predictions preds.jsonl
```

Results go to `eval-out/<time>/report.md`, `report.json` and `predictions.jsonl`. Exit codes: `0` = M1–M6 all pass, `1` = gate failed, `2` = run incomplete (requests failed or Test Set too small).

How each receipt is counted (same routing as production, DESIGN 6.3):

- An answer that is not a complete 5-field JSON, or that says `{"unreadable": true}`, counts as a failed read. It goes to the "อ่านไม่ได้" pile and a person types the receipt in, so it is **not** a silent error. It counts toward the M3 numerator and toward M4, the same as a flag (conservative for M4).
- A complete answer gets flags from BR-04 and BR-05. A receipt with both flags counts as 1 flagged receipt.
- "Total correct" means the model's total, rounded to 2 decimal places (half-up), equals the true total exactly. Comparison is in satang.
- `total_confidence` is missing → treated as "not sure" (flagged).
- `--attempts 3` re-asks after an invalid answer, as BR-07 does (default 1; never more than 3).
- `--sweep` reports M2–M5 at other thresholds, to help answer DESIGN D-02. The gate always uses 0.90 and 1.00.

## Contract with the GPU worker (must match training)

- Prompt: `receipt_common.SYSTEM_PROMPT` + `USER_PROMPT`, with the image placed before the text. Its hash is in `receiptdesk_train_meta.json`.
- Expected answer: `{"merchant", "date": "YYYY-MM-DD", "items": [{"name", "price": "0.00"}], "total": "0.00"}` or `{"unreadable": true}`. Parse it with `receipt_common.parse_model_output`.
- `total_confidence` = `exp(sum of logprobs of the tokens that overlap the "total" value)`. Use `confidence_from_token_spans(text, spans_from_token_pieces([(bytes, logprob), ...]))` with `logprobs: true` from vLLM.

## Dry-run on CPU (no GPU, no model download)

```bash
python3 -m venv .venv && .venv/bin/pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu \
  && .venv/bin/pip install transformers peft accelerate pillow
.venv/bin/python ai/train/train_lora.py --dry-run                                   # 1 process
.venv/bin/torchrun --nproc_per_node 2 ai/train/train_lora.py --dry-run              # 2 processes (gloo), same arguments
python3 ai/train/evaluate.py --dry-run --backend predictions                        # needs no torch
python3 ai/train/evaluate.py --dry-run --backend vllm                               # fake local vLLM server + logprobs
.venv/bin/python ai/train/evaluate.py --dry-run --backend hf                        # tiny random VLM, real generate()
```

- The training dry-run builds a tiny random Qwen2-VL offline. It trains LoRA for 3 steps on 18 synthetic receipts, saves the adapter, then reloads it and generates once.
- The evaluation dry-run first tests the rules against TEST-DATA TD-BR04-a…e and TD-BR05-a…e, plus the boundary examples in the NFR-01 table. It then runs 200+20 synthetic receipts through a scripted model and checks that the counts match exactly (M1 95.5%, M2 0.5%, M3 88.89%, M4 4.5%, M5 0, M6 99.5%).
