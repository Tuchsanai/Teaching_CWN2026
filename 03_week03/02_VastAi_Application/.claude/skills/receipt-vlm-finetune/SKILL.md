---
name: receipt-vlm-finetune
description: Fine-tune โมเดล Vision-Language Qwen3-VL-2B-Instruct ด้วย LoRA ให้อ่านใบเสร็จ (Dataset CORD-v2) แล้วตอบเป็น JSON บนเครื่อง GPU ที่เช่าจาก Vast.ai ครบวงจรในคำสั่งเดียว — เช่าเครื่อง → เตรียม Dataset → Training → เปิด AI server vLLM สองโมเดล (receipt-base / receipt-ft) → Evaluation Base vs Fine-tuned บน Test Set → (เลือกได้) เว็บสมุดรายจ่าย → ลบเครื่องและสรุปค่าใช้จ่าย ใช้เมื่อผู้ใช้สั่ง "ใช้สกิล receipt-vlm-finetune", "fine-tune โมเดลอ่านใบเสร็จ", "ทำ LAB 2 ซ้ำ", "เทรน VLM/Qwen-VL อ่านใบเสร็จบน Vast.ai" หรือขอทำซ้ำด้วยจำนวน Epoch / learning rate / LoRA rank / GPU / งบที่ต่างไปจากเดิม
---

# receipt-vlm-finetune (เวอร์ชัน 0)

ทำซ้ำงานของ LAB 2 ทั้งหมดในคำสั่งเดียว ทุกงานที่แตะ Vast.ai (ค้นหา เช่า SSH คัดลอกไฟล์ ดูบิล ลบเครื่อง) **ให้ใช้สกิล `vastai`** ใน container `multi-account` (`/root/ai-accounts/.Claude/shared/skills/vastai/SKILL.md`) — อ่านสกิลนั้นก่อนเริ่ม สกิลนี้ไม่สอนวิธีใช้ Vast.ai ซ้ำ บอกแค่ว่าต้องทำอะไร

โค้ดทั้งหมดใช้ชุดที่ทดสอบจริงแล้วในโฟลเดอร์ `scripts/` ข้างไฟล์นี้ **ห้ามเขียนใหม่** คัดลอกขึ้นเครื่องเช่าที่ `/workspace/lab2/code/` แล้วรันตามขั้นตอน

| สคริปต์ | หน้าที่ |
|---|---|
| `receipt_data.py` | โหลด CORD-v2 (แบ่ง train/validation/test ตาม Dataset) ย่อภาพด้านยาว ≤ 1280 px แปลงเฉลยเป็น JSON และเก็บ `PROMPT` ชุดเดียวที่ใช้ทั้งเทรน วัดผล และเว็บ |
| `train.py` | LoRA บนชั้น Linear ของส่วนภาษา (ส่วนมองภาพไม่แตะ) loss เฉพาะคำตอบ JSON วัด validation loss ก่อนเทรนและหลังทุก Epoch มี checkpoint ทุก 25 step รันซ้ำแล้วเทรนต่อได้ |
| `run_train.sh` | รัน `train.py` แยกจาก SSH ล้มแล้วรันใหม่ต่อจาก checkpoint (อาร์กิวเมนต์เพิ่มส่งต่อให้ `train.py`) |
| `serve.sh` | vLLM OpenAI-compatible พอร์ต 8000 · `receipt-base` + `receipt-ft` (LoRA) บน GPU ใบเดียว · สุ่ม API key เก็บบนเครื่องเช่าเท่านั้น · `start` / `status` / `stop` |
| `eval.py` | ส่ง Test Set 100 ใบให้ทั้งสองโมเดล temperature 0 · คะแนน JSON อ่านได้ / ยอดรวมตรง / Item F1 / วินาทีต่อใบ · `metrics.json` กราฟ และภาพตัวอย่าง · รันซ้ำแล้วข้ามใบที่ทำแล้ว |

## ค่าที่ปรับได้ (ผู้ใช้ไม่บอก = ใช้ค่าเริ่มต้น)

| ค่า | ค่าเริ่มต้น | ความหมาย |
|---|---|---|
| `label` | `vapp-lab2` | ป้ายเครื่องบน Vast.ai (แตะเฉพาะเครื่องป้ายนี้) |
| `gpu` | RTX 4090 × 1 | รุ่นและจำนวน GPU (ต้องมี VRAM ≥ 24 GB) |
| `max_price` | $0.80/ชม. | ราคารวมสูงสุด (GPU + disk) |
| `offer_filter` | verified · เน็ตลง ≥ 500 Mbps · ค่าดาวน์โหลด ≤ $0.01/GB · driver รองรับ CUDA 13 · เลือกถูกสุด | เกณฑ์เลือกเครื่อง (งานนี้โหลดราว 11–15 GB) |
| `image` | `pytorch/pytorch:2.7.1-cuda12.8-cudnn9-devel` | image ของเครื่อง |
| `disk_gb` | 60 | ขนาด disk |
| `min_hf_speed` | 20 MB/s | ทดสอบโหลดจาก Hugging Face ช้ากว่านี้ → ลบแล้วเช่าเครื่องอื่น |
| `ready_timeout` | 10 นาที | รอเครื่องพร้อมเกินนี้ → ลบแล้วเช่าเครื่องอื่น |
| `base_model` | `Qwen/Qwen3-VL-2B-Instruct` | โมเดลตั้งต้น (ค่าคงที่ใน `train.py` / `serve.sh`) |
| `dataset` | `naver-clova-ix/cord-v2` (train 800 · validation 100 · test 100) | Dataset |
| `epochs` | 2 | จำนวน Epoch → `--epochs` |
| `lr` | 0.0002 | learning rate → `--lr` (warmup 10 step แล้วลดเชิงเส้นถึง 0) |
| `lora_rank` / `lora_alpha` | 8 / 16 | LoRA → `--rank` `--alpha` (rank > 8 ต้องเปิด server ด้วย `MAX_LORA_RANK=<rank>`) |
| `grad_accum` | 4 | ป้อนทีละ 1 ใบ สะสม gradient กี่ใบก่อนปรับน้ำหนัก → `--grad-accum` |
| `seed` | 0 | → `--seed` |
| `out_dir` | `lab2_vlm/results` | โฟลเดอร์เก็บผลบนเครื่องนี้ (มีผลเดิมอยู่และผู้ใช้ไม่ได้สั่งให้ทับ → ใช้โฟลเดอร์ย่อยใหม่ เช่น `lab2_vlm/results/skill_v0_run`) |
| `web` | เปิด | เปิดเว็บสมุดรายจ่าย `lab2_vlm/code/web` ที่ http://localhost:3404 และทดสอบ test_092 test_051 test_020 |
| `keep_machine` | ไม่ | `ใช่` = ไม่ลบเครื่องตอนจบ (ต้องบอกผู้ใช้ชัดว่ายังคิดเงิน) |
| `container` | `multi-account` · `/workspace/vastapp_lab` | ที่ทำงานของสกิล vastai |
| `ssh_key` | `/workspace/vastai_lab/Devtool_SSH/devtoolSSH` | กุญแจ SSH ใน container |

## ขั้นตอน

จับเวลาทุกขั้นไว้ใช้ในสรุป · ทุกคำตอบห้ามแสดงค่า key ใด ๆ (Vast · HF_TOKEN · RECEIPT_API_KEY)

1. **เช่าเครื่อง** — ด้วยสกิล vastai ค้นหาตาม `gpu` `max_price` `offer_filter` เช่าด้วย `image` `disk_gb` ตั้งป้าย `label` **เปิดพอร์ต 8000** รอจน SSH เข้าได้และ `nvidia-smi` เห็น GPU
   - ทดสอบความเร็วโหลดจาก Hugging Face (โหลด `base_model` ไปเลยเพื่อไม่ต้องโหลดซ้ำ) ช้ากว่า `min_hf_speed` หรือเกิน `ready_timeout` → ลบทันทีแล้วเช่าเครื่องถัดไป
   - เครื่องที่ถูกที่สุดอาจถูกคนอื่นเช่าไปแล้ว (สร้างไม่ได้) → ข้ามไปเครื่องถัดไป
2. **เตรียมเครื่องและ Dataset** — บนเครื่องเช่าสร้าง venv `/workspace/lab2/venv` ติดตั้ง `vllm peft datasets matplotlib` (vllm ดึง torch ที่ตรงกับตัวเองมาให้) คัดลอก `scripts/*` ขึ้นไปที่ `/workspace/lab2/code/` แล้วรัน
   `python receipt_data.py prepare --out /workspace/lab2/data` และ `python receipt_data.py samples --out /workspace/lab2/data --save /workspace/lab2/dataset_samples.jpg`
   - `HF_TOKEN` อ่านจาก `.env` ของโฟลเดอร์บท ส่งผ่าน stdin ของ SSH ใช้แค่ในคำสั่งนั้น ห้ามใส่ในบรรทัดคำสั่ง ห้ามเขียนลงไฟล์ เสร็จแล้วตรวจว่าไม่มี `~/.cache/huggingface/token` และตัวแปร `HF_TOKEN` ค้าง
3. **Training** — `cd /workspace/lab2/code && setsid nohup bash run_train.sh --epochs <epochs> --lr <lr> --rank <lora_rank> --alpha <lora_alpha> --grad-accum <grad_accum> --seed <seed> &` (แยกจาก SSH)
   รายงานความคืบหน้าทุก ~2 นาทีจาก `/workspace/lab2/out/train.log` (ขึ้นทุก 10 step) จนเจอบรรทัด `DONE`
   ผล: `/workspace/lab2/out/adapter/` · `loss_curve.png` · `train_info.json` · `history.json` · `train.log`
4. **AI server** — `bash serve.sh start` (รอจนพร้อม ปกติ ~3 นาที) หาพอร์ตภายนอกที่แมปกับ 8000 แล้วทดสอบจากนอกเครื่อง 3 ข้อ: `GET /v1/models` เห็น `receipt-base` และ `receipt-ft` · ส่ง `test_020` ให้ `receipt-ft` พร้อม key ได้ JSON · ไม่มี key ได้ 401
   - ถ้า `web` เปิด: เขียน `lab2_vlm/code/receipt.env` (`RECEIPT_BASE_URL=http://<ip>:<port>/v1` `RECEIPT_API_KEY` `RECEIPT_MODEL_BASE=receipt-base` `RECEIPT_MODEL_FT=receipt-ft`) อ่าน key จาก `/workspace/lab2/secret/api_key` ผ่าน SSH โดยไม่พิมพ์ค่าออกมา
5. **Evaluation** — บนเครื่องเช่า `cd /workspace/lab2/code && /workspace/lab2/venv/bin/python eval.py --data /workspace/lab2/data --out /workspace/lab2/eval --train-info /workspace/lab2/out/train_info.json` (รันแยกจาก SSH, ~3–5 นาที)
   ดึงผลกลับมาที่ `out_dir`: `eval/` (metrics.json · predictions_*.jsonl · images/) · `adapter/` · `train/` (loss_curve.png · train_info.json · history.json · train.log) · `dataset_samples.jpg` เปิดดู `eval/images/examples.jpg` อย่างน้อย 1 รูป
6. **เว็บ** (ถ้า `web`) — `docker compose up -d --build` ใน `lab2_vlm/code/web` (project `vapp-lab2`) รอ http://localhost:3404 ได้ 200 แล้วอ่าน test_092 test_051 test_020 ผ่านเว็บด้วยทั้งสองโมเดล จด รายการที่อ่านถูก · ยอดรวมถูก/ผิด · เวลา
7. **ปิดทุกอย่าง (ห้ามข้าม เว้นแต่ `keep_machine`)** — ตรวจว่าผลใน `out_dir` ครบก่อน แล้วด้วยสกิล vastai ลบเครื่องป้าย `label` และตรวจซ้ำว่าไม่เหลือในบัญชี · ถ้าเปิดเว็บ `docker compose down` **ไม่ใส่ `-v`** (เก็บรายจ่ายใน volume `vapp-lab2_dbdata`) · ดูบิลจริง (invoices): อายุเครื่อง ราคาต่อชั่วโมง ยอด GPU · disk · รับส่งข้อมูล

## เกณฑ์ตรวจผ่าน

- [ ] เครื่องเห็น GPU ตาม `gpu` ราคารวม ≤ `max_price` และโหลดจาก Hugging Face ≥ `min_hf_speed`
- [ ] Dataset ครบ: Training 800 ใบ (2,416 รายการ) · Validation 100 (270) · Test 100 (287) และไม่มี HF_TOKEN ค้างบนเครื่องเช่า
- [ ] `train.log` มี `DONE` · พารามิเตอร์ที่เทรน ≈ 0.4% ของทั้งโมเดล (rank 8) · validation loss หลัง Epoch สุดท้าย < ก่อนเทรน
- [ ] server ผ่านทดสอบครบ 3 ข้อ (เห็นสองโมเดล · ได้ JSON · ไม่มี key = 401)
- [ ] `out_dir/eval/metrics.json` มี `base` และ `fine_tuned` ครบ 100 ใบ · `fine_tuned.total_exact_pct` ≥ `base.total_exact_pct` และ `fine_tuned.item_f1_pct` > `base.item_f1_pct`
  - ค่าอ้างอิง (2 Epoch, RTX 4090): ยอดรวมตรง 88.4% → 100% · Item F1 69.9% → 88.4% · val loss 0.299 → 0.022 · เทรน 9.2 นาที · VRAM สูงสุด 8.6 GB · adapter 34.9 MB
  - `epochs` ≥ 2 ต้องได้ Item F1 ของ Fine-tuned ≥ 85% · 1 Epoch ต้อง ≥ 80%
- [ ] `out_dir` มี adapter · กราฟ loss · กราฟ Base vs Fine-tuned · ภาพตัวอย่าง
- [ ] (ถ้า `web`) เว็บตอบ 200 และอ่านใบตัวอย่างได้ครบ 3 ใบด้วยทั้งสองโมเดล
- [ ] ไม่มีเครื่องป้าย `label` ค้างในบัญชี (ยกเว้น `keep_machine`)
- [ ] ไม่มีค่า key ใด ๆ ปรากฏในคำตอบหรือไฟล์ผลลัพธ์ (`receipt.env` อยู่ใน `.gitignore` / ไม่ commit)

## กติกาเรื่องเงิน

1. **ลบเครื่องเสมอ** เมื่อจบงาน และเมื่อขั้นใดล้มจนไปต่อไม่ได้ — ก่อนหยุดให้ดึงผลที่มีกลับมา ลบเครื่อง แล้วค่อยรายงานปัญหา
2. ห้ามเช่าเครื่องที่ราคารวมเกิน `max_price` ห้ามเช่าพร้อมกันเกิน 1 เครื่อง (เครื่องไม่ผ่านต้องลบก่อนเช่าใหม่)
3. แตะเฉพาะเครื่องป้าย `label` ห้ามลบหรือแก้เครื่องป้ายอื่นในบัญชี
4. `keep_machine` = ใช่ จึงข้ามการลบได้ — ต้องบอกชัดในสรุปว่าเครื่องยังเปิดและคิดเงินชั่วโมงละเท่าไร
5. งานนานบนเครื่องเช่า (เทรน · server · วัดผล) รันแยกจาก SSH เสมอ การเชื่อมต่อหลุดต้องไม่ทำให้เทรนหรือวัดผลซ้ำ (สคริปต์เทรนต่อจาก checkpoint และวัดผลต่อจากใบที่ทำแล้วได้)
6. งบอ้างอิงรอบเต็ม (2 Epoch + เว็บ): เครื่องเปิด ~74 นาที จ่ายจริง ~$0.53 — ถ้าเครื่องเปิดเกิน 2 ชั่วโมงให้รายงานผู้ใช้ก่อนทำต่อ

## สรุปตอนจบ (ภาษาไทย)

ตาราง: เครื่องที่ได้ (GPU · ราคา · ประเทศ · ความเร็วโหลด HF) · เวลาแต่ละขั้น · ตัวเลขการเทรน (พารามิเตอร์ที่เทรน · val loss ก่อน/หลังแต่ละ Epoch · เวลา · VRAM · ขนาด adapter) · Base vs Fine-tuned (JSON อ่านได้ · ยอดรวมตรง · Item F1 · วินาทีต่อใบ) · ผลทดสอบ server/เว็บ · ค่าใช้จ่ายจริง · ผลเกณฑ์ตรวจผ่านทีละข้อ · สถานะเครื่อง (ลบแล้ว / ยังเปิด)
