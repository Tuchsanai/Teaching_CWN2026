---
name: qlora-chatbot-tune
description: Fine-tune โมเดลเล็ก Qwen3-4B-Instruct-2507 ด้วย QLoRA (4-bit + LoRA rank 8) ให้เป็นพนักงานต้อนรับแชทบอทร้านนวด "สบายใจ" (ตอบข้อมูลร้าน ราคา ส่วนลด จองคิวด้วยแท็ก [BOOKING]) บนเครื่อง GPU ที่เช่าจาก Vast.ai ครบวงจรในคำสั่งเดียว — (เลือกได้) สร้างคำถามลูกค้า + เช่า RTX 5090 เปิดโมเดลครู Qwen3.8 27B ด้วย NInfer ให้ตอบแล้วคัดเป็น Dataset → เช่า RTX 3090 เทรน QLoRA → เปิด AI server vLLM สองโมเดล (qwen3-4b-base / qwen3-4b-sabaijai) → วัดผล Base vs Fine-tuned บน Validation Set → (เลือกได้) เว็บแชทบอท + หน้าเทียบคำตอบ + ชุดทดสอบ 26 เคส → ลบเครื่องและสรุปค่าใช้จ่าย ใช้เมื่อผู้ใช้สั่ง "ใช้สกิล qlora-chatbot-tune", "เทรนโมเดลเล็กให้แชทบอทร้านนวด", "ทำ LAB 3 ซ้ำ", "QLoRA / distill โมเดลครูลงโมเดลเล็ก", "fine-tune Qwen3-4B บน Vast.ai" หรือขอทำซ้ำด้วย GPU / เพดานราคา / ป้ายเครื่อง / โมเดลตั้งต้น / จำนวน Epoch / Dataset ใหม่หรือเดิม / เปิดเว็บหรือไม่ ที่ต่างไปจากเดิม
---

# qlora-chatbot-tune (เวอร์ชัน 0)

ทำซ้ำงานของ LAB 3 (ขั้นที่ 1–8) ในคำสั่งเดียว ทุกงานที่แตะ Vast.ai (ค้นหา เช่า SSH คัดลอกไฟล์ ดูบิล ลบเครื่อง) **ให้ใช้สกิล `vastai`** ใน container `multi-account` (`/root/ai-accounts/.Claude/shared/skills/vastai/SKILL.md`) — อ่านสกิลนั้นก่อนเริ่ม สกิลนี้ไม่สอนวิธีใช้ Vast.ai ซ้ำและไม่แก้สกิล vastai บอกแค่ว่าต้องทำอะไร

โค้ดทั้งหมดใช้ชุดที่รันจริงแล้วในโฟลเดอร์ `scripts/` ข้างไฟล์นี้ **ห้ามเขียนใหม่** สคริปต์อ้างไฟล์กันด้วย path แบบสัมพัทธ์ จึงต้องวางเป็น `<lab>/code/` เสมอ (ดูขั้นที่ 0)

| สคริปต์ (`scripts/` → `<lab>/code/`) | หน้าที่ |
|---|---|
| `make_questions.py` | สร้างบทสนทนาฝั่งลูกค้า ≥ 500 บท (seed 2026) พร้อมเงื่อนไขของคำตอบทุกข้อความ (`expect`) ข้อมูลร้านอ่านจาก `web/db/init.sql` ตัดข้อความที่ซ้ำ/คล้ายชุดทดสอบ 26 เคสและปุ่มลัด → `<lab>/data/questions.jsonl` |
| `make_dataset.py` | ส่งคำถามให้โมเดลครูตอบ (system prompt เดียวกับเว็บ · temperature 0.3) ตรวจด้วย `expect` ผิดตอบใหม่ได้ 1 ครั้ง ยังผิดทิ้งทั้งบท แบ่ง Training 90% / Validation 10% (seed 7) · ทำต่อจากที่ค้างได้ → `data/train.jsonl` `val.jsonl` `teacher_raw.jsonl` `results/dataset_report.json` |
| `train.py` | QLoRA: โหลด 4-bit NF4 · LoRA r 8 / alpha 16 ที่ q k v o gate up down · ทีละ 1 บท สะสม 8 · lr 0.0002 · seed 0 · loss เฉพาะคำตอบผู้ช่วย · Validation loss ก่อนเทรนและทุก 20 step · เก็บ adapter รอบที่ดีที่สุด · เทรนต่อจาก checkpoint ได้ · `--epochs` `--model` `--out_dir` |
| `run_train.sh` | รัน `train.py` ซ้ำอัตโนมัติถ้า process ตาย (สูงสุด 5 ครั้ง) อาร์กิวเมนต์ส่งต่อให้ `train.py` · จบด้วย `TRAIN_OK` / `TRAIN_FAILED` |
| `serve.sh` | vLLM 0.11.0 พอร์ต 8000 OpenAI API · `qwen3-4b-base` + `qwen3-4b-sabaijai` (LoRA) บน GPU ใบเดียว · สุ่ม API key เก็บใน `/workspace/lab3/.vllm_api_key` (chmod 600) ไม่พิมพ์ออกจอ · ตัวแปร `BASE_MODEL` `ADAPTER_DIR` |
| `eval_val.py` | ให้ทั้งสองโมเดลตอบทุกข้อความใน Validation Set ด้วยประวัติแชทเดียวกัน (temperature 0) ตรวจด้วย `expect` · อ่าน VRAM ผ่าน `--ssh` · `--out` |
| `web/` | เว็บแชทบอท Next.js + PostgreSQL (Docker Compose project `vapp-lab3` พอร์ต 3403) · ตัวเลือกโมเดล Base/Fine-tuned · `/compare` · `/bookings` · `PUT /api/model` · `POST /api/reset` · อ่าน `../../chatbot.env` |
| `e2e/` | ชุดทดสอบ 26 เคส (Playwright) · `run-both.sh` รันกับ Base แล้ว Fine-tuned + รันซ้ำผ่าน API (`repeat.mjs`) + เทียบผล (`compare.mjs`) |

คู่มือเปิดโมเดลครูด้วย NInfer อยู่ที่ `references/ninfer_teacher.md` (ใช้เฉพาะเมื่อสร้าง Dataset ใหม่)

## ค่าที่ปรับได้ (ผู้ใช้ไม่บอก = ใช้ค่าเริ่มต้น)

| ค่า | ค่าเริ่มต้น | ความหมาย |
|---|---|---|
| `label` | `vapp-lab3` | ป้ายเครื่องเทรน/เสิร์ฟ · เครื่องครูใช้ `<label>-teacher` · แตะเฉพาะสองป้ายนี้ |
| `gpu` | RTX 3090 × 1 | GPU เครื่องเทรน+เสิร์ฟ (VRAM ≥ 24 GB · ใบเดียว) |
| `max_price` | $0.40/ชม. | เพดานราคารวม (GPU + disk) ของเครื่องเทรน |
| `teacher_gpu` / `teacher_max_price` | RTX 5090 × 1 / $1.20/ชม. | เครื่องโมเดลครู (ใช้เมื่อ `dataset` = ใหม่ เท่านั้น) |
| `base_model` | `Qwen/Qwen3-4B-Instruct-2507` | โมเดลตั้งต้น → `train.py --model` และ `BASE_MODEL=` ของ `serve.sh` (ต้องเป็นโมเดลแชทที่มี chat template และชั้นชื่อ q/k/v/o/gate/up/down_proj เช่นตระกูล Qwen / Llama ชื่อใน API ยังเป็น `qwen3-4b-base` / `qwen3-4b-sabaijai`) |
| `epochs` | 3 | จำนวน Epoch → `--epochs` (1 Epoch ≈ 55 step) |
| `dataset` | เดิม | `เดิม` = ใช้ `<lab>/data/train.jsonl` + `val.jsonl` ที่มีอยู่ ไม่เปิดโมเดลครู (ถ้าไม่มีไฟล์ → ถือเป็น `ใหม่`) · `ใหม่` = ขั้นที่ 1–2 ครบ |
| `web` | เปิด | `เปิด` = เว็บแชทบอท + ทดสอบ 26 เคสกับทั้งสองโมเดล · `ไม่` = จบที่วัดผล Validation Set |
| `e2e_repeat` | 5 | รันโจทย์ 26 เคสซ้ำกี่รอบต่อโมเดลผ่าน API (ใช้เมื่อ `web` เปิด) |
| `lab` | `lab3_qlora` | โฟลเดอร์งานบนเครื่องนี้ (มี `code/` `data/` `results/` และไฟล์ `.env`) |
| `out_dir` | `<lab>/results` | ที่เก็บผล ถ้ามีผลเดิมอยู่และผู้ใช้ไม่ได้สั่งให้ทับ → ใช้โฟลเดอร์ย่อยใหม่ เช่น `<lab>/results/skill_v0_run` |
| `keep_machine` | ไม่ | `ใช่` = ไม่ลบเครื่องตอนจบ (ต้องบอกผู้ใช้ชัดว่ายังคิดเงิน) |
| `container` | `multi-account` · `/workspace/vastapp_lab` | ที่ทำงานของสกิล vastai (โฟลเดอร์ `<lab>` ต้องมีใน container ด้วย) |
| `ssh_key` | `/workspace/vastai_lab/Devtool_SSH/devtoolSSH` | กุญแจ SSH ใน container |

## ขั้นตอน

จับเวลาทุกขั้นไว้ใช้ในสรุป · ห้ามแสดงค่า key ใด ๆ บนจอ (Vast API key · `instance_api_key` ที่คำสั่งสร้างเครื่องพิมพ์ออกมา — กรองผลก่อนแสดง · key ของครู · key ของ vLLM)

0. **เตรียมโฟลเดอร์** — ถ้า `<lab>/code/` ยังไม่มี ให้คัดลอก `scripts/*` ไปเป็น `<lab>/code/` (ถ้ามีแล้วใช้ของเดิม ไม่ทับ) และให้ `<lab>` มีครบทั้งบนเครื่องนี้และใน container `multi-account` · `.gitignore` ของ `<lab>` ต้องมี `*.env`
1. **คำถามลูกค้า** (เฉพาะ `dataset` = ใหม่) — `python3 code/make_questions.py` ตรวจว่าได้ ≥ 500 บท และรายงานผลตรวจไม่ซ้ำกับชุดทดสอบ
2. **โมเดลครู → Dataset** (เฉพาะ `dataset` = ใหม่)
   - ด้วยสกิล vastai เช่า `teacher_gpu` ราคา ≤ `teacher_max_price` ป้าย `<label>-teacher` ตามเกณฑ์และคำสั่งใน `references/ninfer_teacher.md` (verified · เน็ต > 2500 Mbps · CUDA ≥ 13.1 · disk 90 GB · `nvidia/cuda:13.1.2-devel-ubuntu24.04` · พอร์ต 8080 · โมเดล `neroued/Qwen3.8-27B-nvfp4-NInfer` ไฟล์ `qwen3_8_27b_nvfp4.ninfer` · ปิดขั้นคิด · API key สุ่มใหม่) ปกติพร้อมใน ~9 นาที
   - เขียน `<lab>/teacher.env` (`TEACHER_BASE_URL` `TEACHER_MODEL=qwen3.8-27b` `TEACHER_API_KEY`) ทดสอบ 1 คำถามไทย แล้วใน container รัน `python3 code/make_dataset.py` (8 บทพร้อมกัน ~10 นาที)
   - เห็น `dataset_report.json` แล้ว **ลบเครื่อง `<label>-teacher` ทันที** และตรวจว่าไม่เหลือ ก่อนไปขั้นถัดไป
3. **เช่าเครื่องเทรน** — ด้วยสกิล vastai ค้น `gpu` ราคา ≤ `max_price` · verified · RAM ≥ 24 GB · CUDA ≥ 13 · disk 60 GB · image `pytorch/pytorch:2.8.0-cuda12.8-cudnn9-devel` · **เปิดพอร์ต 8000** · ป้าย `label` รอจน SSH ได้และ `nvidia-smi` เห็น GPU (เครื่องถูกสุดอาจถูกเช่าไปแล้ว → ข้ามไปเครื่องถัดไป · ค้าง loading เกิน 10 นาที → ลบแล้วเช่าใหม่) สร้างไฟล์ช่วย SSH เช่น `/workspace/vastapp_lab/.lab3ssh` (รับคำสั่งเป็นอาร์กิวเมนต์) ไว้ใช้ต่อ
4. **ติดตั้งและอัปโหลด** — บนเครื่องเช่า (Python ของ `/opt/conda`): `pip install transformers peft bitsandbytes accelerate matplotlib` แล้ว `uv pip install --system vllm==0.11.0` (หรือ `pip install vllm==0.11.0`) คัดลอก `code/train.py` `run_train.sh` `serve.sh` → `/workspace/lab3/code/` และ `data/train.jsonl` `val.jsonl` → `/workspace/lab3/data/` โหลด `base_model` ล่วงหน้า (`hf download`)
5. **Training** — `cd /workspace/lab3/code && mkdir -p ../results/logs && setsid nohup bash run_train.sh --epochs <epochs> --model <base_model> > ../results/logs/train.log 2>&1 &`
   รายงานทุก ~5 นาทีจาก `/workspace/lab3/results/progress.json` (step · loss · val_loss) จนเจอ `TRAIN_OK` ใน log (3 Epoch ≈ 36 นาทีบน RTX 3090)
   ดึงกลับมาที่ `out_dir`: `adapter/` · `train_log.json` · `loss_curve.png` · `progress.json` · `run_state.json` · `logs/` (ไม่ต้องดึง `checkpoints/`) แล้วเปิดดู `loss_curve.png`
6. **AI server** — `ADAPTER_DIR=/workspace/lab3/results/adapter BASE_MODEL=<base_model> bash /workspace/lab3/code/serve.sh` (รอจน `ready: qwen3-4b-base, qwen3-4b-sabaijai` ~2–3 นาที) หาพอร์ตภายนอกที่แมปกับ 8000 แล้วเขียน `<lab>/chatbot.env` ทั้งบนเครื่องนี้และใน container:
   `OPENAI_BASE_URL=http://<ip>:<port>/v1` · `OPENAI_API_KEY` (อ่านจาก `/workspace/lab3/.vllm_api_key` ผ่าน SSH โดยไม่พิมพ์ค่า) · `BASE_MODEL=qwen3-4b-base` · `FT_MODEL=qwen3-4b-sabaijai`
   ทดสอบจากนอกเครื่อง: `/v1/models` เห็นสองชื่อ · ถามทั้งสองโมเดลได้คำตอบ · ไม่มี key ได้ 401
7. **วัดผล Validation Set** — ใน container ที่ `<lab>`: `python3 code/eval_val.py --out <out_dir>/val_eval.json --ssh /workspace/vastapp_lab/.lab3ssh > <out_dir>/val_eval.log` (~5 นาที) แล้วคัดลอกผลกลับมาบนเครื่องนี้
8. **เว็บ + ทดสอบ 26 เคส** (ถ้า `web` เปิด)
   - บนเครื่องนี้ (ไม่ใช่ใน container): `docker compose up -d --build` ใน `<lab>/code/web` รอ http://localhost:3403 ได้ 200 ลองหน้าแชทโมเดลละ 1 คำถาม · `/compare` 1 คำถาม · จอง 1 รายการให้ขึ้นใน `/bookings`
   - ใน container: `cd <lab>/code/e2e && BASE_URL=http://host.docker.internal:3403 REPEAT=<e2e_repeat> bash run-both.sh` (~20 นาที) แล้วเก็บผลไว้ที่ `<out_dir>/e2e/`: `COMPARE.md` `compare.json` `repeat.json` `run-both.log` · `base/` `ft/` (`TEST_REPORT.md` `results.json` `gifs/` `answers/`) · `diff-gifs/` (≤ 4 เคส) · ตรวจว่าไม่มี key/IP ในไฟล์ผล
9. **ปิดทุกอย่าง (ห้ามข้าม เว้นแต่ `keep_machine`)** — ตรวจว่าผลใน `out_dir` ครบก่อน · จดข้อมูลเครื่องลง `<out_dir>/close_record.json` (GPU · ราคา/ชม. · เวลาเปิด · GB ดาวน์โหลด/อัปโหลด · ค่าเช่าโดยประมาณ) · ด้วยสกิล vastai ลบเครื่องป้าย `label` (และ `<label>-teacher` ถ้ายังเหลือ) แล้วตรวจซ้ำว่าไม่เหลือ · ถ้าเปิดเว็บ `docker compose down` ใน `<lab>/code/web`

## เกณฑ์ตรวจผ่าน

- [ ] เครื่องเทรนเห็น GPU ตาม `gpu` ราคารวม ≤ `max_price` (เครื่องครู ≤ `teacher_max_price`)
- [ ] (ถ้า `dataset` ใหม่) `questions.jsonl` ≥ 500 บทไม่ซ้ำชุดทดสอบ · `dataset_report.json` มี passed / train / val · เครื่องครูถูกลบก่อนเช่าเครื่องเทรน
  - ค่าอ้างอิง: 570 บท → ผ่าน 485 (Training 437 · Validation 48) · ครูบน RTX 5090 $0.745/ชม.
- [ ] `train.log` มี `TRAIN_OK` · `train_log.json` มี `best_val_loss` < `val_loss_before` · มี `adapter/adapter_model.safetensors` และ `loss_curve.png`
  - ค่าอ้างอิง (3 Epoch, RTX 3090): Validation loss 1.004 → 0.307 (ดีสุด step 120 จาก 165) · เทรน 35.6 นาที · VRAM สูงสุด 22.9 GB · adapter 63 MB · 1 Epoch ควรได้ best_val_loss ≤ ~0.45
- [ ] server ผ่านทดสอบ 3 ข้อ (เห็นสองชื่อโมเดล · ตอบได้ทั้งคู่ · ไม่มี key = 401)
- [ ] `val_eval.json` มี `summary.base` และ `summary.finetuned` ครบทุกข้อความ (85 ข้อกับ Dataset เดิม) · `finetuned.correct_pct` ≥ `base.correct_pct`
  - ค่าอ้างอิง: คำตอบถูก 87.1% → 94.1% · ใส่แท็กจองก่อนข้อมูลครบ 6.5% → 1.3% · ไทยปนในคำตอบอังกฤษ 100% → 0% · แท็กจองรูปแบบ/ค่าถูก 100% ทั้งคู่ · ~50–55 token/วินาที
- [ ] (ถ้า `web`) เว็บตอบ 200 ลองครบ 4 อย่าง · มีรายงาน 26 เคสของทั้งสองโมเดลและ `repeat.json` — รายงานตามจริงแม้ Fine-tuned ไม่ดีขึ้น (ค่าอ้างอิง: Base 25/26 · Fine-tuned 25/26 ตกคนละเคส · รันซ้ำ 5 รอบได้ 25 ทุกรอบ · โมเดลครู 27B ผ่าน 26/26)
- [ ] ไม่มีเครื่องป้าย `label` / `<label>-teacher` ค้างในบัญชี (ยกเว้น `keep_machine`) และเว็บปิดแล้ว
- [ ] ไม่มีค่า key ใด ๆ ในคำตอบหรือไฟล์ผล · `teacher.env` `chatbot.env` ไม่ถูก commit

## กติกาเรื่องเงิน

1. **ลบเครื่องเสมอ** เมื่อจบงาน และเมื่อขั้นใดล้มจนไปต่อไม่ได้ — ดึงผลที่มีกลับมาก่อน ลบเครื่อง แล้วค่อยรายงานปัญหา
2. เครื่องครู (แพงกว่า ~3 เท่า) ลบทันทีที่ Dataset เสร็จ ห้ามเปิดค้างระหว่างเทรน · ห้ามมีเครื่องของงานนี้เปิดพร้อมกันเกิน 1 เครื่อง (เครื่องไม่ผ่านต้องลบก่อนเช่าใหม่)
3. ห้ามเช่าเครื่องที่ราคารวมเกินเพดาน ไม่มีเครื่องในเพดาน → หยุดแล้วถามผู้ใช้ ห้ามขยับเพดานเอง
4. แตะเฉพาะเครื่องป้าย `label` และ `<label>-teacher` ห้ามลบหรือแก้เครื่องป้ายอื่นในบัญชี (แม้ขึ้นต้นคล้ายกัน)
5. งานนานบนเครื่องเช่า (เทรน · server) รันแยกจาก SSH เสมอ การเชื่อมต่อหลุดต้องไม่ทำให้เทรนซ้ำ (`run_train.sh` + checkpoint ทุก 20 step)
6. `keep_machine` = ใช่ จึงข้ามการลบได้ — ต้องบอกชัดในสรุปว่าเครื่องยังเปิดและคิดเงินชั่วโมงละเท่าไร
7. งบอ้างอิงรอบเต็ม: เครื่องเทรน RTX 3090 $0.241/ชม. เปิด 1.41 ชม. ≈ $0.36 · เครื่องครู RTX 5090 $0.745/ชม. ~30 นาที ≈ $0.40 — ถ้าเครื่องใดเปิดเกิน 2 ชั่วโมงให้รายงานผู้ใช้ก่อนทำต่อ

## สรุปตอนจบ (ภาษาไทย)

ตาราง: เครื่องที่ได้ (GPU · ราคา · ที่ตั้ง) · เวลาแต่ละขั้น · Dataset (ทั้งหมด · ผ่าน · Training · Validation) · ตัวเลขการเทรน (Validation loss ก่อน/หลัง · step ที่ดีสุด · เวลา · VRAM · ขนาด adapter) · Base vs Fine-tuned บน Validation Set (ตัวเลข 6 ตัว + token/วินาที + VRAM server) · (ถ้าเปิดเว็บ) ผล 26 เคสและรันซ้ำ · ค่าใช้จ่ายจริง · ผลเกณฑ์ตรวจผ่านทีละข้อ · สถานะเครื่องและเว็บ (ลบ/ปิดแล้ว หรือยังเปิด)
